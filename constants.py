# Board / grid

COLS = 15
ROWS = 25
CELL_SIZE = 30

# Window layout

SIDE_PANEL_WIDTH = 200                      # score, level, next piece
BOARD_WIDTH = COLS * CELL_SIZE
BOARD_HEIGHT = ROWS * CELL_SIZE
SCREEN_WIDTH = BOARD_WIDTH + SIDE_PANEL_WIDTH
SCREEN_HEIGHT = BOARD_HEIGHT
FPS = 60
TITLE = "Block Blusters"

# Colors (R, G, B)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
LIGHT_GRAY = (120, 120, 120)
BACKGROUND = (20, 20, 30)
GRID_LINE = (50, 50, 60)

PIECE_COLORS = {
    "I": (0, 240, 240),    # cyan
    "O": (240, 240, 0),    # yellow
    "T": (160, 0, 240),    # purple
    "S": (0, 240, 0),      # green
    "Z": (240, 0, 0),      # red
    "J": (0, 0, 240),      # blue
    "L": (240, 160, 0),    # orange
}

# Shapes: relative (x, y) offsets around a pivot at (0, 0)
# x grows to the right, y grows downward

SHAPES = {
    "I": [(-1, 0), (0, 0), (1, 0), (2, 0)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(-1, 0), (0, 0), (1, 0), (0, -1)],
    "S": [(-1, 0), (0, 0), (0, -1), (1, -1)],
    "Z": [(-1, -1), (0, -1), (0, 0), (1, 0)],
    "J": [(-1, -1), (-1, 0), (0, 0), (1, 0)],
    "L": [(1, -1), (-1, 0), (0, 0), (1, 0)],
}

SHAPE_TYPES = list(SHAPES.keys())
# Spawn position (top-center of the board)
SPAWN_X = COLS // 2 - 1
SPAWN_Y = 1

# Gravity / speed

INITIAL_FALL_DELAY = 800        # ms between automatic drops at level 1
MIN_FALL_DELAY = 80             # fastest possible fall speed (ms)
SPEED_STEP = 70                 # ms removed from delay per level
SOFT_DROP_DELAY = 50            # ms between drops while holding down
LINES_PER_LEVEL = 10

# Input repeat (ms) for holding left/right

KEY_REPEAT_DELAY = 170
KEY_REPEAT_INTERVAL = 50

# Scoring (multiplied by current level)

LINE_SCORES = {
    0: 0,
    1: 100,
    2: 300,
    3: 500,
    4: 800,
}
SOFT_DROP_POINTS = 1            # per cell
HARD_DROP_POINTS = 2            # per cell

# Files

HIGH_SCORE_FILE = "highscore.json"