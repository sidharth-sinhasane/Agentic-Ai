import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

class CreateZerodhaAgent:
    def __init__(self):
        self.client = MultiServerMCPClient({
            "kite": {
                "command": "npx",
                "args": ["mcp-remote", "https://mcp.kite.trade/sse"],
                "transport": "stdio"
            }
        })
        self.model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
        self.query_queue = asyncio.Queue()
        self.response_queue = asyncio.Queue()
        self.task = None
        self.agent_ready = asyncio.Event()  # defined ONCE

    async def _session_worker(self):
        async with self.client.session("kite") as session:
            tools = await load_mcp_tools(session)
            print("Tools loaded:", [tool.name for tool in tools])
            agent = create_react_agent(self.model, tools)

            self.agent_ready.set()  # mark ready after tools are loaded

            while True:
                prompt = await self.query_queue.get()
                if prompt is None:
                    break
                response = await agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
                await self.response_queue.put(response["messages"][-1].content)

    async def setup(self):
        self.task = asyncio.create_task(self._session_worker())
        await self.agent_ready.wait()  # wait until tools loaded

    async def query(self, prompt: str):
        await self.query_queue.put(prompt)
        return await self.response_queue.get()

    async def close(self):
        await self.query_queue.put(None)
        await self.task
