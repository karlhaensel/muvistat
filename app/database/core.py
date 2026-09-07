"""Utilities for sqlite database."""

import logging
import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
DB_PATH = Path(os.environ.get("DB_PATH", "tracker.db"))

SQL_CREATE_VIDEOS = """
    CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT PRIMARY KEY,
        duration TEXT,
        my_comment TEXT,
        added_at TEXT NOT NULL  -- ISO datetime string
        )
"""

SQL_CREATE_METADATA = """
    CREATE TABLE IF NOT EXISTS metadata (
        video_id TEXT PRIMARY KEY,
        duration TEXT NOT NULL,  -- ISO 8601 duration string
        title TEXT NOT NULL,
        channel TEXT NOT NULL,
        published_at TEXT NOT NULL,  -- ISO datetime string
        my_comment TEXT,  -- nullable
        updated_at TEXT PRIMARY KEY,  -- ISO datetime string
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    )
"""

SQL_CREATE_SNAPSHOTS = """
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT NOT NULL,
        views INTEGER NOT NULL,
        likes INTEGER NOT NULL,
        dislikes INTEGER NOT NULL,
        comments INTEGER NOT NULL,
        recorded_at TEXT NOT NULL,  -- ISO datetime string
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    )
"""

logger = logging.getLogger("api.database.core")


def get_db():
    """Get sqlite database connection."""

    logger.debug(f"Attempting to establish connection to SQLite database at {DB_PATH}")
    if DB_PATH.parent != Path(".."):
        try:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(
                f"Successfully created directory structure for DB path: {DB_PATH}"
            )
        except OSError as e:
            logger.error(f"Failed to create directory structure for {DB_PATH}: {e}")
            raise

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Access row by column name instead of index.
        logger.debug(
            f"Successfully established connection to SQLite database at {DB_PATH}"
        )
        return conn
    except sqlite3.Error as e:
        logger.error(
            f"Failed to establish connection to SQLite database at {DB_PATH}: {e}"
        )
        raise


def init_db():
    """Initialise sqlite database."""
    logger.debug(f"Attempting to initialise SQLite database at {DB_PATH}")
    conn = get_db()
    conn.execute(SQL_CREATE_VIDEOS)
    conn.execute(SQL_CREATE_METADATA)
    conn.execute(SQL_CREATE_SNAPSHOTS)
    conn.commit()
    logger.debug(f"Successfully initialised SQLite database at {DB_PATH}")
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Application is starting up.")
    init_db()
    yield
