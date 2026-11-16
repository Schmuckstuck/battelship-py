"""Game engine: places fleets and runs the shooting loop."""

from __future__ import annotations

from enum import Enum

from .map import Map, Point
from .player import Bot, CellState, PlayerView
from .recorder import Recorder
from .ship import Ship, validate_fleet


class ShotResult(Enum):
    MISS = "miss"
    HIT = "hit"
    SUNK = "sunk"


class GamePhase(Enum):
    """Lifecycle of one game."""

    INIT = "init"
    HUNT = "hunt"
    FINISHED = "finished"


class Fleet:
    """A player's placed fleet on a map, tracking hits and misses."""

    def __init__(self, board: Map, ships: list[Ship]) -> None:
        self.board = board
        self.ships = ships
        self._cell_to_ship: dict[Point, Ship] = {}
        for ship in ships:
            for p in ship.points:
                self._cell_to_ship[p] = ship

    def shoot(self, point: Point) -> ShotResult:
        ship = self._cell_to_ship.get(point)
        if ship is None:
            return ShotResult.MISS
        ship.hit(point)
        return ShotResult.SUNK if ship.sunk else ShotResult.HIT

    def ship_at(self, point: Point) -> Ship | None:
        return self._cell_to_ship.get(point)

    def remaining_lengths(self) -> list[int]:
        return [s.length for s in self.ships if not s.sunk]

    def all_sunk(self) -> bool:
        return all(s.sunk for s in self.ships)


class BattleshipGame:
    """A single game between two players on a shared map."""

    def __init__(
        self,
        board: Map,
        player0: Bot,
        player1: Bot,
        recorder: Recorder | None = None,
    ) -> None:
        self.board = board
        self.players = [player0, player1]
        self.recorder = recorder
        self.phase = GamePhase.INIT
        # Shots per player that were invalid and replaced by a random untried cell
        self.invalid_shots = [0, 0]

    def run(self, first: int = 0) -> tuple[int, list[int]]:
        """Play until a fleet is sunk.

        Returns ``(winner_index, [shots_player0, shots_player1])``.
        """
        fleets: list[Fleet] = []
        for player in self.players:
            try:
                ships = validate_fleet(self.board, player.place_ships(self.board))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{player.name}: invalid fleet: {exc}") from exc
            fleets.append(Fleet(self.board, ships))

        if self.recorder is not None:
            self.recorder.start_round(
                player0=self.players[0].name,
                player1=self.players[1].name,
                first=first,
                fleets=[self._serialize_fleet(f) for f in fleets],
            )

        self.phase = GamePhase.HUNT
        grids: list[dict[Point, CellState]] = [{}, {}]
        shots = [0, 0]
        current = first

        while True:
            enemy = 1 - current
            shooter = self.players[current]
            view = PlayerView(
                self.board,
                grids[current],
                fleets[enemy].remaining_lengths(),
                shots[current],
            )

            point = shooter.take_turn(view)
            point = self._sanitize(point, grids[current], current)
            shots[current] += 1

            result = fleets[enemy].shoot(point)
            if self.recorder is not None:
                self.recorder.record(
                    "shot",
                    player=current,
                    x=point.x,
                    y=point.y,
                    result=result.value,
                )
            if result is ShotResult.MISS:
                grids[current][point] = CellState.MISS
                current = enemy
            elif result is ShotResult.HIT:
                grids[current][point] = CellState.HIT
            # The ship is sunk.
            else:
                ship = fleets[enemy].ship_at(point)
                assert ship is not None
                for p in ship.points:
                    grids[current][p] = CellState.SUNK

            if fleets[enemy].all_sunk():
                if self.recorder is not None:
                    self.recorder.record(
                        "game_over",
                        winner=self.players[current].name,
                        shots=[shots[0], shots[1]],
                    )
                self.phase = GamePhase.FINISHED
                return current, shots

    @staticmethod
    def _serialize_fleet(fleet: Fleet) -> list[list[list[int]]]:
        return [[[p.x, p.y] for p in ship.points] for ship in fleet.ships]

    def _sanitize(self, point: object, grid: dict[Point, CellState], current: int) -> Point:
        """Fall back to a random untried cell if the bot returned an invalid shot."""
        if (
            not isinstance(point, Point)
            or self.board.point(point.x, point.y) is None
            or point in grid
        ):
            self.invalid_shots[current] += 1
            unknown = [p for p in self.board.points() if p not in grid]
            return self.players[current].rng.choice(unknown)
        return point
