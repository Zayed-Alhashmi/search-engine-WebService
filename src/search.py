# search.py
# Query functions for looking up words and finding matching pages in the index.

import math


# Looks up a single word in the index and returns a formatted result string
def print_word(index: dict, word: str) -> str:
    word = word.lower()

    if word not in index:
        return f"Word '{word}' not found in index."

    lines = [f"Results for '{word}':"]
    for url, data in index[word].items():
        lines.append(f"  {url}")
        lines.append(f"    count: {data['count']}")
        lines.append(f"    positions: {data['positions']}")

    return "\n".join(lines)


# Calculates the TF-IDF relevance score for a single word on a single page
def calculate_tfidf(index: dict, word: str, page_url: str, total_pages: int) -> float:
    count = index[word][page_url]["count"]

    # Total words on this page = sum of all word counts for this URL
    total_words_on_page = sum(
        index[w][page_url]["count"]
        for w in index
        if page_url in index[w]
    )

    tf = count / total_words_on_page if total_words_on_page > 0 else 0  # normalises for page length

    pages_with_word = len(index[word])  # number of pages the word appears on

    idf = math.log(1 + total_pages / pages_with_word)  # smoothed to avoid 0 when word is on every page

    return tf * idf


# Returns a TF-IDF ranked list of page URLs that contain every word in the query (AND logic)
def find_pages(index: dict, query: str) -> list[str]:
    words = query.lower().split()

    if not words:
        return []

    # Find pages that contain every query word
    matching_pages = None
    for word in words:
        if word not in index:
            return []  # if any word is missing entirely, no results possible
        pages_for_word = set(index[word].keys())
        if matching_pages is None:
            matching_pages = pages_for_word
        else:
            matching_pages = matching_pages & pages_for_word  # AND intersection

    if not matching_pages:
        return []

    # Total unique pages across the entire index
    all_pages = set(url for word_data in index.values() for url in word_data)
    total_pages = len(all_pages)

    # Rank by summed TF-IDF score across all query words (highest score first)
    def tfidf_score(url):
        return sum(calculate_tfidf(index, word, url, total_pages) for word in words)

    return sorted(matching_pages, key=tfidf_score, reverse=True)
