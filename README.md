# Search Engine

A command-line search engine tool that crawls [quotes.toscrape.com](https://quotes.toscrape.com), builds an inverted index, and lets you search for words and phrases through a simple terminal interface.

---

## Project Overview

This tool downloads every page on the target website, extracts the visible text, and builds an inverted index that records every word along with which pages it appears on, how many times, and at what positions. You can then query the index to find pages by word or phrase, all without making any further network requests.


## Project Structure

```
search-engine-WebService/
├── src/
│   ├── crawler.py       - Web crawler
│   ├── indexer.py       - Tokeniser and inverted index builder
│   ├── search.py        - Search and query processing
│   ├── storage.py       - Save and load index to/from file
│   └── main.py          - Command-line interface
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   ├── test_search.py
│   └── test_storage.py
├── data/                - Generated index file stored here (not tracked by git)
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone <repo-url>
cd search-engine-WebService
pip install -r requirements.txt
```


## Usage

```bash
python src/main.py
```

Once running, type one of the following commands at the `>` prompt:

| Command | Description | Example |
|---|---|---|
| `build` | Crawls the site and builds the index (takes several minutes due to the 6-second politeness window) | `build` |
| `load` | Loads a previously built index instantly from file | `load` |
| `print <word>` | Looks up a single word and shows which pages contain it | `print love` |
| `find <query>` | Finds all pages containing every word in the query, ranked by frequency | `find good friends` |
| `quit` | Exits the program | `quit` |


## How It Works

The tool runs a four-stage pipeline. The **crawler** downloads every page on the site using a 6-second delay between requests, staying within the same domain. The raw HTML is passed to the **indexer**, which strips tags, lowercases all text, removes punctuation, and splits the content into tokens. These tokens are stored in an **inverted index** that maps each word to the pages it appears on, including a count and a list of positions. The index is then saved to disk as a JSON file by the **storage** module, and can be queried at any time using the **search** module.


## Testing

```bash
pytest tests/ -v
```

There are **34 tests** in total covering the crawler, indexer, storage, and search modules. All tests use mocking and do not make real network calls.

## Design Decisions

- The inverted index stores both word count and positions for each page, allowing frequency-based ranking and potential future use of positional data.
- Multi-word queries use AND logic: a page must contain every query word to appear in results.
- Results are ranked by total word frequency across all query terms, so the most relevant pages appear first.
- A 6-second politeness window is enforced between every request as required by the coursework specification.
- Single-character tokens are filtered out during tokenisation to reduce noise in the index.
- The index is saved as JSON for simplicity and human readability.


## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP requests |
| `beautifulsoup4` | HTML parsing |
| `pytest` | Testing |
