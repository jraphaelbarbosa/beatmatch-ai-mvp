"""
Unit tests for cascading artist matching logic in BeatMatch AI MVP.
"""

from unittest.mock import MagicMock
import pytest
from src.find_matches import ArtistMatcher


def test_find_matches_tier_1_perfect():
    mock_db = MagicMock()
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_db.get_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur

    # Simulate 5 strict rows
    mock_cur.fetchall.return_value = [
        ("id_1", "Artist 1", "handle_1", ["trap"], 80),
        ("id_2", "Artist 2", "handle_2", ["trap"], 75),
        ("id_3", "Artist 3", "handle_3", ["trap"], 70),
        ("id_4", "Artist 4", "handle_4", ["trap"], 65),
        ("id_5", "Artist 5", "handle_5", ["trap"], 60),
    ]

    matcher = ArtistMatcher(db_manager=mock_db)
    results = matcher.find_matches("Trap", "Dark", limit=10)

    assert len(results) == 5
    assert results[0]["match_type"] == "PERFECT"
    assert results[0]["name"] == "Artist 1"


def test_find_matches_tier_2_broad_fallback():
    mock_db = MagicMock()
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_db.get_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur

    # Strict returns only 1 row (triggering fallback), broad returns 2 rows
    mock_cur.fetchall.side_effect = [
        [("id_1", "Artist 1", "handle_1", ["boombap"], 80)],
        [("id_2", "Artist 2", "handle_2", ["boombap"], 60), ("id_3", "Artist 3", "handle_3", ["boombap"], 55)]
    ]

    matcher = ArtistMatcher(db_manager=mock_db)
    results = matcher.find_matches("Boombap", "Nostalgic", limit=10)

    assert len(results) == 3
    assert results[0]["match_type"] == "PERFECT"
    assert results[1]["match_type"] == "BROAD_STYLE"
