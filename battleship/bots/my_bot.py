"""Student bot template.

A bot has two jobs: place its fleet and choose a shot. Override place_ships
and choose_shot. Everything else (name, rng, last_shot, last_result) comes
from Bot.
"""

# Map — тип игрового поля; Point — одна клетка.
from ..map import Map, Point
# Bot — базовый класс; PlayerView — представление на один ход.
from ..player import Bot, PlayerView
# Общая функция возвращает корректный случайный флот.
from ..ship import random_placement


# Атрибуты name, rng, last_shot, last_result и метод take_turn наследуются от Bot.
class MyBot(Bot):
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
        # Выбирается клетка, по которой ещё не было выстрелов.
        return self.rng.choice(view.unknown_points())
