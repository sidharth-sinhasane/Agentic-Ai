from fastapi import FastAPI, Request
from pydantic import BaseModel
from agents.MasterAgent import app as agent
from fastapi.responses import StreamingResponse

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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
    print(initial_state)

    async def event_stream():
        async for step in agent.astream(initial_state, config=config):
            # Ensure 'response' exists and normalize value
            response_data = step.get("response")
            
            if isinstance(response_data, dict):
                # Master agent node format
                message = response_data.get("response", "")
            else:
                # Zerodha/Search nodes format
                message = response_data or ""
            
            if message:
                yield message + "\n"


    return StreamingResponse(event_stream(),media_type="text/plain")

@app.post("/invokeNonStream")
async def invokeNonStream(request_data: query):
    config = {"configurable": {"thread_id": request_data.threadId}}
    initial_state = {"next_step": "", "query": request_data.content, "response": ""}
    result = await agent.ainvoke(initial_state, config=config)
    return result["response"]["response"]