# How to write a bot

This is the short bot-writing guide. The complete lab guide, rules and worked examples are in [note.md](note.md); the repository overview is in [README.md](README.md).

The file you edit is [battleship/bots/my_bot.py](battleship/bots/my_bot.py). Keep the class name `MyBot`: the CLI looks for it.

## The contract

A bot is a subclass of `Bot` with two jobs:

| Method | When it is called | What it returns |
| - | - | - |
| `place_ships(board)` | once, in the init phase | 10 ships, each a list of `Point` |
| `choose_shot(view)` | every turn | one `Point` to fire at |

Everything else is already in `Bot`: `name`, `rng`, `last_shot`, `last_result` and the `take_turn` bookkeeping. You do not write `__init__`, and there is no state-machine boilerplate to fill in.

## The smallest bot

Start with this. It places a random valid fleet and shoots a random unknown cell.

```python
from ..map import Map, Point
from ..player import Bot, PlayerView
from ..ship import random_placement


class MyBot(Bot):
    def place_ships(self, board: Map) -> list[list[Point]]:
        return random_placement(board, self.rng)

    def choose_shot(self, view: PlayerView) -> Point:
        return self.rng.choice(view.unknown_points())
```

That is a complete, valid bot. It will not win 70% of the games, but it runs, and every part of it is replaceable.

### Placement

`place_ships` must return 10 ships with lengths `4, 3, 3, 2, 2, 2, 1, 1, 1, 1`. Each ship is a list of `Point` cells in a straight horizontal or vertical line. Ships must stay on the board, must not overlap, and must not touch even diagonally. `random_placement(board, self.rng)` is a valid default; the full placement rules and diagrams are in [note.md](note.md#placement).

The engine validates the fleet and raises `ValueError` with the bot name and the reason if it is wrong.

### What the base class gives you

- `self.name` - the bot name.
- `self.rng` - the seeded random generator. Use only this for randomness.
- `self.last_shot` - the point you fired at on your previous turn.
- `self.last_result` - `CellState.MISS`, `HIT`, `SUNK`, or `None` on the first turn.
- `self.take_turn(view)` - called by the engine. It updates `last_result` and then calls `choose_shot`. You do not override it.

### What the view gives you

`view` is your knowledge of the **enemy** board on this turn. It is a snapshot; it does not change after you return from `choose_shot`.

| Expression | Meaning |
| - | - |
| `view.board` | the `Map`; use `board.neighbours(point)` for the eight surrounding cells |
| `view.state(point)` | `CellState.UNKNOWN`, `MISS`, `HIT` or `SUNK` |
| `view.points_of(state)` | all enemy cells in that state |
| `view.unknown_points()` | cells you have not shot at yet |
| `view.remaining_ships` | lengths of enemy ships that are not sunk |
| `view.shots_fired` | how many shots you have made before this turn |

## Example: follow up on a hit

A hit keeps your turn. The simplest useful improvement is to shoot an unknown side neighbour of a cell you already hit.

```python
from ..map import Map, Point
from ..player import Bot, CellState, PlayerView
from ..ship import random_placement


class MyBot(Bot):
    def place_ships(self, board: Map) -> list[list[Point]]:
        return random_placement(board, self.rng)

    def choose_shot(self, view: PlayerView) -> Point:
        hits = view.points_of(CellState.HIT)
        if hits:
            targets = []
            for hit in hits:
                for point in view.board.neighbours(hit):
                    if point.x != hit.x and point.y != hit.y:
                        continue
                    if view.state(point) is CellState.UNKNOWN and point not in targets:
                        targets.append(point)
            if targets:
                return self.rng.choice(targets)

        return self.rng.choice(view.unknown_points())
```

Why this works:

- `view.points_of(CellState.HIT)` gives every hit that is still part of an unsunk ship.
- `view.board.neighbours(hit)` gives all eight surrounding cells.
- We skip the four diagonal cells: a straight ship can only continue left, right, up or down.
- We keep only `UNKNOWN` cells, so we do not shoot the same cell twice.
- If there is no open hit, we go back to hunting.

This is the first real step of the lab. The full hunting strategy and the complete worked examples are in [note.md](note.md#example-1-hunting-only-bot).

## Understanding parity in one paragraph

A checkerboard colour is the set of cells where `(x + y) % 2 == 0`. Every ship of length two or more covers both colours, so searching one colour cannot miss a large ship; one-cell ships can hide on the other colour, which is why the fallback to all unknown cells matters. The full explanation is in [note.md](note.md#understanding-paritybot).

## How to run it

From the repository root:

```bash
# Quick check against one bot.
python main.py --bot MyBot --opponent RandomBot --games 100 --seed 42

# Full benchmark against RandomBot, HuntBot and ParityBot.
python main.py --bot MyBot --games 1000 --seed 42

# Export ten games so the viewer can show them.
python main.py --bot MyBot --opponent ParityBot --games 10 --seed 42 --export-json web/public/data/latest.json
```

The output contains wins, win rate, average shots to win and **invalid shots**. Aim to keep invalid shots at zero: an invalid shot is replaced by a random cell and wastes a turn.

The same seed must reproduce the same series. If it does not, you are probably using the global `random` module somewhere.

## Common mistakes

| Mistake | What happens | Fix |
| - | - | - |
| Returning `None` or a string from `choose_shot` | the engine replaces it with a random shot and counts an invalid shot | always return a `Point` |
| Shooting a cell that is already `MISS`, `HIT` or `SUNK` | same invalid-shot penalty | choose from `view.unknown_points()` or check `view.state(point)` |
| Returning a point outside the board | invalid shot | use `view.unknown_points()`, or check `board.point(x, y) is not None` |
| Using `random.choice` instead of `self.rng.choice` | the series is no longer reproducible | use `self.rng` everywhere |
| Keeping target state in a local variable | it disappears before the next turn | store it as `self.something` |
| Returning the wrong fleet | `ValueError` with the bot name and the reason | 10 ships, lengths `4, 3, 3, 2, 2, 2, 1, 1, 1, 1`, no overlap, no touching |
| Using `view` after the turn | it is a snapshot and will not update | store the data you need on `self`, or use the next view |
| Printing on every shot | thousands of games become slow | print only in a small run |

## Where to look next

- [note.md](note.md#lab-stages) - game rules, the five lab stages and the 70% target.
- [note.md](note.md#bot-api) - the full `Bot` and `PlayerView` reference.
- [note.md](note.md#example-1-hunting-only-bot) - the complete hunting-only and placement-only teaching examples.
- [README.md](README.md) - setup, requirements and the replay viewer.
