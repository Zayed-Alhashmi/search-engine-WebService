"""
crawler.py
Web crawler: downloads pages, extracts links, and stays within the same domain.
"""

import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

CRAWL_DELAY = 6  # seconds to wait between requests (politeness requirement)


# Returns just the domain part of a URL, used to check if a link is on the same site
def get_domain(url: str) -> str:
    """Return the domain of a URL, e.g. 'quotes.toscrape.com'."""
    return urlparse(url).netloc


# Downloads a single page and returns its HTML, or None if something goes wrong
def fetch_page(url: str, session: requests.Session) -> str | None:
    """
    Fetch a page and return its HTML, or None if the request fails.

    Args:
        url: The page URL to fetch.
        session: Active requests session.

    Returns:
        Raw HTML string, or None on error or non-200 status.
    """
    try:
        response = session.get(url, timeout=10)
        if response.status_code != 200:
            print(f"  [SKIP] {url} status {response.status_code}")
            return None
        return response.text
    except requests.RequestException as exc:
        print(f"  [ERROR] Could not fetch {url}: {exc}")
        return None


# Parses all anchor tags from a page and converts relative links to absolute URLs
def extract_links(html: str, base_url: str) -> list[str]:
    """
    Extract all links from a page as absolute URLs.

    Args:
        html: Raw HTML of the page.
        base_url: Used to resolve relative links (e.g. /page/2/).

    Returns:
        List of absolute URLs found in <a href> tags.
    """
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for tag in soup.find_all("a", href=True):
        absolute = urljoin(base_url, tag["href"])  # convert relative to absolute
        links.append(absolute)
    return links


# Main crawl loop: visits pages on the same domain, skips duplicates, enforces delay
def crawl(seed_url: str = "https://quotes.toscrape.com") -> dict[str, str]:
    """
    Crawl a website from seed_url and return all pages found.

    Only follows links on the same domain. Skips already-visited pages.
    Waits CRAWL_DELAY seconds between each request.

    Args:
        seed_url: Starting URL for the crawl.

    Returns:
        Dict mapping each visited URL to its raw HTML content.
    """
    domain = get_domain(seed_url)
    visited: set[str] = set()
    queue: list[str] = [seed_url]
    pages: dict[str, str] = {}

    with requests.Session() as session:
        session.headers.update({"User-Agent": "SearchEngineCrawler/1.0"})

        while queue:
            url = queue.pop(0)

            if url in visited:
                continue

            if get_domain(url) != domain:  # skip external domains
                continue

            print(f"Crawling: {url}")
            visited.add(url)

            html = fetch_page(url, session)
            if html is None:
                time.sleep(CRAWL_DELAY)  # still wait even on failure
                continue

            pages[url] = html

            # Add new same-domain links to the queue
            for link in extract_links(html, url):
                if link not in visited and get_domain(link) == domain:
                    queue.append(link)

            time.sleep(CRAWL_DELAY)

    print(f"Crawl complete. {len(pages)} page(s) collected.")
    return pages
