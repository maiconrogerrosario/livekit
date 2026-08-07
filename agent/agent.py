import logging, os
from dotenv import load_dotenv
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, cli
from livekit.plugins import openai
load_dotenv(); logging.basicConfig(level=logging.INFO)
logger=logging.getLogger("livekit-agent")
INSTRUCTIONS="""Você é um assistente de voz em português do Brasil. Responda de forma curta, clara e natural. Pare de falar quando o usuário interromper."""
class Assistant(Agent):
    def __init__(self): super().__init__(instructions=INSTRUCTIONS)
server=AgentServer()
@server.rtc_session()
async def entrypoint(ctx: JobContext):
    logger.info("Job recebido para a sala: %s", ctx.room.name)
    await ctx.connect()
    session=AgentSession(llm=openai.realtime.RealtimeModel(
        model=os.getenv("OPENAI_REALTIME_MODEL","gpt-realtime-2"),
        voice=os.getenv("OPENAI_REALTIME_VOICE","marin"),
        modalities=["text","audio"],
    ))
    await session.start(room=ctx.room, agent=Assistant())
    await session.generate_reply(instructions="Cumprimente o usuário brevemente em português e pergunte como pode ajudá-lo.")
if __name__=="__main__": cli.run_app(server)
