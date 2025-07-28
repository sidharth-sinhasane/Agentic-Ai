import asyncio
from ZerodhaAgent import CreateZerodhaAgent

async def main():
    zerodha_agent = CreateZerodhaAgent()
    await zerodha_agent.setup()  # start session

    while True:
        query = input("\nAsk (or type exit): ")
        if query.lower() in ["exit", "quit"]:
            break
        response = await zerodha_agent.query(query)
        print("\n" + response)

    await zerodha_agent.close()

if __name__ == "__main__":
    asyncio.run(main())
