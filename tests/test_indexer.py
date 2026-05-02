# test_indexer.py
# Unit tests for src/indexer.py. No network calls are made.

import pytest

from src.indexer import build_index, tokenise

# Simple HTML page used in build_index tests
PAGE_A_URL = "https://quotes.toscrape.com/"
PAGE_A_HTML = """
<html><body>
  <p>The quick brown fox jumps over the lazy dog</p>
</body></html>
"""

PAGE_B_URL = "https://quotes.toscrape.com/page/2/"
PAGE_B_HTML = """
<html><body>
  <p>The fox ran quickly across the field</p>
</body></html>
"""


# Checks that tokenise lowercases all words correctly
def test_tokenise_lowercases_text():
    result = tokenise("Hello World PYTHON")
    assert result == ["hello", "world", "python"]


# Checks that punctuation is stripped from tokens
def test_tokenise_removes_punctuation():
    result = tokenise("hello, world! it's great.")
    assert "hello" in result
    assert "world" in result
    assert "great" in result


# Checks that single-character tokens like "a" or "I" are filtered out
def test_tokenise_filters_single_char_tokens():
    result = tokenise("I ate a big apple")
    assert "i" not in result
    assert "a" not in result
    assert "big" in result
    assert "apple" in result


# Checks that an empty string produces an empty list
def test_tokenise_empty_input():
    assert tokenise("") == []


# Checks that the index key for a word points to the correct pages
def test_build_index_records_correct_pages():
    pages = {PAGE_A_URL: PAGE_A_HTML}
    index = build_index(pages)
    assert "fox" in index
    assert PAGE_A_URL in index["fox"]


# Checks that the count field reflects how many times a word appears on a page
def test_build_index_counts_word_frequency():
    html = "<html><body><p>cat cat dog cat</p></body></html>"
    index = build_index({"http://example.com": html})
    assert index["cat"]["http://example.com"]["count"] == 3
    assert index["dog"]["http://example.com"]["count"] == 1


# Checks that positions list contains the correct 0-indexed word positions
def test_build_index_records_word_positions():
    html = "<html><body><p>the quick brown fox</p></body></html>"
    url = "http://example.com"
    index = build_index({url: html})
    assert index["fox"][url]["positions"] == [3]   # "fox" is the 4th token (index 3)
    assert index["the"][url]["positions"] == [0]   # "the" is the 1st token


# Checks that words appearing on multiple pages are tracked across all of them
def test_build_index_handles_multiple_pages():
    pages = {PAGE_A_URL: PAGE_A_HTML, PAGE_B_URL: PAGE_B_HTML}
    index = build_index(pages)
    assert PAGE_A_URL in index["fox"]   # "fox" appears on page A
    assert PAGE_B_URL in index["fox"]   # "fox" also appears on page B


# Checks that build_index returns an empty dict when given no pages
def test_build_index_empty_input():
    assert build_index({}) == {}
