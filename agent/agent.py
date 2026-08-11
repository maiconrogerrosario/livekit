import logging
import os

from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    cli,
    UserInputTranscribedEvent,
    ConversationItemAddedEvent,
)

from livekit.agents.llm import ChatMessage
from livekit.plugins import openai


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("livekit-agent")


INSTRUCTIONS = """
Você é um assistente de voz em português do Brasil.
Responda de forma curta, clara e natural.
Pare de falar quando o usuário interromper.
"""


class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions=INSTRUCTIONS
        )


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext):

    logger.info("Job recebido para a sala: %s", ctx.room.name)

    await ctx.connect()

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model=os.getenv(
                "OPENAI_REALTIME_MODEL",
                "gpt-realtime-2",
            ),
            voice=os.getenv(
                "OPENAI_REALTIME_VOICE",
                "marin",
            ),
            modalities=["text", "audio"],
        )
    )

    # =========================================================
    # TRANSCRIÇÃO DO USUÁRIO
    # =========================================================
    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event: UserInputTranscribedEvent):

        if event.is_final:
            print(
                f"\n👤 USUÁRIO: {event.transcript}",
                flush=True,
            )

    # =========================================================
    # MENSAGENS DA CONVERSA
    # Inclui mensagens do usuário e do agente
    # =========================================================
    @session.on("conversation_item_added")
    def on_conversation_item_added(
        event: ConversationItemAddedEvent
    ):

        item = event.item

        if not isinstance(item, ChatMessage):
            return

        # Evita imprimir novamente a fala do usuário,
        # pois já imprimimos acima.
        if item.role == "assistant":
            print(
                f"\n🤖 AGENTE: {item.text_content}",
                flush=True,
            )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
    )

    await session.generate_reply(
        instructions=(
            "Cumprimente o usuário brevemente em português "
            "e pergunte como pode ajudá-lo."
        )
    )


if __name__ == "__main__":
    cli.run_app(server)