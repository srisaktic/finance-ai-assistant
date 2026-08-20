from src.rag.query_processing import detect_ticker


def test_detect_ticker_apple():
    assert detect_ticker("What does Apple say about risk?") == "AAPL"


def test_detect_ticker_nvidia_lowercase():
    assert detect_ticker("nvda stock price") == "NVDA"


def test_detect_ticker_none():
    assert detect_ticker("What is the weather today?") is None