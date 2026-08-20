import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Finance RAG Project sri.sakticharan.ny@gmail.com"}
TICKERS = ["AAPL", "MSFT", "NVDA"]
RAW_DIR = Path("data/raw")


def get_cik_map() -> dict:
    """Map ticker symbols to their 10-digit zero-padded CIK numbers."""
    url = "https://www.sec.gov/files/company_tickers.json"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    return {entry["ticker"]: str(entry["cik_str"]).zfill(10) for entry in data.values()}


def get_latest_10k(cik: str):
    """Return (accession_number, primary_doc_filename, filing_date) for the most recent 10-K."""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    recent = r.json()["filings"]["recent"]

    for i, form in enumerate(recent["form"]):
        if form == "10-K":
            accession = recent["accessionNumber"][i].replace("-", "")
            primary_doc = recent["primaryDocument"][i]
            filing_date = recent["filingDate"][i]
            return accession, primary_doc, filing_date
    return None


def download_filing_text(cik: str, accession: str, primary_doc: str) -> str:
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary_doc}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Strip out hidden XBRL metadata block + scripts/styles - not part of the readable filing
    for tag in soup.find_all(["ix:header", "script", "style"]):
        tag.decompose()
    for tag in soup.find_all(style=re.compile(r"display:\s*none")):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cik_map = get_cik_map()

    for ticker in TICKERS:
        cik = cik_map.get(ticker)
        if not cik:
            print(f"[skip] No CIK found for {ticker}")
            continue

        result = get_latest_10k(cik)
        if not result:
            print(f"[skip] No 10-K found for {ticker}")
            continue

        accession, primary_doc, filing_date = result
        print(f"Downloading {ticker} 10-K (filed {filing_date})...")
        text = download_filing_text(cik, accession, primary_doc)

        out_path = RAW_DIR / f"{ticker}_{filing_date}_10k.txt"
        out_path.write_text(text, encoding="utf-8")
        print(f"  Saved {out_path}  ({len(text):,} characters)")

        time.sleep(0.5)  # stay well under SEC's rate limit


if __name__ == "__main__":
    main()