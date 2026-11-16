#!/usr/bin/env python3
"""CLI to benchmark one bot against a reference bot and optionally export a replay."""

import argparse

from battleship.bots import HuntBot, MyBot, ParityBot, RandomBot
from battleship.exporter import write_replay
from battleship.recorder import Recorder
from battleship.simulator import play_series, print_series

BOTS = {
    "RandomBot": RandomBot,
    "HuntBot": HuntBot,
    "ParityBot": ParityBot,
    "MyBot": MyBot,
}

# Bots the benchmark compares against. MyBot is the student's working copy, so it
# only shows up as an opponent when requested explicitly with --opponent.
REFERENCE_BOTS = ["RandomBot", "HuntBot", "ParityBot"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Battleship bot benchmark")
    parser.add_argument("--games", "-g", type=int, default=1000, help="games per matchup")
    parser.add_argument("--seed", "-s", type=int, default=None, help="random seed")
    parser.add_argument(
        "--bot", "-b", choices=list(BOTS), default="ParityBot", help="bot to benchmark"
    )
    parser.add_argument(
        "--opponent",
        choices=list(BOTS),
        default=None,
        help="play against a single reference bot instead of benchmarking all",
    )
    parser.add_argument(
        "--export-json",
        type=str,
        default=None,
        metavar="PATH",
        help="save a replay JSON (requires --opponent) for the web viewer",
    )
    args = parser.parse_args()

    if args.games < 1:
        parser.error("--games must be at least 1")
    if args.export_json is not None and args.opponent is None:
        parser.error("--export-json requires --opponent")

    my_bot = BOTS[args.bot]

    if args.opponent is not None:
        recorder = Recorder() if args.export_json else None
        result = play_series(
            my_bot, BOTS[args.opponent], args.games, seed=args.seed, recorder=recorder
        )
        print_series(result)
        if recorder is not None:
            path = write_replay(args.export_json, recorder)
            print(f"Replay saved to {path}")
        return

    print(f"{args.bot} vs reference bots, {args.games} games each (seed={args.seed}):\n")
    for name in REFERENCE_BOTS:
        ref = BOTS[name]
        if ref is my_bot:
            continue
        result = play_series(my_bot, ref, args.games, seed=args.seed)
        rate = result["win_rate"][0] * 100
        avg = result["avg_shots_to_win"][0]
        invalid = result["invalid_shots"][0]
        print(
            f"  vs {name:<10}  {args.bot} wins {rate:5.1f}%  (avg {avg:5.1f} shots to win)"
            + (f"  invalid shots: {invalid}" if invalid else "")
        )


if __name__ == "__main__":
    main()
