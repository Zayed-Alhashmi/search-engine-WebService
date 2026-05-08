# indexer.py
# Builds an inverted index from crawled HTML pages for use by the search engine.
# Also handles saving and loading the index to and from disk as a JSON file.

import json
import os
import re

from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_INDEX_PATH = os.path.join(BASE_DIR, "data", "index.json")


# Strips all HTML tags, scripts, and styles and returns plain readable text
def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style"]):  # remove non-visible content
        tag.decompose()

    return soup.get_text(separator=" ")


# Converts raw text into a clean list of lowercase words with no punctuation
def tokenise(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)  # strip punctuation
    tokens = text.split()
    tokens = [t for t in tokens if len(t) > 1]  # drop single-char tokens
    return tokens


# Builds the full inverted index from a dict of {url: html} pages
# Structure: {word: {url: {"count": int, "positions": [int, ...]}}}
def build_index(pages: dict[str, str]) -> dict:
    index: dict = {}

    for url, html in pages.items():
        text = extract_text(html)
        tokens = tokenise(text)

        for position, word in enumerate(tokens):
            if word not in index:
                index[word] = {}

            if url not in index[word]:
                index[word][url] = {"count": 0, "positions": []}

            index[word][url]["count"] += 1
            index[word][url]["positions"].append(position)

    return index


# Serialises the index dict to JSON and writes it to the given filepath
def save_index(index: dict, filepath: str = DEFAULT_INDEX_PATH) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)  # create folder if missing
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print(f"Index saved to {filepath}")


# Reads the JSON file at filepath and returns it as a Python dict
def load_index(filepath: str = DEFAULT_INDEX_PATH) -> dict:
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Index file not found at '{filepath}'. "
            "Please run the 'build' command first."
        )
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
