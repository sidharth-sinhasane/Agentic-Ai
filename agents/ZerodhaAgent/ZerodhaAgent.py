from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import asyncio
import logging
load_dotenv()


class ZerodhaAgent1:
    client = MultiServerMCPClient({
        "kite": {
            "command": "npx",
            "args": ["mcp-remote", "https://mcp.kite.trade/sse"],
            "transport": "stdio"
        }
    })

    model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
    
    async def initialize(self):
        async with self.client.session("kite") as session:
            tools = await load_mcp_tools(session)
            print("Tools loaded:", [tool.name for tool in tools])
            agent = create_react_agent(self.model, tools)
        return agent


