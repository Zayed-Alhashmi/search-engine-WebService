# test_storage.py
# Unit tests for src/storage.py. Uses pytest tmp_path so no real files are created.

import pytest

from src.storage import load_index, save_index

# A small but complete index structure used across tests
SAMPLE_INDEX = {
    "python": {
        "https://example.com/": {"count": 2, "positions": [0, 5]},
    },
    "search": {
        "https://example.com/about": {"count": 1, "positions": [3]},
    },
}


# Checks that save_index creates a file at the expected path
def test_save_index_creates_file(tmp_path):
    filepath = str(tmp_path / "index.json")
    save_index(SAMPLE_INDEX, filepath)
    assert (tmp_path / "index.json").exists()


# Checks that an index saved then loaded returns exactly the same data (round-trip)
def test_save_and_load_roundtrip(tmp_path):
    filepath = str(tmp_path / "index.json")
    save_index(SAMPLE_INDEX, filepath)
    result = load_index(filepath)
    assert result == SAMPLE_INDEX


# Checks that load_index raises FileNotFoundError when no file exists at the path
def test_load_index_raises_when_file_missing(tmp_path):
    filepath = str(tmp_path / "nonexistent.json")
    with pytest.raises(FileNotFoundError):
        load_index(filepath)


# Checks that nested count and positions values survive a save/load cycle intact
def test_save_and_load_preserves_nested_structure(tmp_path):
    filepath = str(tmp_path / "index.json")
    save_index(SAMPLE_INDEX, filepath)
    result = load_index(filepath)
    assert result["python"]["https://example.com/"]["count"] == 2
    assert result["python"]["https://example.com/"]["positions"] == [0, 5]
    assert result["search"]["https://example.com/about"]["count"] == 1
    assert result["search"]["https://example.com/about"]["positions"] == [3]
