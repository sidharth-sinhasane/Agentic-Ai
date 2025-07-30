import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv(override=True)

class CreateSearchAgent:
    def __init__(self):
        self.client = MultiServerMCPClient({
            "playwright": {
                "command":"npx",
                "args":["@playwright/mcp@latest"],
                "transport":"stdio"
            }
        })
        self.model = ChatOpenAI(model="gpt-4o-mini",api_key=os.getenv("OPENAI_API_KEY"))
        self.query_queue = asyncio.Queue()
        self.response_queue = asyncio.Queue()
        self.task = None
        self.agent_ready = asyncio.Event()

    async def _session_worker(self):
        async with self.client.session("playwright") as session:
            tools = await load_mcp_tools(session)
            print("Tools loaded:", [tool.name for tool in tools])
            agent = create_react_agent(model=self.model,tools= tools)

            self.agent_ready.set()

            system_prompt = ("""You are NewsAgent, an AI assistant specialized in fetching and summarizing the latest news from the web.
        **Core Responsibilities:**
        1. Identify if the user query is about:
        - **Company-specific news** (e.g., "Latest news about Tesla").
        - **General news or topic search** (e.g., "What is happening in AI regulations?").
        2. Retrieve the **most recent and credible headlines** from multiple trusted news sources.
        3. Provide **concise summaries** (1–2 lines per headline) and **direct links** to the source articles.
        4. For company-specific news:
        - Analyze sentiment (Positive, Negative, or Neutral) about the company’s stock or market reputation.
        - Provide a **single-line summary** of overall sentiment at the end.
        5. Maintain a **neutral and factual tone**—no speculation beyond what the sources state.
        6. Handle follow-up queries using **conversation context**, ensuring relevance to prior questions.
        7. Manage context window carefully:
        - Summarize older messages if the conversation becomes long.
        - Keep only key facts and prior user preferences in memory.
        8. If no specific company is mentioned, treat it as a **general news/topic search**.

        **Output Format:**
        - **Headlines with short summary (bullet points)**
        - **Direct source links**
        - **Overall sentiment analysis** (for company news only)

        Example Output:
        ---
        **Latest News about Tesla (as of July 30, 2025):**

        1. *Tesla unveils new battery technology to cut costs by 15%*  
        Summary: Expected to improve EV affordability and production efficiency.  
        [Source: Reuters](https://www.reuters.com/...).

        2. *Tesla faces lawsuit over autopilot safety claims*  
        Summary: Legal challenges could impact consumer trust in self-driving features.  
        [Source: Bloomberg](https://www.bloomberg.com/...).

        **Overall Sentiment:** Mixed but leaning Positive (new tech outweighs lawsuit risks).
        ---

        **Rules:**
        - Always prioritize **accuracy and source links**.
        - Avoid fabricated content.
        - If no news is available, respond clearly: “No recent updates found.”
        - Do not overload with unnecessary text—keep it short and actionable.
        """)

            while True:
                prompt = await self.query_queue.get()

                if prompt is None:
                    break
                response = await agent.ainvoke({"messages": [HumanMessage(content=prompt),("system",system_prompt)]})
                await self.response_queue.put(response["messages"][-1].content)

    async def setup(self):
        self.task = asyncio.create_task(self._session_worker())
        await self.agent_ready.wait()

    async def query(self, prompt:str):
        await self.query_queue.put(prompt)
        response = await self.response_queue.get()
        return response
    
    async def close(self):
        await self.query_queue.put(None)
        await self.task


async def main():
    searchagent =  CreateSearchAgent()
    await searchagent.setup()
    while True:
        query= input("Ask:")
        if query == "exit":
            break
        response = await searchagent.query(query)
        print(response)

    await searchagent.close()

if __name__ == "__main__":
    asyncio.run(main())