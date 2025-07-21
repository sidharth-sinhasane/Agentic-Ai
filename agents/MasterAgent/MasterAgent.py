from langchain_core.messages import HumanMessage
import ZerodhaAgent.ZerodhaAgent as ZerodhaAgent

async def main():
    while True:
        prompt = input("\nAsk: ")
        if prompt.lower() in ["exit", "quit"]:
            break

        zerodha_agent = ZerodhaAgent.ZerodhaAgent1()

        agent = await zerodha_agent.initialize()
        response = await agent.ainvoke({
            "messages": [HumanMessage(content=prompt)]
        })

        print("\n" + response["messages"][-1].content)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())