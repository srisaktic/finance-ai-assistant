from fastapi import FastAPI
from pydantic import BaseModel
from src.agent.orchestrator import run_agent
from src.llm_client import call_gemini

app = FastAPI(title="Finance AI Assistant")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "https://finance-ai-ui-vercel.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str
    previous_interaction_id: str | None = None


class AnswerResponse(BaseModel):
    answer: str
    interaction_id: str


class SummarizeRequest(BaseModel):
    text: str


class SummarizeResponse(BaseModel):
    summary: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest):
    answer, interaction_id = run_agent(
        request.question,
        previous_interaction_id=request.previous_interaction_id,
    )
    return AnswerResponse(answer=answer, interaction_id=interaction_id)


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    interaction = call_gemini(
        system_instruction=(
            "Condense the following financial answer into 2-3 short, plain-English "
            "sentences. Keep the key numbers and facts. Do not add new information "
            "that isn't already in the text."
        ),
        input=request.text,
    )
    return SummarizeResponse(summary=interaction.output_text.strip())