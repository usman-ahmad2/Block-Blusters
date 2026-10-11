import sys
import pygame

from constants import (
    BACKGROUND,
    BOARD_HEIGHT,
    BOARD_WIDTH,
    CELL_SIZE,
    COLS,
    FPS,
    GRAY,
    GRID_LINE,
    KEY_REPEAT_DELAY,
    KEY_REPEAT_INTERVAL,
    LIGHT_GRAY,
    ROWS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TITLE,
    WHITE,
)
from game import GAME_OVER, MENU, PAUSED, PLAYING, Game, save_high_score

PANEL_X = BOARD_WIDTH + 20

# Drawing helpers

def shade(color, amount):
    return tuple(max(0, min(255, c + amount)) for c in color)

def draw_cell(surface, px, py, color, size=CELL_SIZE):
    rect = pygame.Rect(px, py, size, size)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.line(surface, shade(color, 70), rect.topleft, rect.topright, 2)
    pygame.draw.line(surface, shade(color, 70), rect.topleft, rect.bottomleft, 2)
    pygame.draw.line(surface, shade(color, -70), rect.bottomleft, rect.bottomright, 2)
    pygame.draw.line(surface, shade(color, -70), rect.topright, rect.bottomright, 2)

def draw_text(surface, text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)

def draw_board(surface, game):
    pygame.draw.rect(surface, BACKGROUND, (0, 0, BOARD_WIDTH, BOARD_HEIGHT))

    # grid lines
    for c in range(COLS + 1):
        pygame.draw.line(surface, GRID_LINE, (c * CELL_SIZE, 0), (c * CELL_SIZE, BOARD_HEIGHT))
    for r in range(ROWS + 1):
        pygame.draw.line(surface, GRID_LINE, (0, r * CELL_SIZE), (BOARD_WIDTH, r * CELL_SIZE))

    # locked cells
    for r in range(ROWS):
        for c in range(COLS):
            color = game.board.grid[r][c]
            if color is not None:
                draw_cell(surface, c * CELL_SIZE, r * CELL_SIZE, color)

    if game.current is not None and game.state in (PLAYING, PAUSED):
        # ghost piece
        ghost, _ = game.ghost_cells()
        for x, y in ghost:
            if y >= 0:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, game.current.color, rect.inflate(-4, -4), 2)
        # active piece
        for x, y in game.current.get_cells():
            if y >= 0:
                draw_cell(surface, x * CELL_SIZE, y * CELL_SIZE, game.current.color)

    # board border
    pygame.draw.rect(surface, LIGHT_GRAY, (0, 0, BOARD_WIDTH, BOARD_HEIGHT), 2)

def draw_preview(surface, block, box, label, fonts, dim=False):
    draw_text(surface, label, fonts["medium"], WHITE, box.x, box.y - 28)
    pygame.draw.rect(surface, GRAY, box)
    pygame.draw.rect(surface, LIGHT_GRAY, box, 2)
    if block is None:
        return
    size = 22
    xs = [x for x, _ in block.cells]
    ys = [y for _, y in block.cells]
    w = (max(xs) - min(xs) + 1) * size
    h = (max(ys) - min(ys) + 1) * size
    ox = box.centerx - w // 2 - min(xs) * size
    oy = box.centery - h // 2 - min(ys) * size
    color = shade(block.color, -90) if dim else block.color
    for x, y in block.cells:
        draw_cell(surface, ox + x * size, oy + y * size, color, size)

def draw_panel(surface, game, fonts):
    pygame.draw.rect(surface, (15, 15, 22), (BOARD_WIDTH, 0, SCREEN_WIDTH - BOARD_WIDTH, SCREEN_HEIGHT))

    draw_preview(surface, game.next_block, pygame.Rect(PANEL_X, 40, 150, 90), "NEXT", fonts)

    # held piece is drawn from its type, so build a temporary block
    from block import Block

    held = Block(game.hold_type) if game.hold_type else None
    draw_preview(surface, held, pygame.Rect(PANEL_X, 175, 150, 90), "HOLD", fonts, dim=not game.can_hold)

    y = 290
    for label, value in (
        ("SCORE", game.score),
        ("LEVEL", game.level),
        ("LINES", game.lines),
        ("BEST", game.high_score),
    ):
        draw_text(surface, label, fonts["small"], LIGHT_GRAY, PANEL_X, y)
        draw_text(surface, str(value), fonts["medium"], WHITE, PANEL_X, y + 18)
        y += 52

    hints = ["Arrows/AD: move", "Up/X: rotate  Z: back", "Space: hard drop", "C: hold   P: pause"]
    y = SCREEN_HEIGHT - 20 * len(hints) - 8
    for h in hints:
        draw_text(surface, h, fonts["tiny"], LIGHT_GRAY, PANEL_X - 8, y)
        y += 20

def draw_overlay(surface, fonts, title, lines):
    shade_surf = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
    shade_surf.fill((0, 0, 0, 180))
    surface.blit(shade_surf, (0, 0))
    cx = BOARD_WIDTH // 2
    draw_text(surface, title, fonts["big"], WHITE, cx, BOARD_HEIGHT // 2 - 60, center=True)
    for i, line in enumerate(lines):
        draw_text(surface, line, fonts["small"], LIGHT_GRAY, cx, BOARD_HEIGHT // 2 + i * 26, center=True)

def render(screen, game, fonts):
    screen.fill(BACKGROUND)
    draw_board(screen, game)
    draw_panel(screen, game, fonts)

    if game.state == MENU:
        draw_overlay(screen, fonts, TITLE, ["Press ENTER to start", "ESC to quit"])
    elif game.state == PAUSED:
        draw_overlay(screen, fonts, "PAUSED", ["Press P to resume"])
    elif game.state == GAME_OVER:
        draw_overlay(
            screen,
            fonts,
            "GAME OVER",
            [f"Score: {game.score}", "Press ENTER to play again", "ESC to quit"],
        )
    pygame.display.flip()

# Input

class HorizontalRepeat:
    def __init__(self):
        self.direction = 0
        self.timer = 0

    def update(self, game, dt):
        if game.state != PLAYING:
            self.direction = 0
            return
        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        direction = int(bool(right)) - int(bool(left))

        if direction == 0:
            self.direction = 0
        elif direction != self.direction:
            self.direction = direction
            game.move(direction, 0)
            self.timer = KEY_REPEAT_DELAY
        else:
            self.timer -= dt
            while self.timer <= 0:
                game.move(direction, 0)
                self.timer += KEY_REPEAT_INTERVAL

def handle_keydown(game, key):
    if game.state == MENU:
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            game.reset()
        elif key == pygame.K_ESCAPE:
            return False
    elif game.state == GAME_OVER:
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_r):
            game.reset()
        elif key == pygame.K_ESCAPE:
            return False
    elif game.state == PAUSED:
        if key in (pygame.K_p, pygame.K_ESCAPE):
            game.toggle_pause()
    elif game.state == PLAYING:
        if key in (pygame.K_UP, pygame.K_w, pygame.K_x):
            game.rotate(True)
        elif key == pygame.K_z:
            game.rotate(False)
        elif key == pygame.K_SPACE:
            game.hard_drop()
        elif key in (pygame.K_c, pygame.K_LSHIFT, pygame.K_RSHIFT):
            game.hold()
        elif key in (pygame.K_p, pygame.K_ESCAPE):
            game.toggle_pause()
    return True

# Main

def main():
    pygame.init()
    pygame.display.set_caption(TITLE + " 🧱")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    fonts = {
        "big": pygame.font.Font(None, 56),
        "medium": pygame.font.Font(None, 36),
        "small": pygame.font.Font(None, 26),
        "tiny": pygame.font.Font(None, 22),
    }

    game = Game()
    repeat = HorizontalRepeat()
    running = True

    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if not handle_keydown(game, event.key):
                    running = False
            elif event.type == pygame.WINDOWFOCUSLOST and game.state == PLAYING:
                game.toggle_pause()

        keys = pygame.key.get_pressed()
        game.soft_dropping = bool(keys[pygame.K_DOWN] or keys[pygame.K_s])
        repeat.update(game, dt)
        game.update(dt)
        render(screen, game, fonts)

    save_high_score(game.high_score)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()