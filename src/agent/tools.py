from src.rag.retrieve import retrieve
from src.tools.market_data import get_stock_price
from src.tools.calculator import calculate_ratio, calculate_percentage_change
from src.tools.news_search import search_news


def tool_search_filings(question: str) -> list[dict]:
    """Search SEC 10-K filings. Wraps retrieve() and returns raw chunks, not a generated answer."""
    chunks, _ = retrieve(question)
    return [
        {
            "ticker": c["payload"]["ticker"],
            "chunk_index": c["payload"]["chunk_index"],
            "text": c["payload"]["text"],
        }
        for c in chunks
    ]


TOOLS = [
    {
        "type": "function",
        "name": "search_filings",
        "description": "Search SEC 10-K filings (Apple, Microsoft, Nvidia) for qualitative info like risks, strategy, business description. Include the company name in the question text.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Question to search the filings for, including the company name"}
            },
            "required": ["question"],
        },
    },
    {
        "type": "function",
        "name": "get_stock_price",
        "description": "Get current stock price and key stats (day/year high-low, market cap) for a ticker.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. AAPL, MSFT, NVDA"}
            },
            "required": ["ticker"],
        },
    },
    {
        "type": "function",
        "name": "calculate_ratio",
        "description": "Compute a ratio between two financial figures (e.g. debt-to-equity, margin).",
        "parameters": {
            "type": "object",
            "properties": {
                "numerator": {"type": "number"},
                "denominator": {"type": "number"},
                "label": {"type": "string", "description": "Name of the ratio, e.g. 'debt-to-equity'"},
            },
            "required": ["numerator", "denominator"],
        },
    },
    {
        "type": "function",
        "name": "calculate_percentage_change",
        "description": "Compute percentage change between two values (e.g. revenue growth).",
        "parameters": {
            "type": "object",
            "properties": {
                "old_value": {"type": "number"},
                "new_value": {"type": "number"},
                "label": {"type": "string", "description": "Name of the metric, e.g. 'revenue growth'"},
            },
            "required": ["old_value", "new_value"],
        },
    },
    {
        "type": "function",
        "name": "search_news",
        "description": "Search recent news articles about a company or topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "description": "Number of articles to return, default 5"},
            },
            "required": ["query"],
        },
    },
]

TOOL_FUNCTIONS = {
    "search_filings": tool_search_filings,
    "get_stock_price": get_stock_price,
    "calculate_ratio": calculate_ratio,
    "calculate_percentage_change": calculate_percentage_change,
    "search_news": search_news,
}