"""
Unit tests for data contracts in BeatMatch AI MVP.
"""

import pytest
from pydantic import ValidationError
from src.models.schemas import AudioAnalysisResult


def test_audio_analysis_valid(sample_audio_analysis):
    assert sample_audio_analysis.master_style == "Trap"
    assert sample_audio_analysis.bpm == 140
    assert sample_audio_analysis.vibe == "Dark"


def test_audio_analysis_bpm_bounds():
    with pytest.raises(ValidationError):
        AudioAnalysisResult(
            master_style="Ambient",
            vibe="Chill",
            bpm=350  # Over 250 BPM bound
        )


def test_artist_match_result(sample_match_result):
    assert sample_match_result.name == "Metro Boomin"
    assert sample_match_result.match_tier == "TIER_1_STRICT"
    assert sample_match_result.instagram_handle == "metroboomin"
