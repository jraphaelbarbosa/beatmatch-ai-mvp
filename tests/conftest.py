"""
Pytest global fixtures and configurations for BeatMatch AI MVP.
"""

import pytest
from src.models.schemas import AudioAnalysisResult, ArtistMatchResult


@pytest.fixture
def sample_audio_analysis():
    """Valid AudioAnalysisResult instance."""
    return AudioAnalysisResult(
        master_style="Trap",
        vibe="Dark",
        bpm=140,
        musical_key="C# Minor",
        mood_tags=["Hard", "808-heavy", "Ominous"],
        confidence=0.92
    )


@pytest.fixture
def sample_match_result():
    """Valid ArtistMatchResult instance."""
    return ArtistMatchResult(
        spotify_id="0iEtIxbK0KxaSlF7G42ZOp",
        name="Metro Boomin",
        instagram_handle="metroboomin",
        matched_genres=["dark trap", "hip hop"],
        popularity=88,
        match_tier="TIER_1_STRICT"
    )
