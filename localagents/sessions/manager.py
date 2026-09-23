"""Local-first session persistence, backed directly by Strands' own `FileSessionManager` — no
custom session-storage format to invent or maintain here."""
from __future__ import annotations

from pathlib import Path

from strands.session.file_session_manager import FileSessionManager


def build_session_manager(session_id: str, sessions_dir: str | Path) -> FileSessionManager:
    Path(sessions_dir).mkdir(parents=True, exist_ok=True)
    return FileSessionManager(session_id=session_id, storage_dir=str(sessions_dir))
