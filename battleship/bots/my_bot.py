"""Student bot template.

A bot has two jobs: place its fleet and choose a shot. Override place_ships
and choose_shot. Everything else (name, rng, last_shot, last_result) comes
from Bot.
"""

# Map is the board type; Point is one cell.
from ..map import Map, Point
# Bot is the base class; PlayerView is the view for one turn.
from ..player import Bot, PlayerView
# The shared helper returns a valid random fleet.
from ..ship import random_placement


# Inherit name, rng, last_shot, last_result and take_turn from Bot.
class MyBot(Bot):
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
        # Pick one cell that has not been shot at.
        return self.rng.choice(view.unknown_points())
