from fastapi import FastAPI
from pydantic import BaseModel
from src.agent.orchestrator import run_agent

app = FastAPI(title="Finance AI Assistant")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest):
    answer = run_agent(request.question)
    return AnswerResponse(answer=answer)