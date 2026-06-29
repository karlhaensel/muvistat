"""FastAPI routers for snapshots."""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from app.models import SnapshotCreate, SnapshotResponse
from app.database import get_db


router = APIRouter(prefix="/videos", tags=["Snapshots"])


@router.post("/{video_id}/snapshots", response_model=SnapshotResponse, status_code=201)
def record_snapshot(video_id: str, snapshot: SnapshotCreate):
    """Record a new video statistics snapshot."""
    conn = get_db()

    video = conn.execute(
        "SELECT video_id FROM videos WHERE video_id = ?", (video_id,)
    ).fetchone()
    if not video:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Video with ID {video_id} not found. Please add it first.",
        )

    recorded_at = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO snapshots (video_id, views, likes, recorded_at) VALUES (?, ?, ?, ?)",
        (video_id, snapshot.views, snapshot.likes, recorded_at),
    )
    conn.commit()
    conn.close()
    return SnapshotResponse(
        video_id=video_id,
        views=snapshot.views,
        likes=snapshot.likes,
        recorded_at=recorded_at,
    )


@router.get("/{video_id}/history", response_model=list[SnapshotResponse])
def get_history(video_id: str):
    """Get history of video statistics snapshots."""
    conn = get_db()

    video = conn.execute(
        "SELECT video_id FROM videos WHERE video_id = ?", (video_id,)
    ).fetchone()
    if not video:
        conn.close()
        raise HTTPException(
            status_code=404, detail=f"Video with ID {video_id} not found."
        )

    rows = conn.execute(
        "SELECT video_id, views, likes, recorded_at FROM snapshots WHERE video_id = ? ORDER BY recorded_at",
        (video_id,),
    ).fetchall()
    conn.close()
    return [SnapshotResponse(**dict(row)) for row in rows]
