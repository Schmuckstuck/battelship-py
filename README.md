# Battleship-Py

Battleship game engine and bot framework for the lab. The complete student guide is [note.md](note.md); a shorter bot-writing walkthrough is [BOT_GUIDE.md](BOT_GUIDE.md).

## Requirements

- **Python 3.11 or newer** (3.12 recommended). The engine, bots and CLI use only the standard library, so there is nothing to `pip install`.
- **Node.js 22.12+ and npm** only if you want to build the Angular replay viewer. The bot lab works without Node.
- **GNU Make** is optional. Every make target has a direct command below.
- A modern browser for the viewer. Git is needed only to clone or update the repository.

## Setup

### Windows tools with winget

`winget` is included with App Installer on Windows 10/11. Open PowerShell and check:

```powershell
winget --version
```

If `winget` is not recognized, install or update **App Installer** from the Microsoft Store, or download Python from [python.org](https://www.python.org/downloads/) and Node.js from [nodejs.org](https://nodejs.org/en/download).

Install the tools with winget:

```powershell
# Python 3.12 (the lab requires 3.11 or newer).
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements

# Node.js current release; npm is included with Node.js.
winget install -e --id OpenJS.NodeJS --accept-package-agreements --accept-source-agreements

# Or use the LTS release instead:
# winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements

# Git, needed only to clone or update the repository.
winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements

# uv, optional Python environment manager.
winget install -e --id astral-sh.uv --accept-package-agreements --accept-source-agreements
```

To install the required three in one loop:

```powershell
$tools = @("Python.Python.3.12", "OpenJS.NodeJS", "Git.Git")
foreach ($tool in $tools) {
    winget install --exact --id $tool --accept-package-agreements --accept-source-agreements
}
```

Close and reopen PowerShell so the new `PATH` is active, then check the versions:

```powershell
python --version
node --version
npm --version
git --version
```

`npm` comes with Node.js; do not install it separately. If `python` opens the Microsoft Store, disable the `python.exe` and `python3.exe` aliases under **Settings > Apps > Advanced app settings > App execution aliases**. The winget Python package is a real interpreter; the Store alias is not.

### Windows Python environment

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell refuses to run the activation script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This creates a project-local `.venv`. Activate it for the `python ...` commands below; if you prefer not to activate, use `.\.venv\Scripts\python.exe ...` instead. You do not need to activate it for `make`: the Makefile detects `.venv\Scripts\python.exe` automatically. If `python` is not available but the Python launcher is, use `py -3 -m venv .venv`.

### macOS and Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Use `python3.12` instead of `python3` if your `python3` is older than 3.11.

### Using uv (optional)

If [uv](https://docs.astral.sh/uv/) is installed, it can create the same environment from `.python-version`:

```bash
uv sync
```

Then activate `.venv` as above, or prefix commands with `uv run`, for example `uv run python main.py --bot MyBot --games 10 --seed 42`.

## Verify the setup

Run a short series from the repository root:

```bash
python main.py --bot MyBot --opponent RandomBot --games 10 --seed 42
```

The output starts with `games=10` and has one line per bot with wins, win rate, average shots to win and invalid shots. If Python cannot import `battleship`, you are not in the repository root.

## Experiment and benchmark

Edit [battleship/bots/my_bot.py](battleship/bots/my_bot.py), then run:

```bash
# Quick feedback against one opponent.
python main.py --bot MyBot --opponent RandomBot --games 100 --seed 42

# Benchmark against RandomBot, HuntBot and ParityBot.
python main.py --bot MyBot --games 1000 --seed 42
```

The same `--seed` must reproduce the same series. Keep `--games` small while iterating and use 1000 for the final result. The five stages and the 70% target are in [note.md](note.md#lab-stages); [BOT_GUIDE.md](BOT_GUIDE.md) walks through a first bot.

## Using make (optional)

If GNU Make is installed, the common commands are:

```bash
# Show the Python interpreter make will use.
make help
# Write the demo replay for the viewer.
make data
# Install viewer dependencies and build the Angular app.
make build
# Serve the built viewer at http://localhost:8000.
make server
# Start the Angular dev server at http://localhost:4200.
make dev
```

The Makefile uses `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` elsewhere when it exists. To force a different interpreter, pass `PYTHON=...`, for example:

```bash
make data PYTHON=.venv/Scripts/python.exe
```

## CLI flags

| Flag | Meaning |
| - | - |
| `--bot NAME` | bot to benchmark; default ParityBot |
| `--opponent NAME` | single opponent; without it all reference bots are used |
| `--games N` | games per series; default 1000 |
| `--seed N` | random seed for reproducibility |
| `--export-json PATH` | save a replay (requires `--opponent`) |

Reference bots: RandomBot, HuntBot and ParityBot.

## Replay viewer

The Angular viewer shows recorded games and the five lab stages. Node.js is needed only to build it; serving the built files uses Python.

```bash
# 1. Generate a demo replay.
make data

# 2. Install viewer dependencies and build (Node.js and npm required).
make build

# 3. Serve it at http://localhost:8000.
make server
```

Without make:

```bash
python main.py --bot ParityBot --opponent HuntBot --games 10 --seed 42 --export-json web/public/data/latest.json
cd web
npm install
npm run build
cd ..
python -m http.server 8000 --directory web/dist/battleship-viewer/browser
```

Open http://localhost:8000. `make data` writes a demo of ParityBot vs HuntBot; to inspect your own bot, export it to the same path:

```bash
python main.py --bot MyBot --opponent ParityBot --games 10 --seed 42 --export-json web/public/data/latest.json
```

After exporting a new replay, run `make build` again so `web/dist` receives the new JSON, or use `make dev` / `npm start`, which serves `web/public` directly at http://localhost:4200.

The full viewer description, including the five stages, is in [note.md](note.md#replay-viewer).

## Structure

```text
battleship/
- map.py        # Point, Map
- ship.py       # Ship, validate_fleet, random_placement
- player.py     # Bot, CellState, PlayerView
- engine.py     # BattleshipGame, Fleet, ShotResult
- recorder.py   # records games for replay
- exporter.py   # saves replay JSON
- simulator.py  # play_series - series statistics
- bots/         # default bots and the my_bot.py template
web/            # Angular replay viewer and the five lab stages
main.py         # CLI
README.md       # this file
BOT_GUIDE.md    # short bot-writing guide
note.md         # complete student guide
```

## Maintainer notes

### Starter and teaching examples

This repository ships the student starter without a worked bot in `battleship/bots/`: `battleship/bots/my_bot.py` is the file the student edits, and the other bots are the opponents used by the lab. The two examples in [note.md](note.md#example-1-hunting-only-bot) are deliberate teaching examples. Do not copy them into `my_bot.py` in the distributed starter, and do not add another complete solution or solution replay to the repository.

### Default bots

The three default bots each carry their own copy of the random placement loop (`place_ships` plus `_place_ship` in the bot module) and do not import `random_placement`. `MyBot` deliberately keeps the one-line `random_placement(board, self.rng)` call as the student's starting point. The placement code is intentionally duplicated so each default bot can be read on its own.

### Engine architecture

- `GamePhase` is INIT, HUNT or FINISHED. In INIT `BattleshipGame` calls `place_ships` while both fleets stay hidden; then the phase switches to HUNT and the shot loop starts. The phase becomes FINISHED when a fleet is sunk.
- `BattleshipGame.run(first)` validates both fleets, then runs the shot loop. A miss passes the turn; a hit or a sunk ship keeps the turn.
- `PlayerView` gives the bot a snapshot of the engine grid, so the bot cannot change it.
- `_sanitize` replaces an invalid shot with a random unknown cell and counts it in `invalid_shots`.
- `Bot` in `battleship/player.py` owns `name`, `rng`, `last_shot` and `last_result`, provides default `place_ships` and `choose_shot`, and implements `take_turn`: it records the result of the previous shot in `last_result`, then calls `choose_shot`.
- `Recorder` collects rounds and events; `write_replay` saves them as JSON.

### Series statistics

`play_series` returns a dict where every metric is a two-element list indexed by seat `[bot0, bot1]` (a bot can play against itself):

| Key | Meaning |
| - | - |
| `games` | number of games |
| `bots` | bot names `[bot0, bot1]` |
| `wins` | wins per seat |
| `win_rate` | win rate per seat |
| `avg_shots_to_win` | average shots to win (won games only) |
| `avg_shots_total` | average shots per game |
| `invalid_shots` | invalid shots replaced by the engine |

### Viewer architecture

- `web/src/app/replay-store.ts` keeps replay state as signals: round, event index, selected seat, playback and derived boards. It also derives the five lab-stage evidence by replaying the shots.
- `web/src/app/lab-stages.ts` holds the five stage descriptions and hints.
- `web/src/app/app.html` renders the stage rail, the active stage panel and the stage-specific body.
- `board-view/` renders one board, including the striped known-water cells.
- `web/dist/battleship-viewer/browser` is the built viewer output; `npm run build` writes it.

### Manual checks

The repository ships without an automated test suite. Verify a change with a short series:

```bash
# Run a short series.
python main.py --bot ParityBot --opponent HuntBot --games 10 --seed 42
# Check the Python style.
ruff check .
# Build the Angular viewer.
make build
```
