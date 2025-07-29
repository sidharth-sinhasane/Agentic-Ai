import asyncio
from ZerodhaAgent import CreateZerodhaAgent

class ZerodhaWrapper:
    _instance = None
    _agent = None
    _isSetUp = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ZerodhaWrapper, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if ZerodhaWrapper._agent is None:
            ZerodhaWrapper._agent = CreateZerodhaAgent()
        # return ZerodhaWrapper._agent

    async def setup(self):
        if self._isSetUp == False:
            self._isSetUp=True
            await self._agent.setup()

    async def query(self, prompt: str):
        print(prompt)

        return await self._agent.query(prompt)

    async def close(self):
        await self._agent.close()

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


# class ZerodhaWrapper:
#     _instance = None
#     _agent = None

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(ZerodhaWrapper, cls).__new__(cls)
#         return cls._instance

#     def __init__(self):
#         if ZerodhaWrapper._agent is None:
#             ZerodhaWrapper._agent = CreateZerodhaAgent()

#     async def setup(self):
#         await self._agent.setup()

#     async def query(self, prompt: str):
#         return await self._agent.query(prompt)

#     async def close(self):
#         await self._agent.close()