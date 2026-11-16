"""ParityBot: hunt one checkerboard colour, then target hits."""

# Map is the board type; Point is one cell.
from ..map import Map, Point
# Bot is the base class; CellState is the shot result; PlayerView is the turn view.
from ..player import Bot, CellState, PlayerView
# The fleet lengths are 4, 3, 3, 2, 2, 2, 1, 1, 1, 1.
from ..ship import SHIP_LENGTHS


# Inherit name, rng, last_shot, last_result and take_turn from Bot.
class ParityBot(Bot):
    """Searches one checkerboard colour, then targets neighbours of hits."""

    # Init-phase job: return the fleet.
    def place_ships(self, board: Map) -> list[list[Point]]:
        """Return a random valid fleet, implemented inside this bot."""
        # Retry the whole fleet if one ship cannot be placed.
        while True:
            # Ships placed so far.
            ships: list[list[Point]] = []
            # Ship cells plus their one-cell frame.
            blocked: set[Point] = set()
            # True if one ship could not be placed.
            failed = False
            # Place the largest ships first.
            for length in sorted(SHIP_LENGTHS, reverse=True):
                # Try one ship of this length.
                cells = self._place_ship(board, length, blocked)
                # No free position for this ship.
                if cells is None:
                    # Mark the fleet as failed.
                    failed = True
                    # Stop placing smaller ships.
                    break
                # Keep the placed ship.
                ships.append(cells)
                # Mark the ship and its frame as blocked.
                for cell in cells:
                    # The ship's own cell.
                    blocked.add(cell)
                    # The one-cell frame around the ship.
                    blocked.update(board.neighbours(cell))
            # Every ship fitted.
            if not failed:
                # Return the valid fleet.
                return ships

    # Try to place one ship of the given length; return None if it does not fit.
    def _place_ship(
        self, board: Map, length: int, blocked: set[Point]
    ) -> list[Point] | None:
        """Try random positions for one ship without touching blocked cells."""
        # Try at most 1000 random positions.
        for _ in range(1000):
            # Pick horizontal or vertical with equal probability.
            horizontal = self.rng.randrange(2) == 0
            # Horizontal ship.
            if horizontal:
                # Leftmost column; leave room for the length.
                x = self.rng.randrange(board.width - length + 1)
                # Any row.
                y = self.rng.randrange(board.height)
                # Consecutive cells to the right.
                cells = [board.point(x + i, y) for i in range(length)]
            # Vertical ship.
            else:
                # Any column.
                x = self.rng.randrange(board.width)
                # Top row; leave room for the length.
                y = self.rng.randrange(board.height - length + 1)
                # Consecutive cells downward.
                cells = [board.point(x, y + i) for i in range(length)]
            # A position is valid only if every cell is on the board and free.
            if all(cell is not None and cell not in blocked for cell in cells):
                # Return the ship cells, without the None checks.
                return [cell for cell in cells if cell is not None]
        # No position found; the caller retries the whole fleet.
        return None

    # Hunt-phase job: return one shot.
    def choose_shot(self, view: PlayerView) -> Point:
        """Target neighbours of hits, otherwise hunt one colour."""
        # Unknown cells next to an open hit.
        targets: list[Point] = []
        # Hits on ships that are not sunk.
        for hit in view.points_of(CellState.HIT):
            # All eight neighbours of the hit.
            for point in view.board.neighbours(hit):
                # Diagonal cells cannot continue a straight ship.
                if point.x != hit.x and point.y != hit.y:
                    # Skip this diagonal cell.
                    continue
                # Free cells that are not already candidates.
                if view.state(point) is CellState.UNKNOWN and point not in targets:
                    # Add this cell as a target.
                    targets.append(point)
        # A damaged ship still has open cells.
        if targets:
            # Finish that ship first.
            return self.rng.choice(targets)
        # No open hit: collect unknown even-parity cells.
        parity: list[Point] = []
        # Check every cell we have not shot.
        for point in view.unknown_points():
            # Even x + y is one checkerboard colour.
            if (point.x + point.y) % 2 == 0:
                # Keep this cell.
                parity.append(point)
        # If parity is empty, fall back to all unknown cells.
        return self.rng.choice(parity or view.unknown_points())
