"""CRUD operations for video metadata table."""

import logging

from app.database.core import get_db
from app.database.videos import read_added_at
from app.models import VideoMetadataResponse

logger = logging.getLogger("api.database.metadata")


def create_metadata(video_metadata: VideoMetadataResponse) -> None:
    """
    Create a new metadata entry in the database for given metadata information..

    :param video_metadata: VideoMetadataResponse object containing metadata information.
    """
    conn = get_db()
    conn.execute(
        "INSERT INTO metadata (video_id, duration, title, channel, published_at, updated_at, my_comment) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            video_metadata.video_id,
            video_metadata.duration,
            video_metadata.title,
            video_metadata.channel,
            video_metadata.published_at,
            video_metadata.updated_at,
            video_metadata.my_comment,
        ),
    )
    conn.commit()
    conn.close()


def read_most_recent_metadata(video_id: str) -> VideoMetadataResponse | None:
    """
    Read last metadata entry for a given video_id from the database.

    :param video_id: YouTube video ID for which to retrieve metadata.
    :return: VideoMetadataResponse object containing metadata information, or None if not found.
    """
    conn = get_db()
    # Get last entry.
    row = conn.execute(
        "SELECT video_id, duration, title, channel, published_at, updated_at, my_comment FROM metadata WHERE video_id = ? ORDER BY updated_at DESC LIMIT 1",
        (video_id,),
    ).fetchone()
    conn.close()

    if row is None:
        return None

    added_at = read_added_at(video_id)
    if added_at is None:
        raise ValueError(
            f"Video with ID {video_id} not found in videos table, but metadata exists in metadata table."
        )

    return VideoMetadataResponse(
        video_id=row["video_id"],
        duration=row["duration"],
        title=row["title"],
        channel=row["channel"],
        published_at=row["published_at"],
        updated_at=row["updated_at"],
        my_comment=row["my_comment"],
        added_at=added_at,
    )


def update_metadata(video_metadata: VideoMetadataResponse) -> None:
    """
    Update an existing metadata entry in the database for given metadata information.

    :param video_metadata: VideoMetadataResponse object containing updated metadata information.
    """
    conn = get_db()
    last_metadata = read_most_recent_metadata(video_metadata.video_id)
    conn.close()

    if last_metadata is None:
        raise ValueError(
            f"No existing metadata found for video with ID {video_metadata.video_id}. Cannot update non-existent metadata."
        )

    if last_metadata == video_metadata:
        logger.info(
            f"No changes detected for video with ID {video_metadata.video_id}. Skipping metadata update."
        )
        return

    # Insert new row with new update time and updated values.
    create_metadata(video_metadata)
