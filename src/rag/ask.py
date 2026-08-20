from src.rag.retrieve import retrieve
from src.rag.generate import generate_answer


def ask(question: str) -> str:
    chunks, rewritten = retrieve(question)
    return generate_answer(question, chunks)


if __name__ == "__main__":
    test_question = "What does Apple say about foreign currency exchange risk?"
    print(ask(test_question))