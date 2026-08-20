import json
import re
from pathlib import Path

import tiktoken

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

CHUNK_SIZE = 400     # target tokens per chunk
CHUNK_OVERLAP = 50   # tokens shared between consecutive chunks

encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(encoding.encode(text))


def split_into_paragraphs(text: str) -> list[str]:
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def split_into_sentences(paragraph: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    return [s.strip() for s in sentences if s.strip()]

SECTION_HEADER_ALLCAPS = re.compile(r'(?m)^ITEM\s+\d+[A-C]?\.')
SECTION_HEADER_MIXEDCASE = re.compile(r'(?m)^Item\s+\d+[A-C]?\.')
MIN_SECTION_GAP = 2000  # chars — filters Table of Contents / inline references out of the mixed-case matches


def find_section_boundaries(text: str) -> list[int]:
    """Find character positions where a real 10-K section starts."""
    allcaps_matches = list(SECTION_HEADER_ALLCAPS.finditer(text))
    if len(allcaps_matches) >= 15:
        return [m.start() for m in allcaps_matches]

    matches = list(SECTION_HEADER_MIXEDCASE.finditer(text))
    positions = [m.start() for m in matches] + [len(text)]
    boundaries = []
    for i in range(len(matches)):
        gap = positions[i + 1] - positions[i]
        if gap > MIN_SECTION_GAP:
            boundaries.append(matches[i].start())
    return boundaries


def split_into_sections(text: str) -> list[str]:
    boundaries = find_section_boundaries(text)
    if not boundaries:
        return [text]  # no sections found — treat whole doc as one section, safe fallback

    if boundaries[0] > 0:
        boundaries = [0] + boundaries  # keep front matter/cover page as its own leading section

    sections = []
    for i in range(len(boundaries)):
        start = boundaries[i]
        end = boundaries[i + 1] if i + 1 < len(boundaries) else len(text)
        sections.append(text[start:end])
    return sections

def chunk_text(text: str) -> list[str]:
    sections = split_into_sections(text)
    all_chunks = []
    for section in sections:
        all_chunks.extend(chunk_section(section))
    return all_chunks

def chunk_section(text: str) -> list[str]:
    paragraphs = split_into_paragraphs(text)
    chunks: list[str] = []
    current, current_tokens = "", 0

    def flush():
        nonlocal current, current_tokens
        if current.strip():
            chunks.append(current.strip())
        current, current_tokens = "", 0

    for para in paragraphs:
        para_tokens = count_tokens(para)

        if para_tokens > CHUNK_SIZE:
            # paragraph too big on its own -> fall back to sentence splitting
            for sentence in split_into_sentences(para):
                sent_tokens = count_tokens(sentence)
                if current_tokens + sent_tokens > CHUNK_SIZE:
                    flush()
                current += sentence + " "
                current_tokens += sent_tokens
            continue

        if current_tokens + para_tokens > CHUNK_SIZE:
            flush()

        current += para + "\n\n"
        current_tokens += para_tokens

    flush()

    # add overlap: prepend the tail of each chunk to the next one
    overlapped = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            overlapped.append(chunk)
        else:
            prev_tokens = encoding.encode(chunks[i - 1])
            tail = encoding.decode(prev_tokens[-CHUNK_OVERLAP:])
            overlapped.append(tail + " " + chunk)

    return overlapped


def process_file(filepath: Path) -> list[dict]:
    text = filepath.read_text(encoding="utf-8")
    ticker = filepath.stem.split("_")[0]
    chunks = chunk_text(text)

    return [
        {
            "id": f"{filepath.stem}_chunk{i}",
            "ticker": ticker,
            "source_file": filepath.name,
            "chunk_index": i,
            "text": chunk,
            "token_count": count_tokens(chunk),
        }
        for i, chunk in enumerate(chunks)
    ]


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for filepath in sorted(RAW_DIR.glob("*.txt")):
        print(f"Chunking {filepath.name}...")
        records = process_file(filepath)
        out_path = PROCESSED_DIR / f"{filepath.stem}_chunks.json"
        out_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        print(f"  {len(records)} chunks -> {out_path}")


if __name__ == "__main__":
    main()