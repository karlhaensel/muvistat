"""Pydantic data models for API."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, BeforeValidator


def validate_iso_format(dt_input: str) -> str:
    """Validate that the input string is in ISO 8601 format for pydantic validator."""
    try:
        # Convert UTC to Python format for validation:
        py_v = dt_input.replace("Z", "+00:00")
        datetime.fromisoformat(py_v)  # Would fail if incorrect ISO format.
        return dt_input
    except (ValueError, TypeError):
        raise ValueError(
            f"{dt_input} is invalid ISO 8601 format. Must be YYYY-MM-DDTHH:MM:SSZ "
            "(e.g. 2026-06-29T22:45:00Z)"
        )


YouTubeID = Annotated[
    str,
    Field(
        min_length=11,
        max_length=11,
        pattern=r"^[a-zA-Z0-9_-]{11}$",
        description="YouTube Base64 unique video ID of length 11, only using "
        "a-z/A-Z characters, digits, hyphens, and underscores.",
    ),
]

Views = Annotated[
    int, Field(ge=0, description="View count of the given YouTube video.")
]

Likes = Annotated[
    int, Field(ge=0, description="Like count of the given YouTube video.")
]

Comments = Annotated[
    int, Field(ge=0, description="Comment count of the given YouTube video.")
]

ISODatetimeStr = Annotated[str, BeforeValidator(validate_iso_format)]


class VideoCreate(BaseModel):
    """Data model for adding a new video via API."""

    video_id: YouTubeID
    title: str | None = None


class VideoResponse(BaseModel):
    """Data model for API response with video information."""

    video_id: YouTubeID
    title: str | None
    added_at: ISODatetimeStr


class SnapshotCreate(BaseModel):
    """Data model for adding a new snapshot of video stats via API."""

    views: Views
    likes: Likes
    comments: Comments


class SnapshotResponse(BaseModel):
    """Data model for API response with snapshot information."""

    video_id: YouTubeID
    views: Views
    likes: Likes
    comments: Comments
    recorded_at: ISODatetimeStr
