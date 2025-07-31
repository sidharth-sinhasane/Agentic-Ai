from fastapi import FastAPI, Request
from pydantic import BaseModel
from agents.MasterAgent import app as agent

app = FastAPI()



@app.get("/heartbeat")
def heartbeat():
    return {"status":"alive"}

class query(BaseModel):
    content: str
    threadId: str

@app.post("/invoke")
async def invoke(request_data: query):
    config = {"configurable": {"thread_id": request_data.threadId}}
    initial_state = {"next_step": "", "query": request_data.content, "response": ""}
    result =await agent.ainvoke(initial_state,config=config)

    return {"response":result["response"]["response"]}