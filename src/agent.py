import logging
from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, JobProcess, RoomInputOptions, RoomOutputOptions, WorkerOptions, cli, metrics
from livekit.agents.voice import MetricsCollectedEvent
from livekit.plugins import elevenlabs, noise_cancellation, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from decrypt import decrypt_system_prompt
logger = logging.getLogger("agent")
load_dotenv(".env.local")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=decrypt_system_prompt())

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    try:
        ctx.log_context_fields = { "room": ctx.room.name }
        session = AgentSession(
            llm=openai.LLM(model="gpt-4.1-nano"),
            stt=openai.STT(model="whisper-1"),
            tts=elevenlabs.TTS(),
            turn_detection=MultilingualModel(),
            vad=ctx.proc.userdata["vad"],
        )
        usage_collector = metrics.UsageCollector()
        @session.on("metrics_collected")
        def _on_metrics_collected(ev: MetricsCollectedEvent):
            try:
                metrics.log_metrics(ev.metrics)
                usage_collector.collect(ev.metrics)
            except Exception as e:
                logger.warning(f"Error collecting metrics: {e}")
        async def log_usage():
            try:
                summary = usage_collector.get_summary()
                logger.info(f"Usage: {summary}")
            except Exception as e:
                logger.warning(f"Error logging usage: {e}")
        ctx.add_shutdown_callback(log_usage)
        await ctx.connect()
        await session.start(
            agent=Assistant(),
            room=ctx.room,
            room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
            room_output_options=RoomOutputOptions(transcription_enabled=True),
        )
    except Exception as e:
        logger.error(f"Error in entrypoint: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
