# Battleship-Py

Игровой движок игры «Морской бой» и фреймворк для разработки ботов, используемые в лабораторной работе. Краткое руководство по написанию бота — в [BOT_GUIDE.md](BOT_GUIDE.md).

## Требования

- **Python 3.11 или новее** (рекомендуется 3.12). Движок, боты и интерфейс командной строки используют только стандартную библиотеку, поэтому `pip install` не требуется.
- **Node.js 22.12+ и npm** — только если требуется собрать средство просмотра повторов на Angular. Для лабораторной работы с ботами Node.js не нужен.
- **GNU Make** — необязательно. Для каждой цели make ниже приведена эквивалентная прямая команда.
- Современный браузер для средства просмотра повторов. Git требуется только для клонирования или обновления репозитория.

## Настройка окружения

### Установка инструментов в Windows с помощью winget

`winget` входит в состав App Installer в Windows 10 и 11. Откройте PowerShell и проверьте:

```powershell
winget --version
```

Если команда `winget` не распознаётся, установите или обновите **App Installer** из Microsoft Store либо загрузите Python с сайта [python.org](https://www.python.org/downloads/), а Node.js — с сайта [nodejs.org](https://nodejs.org/en/download).

Установите инструменты с помощью winget:

```powershell
# Python 3.12 (для лабораторной работы требуется версия 3.11 или новее).
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements

# Текущая версия Node.js; npm входит в состав Node.js.
winget install -e --id OpenJS.NodeJS --accept-package-agreements --accept-source-agreements

# Вместо неё можно установить версию LTS:
# winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements

# Git — только для клонирования или обновления репозитория.
winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements

# uv — необязательный менеджер окружений Python.
winget install -e --id astral-sh.uv --accept-package-agreements --accept-source-agreements
```

Чтобы установить три обязательных инструмента одним циклом:

```powershell
$tools = @("Python.Python.3.12", "OpenJS.NodeJS", "Git.Git")
foreach ($tool in $tools) {
    winget install --exact --id $tool --accept-package-agreements --accept-source-agreements
}
```

Закройте и снова откройте PowerShell, чтобы новый `PATH` вступил в силу, затем проверьте версии:

```powershell
python --version
node --version
npm --version
git --version
```

`npm` поставляется вместе с Node.js, поэтому отдельно устанавливать его не нужно. Если команда `python` открывает Microsoft Store, отключите псевдонимы `python.exe` и `python3.exe` в разделе **Параметры > Приложения > Дополнительные параметры приложений > Псевдонимы выполнения приложений**. Пакет Python из winget представляет собой полноценный интерпретатор, тогда как псевдоним Microsoft Store им не является.

### Виртуальное окружение Python в Windows

Из корня репозитория:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Если PowerShell отказывается выполнять сценарий активации:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

В результате создаётся локальное для проекта окружение `.venv`. Активируйте его для приведённых ниже команд `python ...`; если активация нежелательна, используйте вместо неё `.\.venv\Scripts\python.exe ...`. Для `make` активация не требуется: Makefile автоматически обнаруживает `.venv\Scripts\python.exe`. Если `python` недоступен, но установлен загрузчик Python, выполните `py -3 -m venv .venv`.

### macOS и Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Если версия `python3` ниже 3.11, используйте `python3.12` вместо `python3`.

### Использование uv (необязательно)

Если установлен [uv](https://docs.astral.sh/uv/), он может создать то же окружение на основе файла `.python-version`:

```bash
uv sync
```

Затем активируйте `.venv`, как описано выше, или добавляйте к командам префикс `uv run`, например: `uv run python main.py --bot MyBot --games 10 --seed 42`.

## Проверка настройки

Запустите короткую серию из корня репозитория:

```bash
python main.py --bot MyBot --opponent RandomBot --games 10 --seed 42 --export-json web/public/data/latest.json

```

Вывод начинается со строки `games=10` и содержит по одной строке на каждого бота: число побед, долю побед, среднее число выстрелов до победы и число некорректных выстрелов. Если Python не может импортировать пакет `battleship`, вы находитесь не в корне репозитория.

## Эксперименты и сравнительное тестирование

Отредактируйте файл [battleship/bots/my_bot.py](battleship/bots/my_bot.py), затем выполните:

```bash
# Быстрая проверка против одного соперника.
python main.py --bot MyBot --opponent RandomBot --games 100 --seed 42 --export-json web/public/data/latest.json

# Сравнительное тестирование против RandomBot, HuntBot и ParityBot.
python main.py --bot MyBot --games 1000 --seed 42 --export-json web/public/data/latest.json

```

Одно и то же значение `--seed` должно воспроизводить одну и ту же серию. Во время итераций задавайте небольшое значение `--games`, а для окончательного результата используйте 1000. Пять этапов и целевой показатель 70 % описаны в [note.md](note.md#lab-stages); в [BOT_GUIDE.md](BOT_GUIDE.md) разобран первый бот.

## Использование make (необязательно)

Если установлен GNU Make, основные команды имеют следующий вид:

```bash
# Показать интерпретатор Python, который будет использовать make.
make help
# Записать демонстрационный повтор для средства просмотра.
make data
# Установить зависимости средства просмотра и собрать приложение Angular.
make build
# Запустить собранное средство просмотра по адресу http://localhost:8000.
make server
# Запустить сервер разработки Angular по адресу http://localhost:4200.
make dev
```

Makefile использует `.venv/Scripts/python.exe` в Windows или `.venv/bin/python` в остальных системах, если соответствующий файл существует. Чтобы принудительно выбрать другой интерпретатор, передайте `PYTHON=...`, например:

```bash
make data PYTHON=.venv/Scripts/python.exe
```

## Параметры командной строки

| Параметр | Назначение |
| - | - |
| `--bot NAME` | бот, для которого выполняется тестирование; по умолчанию ParityBot |
| `--opponent NAME` | единственный соперник; если параметр не указан, используются все эталонные боты |
| `--games N` | число партий в серии; по умолчанию 1000 |
| `--seed N` | зерно генератора случайных чисел для воспроизводимости |
| `--export-json PATH` | сохранить повтор (требуется `--opponent`) |

Эталонные боты: RandomBot, HuntBot и ParityBot.

## Средство просмотра повторов

Приложение на Angular отображает записанные партии и пять этапов лабораторной работы. Node.js требуется только для его сборки; для раздачи собранных файлов используется Python.

```bash
# 1. Сгенерировать демонстрационный повтор.
make data

# 2. Установить зависимости средства просмотра и выполнить сборку (требуются Node.js и npm).
make build

# 3. Запустить его по адресу http://localhost:8000.
make server
```

Без make:

```bash
python main.py --bot ParityBot --opponent HuntBot --games 10 --seed 42 --export-json web/public/data/latest.json
cd web
npm install
npm run build
cd ..
python -m http.server 8000 --directory web/dist/battleship-viewer/browser
```

Откройте http://localhost:8000. Команда `make data` записывает демонстрационную партию ParityBot против HuntBot; чтобы просмотреть собственного бота, экспортируйте его в тот же путь:

```bash
python main.py --bot MyBot --opponent ParityBot --games 10 --seed 42 --export-json web/public/data/latest.json
```

После экспорта нового повтора выполните `make build` ещё раз, чтобы новый файл JSON попал в `web/dist`, или используйте `make dev` / `npm start`, которые напрямую раздают каталог `web/public` по адресу http://localhost:4200.

Полное описание средства просмотра, включая пять этапов, приведено в [note.md](note.md#replay-viewer).

## Структура проекта

```text
battleship/
- map.py        # Point, Map
- ship.py       # Ship, validate_fleet, random_placement
- player.py     # Bot, CellState, PlayerView
- engine.py     # BattleshipGame, Fleet, ShotResult
- recorder.py   # записывает партии для повторов
- exporter.py   # сохраняет повтор в формате JSON
- simulator.py  # play_series — статистика серии
- bots/         # стандартные боты и шаблон my_bot.py
web/            # средство просмотра повторов на Angular и пять этапов лабораторной работы
main.py         # интерфейс командной строки
README.md       # этот файл
BOT_GUIDE.md    # краткое руководство по написанию бота
note.md         # полное руководство для студентов
```

## Заметки для сопровождающих

### Стартовый вариант и учебные примеры

Репозиторий поставляется со стартовым вариантом для студентов, не содержащим готового бота в каталоге `battleship/bots/`: файл `battleship/bots/my_bot.py` предназначен для редактирования студентом, а остальные боты являются соперниками, используемыми в лабораторной работе. Два примера в [note.md](note.md#example-1-hunting-only-bot) представляют собой специально подобранные учебные примеры. Не следует копировать их в `my_bot.py` распространяемого стартового варианта, а также добавлять в репозиторий другие полные решения или повторы с решениями.

### Стандартные боты

Каждый из трёх стандартных ботов содержит собственную копию цикла случайной расстановки (функции `place_ships` и `_place_ship` в модуле бота) и не импортирует `random_placement`. В `MyBot` намеренно сохранён вызов `random_placement(board, self.rng)` в одну строку как отправная точка для студента. Код расстановки намеренно дублируется, чтобы каждый стандартный бот можно было читать независимо от остальных.

### Архитектура движка

- `GamePhase` принимает одно из значений: INIT, HUNT или FINISHED. В фазе INIT `BattleshipGame` вызывает `place_ships`, при этом оба флота остаются скрытыми; затем фаза переключается в HUNT и начинается цикл выстрелов. Фаза переходит в FINISHED, когда один из флотов полностью потоплен.
- `BattleshipGame.run(first)` проверяет корректность обоих флотов, после чего запускает цикл выстрелов. При промахе ход переходит к сопернику; при попадании или потоплении корабля ход сохраняется.
- `PlayerView` предоставляет боту снимок сетки движка, поэтому бот не может её изменить.
- `_sanitize` заменяет некорректный выстрел случайной неизвестной клеткой и учитывает его в счётчике `invalid_shots`.
- `Bot` из модуля `battleship/player.py` хранит атрибуты `name`, `rng`, `last_shot` и `last_result`, предоставляет реализации `place_ships` и `choose_shot` по умолчанию и реализует метод `take_turn`: он записывает результат предыдущего выстрела в `last_result`, после чего вызывает `choose_shot`.
- `Recorder` накапливает раунды и события; `write_replay` сохраняет их в формате JSON.

### Статистика серии

`play_series` возвращает словарь (dict), в котором каждый показатель представлен списком из двух элементов по числу мест — `[bot0, bot1]` (бот может играть сам с собой):

| Ключ | Назначение |
| - | - |
| `games` | число партий |
| `bots` | имена ботов `[bot0, bot1]` |
| `wins` | число побед для каждого места |
| `win_rate` | доля побед для каждого места |
| `avg_shots_to_win` | среднее число выстрелов до победы (только для выигранных партий) |
| `avg_shots_total` | среднее число выстрелов за партию |
| `invalid_shots` | некорректные выстрелы, заменённые движком |

### Архитектура средства просмотра

- `web/src/app/replay-store.ts` хранит состояние повтора в виде сигналов: раунд, индекс события, выбранное место, воспроизведение и производные игровые поля. Кроме того, он вычисляет признаки выполнения пяти этапов лабораторной работы, повторно воспроизводя последовательность выстрелов.
- `web/src/app/lab-stages.ts` содержит описания и подсказки для пяти этапов.
- `web/src/app/app.html` отображает ленту этапов, панель активного этапа и содержимое, зависящее от этапа.
- `board-view/` отображает одно игровое поле, включая клетки известной воды со штриховкой.
- `web/dist/battleship-viewer/browser` — каталог с результатами сборки средства просмотра; файлы в него записывает команда `npm run build`.

### Ручные проверки

Репозиторий не содержит автоматизированного набора тестов. Проверяйте изменения с помощью короткой серии:

```bash
# Запустить короткую серию.
python main.py --bot ParityBot --opponent HuntBot --games 10 --seed 42
# Проверить соблюдение стиля Python.
ruff check .
# Собрать приложение просмотра на Angular.
make build
```
