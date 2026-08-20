import os
#import anthropic
#from google import genai
from dotenv import load_dotenv
from src.llm_client import call_gemini

load_dotenv()

#client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

#client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

ANSWER_PROMPT = """You are a financial research assistant. Answer the user's question using ONLY the information in the context below, which is excerpted from company SEC filings (10-Ks).

Rules:
- Only use information present in the context. Do not use outside knowledge.
- If the context does not contain enough information to answer the question, say so clearly instead of guessing.
- Write a direct, synthesized answer in your own words — do not summarize each source separately. Weave information from multiple sources together into one coherent answer that directly addresses the question first.
- Cite which source you used for each claim, using the format [Ticker, chunk #N] right after the relevant sentence.
- Keep the answer focused and readable — a few short paragraphs, not an exhaustive report with many subheadings, unless the question specifically asks for a breakdown.

Context:
{context}

Question: {question}

Answer:"""

def format_context(chunks: list) -> str:
    parts = []
    for c in chunks:
        p = c["payload"]
        parts.append(f"[{p['ticker']}, chunk#{p['chunk_index']}]\n{p['text']}")
    return "\n\n".join(parts)


''' 
def generate_answer(question: str, chunks: list) -> str:
    if not chunks:
        return "I couldn't find enough information in the filings to answer this question confidently."

    context = format_context(chunks)
    prompt = ANSWER_PROMPT.format(context=context, question=question)

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()

    '''
def generate_answer(question: str, chunks: list) -> str:
    if not chunks:
        return "I couldn't find enough information in the filings to answer this question confidently."

    context = format_context(chunks)
    prompt = ANSWER_PROMPT.format(context=context, question=question)

    interaction = call_gemini(input=prompt, generation_config={"max_output_tokens": 1500})
    return interaction.output_text.strip()

