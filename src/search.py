# search.py
# Query functions for looking up words and finding matching pages in the index.


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


# Returns a ranked list of page URLs that contain every word in the query (AND logic)
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

    # Rank by total frequency across all query words (highest count first)
    def total_count(url):
        return sum(index[word][url]["count"] for word in words)

    return sorted(matching_pages, key=total_count, reverse=True)
