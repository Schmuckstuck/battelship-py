"""Student bot template.

A bot has two jobs: place its fleet and choose a shot. Override place_ships
and choose_shot. Everything else (name, rng, last_shot, last_result) comes
from Bot.
"""

# Map — тип игрового поля; Point — одна клетка.
from ..map import Map, Point
# Bot — базовый класс; PlayerView — представление на один ход.
from ..player import Bot, PlayerView, CellState
# Общая функция возвращает корректный случайный флот.
from ..ship import random_placement


# Атрибуты name, rng, last_shot, last_result и метод take_turn наследуются от Bot.
class TestBot(Bot):
    """Your bot: edit the two methods below."""

    # Задача фазы инициализации: вернуть флот.
    def place_ships(self, board: Map) -> list[list[Point]]:
        """Return your fleet. random_placement is a valid starting point."""
        # Вызов общей функции.
        return random_placement(board, self.rng)

    # Задача фазы поиска: вернуть один выстрел.
    def choose_shot(self, view: PlayerView) -> Point:
        """Return the next point to fire at.

        Hint: self.last_result is the result of your previous shot.
        """

        water : set[Point] = set()

        for sunk in view.points_of(CellState.SUNK):
            water.update(view.board.neighbours(sunk))


        targets : list[Point] = []

        for hit in view.points_of(CellState.HIT):
            # Все восемь соседних клеток попадания.
            for point in view.board.neighbours(hit):
                # Диагональные клетки не могут продолжать прямой корабль.

                if point.x != hit.x and point.y != hit.y:
                    # Диагональная клетка пропускается.
                    continue

                if point in water:
                    continue

                # Свободные клетки, ещё не добавленные в список целей.
                if view.state(point) is CellState.UNKNOWN and point not in targets:
                    # Клетка добавляется в список целей.
                    targets.append(point)
        if targets:
            # Сначала добивается этот корабль.
            return self.rng.choice(targets)


        open_cells : list[Point] = [
            point for point in view.unknown_points() if point not in water
        ]

        parity_cells : list[Point] = [
            point for point in open_cells if (point.x + point.y) % 2 == 0
        ]

        return self.rng.choice(parity_cells or open_cells or view.unknown_points())
