"""
test_crawler.py
Unit tests for src/crawler.py. All HTTP calls are mocked, no real network requests.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.crawler import crawl, extract_links, fetch_page, get_domain

# Sample HTML used across multiple tests
SAMPLE_HTML = """
<html>
<body>
  <a href="/page/2/">Page 2</a>
  <a href="/author/einstein/">Einstein</a>
  <a href="https://external.com/about">External Site</a>
</body>
</html>
"""

SEED = "https://quotes.toscrape.com"

# Minimal two-page site: seed links to /page/2/ which has no further links
SEED_HTML = """
<html><body>
  <a href="/page/2/">Next</a>
  <a href="https://external.com/">External</a>
</body></html>
"""

PAGE2_HTML = """
<html><body>
  <p>No more links</p>
</body></html>
"""


# Helper to build a mock requests.Response with a given status code and body text
def _make_response(status: int, text: str) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.text = text
    return resp


# Checks that relative hrefs like /page/2/ are turned into full absolute URLs
def test_extract_links_returns_absolute_urls():
    links = extract_links(SAMPLE_HTML, SEED)
    assert "https://quotes.toscrape.com/page/2/" in links
    assert "https://quotes.toscrape.com/author/einstein/" in links


# Checks that external links are included by extract_links (filtering happens in crawl)
def test_extract_links_includes_external_links():
    links = extract_links(SAMPLE_HTML, SEED)
    assert "https://external.com/about" in links


# Checks that a page with no anchor tags returns an empty list
def test_extract_links_empty_page():
    links = extract_links("<html><body><p>No links</p></body></html>", SEED)
    assert links == []


# Checks that a successful 200 response returns the page HTML as a string
def test_fetch_page_returns_html_on_200():
    mock_session = MagicMock()
    mock_session.get.return_value = _make_response(200, "<html>OK</html>")
    assert fetch_page(SEED, mock_session) == "<html>OK</html>"


# Checks that a non-200 status causes fetch_page to return None
def test_fetch_page_returns_none_on_404():
    mock_session = MagicMock()
    mock_session.get.return_value = _make_response(404, "")
    assert fetch_page(SEED, mock_session) is None


# Checks that a network exception is caught and None is returned instead of crashing
def test_fetch_page_returns_none_on_network_error():
    import requests as req
    mock_session = MagicMock()
    mock_session.get.side_effect = req.RequestException("Connection refused")
    assert fetch_page(SEED, mock_session) is None


# Checks that crawl() returns a dict with URLs as keys and HTML strings as values
@patch("src.crawler.time.sleep")  # suppress the 6-second delay during tests
@patch("src.crawler.requests.Session")
def test_crawl_returns_dict_of_url_to_html(mock_session_cls, mock_sleep):
    session = mock_session_cls.return_value.__enter__.return_value
    session.get.side_effect = [
        _make_response(200, SEED_HTML),
        _make_response(200, PAGE2_HTML),
    ]
    result = crawl(SEED)
    assert isinstance(result, dict)
    assert SEED in result
    assert result[SEED] == SEED_HTML


# Checks that relative links are resolved and the resulting pages are visited
@patch("src.crawler.time.sleep")
@patch("src.crawler.requests.Session")
def test_crawl_follows_relative_links(mock_session_cls, mock_sleep):
    session = mock_session_cls.return_value.__enter__.return_value
    session.get.side_effect = [
        _make_response(200, SEED_HTML),
        _make_response(200, PAGE2_HTML),
    ]
    result = crawl(SEED)
    assert "https://quotes.toscrape.com/page/2/" in result


# Checks that URLs from other domains are never fetched or added to the result
@patch("src.crawler.time.sleep")
@patch("src.crawler.requests.Session")
def test_crawl_ignores_external_links(mock_session_cls, mock_sleep):
    session = mock_session_cls.return_value.__enter__.return_value
    session.get.side_effect = [
        _make_response(200, SEED_HTML),
        _make_response(200, PAGE2_HTML),
    ]
    result = crawl(SEED)
    for url in result:
        assert "external.com" not in url


# Checks that duplicate links on a page do not cause the same URL to be fetched twice
@patch("src.crawler.time.sleep")
@patch("src.crawler.requests.Session")
def test_crawl_does_not_visit_same_page_twice(mock_session_cls, mock_sleep):
    html_with_duplicates = """
    <html><body>
      <a href="/page/2/">Link A</a>
      <a href="/page/2/">Link B (duplicate)</a>
    </body></html>
    """
    session = mock_session_cls.return_value.__enter__.return_value
    session.get.side_effect = [
        _make_response(200, html_with_duplicates),
        _make_response(200, PAGE2_HTML),
    ]
    crawl(SEED)
    assert session.get.call_count == 2  # seed + page2, not seed + page2 + page2


# Checks that a 404 page is skipped gracefully and does not appear in the result
@patch("src.crawler.time.sleep")
@patch("src.crawler.requests.Session")
def test_crawl_skips_page_on_non_200_status(mock_session_cls, mock_sleep):
    html_with_bad_link = """
    <html><body>
      <a href="/missing/">Missing Page</a>
    </body></html>
    """
    session = mock_session_cls.return_value.__enter__.return_value
    session.get.side_effect = [
        _make_response(200, html_with_bad_link),
        _make_response(404, ""),
    ]
    result = crawl(SEED)
    assert SEED in result
    assert "https://quotes.toscrape.com/missing/" not in result


# Checks that time.sleep is called once per page with exactly 6 seconds
@patch("src.crawler.time.sleep")
@patch("src.crawler.requests.Session")
def test_crawl_enforces_politeness_delay(mock_session_cls, mock_sleep):
    session = mock_session_cls.return_value.__enter__.return_value
    session.get.side_effect = [
        _make_response(200, SEED_HTML),
        _make_response(200, PAGE2_HTML),
    ]
    crawl(SEED)
    assert mock_sleep.call_count == 2         # one call per page
    for call in mock_sleep.call_args_list:
        assert call.args[0] == 6             # must be exactly 6 seconds
