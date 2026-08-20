from fastapi import FastAPI
from pydantic import BaseModel
from src.agent.orchestrator import run_agent

app = FastAPI(title="Finance AI Assistant")


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