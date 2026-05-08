# test_search.py
# Unit tests for src/search.py. Uses a small hand-built index, no file I/O.

import pytest

from src.search import calculate_tfidf, find_pages, print_word, suggest_words

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


# TFIDF_INDEX: "rare" is on 1 of 10 pages, "common" is on 9 of 10, both appear once on target
TFIDF_INDEX = {
    "rare": {
        "http://target.com": {"count": 1, "positions": [0]},
    },
    "common": {
        "http://target.com": {"count": 1, "positions": [1]},
        "http://p2.com": {"count": 1, "positions": [0]},
        "http://p3.com": {"count": 1, "positions": [0]},
        "http://p4.com": {"count": 1, "positions": [0]},
        "http://p5.com": {"count": 1, "positions": [0]},
        "http://p6.com": {"count": 1, "positions": [0]},
        "http://p7.com": {"count": 1, "positions": [0]},
        "http://p8.com": {"count": 1, "positions": [0]},
        "http://p9.com": {"count": 1, "positions": [0]},
        "http://p10.com": {"count": 1, "positions": [0]},
    },
}


# Checks that calculate_tfidf returns a higher score for a word that is rare across pages
def test_calculate_tfidf_higher_for_rare_word():
    url = "http://target.com"
    total_pages = 10
    rare_score = calculate_tfidf(TFIDF_INDEX, "rare", url, total_pages)    # on 1/10 pages
    common_score = calculate_tfidf(TFIDF_INDEX, "common", url, total_pages)  # on 9/10 pages
    assert rare_score > common_score


# Checks that calculate_tfidf returns a lower score for a word that appears on almost every page
def test_calculate_tfidf_lower_for_common_word():
    url = "http://target.com"
    total_pages = 10
    rare_score = calculate_tfidf(TFIDF_INDEX, "rare", url, total_pages)
    common_score = calculate_tfidf(TFIDF_INDEX, "common", url, total_pages)
    assert common_score < rare_score  # common word is penalised by low IDF


# Checks that find_pages ranks by TF-IDF so the shorter, more focused page wins over a longer one
def test_find_pages_tfidf_ranks_relevant_page_first():
    tfidf_test_index = {
        "alpha": {
            "http://page-a.com": {"count": 10, "positions": list(range(10))},
            "http://page-b.com": {"count": 3, "positions": [0, 1, 2]},
        },
        "filler": {
            "http://page-a.com": {"count": 90, "positions": list(range(10, 100))},  # inflates page A word count
        },
    }
    result = find_pages(tfidf_test_index, "alpha")
    assert result[0] == "http://page-b.com"  # page B: TF = 3/3 = 1.0 beats page A: TF = 10/100 = 0.1
    assert result[1] == "http://page-a.com"


# Index used by suggest_words tests
SUGGEST_INDEX = {
    "friend": {"https://example.com/a": {"count": 1, "positions": [0]}},
    "friendship": {"https://example.com/a": {"count": 1, "positions": [1]}},
    "friday": {"https://example.com/b": {"count": 1, "positions": [0]}},
    "frame": {"https://example.com/b": {"count": 1, "positions": [1]}},
    "free": {"https://example.com/b": {"count": 1, "positions": [2]}},
    "frozen": {"https://example.com/b": {"count": 1, "positions": [3]}},
    "hello": {"https://example.com/c": {"count": 1, "positions": [0]}},
}


# Checks that suggest_words returns words that start with the given prefix
def test_suggest_words_returns_prefix_matches():
    result = suggest_words(SUGGEST_INDEX, "fri")
    assert "friend" in result
    assert "friendship" in result
    assert "friday" in result
    assert "hello" not in result  # does not start with "fri"


# Checks that suggest_words is case-insensitive so "FRI" matches the same words as "fri"
def test_suggest_words_is_case_insensitive():
    result_lower = suggest_words(SUGGEST_INDEX, "fri")
    result_upper = suggest_words(SUGGEST_INDEX, "FRI")
    assert result_lower == result_upper


# Checks that suggest_words returns an empty list when no words share the given prefix
def test_suggest_words_no_match_returns_empty():
    result = suggest_words(SUGGEST_INDEX, "xyz")
    assert result == []


# Checks that suggest_words never returns more than 5 results even when more matches exist
def test_suggest_words_caps_at_five_results():
    # SUGGEST_INDEX has 6 words starting with "fr": frame, free, friday, friend, friendship, frozen
    result = suggest_words(SUGGEST_INDEX, "fr")
    assert len(result) <= 5
