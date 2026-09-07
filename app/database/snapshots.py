"""CRUD operations for snapshots table."""

from sqlite3 import Row

from app.database.core import get_db


def create_snapshot(
    video_id: str,
    views: int,
    likes: int,
    dislikes: int,
    comments: int,
    recorded_at: str,
) -> None:
    """
    Create a new snapshot entry in the database.

    :param video_id: YouTube video ID for which the snapshot is recorded.
    :param views: View count of the video at the time of recording.
    :param likes: Like count of the video at the time of recording.
    :param dislikes: Dislike count of the video at the time of recording.
    :param comments: Comment count of the video at the time of recording.
    :param recorded_at: ISO formatted datetime str for when the snapshot was recorded.
    """
    conn = get_db()
    conn.execute(
        "INSERT INTO snapshots (video_id, views, likes, dislikes, comments, recorded_at) VALUES (?, ?, ?, ?, ?, ?)",
        (video_id, views, likes, dislikes, comments, recorded_at),
    )
    conn.commit()
    conn.close()


def read_all_snapshots(video_id: str) -> list[Row]:
    """
    Read all snapshot entries for a given video_id from the database.

    :param video_id: YouTube video ID for which to retrieve snapshots.
    :return: list of sqlite3.Row objects containing snapshot data for given video_id
    """
    conn = get_db()
    rows = conn.execute(
        "SELECT video_id, views, likes, dislikes, comments, recorded_at FROM snapshots "
        "WHERE video_id = ? ORDER BY recorded_at",
        (video_id,),
    ).fetchall()
    conn.close()

    return rows
