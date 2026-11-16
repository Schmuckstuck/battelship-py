"""Series runner: measures one bot against another over many games."""

from __future__ import annotations

import random

from .engine import BattleshipGame
from .map import Map
from .player import Bot
from .recorder import Recorder


def play_series(
    bot0: type[Bot],
    bot1: type[Bot],
    games: int,
    seed: int | None = None,
    recorder: Recorder | None = None,
) -> dict:
    """Play ``games`` matches between two bot classes, alternating who goes first.

    Returns a dict with win rates and the average number of shots each bot needed
    to win (an important secondary metric for the lab). If ``recorder`` is given,
    every shot of every game is captured for later playback.

    Every statistic is a two-item list indexed by seat: ``[bot0, bot1]``, so a bot
    can also play against itself.

    Raises:
        ValueError: if ``games`` is not a positive integer.
    """
    if games < 1:
        raise ValueError("games must be at least 1")

    rng = random.Random(seed)
    name0, name1 = bot0.__name__, bot1.__name__

    if recorder is not None:
        recorder.set_meta(bots=[name0, name1], games=games, seed=seed)

    wins = [0, 0]
    win_shots: list[list[int]] = [[], []]
    total_shots: list[list[int]] = [[], []]
    invalid_shots = [0, 0]

    for g in range(games):
        first = g % 2
        p0 = bot0(name0, seed=rng.getrandbits(31))
        p1 = bot1(name1, seed=rng.getrandbits(31))
        game = BattleshipGame(Map(), p0, p1, recorder=recorder)
        winner, counts = game.run(first=first)

        wins[winner] += 1
        win_shots[winner].append(counts[winner])
        for seat in (0, 1):
            total_shots[seat].append(counts[seat])
            invalid_shots[seat] += game.invalid_shots[seat]

    result = {
        "games": games,
        "bots": [name0, name1],
        "wins": wins,
        "win_rate": [w / games for w in wins],
        "avg_shots_to_win": [(sum(v) / len(v)) if v else 0.0 for v in win_shots],
        "avg_shots_total": [(sum(v) / len(v)) if v else 0.0 for v in total_shots],
        "invalid_shots": invalid_shots,
    }

    if recorder is not None:
        recorder.stats = result

    return result


def print_series(result: dict) -> None:
    print(f"games={result['games']}")
    for seat, name in enumerate(result["bots"]):
        print(
            f"  [{seat}] {name:<12} wins {result['wins'][seat]:>5} "
            f"({result['win_rate'][seat] * 100:5.1f}%)  "
            f"avg shots to win {result['avg_shots_to_win'][seat]:5.1f}  "
            f"invalid shots {result['invalid_shots'][seat]}"
        )
