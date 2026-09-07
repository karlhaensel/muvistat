"""CRUD operations for videos table."""

from typing import Literal

from fastapi import HTTPException

from app.database.core import get_db
from app.models import VideoCreate


def check_video_exists(
    video_id: str, raise_for: Literal["already_existing", "not_found"] | None = None
) -> bool:
    """
    Check if a video with given video_id exists in database.

    :param video_id: YouTube video ID to check for in videos table of database.
    :param raise_for: Optional; if 'already_existing', raises ValueError if video
        exists in database; if 'not_found', raises ValueError if video does not exist.
        If None, simply returns True if video exists, False otherwise.
    :return: True if video exists, False otherwise.
    """

    conn = get_db()
    result = conn.execute(
        "SELECT video_id FROM videos WHERE video_id = ?", (video_id,)
    ).fetchone()
    conn.close()

    existing = False if result is None else True

    if raise_for == "already_existing" and existing:
        raise HTTPException(
            status_code=409, detail=f"Video with ID {video_id} already tracked."
        )

    if raise_for == "not_found" and not existing:
        raise HTTPException(
            status_code=404, detail=f"Video with ID {video_id} not found in database."
        )

    return existing


def create_video(video: VideoCreate, added_at: str) -> None:
    """
    Create a new video entry in the database.

    :param video: VideoCreate object containing video_id and (optional) title.
    :param added_at: ISO formatted datetime string for when the video was added.
    """
    conn = get_db()
    conn.execute(
        "INSERT INTO videos (video_id, added_at) VALUES (?, ?)",
        (video.video_id, added_at),
    )
    conn.commit()
    conn.close()


def read_added_at(video_id: str) -> str | None:
    """
    Read the added_at timestamp for a given video_id from the database.

    :param video_id: YouTube video ID for which to retrieve the added_at timestamp.
    :return: ISO formatted datetime string for when the video was added, or None if not found.
    """
    conn = get_db()
    result = conn.execute(
        "SELECT added_at FROM videos WHERE video_id = ?", (video_id,)
    ).fetchone()
    conn.close()

    return result[0] if result else None
