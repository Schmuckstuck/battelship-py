"""HuntBot: search at random, then target neighbours of hits."""

# Map — тип игрового поля; Point — одна клетка.
from ..map import Map, Point
# Bot — базовый класс; CellState — результат выстрела; PlayerView — представление на ход.
from ..player import Bot, CellState, PlayerView
# Длины кораблей флота: 4, 3, 3, 2, 2, 2, 1, 1, 1, 1.
from ..ship import SHIP_LENGTHS


# Атрибуты name, rng, last_shot, last_result и метод take_turn наследуются от Bot.
class HuntBot(Bot):
    """Searches at random, then targets neighbours of hits."""

    # Задача фазы инициализации: вернуть флот.
    def place_ships(self, board: Map) -> list[list[Point]]:
        """Return a random valid fleet, implemented inside this bot."""
        # При неудаче с одним кораблём флот расставляется заново.
        while True:
            # Уже расставленные корабли.
            ships: list[list[Point]] = []
            # Клетки кораблей и их рамка шириной в одну клетку.
            blocked: set[Point] = set()
            # Признак того, что корабль не удалось расставить.
            failed = False
            # Сначала расставляются самые длинные корабли.
            for length in sorted(SHIP_LENGTHS, reverse=True):
                # Попытка расставить корабль данной длины.
                cells = self._place_ship(board, length, blocked)
                # Свободной позиции для корабля нет.
                if cells is None:
                    # Флот помечается как неудачный.
                    failed = True
                    # Расстановка более коротких кораблей прекращается.
                    break
                # Расставленный корабль сохраняется.
                ships.append(cells)
                # Клетки корабля и его рамка помечаются как заблокированные.
                for cell in cells:
                    # Собственная клетка корабля.
                    blocked.add(cell)
                    # Рамка шириной в одну клетку вокруг корабля.
                    blocked.update(board.neighbours(cell))
            # Все корабли расставлены.
            if not failed:
                # Возвращается корректный флот.
                return ships

    # Попытка расставить корабль заданной длины; None, если подходящей позиции нет.
    def _place_ship(
        self, board: Map, length: int, blocked: set[Point]
    ) -> list[Point] | None:
        """Try random positions for one ship without touching blocked cells."""
        # Проверяется не более 1000 случайных позиций.
        for _ in range(1000):
            # Горизонтальная или вертикальная ориентация выбирается равновероятно.
            horizontal = self.rng.randrange(2) == 0
            # Горизонтальный корабль.
            if horizontal:
                # Левый столбец; оставляется место под длину корабля.
                x = self.rng.randrange(board.width - length + 1)
                # Произвольная строка.
                y = self.rng.randrange(board.height)
                # Последовательные клетки вправо.
                cells = [board.point(x + i, y) for i in range(length)]
            # Вертикальный корабль.
            else:
                # Произвольный столбец.
                x = self.rng.randrange(board.width)
                # Верхняя строка; оставляется место под длину корабля.
                y = self.rng.randrange(board.height - length + 1)
                # Последовательные клетки вниз.
                cells = [board.point(x, y + i) for i in range(length)]
            # Позиция корректна, только если все её клетки в пределах поля и свободны.
            if all(cell is not None and cell not in blocked for cell in cells):
                # Возвращаются клетки корабля без проверок на None.
                return [cell for cell in cells if cell is not None]
        # Позиция не найдена; вызывающий код расставляет флот заново.
        return None

    # Задача фазы поиска: вернуть один выстрел.
    def choose_shot(self, view: PlayerView) -> Point:
        """Target neighbours of hits, otherwise hunt at random."""
        # Неизвестные клетки рядом с открытым попаданием.
        targets: list[Point] = []
        # Попадания в непотопленные корабли.
        for hit in view.points_of(CellState.HIT):
            # Все восемь соседних клеток попадания.
            for point in view.board.neighbours(hit):
                # Диагональные клетки не могут продолжать прямой корабль.
                if point.x != hit.x and point.y != hit.y:
                    # Диагональная клетка пропускается.
                    continue
                # Свободные клетки, ещё не добавленные в список целей.
                if view.state(point) is CellState.UNKNOWN and point not in targets:
                    # Клетка добавляется в список целей.
                    targets.append(point)
        # У повреждённого корабля остаются открытые клетки.
        if targets:
            # Сначала добивается этот корабль.
            return self.rng.choice(targets)
        # Иначе выполняется поиск по любой неизвестной клетке.
        return self.rng.choice(view.unknown_points())
