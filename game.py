import json
import os

from block import Bag, Block
from board import Board
from constants import (
    HARD_DROP_POINTS,
    HIGH_SCORE_FILE,
    INITIAL_FALL_DELAY,
    LINE_SCORES,
    LINES_PER_LEVEL,
    MIN_FALL_DELAY,
    SOFT_DROP_DELAY,
    SOFT_DROP_POINTS,
    SPEED_STEP,
)

SCORE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), HIGH_SCORE_FILE)

# Positions to try when a rotation is blocked (simple wall kicks)
KICKS = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]

MENU, PLAYING, PAUSED, GAME_OVER = "menu", "playing", "paused", "game_over"

def load_high_score():
    try:
        with open(SCORE_PATH, "r") as f:
            return int(json.load(f).get("high_score", 0))
    except (OSError, ValueError, TypeError, AttributeError):
        return 0

def save_high_score(score):
    try:
        with open(SCORE_PATH, "w") as f:
            json.dump({"high_score": score}, f)
    except OSError:
        pass

class Game:
    def __init__(self):
        self.high_score = load_high_score()
        self.reset()
        self.state = MENU

    # setup
    def reset(self):
        self.board = Board()
        self.bag = Bag()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.fall_timer = 0
        self.soft_dropping = False
        self.hold_type = None
        self.can_hold = True
        self.state = PLAYING
        self.next_block = Block(self.bag.next())
        self.current = None
        self.spawn()

    def spawn(self):
        self.current = self.next_block
        self.next_block = Block(self.bag.next())
        self.can_hold = True
        self.fall_timer = 0
        if not self.board.is_valid(self.current.get_cells()):
            self.end_game()

    def end_game(self):
        self.state = GAME_OVER
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)

    # helpers
    @property
    def fall_delay(self):
        delay = max(MIN_FALL_DELAY, INITIAL_FALL_DELAY - (self.level - 1) * SPEED_STEP)
        if self.soft_dropping:
            delay = min(delay, SOFT_DROP_DELAY)
        return delay

    def ghost_cells(self):
        dy = 0
        while self.board.is_valid(self.current.get_cells(0, dy + 1)):
            dy += 1
        return self.current.get_cells(0, dy), dy

    # actions
    def move(self, dx, dy):
        if self.state != PLAYING:
            return False
        if self.board.is_valid(self.current.get_cells(dx, dy)):
            self.current.x += dx
            self.current.y += dy
            return True
        return False

    def rotate(self, clockwise=True):
        if self.state != PLAYING:
            return False
        rel = self.current.rotated(clockwise)
        for dx, dy in KICKS:
            if self.board.is_valid(self.current.get_cells(dx, dy, rel)):
                self.current.cells = rel
                self.current.x += dx
                self.current.y += dy
                return True
        return False

    def hard_drop(self):
        if self.state != PLAYING:
            return
        _, dy = self.ghost_cells()
        self.current.y += dy
        self.score += dy * HARD_DROP_POINTS
        self.lock_piece()

    def hold(self):
        if self.state != PLAYING or not self.can_hold:
            return
        held = self.hold_type
        self.hold_type = self.current.type
        if held is None:
            self.spawn()
        else:
            self.current = Block(held)
            self.fall_timer = 0
            if not self.board.is_valid(self.current.get_cells()):
                self.end_game()
                return
        self.can_hold = False

    def toggle_pause(self):
        if self.state == PLAYING:
            self.state = PAUSED
        elif self.state == PAUSED:
            self.state = PLAYING

    # core loop
    def lock_piece(self):
        self.board.lock(self.current.get_cells(), self.current.color)
        cleared = self.board.clear_lines()
        if cleared:
            self.lines += cleared
            self.score += LINE_SCORES.get(cleared, 0) * self.level
            self.level = self.lines // LINES_PER_LEVEL + 1
        if self.score > self.high_score:
            self.high_score = self.score
        self.spawn()

    def update(self, dt):
        if self.state != PLAYING:
            return
        self.fall_timer += dt
        while self.fall_timer >= self.fall_delay and self.state == PLAYING:
            self.fall_timer -= self.fall_delay
            if self.move(0, 1):
                if self.soft_dropping:
                    self.score += SOFT_DROP_POINTS
            else:
                self.lock_piece()
                break