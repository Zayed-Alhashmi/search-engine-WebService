# main.py
# Command-line interface that ties together the crawler, indexer, storage, and search modules.

import sys
import os

# Add the project root to sys.path so imports work when run as: python src/main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crawler import crawl
from src.indexer import build_index
from src.storage import load_index, save_index
from src.search import find_pages, print_word


# Handles the 'build' command: crawls the site, builds the index, and saves it to disk
def handle_build() -> dict:
    print("Building index, this will take a few minutes...")
    pages = crawl("https://quotes.toscrape.com")
    index = build_index(pages)
    save_index(index)
    print("Index built and saved successfully.")
    return index


# Handles the 'load' command: reads the saved index file into memory
def handle_load() -> dict | None:
    try:
        index = load_index()
        print(f"Index loaded successfully. {len(index)} words indexed.")
        return index
    except FileNotFoundError as e:
        print("No index found. Please run 'build' first.")
        return None


# Handles the 'print <word>' command: looks up a word and prints its index entry
def handle_print(index: dict | None, args: str) -> None:
    if not args.strip():
        print("Usage: print <word>")
        return
    if index is None:
        print("No index in memory. Run 'build' or 'load' first.")
        return
    print(print_word(index, args.strip()))


# Handles the 'find <query>' command: searches for pages matching all query words
def handle_find(index: dict | None, args: str) -> None:
    if not args.strip():
        print("Usage: find <query>")
        return
    if index is None:
        print("No index in memory. Run 'build' or 'load' first.")
        return

    results = find_pages(index, args.strip())
    if not results:
        print(f"No pages found for query: {args.strip()}")
        return

    print(f"Found {len(results)} page(s):")
    for i, url in enumerate(results, start=1):
        print(f"  {i}. {url}")


# Main entry point: displays the welcome message and runs the command loop
def main() -> None:
    print("Search Engine  COMP3011")
    print("Type 'build' to crawl and index the site, or 'load' to load an existing index.")
    print("Type 'quit' to exit.")
    print()

    index = None  # holds the index in memory once built or loaded

    try:
        while True:
            raw = input("> ").strip()

            if not raw:
                continue

            # Split into command and optional arguments
            parts = raw.split(" ", 1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == "build":
                index = handle_build()

            elif command == "load":
                index = handle_load()

            elif command == "print":
                handle_print(index, args)

            elif command == "find":
                handle_find(index, args)

            elif command in ("quit", "exit"):
                print("Goodbye!")
                break

            else:
                print("Unknown command. Available commands: build, load, print <word>, find <query>, quit")

    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
