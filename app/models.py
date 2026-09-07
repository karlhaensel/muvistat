"""Pydantic data models for API."""

import datetime as dt
from typing import Annotated, Self

from pydantic import BaseModel, Field, BeforeValidator


ERROR_MSG_YOUTUBE_RESPONSE_ITEMS_EMPTY = "YouTube API response items list is empty."


def validate_iso_format(dt_input: str) -> str:
    """Validate that the input string is in ISO 8601 format for pydantic validator."""
    try:
        # Convert UTC to Python format for validation:
        py_v = dt_input.replace("Z", "+00:00")
        dt.datetime.fromisoformat(py_v)  # Would fail if incorrect ISO format.
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

Duration = Annotated[
    str,
    Field(
        pattern=r"^PT(\d+H)?(\d+M)?(\d+S)$",
        description="ISO 8601 duration format (e.g. PT1H2M3S for 1 hour, 2 minutes, 3 seconds).",
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
    my_comment: str | None = Field(
        default=None,
        description="Optional; own comment on video for tracking purposes.",
    )


class VideoMetadataUpdate(BaseModel):
    """Data model for updating video metadata via API."""

    video_id: YouTubeID
    duration: Duration
    title: str
    channel: str
    my_comment: str | None = Field(
        default=None,
        description="Optional; own comment on video for tracking purposes.",
    )

    @classmethod
    def from_youtube_api_response_items(
        cls,
        video_id: str,
        items: list[dict],
        my_comment: str | None,
    ) -> Self:
        """
        Create a VideoMetadataUpdate instance from YouTube API response items.

        :param video_id: YouTube video ID for which the metadata is retrieved.
        :param items: List of items from YouTube API response.
        :param my_comment: Optional; own comment on video for tracking.
        :return: VideoMetadataUpdate instance with extracted metadata.
        """

        if not items:
            raise ValueError(ERROR_MSG_YOUTUBE_RESPONSE_ITEMS_EMPTY)

        snippet = items[0].get("snippet", {})
        content_details = items[0].get("contentDetails", {})

        duration = content_details.get("duration", "")
        title = snippet.get("title", "")
        channel = snippet.get("channelTitle", "")

        return cls(
            video_id=video_id,
            duration=duration,
            title=title,
            channel=channel,
            my_comment=my_comment,
        )


class VideoMetadataResponse(BaseModel):
    """Data model for API response with video metadata information."""

    video_id: YouTubeID
    duration: Duration
    title: str
    channel: str
    published_at: ISODatetimeStr
    my_comment: str | None
    updated_at: ISODatetimeStr

    added_at: ISODatetimeStr  # not in metadata, only in video table

    @classmethod
    def from_youtube_api_response_items(
        cls,
        video_id: str,
        items: list[dict],
        video_added_at: str,
        metadata_updated_at: str,
        my_comment: str | None,
    ) -> Self:
        """
        Create a MetadataResponse instance from YouTube API response items.

        :param video_id: YouTube video ID for which the metadata is retrieved.
        :param items: List of items from YouTube API response.
        :param video_added_at: ISO 8601 formatted datetime string for when
            the video was added the first time to the database (videos table).
        :param metadata_updated_at: ISO 8601 formatted datetime string for when
            the metadata was last updated.
        :param my_comment: Optional; own comment on video for tracking.
        :return: MetadataResponse instance with extracted metadata.
        """

        if not items:
            raise ValueError(ERROR_MSG_YOUTUBE_RESPONSE_ITEMS_EMPTY)

        snippet = items[0].get("snippet", {})
        content_details = items[0].get("contentDetails", {})

        duration = content_details.get("duration", "")
        title = snippet.get("title", "")
        channel = snippet.get("channelTitle", "")
        published_at = snippet.get("publishedAt", "")

        return cls(
            video_id=video_id,
            title=title,
            duration=duration,
            channel=channel,
            published_at=published_at,
            my_comment=my_comment,
            updated_at=metadata_updated_at,
            added_at=video_added_at,
        )

    def __eq__(self, other):
        """Override equality operator to see whether relevant metadata got updated."""
        if not isinstance(other, VideoMetadataResponse):
            return NotImplemented
        return (
            self.video_id == other.video_id
            and self.duration == other.duration
            and self.title == other.title
            and self.channel == other.channel
            and self.my_comment == other.my_comment
        )


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
            raise ValueError(ERROR_MSG_YOUTUBE_RESPONSE_ITEMS_EMPTY)

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
