"""Pydantic data models for API."""

from datetime import datetime
from typing import Annotated, Self

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

Dislikes = Annotated[
    int, Field(ge=0, description="Dislike count of the given YouTube video.")
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
    dislikes: Dislikes
    comments: Comments


class SnapshotResponse(BaseModel):
    """Data model for API response with snapshot information."""

    video_id: YouTubeID
    views: Views
    likes: Likes
    dislikes: Dislikes
    comments: Comments
    recorded_at: ISODatetimeStr

    @classmethod
    def from_youtube_api_response_items(
        cls, video_id: str, items: list[dict], recorded_at: str
    ) -> Self:
        """
        Create a SnapshotResponse instance from YouTube API response items.

        :param video_id: YouTube video ID for which the snapshot is recorded.
        :param items: List of items from YouTube API response.
        :param recorded_at: ISO 8601 formatted datetime string for when
            the snapshot was recorded.
        :return: SnapshotResponse instance with extracted statistics.
        """

        if not items:
            raise ValueError("YouTube API response items list is empty.")

        stats = items[0].get("statistics", {})
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        dislikes = int(stats.get("dislikeCount", 0))
        comments = int(stats.get("commentCount", 0))

        return cls(
            video_id=video_id,
            views=views,
            likes=likes,
            dislikes=dislikes,
            comments=comments,
            recorded_at=recorded_at,
        )
