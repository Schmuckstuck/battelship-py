"""Battleship engine and bot framework for the lab."""

from .engine import BattleshipGame, Fleet, GamePhase, ShotResult
from .exporter import write_replay
from .map import Map, Point
from .player import Bot, CellState, PlayerView
from .recorder import Recorder
from .ship import SHIP_LENGTHS, Ship, random_placement, validate_fleet
from .simulator import play_series, print_series

__all__ = [
    "SHIP_LENGTHS",
    "BattleshipGame",
    "Bot",
    "CellState",
    "Fleet",
    "GamePhase",
    "Map",
    "PlayerView",
    "Point",
    "Recorder",
    "Ship",
    "ShotResult",
    "play_series",
    "print_series",
    "random_placement",
    "validate_fleet",
    "write_replay",
]
