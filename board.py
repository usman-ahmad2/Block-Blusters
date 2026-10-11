from constants import COLS, ROWS

class Board:
    def __init__(self):
        # grid[row][col] is None (empty) or an (R, G, B) color
        self.grid = [[None] * COLS for _ in range(ROWS)]

    def is_valid(self, cells):
        for x, y in cells:
            if x < 0 or x >= COLS or y >= ROWS:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def lock(self, cells, color):
        for x, y in cells:
            if 0 <= y < ROWS and 0 <= x < COLS:
                self.grid[y][x] = color

    def clear_lines(self):
        remaining = [row for row in self.grid if any(c is None for c in row)]
        cleared = ROWS - len(remaining)
        if cleared:
            self.grid = [[None] * COLS for _ in range(cleared)] + remaining
        return cleared