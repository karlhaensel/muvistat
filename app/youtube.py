"""YouTube API integration for fetching video information."""

import logging
import os

import httpx
from fastapi import HTTPException

logger = logging.getLogger("api.youtube")


def get_youtube_video_information(video_id: str) -> list[dict]:
    """Fetch video information from YouTube API for given video ID."""
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key:
        error_msg = "YOUTUBE_API_KEY environment variable not set. Please set it first."
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    logger.debug("Successfully retrieved YOUTUBE_API_KEY from environment variables.")

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "statistics",
        "id": video_id,
        "key": api_key,
    }

    response = httpx.get(url, params=params)
    if response.status_code != 200:
        logger.error(
            f"YouTube API failed for video with ID {video_id}.\n"
            f"Status code: {response.status_code}\n"
            f"Response: {response.text}"
        )
        # Raise own error without further details to avoid security risks:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "YouTube API request failed.",
                "upstream_status_code": response.status_code,
            },
        )

    items = response.json().get("items")
    if not items:
        logger.error(
            f"YouTube API did not find with ID {video_id}.\n"
            f"Status code: {response.status_code}\n"
            f"Response: {response.text}"
        )
        raise HTTPException(
            status_code=404, detail=f"Video with ID {video_id} not found on YouTube."
        )

    return items
