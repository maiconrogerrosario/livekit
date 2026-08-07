import asyncio
import os

from dotenv import load_dotenv
from livekit import api


load_dotenv()


async def main() -> None:
    livekit_url = os.getenv("LIVEKIT_HTTP_URL", "http://localhost:7880")
    api_key = os.getenv("LIVEKIT_API_KEY", "devkey")
    api_secret = os.getenv("LIVEKIT_API_SECRET", "secret")

    lkapi = api.LiveKitAPI(
        url=livekit_url,
        api_key=api_key,
        api_secret=api_secret,
    )

    try:
        # Cria o inbound trunk para chamadas ao número 500.
        trunk_request = api.CreateSIPInboundTrunkRequest(
            trunk=api.SIPInboundTrunkInfo(
                name="MicroSIP local",
                numbers=["500"],
            )
        )

        trunk = await lkapi.sip.create_inbound_trunk(trunk_request)

        print("Inbound trunk criado:")
        print(f"ID: {trunk.sip_trunk_id}")
        print(f"Nome: {trunk.name}")

        # Cria uma regra que coloca cada chamada em uma sala exclusiva.
        dispatch_rule = api.SIPDispatchRule(
            dispatch_rule_individual=api.SIPDispatchRuleIndividual(
                room_prefix="microsip-",
            )
        )

        dispatch_request = api.CreateSIPDispatchRuleRequest(
            dispatch_rule=api.SIPDispatchRuleInfo(
                name="MicroSIP para agente",
                rule=dispatch_rule,
                trunk_ids=[trunk.sip_trunk_id],
            )
        )

        dispatch = await lkapi.sip.create_dispatch_rule(dispatch_request)

        print("\nDispatch rule criada:")
        print(f"ID: {dispatch.sip_dispatch_rule_id}")
        print(f"Nome: {dispatch.name}")

        print("\nConfiguração concluída.")
        print("Ligue pelo MicroSIP para:")
        print("sip:500@192.168.15.8:5060")

    finally:
        await lkapi.aclose()


if __name__ == "__main__":
    asyncio.run(main())