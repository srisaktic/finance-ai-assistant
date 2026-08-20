from src.rag.query_processing import detect_ticker, rewrite_query
from src.rag.search import search
from src.rag.rerank import rerank
from src.logger import logger

MIN_CONFIDENCE_SCORE = 0.5  # calibrated from real eval data: strong matches mostly 0.7+, weak-but-plausible ones ~0.5-0.55


def retrieve(question: str, top_k: int = 5, fetch_k: int = 15):
    ticker = detect_ticker(question)
    logger.info(f"Question: '{question}' | Detected ticker: {ticker}")
    rewritten = rewrite_query(question)
    logger.info(f"Rewritten query: '{rewritten}'")

    original_results = search(question, top_k=fetch_k, ticker=ticker)
    rewritten_results = search(rewritten, top_k=fetch_k, ticker=ticker)

    combined = {}
    for r in original_results + rewritten_results:
        if r.id not in combined or r.score > combined[r.id].score:
            combined[r.id] = r
    candidates = list(combined.values())
    logger.info(f"Candidate pool size: {len(candidates)}")

    reranked = rerank(question, candidates, top_k=top_k)

    if not reranked or reranked[0]["rerank_score"] < MIN_CONFIDENCE_SCORE:
        top_score = reranked[0]["rerank_score"] if reranked else "N/A"
        logger.warning(f"Low confidence (top score: {top_score}, threshold: {MIN_CONFIDENCE_SCORE}) — returning no results")
        return [], rewritten

    logger.info(f"Top rerank score: {reranked[0]['rerank_score']:.3f} — returning {len(reranked)} chunks")
    return reranked, rewritten

'''

    candidates = list(combined.values())
    reranked = rerank(question, candidates, top_k=top_k)

    if not reranked or reranked[0]["rerank_score"] < MIN_CONFIDENCE_SCORE:
        return [], rewritten

    return reranked, rewritten

'''

