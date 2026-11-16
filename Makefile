# Battleship: build the viewer, generate replays, serve a replay.

# Use the project venv when it exists; otherwise use the platform default.
VENV_PYTHON := $(firstword $(wildcard .venv/Scripts/python.exe .venv/bin/python))
ifeq ($(VENV_PYTHON),)
ifeq ($(OS),Windows_NT)
PYTHON ?= python
else
PYTHON ?= python3
endif
else
PYTHON ?= $(VENV_PYTHON)
endif

NPM := npm
PORT := 8000
GAMES := 10
SEED := 42
BOT := ParityBot
OPPONENT := HuntBot
REPLAY := web/public/data/latest.json
VIEWER_DIST := web/dist/battleship-viewer/browser

.PHONY: help build data server dev clean

help:
	@echo "Python: $(PYTHON)"
	@echo "make build     install viewer deps and build the Angular app"
	@echo "make data      generate the demo replay for the viewer"
	@echo "make server    serve the built viewer at http://localhost:$(PORT)"
	@echo "make dev       start the Angular dev server at http://localhost:4200"
	@echo "make clean     remove build outputs and caches"

# Install viewer dependencies and build the Angular app.
build:
	cd web && $(NPM) install --no-fund --no-audit && $(NPM) run build

# Generate the replay JSON the viewer loads.
data:
	$(PYTHON) main.py --bot $(BOT) --opponent $(OPPONENT) --games $(GAMES) --seed $(SEED) --export-json $(REPLAY)

# Serve the built viewer (run make build first).
server:
	$(PYTHON) -m http.server $(PORT) --directory $(VIEWER_DIST)

# Start the Angular dev server at http://localhost:4200.
dev:
	cd web && $(NPM) start

# Remove build outputs, caches and local artifacts.
clean:
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in [pathlib.Path('web/dist'), pathlib.Path('web/.angular'), pathlib.Path('build'), pathlib.Path('.ruff_cache')]]; [p.unlink(missing_ok=True) for p in pathlib.Path('.').glob('web-viewer*.png')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
