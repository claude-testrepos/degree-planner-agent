from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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
    answer, trace = agent.run([m.model_dump() for m in req.messages])
    return {"answer": answer, "trace": trace}


@app.get("/api/health")
def health():
    return {"ok": True}


app.mount("/", StaticFiles(directory="web", html=True), name="web")
