from src.rag.retrieve import retrieve


def print_results(query: str, results, rewritten: str = None):
    print(f"\nQuery: {query}")
    if rewritten:
        print(f"  (rewritten: {rewritten})")
    if not results:
        print("  No confident match found.")
        return
    for r in results:
        p = r["payload"]
        snippet = p["text"][:200].replace("\n", " ")
        print(f"  [rerank={r['rerank_score']:.3f}, orig={r['original_score']:.3f}] {p['ticker']} chunk#{p['chunk_index']} - {snippet}...")



EVAL_QUESTIONS = [
    # Apple
    "What does Apple say about supply chain risks?",
    "What is Apple's strategy for growing its services revenue?",
    "What risks does Apple identify related to competition?",
    "What does Apple say about foreign currency exchange risk?",
    "What does Apple say about tariffs and trade regulations?",

    # Microsoft
    "How does Microsoft describe its cloud computing segment?",
    "What does Microsoft say about cybersecurity risks?",
    "What is Microsoft's approach to artificial intelligence investments?",
    "How does Microsoft describe its competitive landscape?",
    "What does Microsoft say about regulatory and antitrust risk?",

    # Nvidia
    "What risks does Nvidia identify related to manufacturing and supply chain?",
    "How does Nvidia describe demand for its data center products?",
    "What does Nvidia say about export restrictions or trade regulations?",
    "What employee-related risks does Nvidia disclose?",
    "What does Nvidia say about competition in the semiconductor industry?",
]



def main():
    for question in EVAL_QUESTIONS:
        results, rewritten = retrieve(question, top_k=3)
        print_results(question, results, rewritten)

if __name__ == "__main__":
    main()