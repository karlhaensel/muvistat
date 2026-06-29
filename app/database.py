"""Utilities for sqlite database."""

import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

DB_PATH = Path(os.environ.get("DB_PATH", "tracker.db"))

SQL_CREATE_VIDEOS = """
    CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT PRIMARY KEY,
        title TEXT,
        added_at TEXT NOT NULL  -- ISO datetime string
        )
"""

SQL_CREATE_SNAPSHOTS = """
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT NOT NULL,
        views INTEGER NOT NULL,
        likes INTEGER NOT NULL,
        recorded_at TEXT NOT NULL,  -- ISO datetime string
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    )
"""


def get_db():
    """Get sqlite database connection."""

    if DB_PATH.parent != Path("."):
        try:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Failed to create directory structure for {DB_PATH}: {e}")
            raise

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Access row by column name instead of index.
        return conn
    except sqlite3.Error as e:
        print(f"Failed to establish connection to SQLite database at {DB_PATH}: {e}")
        raise


def init_db():
    """Initialise sqlite database."""
    conn = get_db()
    conn.execute(SQL_CREATE_VIDEOS)
    conn.execute(SQL_CREATE_SNAPSHOTS)
    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
