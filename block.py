import random

from constants import PIECE_COLORS, SHAPES, SHAPE_TYPES, SPAWN_X, SPAWN_Y


class Block:

    def __init__(self, shape_type):
        self.type = shape_type
        self.color = PIECE_COLORS[shape_type]
        self.cells = list(SHAPES[shape_type])   # relative offsets
        self.x = SPAWN_X
        self.y = SPAWN_Y

    def get_cells(self, dx=0, dy=0, relative=None):
        rel = self.cells if relative is None else relative
        return [(self.x + cx + dx, self.y + cy + dy) for cx, cy in rel]

    def rotated(self, clockwise=True):
        if self.type == "O":
            return list(self.cells)
        if clockwise:
            return [(-y, x) for x, y in self.cells]
        return [(y, -x) for x, y in self.cells]

class Bag:
    def __init__(self):
        self.queue = []

    def next(self):
        if not self.queue:
            self.queue = SHAPE_TYPES[:]
            random.shuffle(self.queue)
        return self.queue.pop()