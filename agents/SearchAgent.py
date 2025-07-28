from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser

# If you get a NotImplementedError here or later, see the Heads Up at the top of the notebook

async_browser =  create_async_playwright_browser(headless=False)  # headful mode
toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
tools = toolkit.get_tools()

for tool in tools:
    print(f"Tool name: {tool.name}, Description: {tool.description}")


from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain.agents import AgentExecutor
from dotenv import load_dotenv
import os
import asyncio
from langchain_ollama import ChatOllama


async def main():
    load_dotenv(override=True)


    llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
    # llm.bind_tools(tools)
    # llm = ChatOllama(model="qwen3:14b")
    agent = create_react_agent(llm, tools)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    while True:
        prompt = input("\nAsk: ")
        if prompt.lower() in ["exit", "quit"]:
            break

        response = await agent_executor.ainvoke({
            "messages": [HumanMessage(content=prompt)]
        })

        print("\n" + response["messages"][-1].content)
    
asyncio.run(main())