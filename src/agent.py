import asyncio
import logging
import uuid
from datetime import datetime
from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, JobProcess, RoomInputOptions, RoomOutputOptions, WorkerOptions, metrics, cli
from livekit.agents.voice import MetricsCollectedEvent
from livekit.agents import ConversationItemAddedEvent
from livekit.agents.llm import ImageContent, AudioContent
from livekit.plugins import elevenlabs, openai, google, silero, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from decrypt import decrypt_system_prompt
from transcription_manager import TranscriptionManager
from report_generator import ReportGenerator
from s3_handler import S3Handler
logger = logging.getLogger("agent")
load_dotenv(".env.local")

class Assistant(Agent):
    def __init__(self, transcription_manager: TranscriptionManager) -> None:
        super().__init__(instructions=decrypt_system_prompt())
        self.transcription_manager = transcription_manager
        self.interview_completed = False
    
    async def add_message(self, role, message):
        """Called when conversation item is added"""
        if 'assistant' in role:
            await self.transcription_manager.add_agent_message(message)
        else:
            await self.transcription_manager.add_user_message(message)

    async def mark_interview_complete(self):
        """Mark the interview as completed"""
        self.interview_completed = True
        await self.transcription_manager.stop_recording()
        logger.info("Interview marked as complete")

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    interview_id = f"INT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
    transcription_manager = TranscriptionManager(interview_id)
    report_generator = ReportGenerator()
    s3_handler = S3Handler()
    try:
        ctx.log_context_fields = { "room": ctx.room.name, "interview_id": interview_id }
        await transcription_manager.start_recording()
        session = AgentSession(
            llm=google.LLM(model="gemini-2.5-pro", temperature=0.3),
            stt=openai.STT(model="whisper-1", language="pt"),
            tts=elevenlabs.TTS(),
            turn_detection=MultilingualModel(),
            vad=ctx.proc.userdata["vad"],
        )
        assistant = Assistant(transcription_manager)
        usage_collector = metrics.UsageCollector()
        
        @session.on("metrics_collected")
        def _on_metrics_collected(ev: MetricsCollectedEvent):
            try:
                metrics.log_metrics(ev.metrics)
                usage_collector.collect(ev.metrics)
            except Exception as e:
                logger.warning(f"Error collecting metrics: {e}")
        
        @session.on("conversation_item_added")
        def _on_conversation_item_added(event: ConversationItemAddedEvent):
            async def handle_conversation_item_added():
                try:
                    for content in event.item.content:
                        if isinstance(content, str):
                            if event.item.interrupted:
                                content += " [INTERROMPIDO]"
                            await assistant.add_message(event.item.role, content)
                        elif isinstance(content, ImageContent):
                            print(f" - image: {content.image}") # image is either a rtc.VideoFrame or URL to the image
                        elif isinstance(content, AudioContent):
                            print(f" - audio: {content.frame}, transcript: {content.transcript}") # frame is a list[rtc.AudioFrame]
                except Exception as e:
                    logger.warning(f"Error handling agent speech: {e}")
            asyncio.create_task(handle_conversation_item_added())
        
        async def process_interview_completion():
            """Process interview completion: generate report and upload to S3"""
            try:
                logger.info("Processing interview completion...")
                full_transcription = await transcription_manager.get_full_transcription()
                conversation_only = await transcription_manager.get_conversation_only()
                logger.info("Uploading full transcription to S3...")
                transcription_key = await s3_handler.upload_transcription(interview_id, full_transcription)
                if transcription_key:
                    logger.info(f"Transcription uploaded to S3: {transcription_key}")
                else:
                    logger.error("Failed to upload transcription to S3")
                logger.info("Generating structured report...")
                report_data = await report_generator.generate_report(conversation_only, interview_id)
                if report_data:
                    logger.info("Uploading report to S3...")
                    report_key = await s3_handler.upload_report(interview_id, report_data)
                    if report_key:
                        logger.info(f"Report uploaded to S3: {report_key}")
                    else:
                        logger.error("Failed to upload report to S3")
                else:
                    logger.error("Failed to generate report")
            except Exception as e:
                logger.error(f"Error processing interview completion: {e}", exc_info=True)
        
        async def log_usage():
            try:
                summary = usage_collector.get_summary()
                logger.info(f"Usage: {summary}")
            except Exception as e:
                logger.warning(f"Error logging usage: {e}")
        
        async def shutdown_callback():
            await log_usage()
            if not assistant.interview_completed:
                await assistant.mark_interview_complete()
            await process_interview_completion()
        
        ctx.add_shutdown_callback(shutdown_callback)
        await ctx.connect()
        await session.start(
            agent=assistant,
            room=ctx.room,
            room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
            room_output_options=RoomOutputOptions(transcription_enabled=True),
        )
    except Exception as e:
        logger.error(f"Error in entrypoint: {e}", exc_info=True)
        try:
            if 'transcription_manager' in locals():
                await transcription_manager.stop_recording()
        except:
            pass
        raise


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
