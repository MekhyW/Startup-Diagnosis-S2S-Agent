import logging
import os
from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, JobProcess, RoomInputOptions, RoomOutputOptions, WorkerOptions, cli, metrics
from livekit.agents.voice import MetricsCollectedEvent
from livekit.plugins import elevenlabs, noise_cancellation, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
logger = logging.getLogger("agent")
load_dotenv(".env.local")

with open("system_prompt.txt", "r", encoding='utf-8') as f:
    system_prompt = f.read()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=system_prompt)

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
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
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)
    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")
    ctx.add_shutdown_callback(log_usage) # shutdown callbacks are triggered when the session is over
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
        room_output_options=RoomOutputOptions(transcription_enabled=True),
    )
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
