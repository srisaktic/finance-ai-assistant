import os
from dotenv import load_dotenv
from tavily import TavilyClient
from src.usage_tracker import track_call

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_news(query: str, max_results: int = 5) -> list[dict]:
    """Search for recent news articles related to the query."""
    track_call("tavily")
    response = tavily_client.search(
        query=query,
        topic="news",
        max_results=max_results,
    )

    return [
        {
            "title": r["title"],
            "url": r["url"],
            "excerpt": r["content"],
            "published_date": r.get("published_date"),
            "relevance_score": r.get("score"),
        }
        for r in response.get("results", [])
    ]


if __name__ == "__main__":
    results = search_news("Nvidia stock news")
    for r in results:
        print(f"[{r['relevance_score']:.2f}] {r['title']} ({r['published_date']})")
        print(f"  {r['url']}")