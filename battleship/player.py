"""Bot base class and the view passed to choose_shot."""

from __future__ import annotations

import random
from collections.abc import Mapping
from enum import Enum

from .map import Map, Point
from .ship import random_placement


class CellState(Enum):
    """What a bot currently knows about a single enemy cell."""

    UNKNOWN = "unknown"
    MISS = "miss"
    HIT = "hit"
    SUNK = "sunk"


class PlayerView:
    """What a bot knows about the enemy board on one turn."""

    def __init__(
        self,
        board: Map,
        grid: Mapping[Point, CellState],
        remaining_ships: list[int],
        shots_fired: int,
    ) -> None:
        self.board: Map = board
        # The bot gets a snapshot; it cannot change the engine's own record.
        self._grid: dict[Point, CellState] = dict(grid)
        self.remaining_ships: list[int] = remaining_ships
        self.shots_fired: int = shots_fired

    def state(self, point: Point) -> CellState:
        """State of an enemy cell (UNKNOWN when never shot at)."""
        return self._grid.get(point, CellState.UNKNOWN)

    def points_of(self, state: CellState) -> list[Point]:
        """All enemy cells currently in the given state."""
        return [point for point in self.board.points() if self.state(point) is state]

    def unknown_points(self) -> list[Point]:
        """Cells not shot at yet."""
        return self.points_of(CellState.UNKNOWN)


class Bot:
    """Base class for every bot.

    A bot has two jobs: place its fleet and choose a shot. Override
    ``place_ships`` and ``choose_shot``. All fields and the turn bookkeeping
    are provided here, so a bot never needs to write ``__init__``.

    The engine calls ``take_turn``, which updates ``last_result`` and then calls
    ``choose_shot``.
    """

    def __init__(self, name: str, seed: int | None = None) -> None:
        self.name: str = name
        self.rng: random.Random = random.Random(seed)
        self.last_shot: Point | None = None
        self.last_result: CellState | None = None

    def place_ships(self, board: Map) -> list[list[Point]]:
        """Return the fleet. The default is a random valid fleet."""
        return random_placement(board, self.rng)

    def choose_shot(self, view: PlayerView) -> Point:
        """Return the next point. The default shoots a random unknown cell."""
        return self.rng.choice(view.unknown_points())

    def take_turn(self, view: PlayerView) -> Point:
        """Engine entry point: update last_result, then call choose_shot."""
        if self.last_shot is not None:
            result = view.state(self.last_shot)
            self.last_result = None if result is CellState.UNKNOWN else result
        self.last_shot = self.choose_shot(view)
        return self.last_shot
