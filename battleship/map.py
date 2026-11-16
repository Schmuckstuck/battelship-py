"""Base geometry for the board: the Map and its Points."""

from __future__ import annotations

COLS = "ABCDEFGHIJ"


class Point:
    """A single cell on the board.

    Coordinates are 0-based: ``x`` is the column (A-J), ``y`` is the row (1-10).
    Two points are equal when their coordinates are equal, regardless of which
    instance you hold, so a bot may freely construct its own ``Point`` objects.
    """

    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __lt__(self, other: Point) -> bool:
        return (self.y, self.x) < (other.y, other.x)

    def __repr__(self) -> str:
        return f"Point({self.label()})"

    def label(self) -> str:
        """Human-readable coordinate such as ``A1`` or ``J10``."""
        return f"{COLS[self.x]}{self.y + 1}"


class Map:
    """A rectangular grid of :class:`Point` objects.

    The map materialises every point once and shares them, so ships, views and
    the engine all refer to the very same point instances.
    """

    def __init__(self, width: int = 10, height: int = 10) -> None:
        self.width = width
        self.height = height
        self._grid: list[list[Point]] = [
            [Point(x, y) for x in range(width)] for y in range(height)
        ]

    def point(self, x: int, y: int) -> Point | None:
        """Return the point at the given coordinates, or ``None`` if out of bounds."""
        if (
            isinstance(x, int)
            and isinstance(y, int)
            and 0 <= x < self.width
            and 0 <= y < self.height
        ):
            return self._grid[y][x]
        return None

    def points(self) -> list[Point]:
        """All points on the map, in row-major order."""
        return [p for row in self._grid for p in row]

    def neighbours(self, p: Point) -> list[Point]:
        """All eight in-bounds neighbours of ``p``."""
        result: list[Point] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                n = self.point(p.x + dx, p.y + dy)
                if n is not None:
                    result.append(n)
        return result
