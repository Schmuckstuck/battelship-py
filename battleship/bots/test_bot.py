"""Student bot template.

A bot has two jobs: place its fleet and choose a shot. Override place_ships
and choose_shot. Everything else (name, rng, last_shot, last_result) comes
from Bot.
"""

# Map is the board type; Point is one cell.
from ..map import Map, Point
# Bot is the base class; PlayerView is the view for one turn.
from ..player import Bot, PlayerView, CellState
# The shared helper returns a valid random fleet.
from ..ship import random_placement


# Inherit name, rng, last_shot, last_result and take_turn from Bot.
class TestBot(Bot):
    """Your bot: edit the two methods below."""

    # Init-phase job: return the fleet.
    def place_ships(self, board: Map) -> list[list[Point]]:
        """Return your fleet. random_placement is a valid starting point."""
        # Delegate to the shared helper.
        return random_placement(board, self.rng)

    # Hunt-phase job: return one shot.
    def choose_shot(self, view: PlayerView) -> Point:
        """Return the next point to fire at.

        Hint: self.last_result is the result of your previous shot.
        """

        water : set[Point] = set()

        for sunk in view.points_of(CellState.SUNK):
            water.update(view.board.neighbours(sunk))


        targets : list[Point] = []

        for hit in view.points_of(CellState.HIT):
            # All eight neighbours of the hit.
            for point in view.board.neighbours(hit):
                # Diagonal cells cannot continue a straight ship.

                if point.x != hit.x and point.y != hit.y:
                    # Skip this diagonal cell.
                    continue

                if point in water:
                    continue

                # Free cells that are not already candidates.
                if view.state(point) is CellState.UNKNOWN and point not in targets:
                    # Add this cell as a target.
                    targets.append(point)
        if targets:
            # Finish that ship first.
            return self.rng.choice(targets)


        open_cells : list[Point] = [
            point for point in view.unknown_points() if point not in water
        ]

        parity_cells : list[Point] = [
            point for point in open_cells if (point.x + point.y) % 2 == 0
        ]

        return self.rng.choice(parity_cells or open_cells or view.unknown_points())
