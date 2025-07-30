from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
# from langchain.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from ZerodhaAgent import CreateZerodhaAgent
from IPython.display import Image, display
from SearchAgent import CreateSearchAgent
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

class SearchWrapper:
    _instance = None
    _agent = None
    _isSetUp= False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchWrapper,cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if SearchWrapper._agent is None:
            SearchWrapper._agent = CreateSearchAgent()

    async def setup(self):
        if self._isSetUp == False:
            self._isSetUp = True
            await self._agent.setup()

    async def query(self, prompt:str):
        return await self._agent.query(prompt)
    
    async def close(self):
        await self._agent.close()



class GraphState(TypedDict):
    next_step: Literal["zerodha_agent", "end","search_agent"]
    query: str
    response: str



from langchain.output_parsers import StructuredOutputParser, ResponseSchema

response_schemas = [
    ResponseSchema(name="next_step", description="Must be either 'zerodha_agent' or 'end' or 'search_agent"),
    ResponseSchema(name="query", description="The query text from the user"),
    ResponseSchema(name="response", description="Your response to the query")
]

parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = parser.get_format_instructions()

prompt = PromptTemplate(
    template="""
You are Master Agent. Answer ONLY in JSON with keys `next_step`, `query`, and `response`.
Next step must be either "zerodha_agent" or "end" or 'search_agent'. if the query is about latest news search about a company then and then only call search_agent
User Query: {query}

{format_instructions}
""",
    input_variables=["query"],
    partial_variables={"format_instructions": format_instructions},
)


master_llm = ChatOpenAI(model="gpt-4o", temperature=0)


async def master_agent_node(state: GraphState) -> GraphState:
    chain = prompt | master_llm | parser
    output = await chain.ainvoke({"query": state["query"]})
    return {"next_step": output["next_step"], "query": output["query"], "response": output}



async def zerodha_node(state: GraphState) -> GraphState:
    print(state["query"])
    await ZerodhaWrapper().setup()
    result = await ZerodhaWrapper().query(state["query"])
    # await ZerodhaWrapper().close()
    return {"next_step": "master_agent", "query": f""" I am zerodha agent, this was the user query {state['query']} forwarded to me from you and this is what my answer to it {result} i have done my job now send this back to user """, "response": result}


async def search_node(state: GraphState)->GraphState:
    print(state["query"])

    await SearchWrapper().setup()
    result = await SearchWrapper().query(state["query"])

    return {"next_step":"master_agent","query" : f""" I am search agent, this was the user query {state['query']} forwarded to me from you and this is what my answer to it {result} i have done my job now send this back to user""","response":result}


from langgraph.graph import StateGraph, END

graph = StateGraph(GraphState)

graph.add_node("master_agent", master_agent_node)
graph.add_node("zerodha_agent", zerodha_node)
graph.add_node("search_agent",search_node)

# Entry point
graph.set_entry_point("master_agent")

# Conditional routing
graph.add_conditional_edges(
    "master_agent",
    lambda state: state["next_step"],
    {
        "zerodha_agent": "zerodha_agent",
        "end": END,
        "search_agent":"search_agent"
    }
)

graph.add_edge("zerodha_agent", "master_agent")
graph.add_edge("search_agent", "master_agent")

app = graph.compile()


if __name__ == "__main__":
    import asyncio

    async def main():
        while True:
            query = input()
            if query == "exit":
                break
            initial_state = {"next_step": "", "query": query, "response": ""}
            result = await app.ainvoke(initial_state)
            print(result["response"]["response"])
        

    asyncio.run(main())
    # png_data = app.get_graph().draw_png()
     
    # with open("graph.png","wb") as f:
    #     f.write(png_data)

    # print("graph saved")

