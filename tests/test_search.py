# test_search.py
# Unit tests for src/search.py. Uses a small hand-built index, no file I/O.

import pytest

from src.search import find_pages, print_word

# Small index used across most tests
# Page A has "good" twice and "morning" once
# Page B has "good" once and "night" once
SAMPLE_INDEX = {
    "good": {
        "https://example.com/a": {"count": 2, "positions": [0, 5]},
        "https://example.com/b": {"count": 1, "positions": [3]},
    },
    "morning": {
        "https://example.com/a": {"count": 1, "positions": [1]},
    },
    "night": {
        "https://example.com/b": {"count": 1, "positions": [4]},
    },
}


# Checks that print_word returns formatted output including count and positions
def test_print_word_returns_formatted_output():
    result = print_word(SAMPLE_INDEX, "morning")
    assert "morning" in result
    assert "https://example.com/a" in result
    assert "count: 1" in result
    assert "[1]" in result


# Checks that print_word lowercases the query so "Good" finds "good" in the index
def test_print_word_is_case_insensitive():
    result = print_word(SAMPLE_INDEX, "Good")
    assert "good" in result
    assert "https://example.com/a" in result


# Checks that print_word returns a not-found message for a word absent from the index
def test_print_word_returns_not_found_message():
    result = print_word(SAMPLE_INDEX, "unknown")
    assert "not found" in result
    assert "unknown" in result


# Checks that find_pages returns pages that contain the queried word
def test_find_pages_single_word_match():
    result = find_pages(SAMPLE_INDEX, "morning")
    assert "https://example.com/a" in result


# Checks that find_pages only returns pages containing every word in a multi-word query
def test_find_pages_multi_word_and_logic():
    result = find_pages(SAMPLE_INDEX, "good morning")
    assert "https://example.com/a" in result     # has both "good" and "morning"
    assert "https://example.com/b" not in result  # missing "morning"


# Checks that find_pages returns an empty list when no page contains all query words
def test_find_pages_no_match_returns_empty():
    result = find_pages(SAMPLE_INDEX, "morning night")  # no page has both
    assert result == []


# Checks that find_pages returns an empty list when the query string is blank
def test_find_pages_empty_query_returns_empty():
    result = find_pages(SAMPLE_INDEX, "")
    assert result == []


# Checks that results are ranked by total frequency with the highest count page first
def test_find_pages_ranks_by_frequency():
    result = find_pages(SAMPLE_INDEX, "good")
    # page A has count 2, page B has count 1, so A should come first
    assert result[0] == "https://example.com/a"
    assert result[1] == "https://example.com/b"


# Checks that find_pages lowercases the query so "Good" matches "good" in the index
def test_find_pages_is_case_insensitive():
    result = find_pages(SAMPLE_INDEX, "GOOD")
    assert "https://example.com/a" in result
    assert "https://example.com/b" in result
