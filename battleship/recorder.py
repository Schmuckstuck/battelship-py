"""Recorder for capturing a full series of games for later playback."""

from __future__ import annotations

from typing import Any


class Recorder:
    """Collects games (rounds) and their shots, plus summary statistics.

    One series of games produces a single JSON payload: the rounds hold every
    shot of every game, and ``stats`` holds the aggregate win rates.
    """

    def __init__(self) -> None:
        self.meta: dict[str, Any] = {}
        self.stats: dict[str, Any] = {}
        self.rounds: list[dict[str, Any]] = []
        self._current_events: list[dict[str, Any]] | None = None

    def set_meta(self, **meta: Any) -> None:
        self.meta.update(meta)

    def start_round(self, **payload: Any) -> None:
        """Begin a new game (round). ``payload`` holds per-round metadata."""
        self._current_events = []
        self.rounds.append({"events": self._current_events, **payload})

    def record(self, event: str, **payload: Any) -> None:
        """Append an event to the current round."""
        if self._current_events is None:
            raise RuntimeError("start_round() must be called before record()")
        self._current_events.append({"event": event, **payload})

    def to_serializable(self) -> dict[str, Any]:
        return {"meta": self.meta, "stats": self.stats, "rounds": self.rounds}
