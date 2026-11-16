"""Ships and fleet placement helpers."""

from __future__ import annotations

import random

from .map import Map, Point

# Classic Russian fleet: battleship (4), cruisers (3, 3), destroyers
# (2, 2, 2) and torpedo boats (1, 1, 1, 1).
SHIP_LENGTHS = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]


class Ship:
    """A contiguous horizontal or vertical sequence of points on a map."""

    def __init__(self, points: list[Point]) -> None:
        self.points = tuple(points)
        self.hits: set[Point] = set()

    @property
    def length(self) -> int:
        return len(self.points)

    @property
    def sunk(self) -> bool:
        return len(self.hits) >= len(self.points)

    def hit(self, point: Point) -> bool:
        """Register a hit. Returns ``True`` if ``point`` belongs to this ship."""
        if point in self.points:
            self.hits.add(point)
            return True
        return False

    def __repr__(self) -> str:
        labels = ",".join(p.label() for p in self.points)
        return f"Ship({labels})"


def _is_straight(ship: list[Point]) -> bool:
    xs = sorted(p.x for p in ship)
    ys = sorted(p.y for p in ship)
    if len(set(xs)) == 1:
        return ys == list(range(ys[0], ys[0] + len(ys)))
    if len(set(ys)) == 1:
        return xs == list(range(xs[0], xs[0] + len(xs)))
    return False


def validate_fleet(board: Map, ships: list[list[Point]]) -> list[Ship]:
    """Validate a fleet and convert it into :class:`Ship` objects.

    Raises ``ValueError`` with a human-readable message if the fleet is invalid.
    """
    if not isinstance(ships, (list, tuple)) or len(ships) != len(SHIP_LENGTHS):
        raise ValueError(f"fleet must contain exactly {len(SHIP_LENGTHS)} ships")

    if sorted(len(s) for s in ships) != sorted(SHIP_LENGTHS):
        raise ValueError(
            f"ship lengths {sorted(len(s) for s in ships)} do not match {sorted(SHIP_LENGTHS)}"
        )

    owner: dict[Point, int] = {}
    for idx, ship in enumerate(ships):
        if not ship:
            raise ValueError("a ship must occupy at least one point")
        for p in ship:
            if board.point(p.x, p.y) is None:
                raise ValueError(f"point {p.label()} is out of bounds")
            if p in owner:
                raise ValueError("ships must not overlap")
            owner[p] = idx
        if not _is_straight(ship):
            raise ValueError(f"ship {ship} is not a straight line")

    for p, idx in owner.items():
        for n in board.neighbours(p):
            other = owner.get(n)
            if other is not None and other != idx:
                raise ValueError("ships must not touch, not even diagonally")

    return [Ship(list(s)) for s in ships]


def _try_place(
    board: Map, length: int, blocked: set[Point], rng: random.Random
) -> list[Point] | None:
    for _ in range(1000):
        horizontal = rng.randrange(2) == 0
        if horizontal:
            x = rng.randrange(board.width - length + 1)
            y = rng.randrange(board.height)
            cells = [board.point(x + i, y) for i in range(length)]
        else:
            x = rng.randrange(board.width)
            y = rng.randrange(board.height - length + 1)
            cells = [board.point(x, y + i) for i in range(length)]
        assert all(c is not None for c in cells)
        if all(c not in blocked for c in cells):
            return [c for c in cells if c is not None]
    return None


def random_placement(board: Map, rng: random.Random) -> list[list[Point]]:
    """Generate a random, valid fleet. Never fails; retries on unlucky draws."""
    while True:
        ships: list[list[Point]] = []
        blocked: set[Point] = set()
        failed = False
        for length in sorted(SHIP_LENGTHS, reverse=True):
            cells = _try_place(board, length, blocked, rng)
            if cells is None:
                failed = True
                break
            ships.append(cells)
            for c in cells:
                blocked.add(c)
                blocked.update(board.neighbours(c))
        if not failed:
            return ships
