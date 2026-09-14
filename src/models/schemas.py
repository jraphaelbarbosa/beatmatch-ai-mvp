"""
Data contracts and schema definitions for BeatMatch AI Sonic Matching MVP.
Enforces validation and serialization using Pydantic v2.
"""

from typing import Literal

from pydantic import BaseModel, Field


class AudioAnalysisResult(BaseModel):
    """Audio feature extraction and aesthetic classification schema."""
    master_style: str = Field(..., min_length=1, description="Primary musical style (e.g., Trap, Boombap, R&B)")
    vibe: str = Field(..., min_length=1, description="Emotional ambiance or mood (e.g., Melodic, Dark, Aggressive)")
    bpm: int | None = Field(default=None, ge=40, le=250, description="Estimated tempo in BPM")
    musical_key: str | None = Field(default=None, description="Estimated musical key")
    mood_tags: list[str] = Field(default_factory=list, description="Descriptive sonic tags")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0, description="Analysis confidence score")


class ArtistMatchResult(BaseModel):
    """Output contract for artist matching recommendations."""
    spotify_id: str = Field(..., min_length=1, description="Spotify artist ID")
    name: str = Field(..., min_length=1, description="Artist display name")
    instagram_handle: str | None = Field(default=None, description="Direct Instagram outreach handle")
    matched_genres: list[str] = Field(default_factory=list, description="Intersecting genres")
    popularity: int = Field(default=0, ge=0, le=100, description="Spotify popularity score")
    match_tier: Literal["TIER_1_STRICT", "TIER_2_BROAD"] = Field(
        default="TIER_1_STRICT",
        description="Cascading search tier match quality"
    )
