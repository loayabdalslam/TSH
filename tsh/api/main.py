from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tsh import get_default_agent
import uvicorn

app = FastAPI(title="TSH API", description="Agentic API for TSH")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@app.post("/ask", response_model=QueryResponse)
async def ask_tsh(request: QueryRequest):
    try:
        agent = get_default_agent()
        response = await agent.run(request.query)
        return QueryResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_api()
