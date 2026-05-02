# storage.py
# Handles saving and loading the inverted index to and from disk as a JSON file.

import json
import os

DEFAULT_INDEX_PATH = "data/index.json"


# Serialises the index dict to JSON and writes it to the given filepath
def save_index(index: dict, filepath: str = DEFAULT_INDEX_PATH) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)  # create folder if missing
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print(f"Index saved to {filepath}")


# Reads the JSON file at filepath and returns it as a Python dict
def load_index(filepath: str = DEFAULT_INDEX_PATH) -> dict:
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Index file not found at '{filepath}'. "
            "Please run the 'build' command first."
        )
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
