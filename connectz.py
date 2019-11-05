import sys
from enum import Enum
from typing import Optional, List, TextIO, Sequence


class IllegalGameException(Exception):
    pass


class ParsingProblem(ValueError):
    pass


class InvalidParametersException(IllegalGameException):
    def __init__(self, x: int, y: int, z: int):
        super(InvalidParametersException, self).__init__(f'Illegal game x={x} y={y} z={z}')


class InvalidColumnException(IllegalGameException):
    def __init__(self, column: int):
        super(InvalidColumnException, self).__init__(f'Invalid column {column}')


class ColumnToHighException(IllegalGameException):
    def __init__(self, column: int):
        super(ColumnToHighException, self).__init__(f'Column {column} is to high')


class ToManyMovesException(IllegalGameException):
    def __init__(self):
        super(ToManyMovesException, self).__init__(f'There are more moves after end of the game')


class LackOfResultException(IllegalGameException):
    def __init__(self):
        super(LackOfResultException, self).__init__(f'There is leak for result after all moves were done')


class Player(Enum):
    FIRST = 1
    SECOND = 2


class GameResult(Enum):
    DRAW = 0
    FIRST_WON = 1
    SECOND_WON = 2


def players():
    while True:
        yield Player.FIRST
        yield Player.SECOND


class ConnectZ:
    def __init__(self, text_io: TextIO):
        self._grid = None
        try:
            self._x, self._y, self._z = (int(parameter) for parameter in text_io.readline().split())
            self._moves = [int(line) for line in text_io]
        except ValueError as e:
            raise ParsingProblem('Problem with parsing input stream', e)

        if self._z > max(self._x, self._y) or min(self._x, self._y, self._z) < 1:
            raise InvalidParametersException(self._x, self._y, self._z)

    def put_disc(self, player: Player, column: int):
        if not 0 < column <= self._x:
            raise InvalidColumnException(column)
        column_list = self._grid[column - 1]
        if len(column_list) >= self._y:
            raise ColumnToHighException(column)

        column_list.append(player)

    def _get_or_none(self, x: int, y: int) -> Optional[Player]:
        column = self._grid[x]
        return None if y >= len(column) else column[y]

    def _diagonals(self):
        for x in range(self._x + 1 - self._z):
            for y in range(self._y + 1 - self._z):
                yield zip(range(x, self._x), range(y, self._y))
                yield zip(range(self._x - 1 - x, -1, -1), range(y, self._y))

    def _possible_lines(self) -> Sequence[List[Optional[Player]]]:
        yield from self._grid

        for y in range(self._y):
            yield [self._get_or_none(x, y) for x in range(self._x)]

        for diagonal in self._diagonals():
            yield [self._get_or_none(x, y) for x, y in diagonal]

    def _check_for_draw(self) -> bool:
        return all(len(column) == self._y for column in self._grid)

    def _check_for_result_in_line(self, line: Sequence[Optional[Player]], player: Player) -> Optional[GameResult]:
        repeats = 0
        for field in line:
            if repeats == self._z:
                return GameResult(player.value)
            if field == player:
                repeats += 1
            else:
                repeats = 0

        if repeats == self._z:
            return GameResult(player.value)

        return None

    def _check_for_result(self, player: Player) -> Optional[GameResult]:
        for line in self._possible_lines():
            result_in_line = self._check_for_result_in_line(line, player)
            if result_in_line:
                return result_in_line

        if self._check_for_draw():
            return GameResult.DRAW

        return None

    @staticmethod
    def get_second_user(player: Player) -> Player:
        return Player.FIRST if player == Player.SECOND else Player.SECOND

    def play(self) -> GameResult:
        self._grid = [[] for _ in range(self._x)]
        for column, player in zip(self._moves, players()):
            if self._check_for_result(self.get_second_user(player)):
                raise ToManyMovesException()
            self.put_disc(player, column)

        result = self._check_for_result(player)

        if not result:
            raise LackOfResultException()

        return result

if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2:
        if len(args) >= 1:
            script_name = args[0]
        else:
            script_name = 'connectz.py'
        print(f'{script_name}: Provide one input file')
    else:
        try:
            with open(args[1]) as file:
                result = ConnectZ(file).play()
            sys.exit(result.value)
        except LackOfResultException:
            sys.exit(3)
        except ToManyMovesException:
            sys.exit(4)
        except ColumnToHighException:
            sys.exit(5)
        except InvalidColumnException:
            sys.exit(6)
        except InvalidParametersException:
            sys.exit(7)
        except ParsingProblem:
            sys.exit(8)
        except FileNotFoundError:
            sys.exit(9)
