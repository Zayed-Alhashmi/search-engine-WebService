# indexer.py
# Builds an inverted index from crawled HTML pages for use by the search engine.

import re

from bs4 import BeautifulSoup


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
