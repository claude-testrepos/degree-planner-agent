from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from openai import OpenAIError
from pydantic import BaseModel

from . import agent

app = FastAPI(title="Planwise")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@app.post("/api/chat")
def chat(req: ChatRequest):
    try:
        answer, trace = agent.run([m.model_dump() for m in req.messages])
    except OpenAIError as e:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {e}") from e
    return {"answer": answer, "trace": trace}


@app.get("/api/health")
def health():
    return {"ok": True}


app.mount("/", StaticFiles(directory="web", html=True), name="web")
