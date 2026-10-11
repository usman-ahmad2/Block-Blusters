# 🧱 Blocks Game

A Tetris-style puzzle game built in Python with Pygame. Stack falling pieces, clear full rows, and survive as the speed increases.

## ✨ Features
- 👻 Ghost piece, 📦 hold piece, and 👀 next-piece preview
- 🎲 7-bag randomizer for fair piece distribution
- 🔄 Wall-kick rotation and collision detection
- 📈 Levels with increasing speed and line-based scoring
- 🏆 Saved high score, pause, and game-over screens

## 🚀 Run It
```bash
pip install pygame
python main.py
```

## ⌨️ Controls
| Key | Action |
|---|---|
| ← → / A D | Move |
| ↓ / S | Soft drop |
| ↑ / X | Rotate clockwise |
| Z | Rotate counter-clockwise |
| Space | Hard drop |
| C / Shift | Hold piece |
| P / Esc | Pause |
| Enter | Start / restart |

## 🏅 Scoring
1 line = 100, 2 = 300, 3 = 500, 4 = 800 (each multiplied by your level). You level up every 10 lines.

## 📁 Structure
```
├── main.py        # window, input, rendering, game loop
├── game.py        # game state, gravity, scoring, hold
├── block.py       # pieces, rotation, 7-bag randomizer
├── board.py       # grid, collisions, line clearing
└── constants.py   # sizes, colors, shapes, speeds
```

## 🧠 How It Works

### 🔄 Rotation = Linear Transformation
Each piece is stored as relative `(x, y)` points around a pivot at `(0, 0)`. Rotating 90° is a **linear transformation**: multiply every point by a rotation matrix.

```
[ 0  -1 ]   [x]   [-y]
[ 1   0 ] × [y] = [ x]
```
```python
new_x, new_y = -y, x      # clockwise (the screen's y-axis points down)
new_x, new_y = y, -x      # counter-clockwise (the inverse matrix)
```
- **Example:** the I-piece `(-1,0) (0,0) (1,0) (2,0)` becomes `(0,-1) (0,0) (0,1) (0,2)`, so horizontal turns vertical.
- Rotating 4 times gives the **identity**, so the piece returns to its original shape.
- The **O piece** looks the same after rotation, so the game skips it.

### 📍 Placing a Piece = Translation
After rotating, the piece's board position is added:
```
absolute cell = rotated offset + (piece.x, piece.y)
```
Rotation followed by translation is an **affine transformation**. It is why one small shape definition works at every position and rotation on the board.

### 🧱 Board = 2D Array (Matrix)
The grid is `board[row][col]`. Each cell holds `None` (empty) or a color. A piece's four cells map straight into this matrix.

### 💥 Collision Detection
Before any move or rotation, the game tests the new cells:
- ❌ outside the left or right wall (`x < 0` or `x >= COLS`)
- ❌ below the floor (`y >= ROWS`)
- ❌ on a cell that is already filled

If any of the 4 cells fails, the move is rejected. This costs the same small amount of work for every piece.

### 🔁 Wall Kicks
If a rotation collides, the game tries small shifts in order: `(0,0) → (-1,0) → (1,0) → (-2,0) → (2,0) → (0,-1)`. The first one that fits is used. This is a search over translations.

### ⏱️ Gravity (Timer Accumulation)
Each frame adds the elapsed time (`dt`) to a timer. When the timer passes the fall delay, the piece moves down one row:
```
fall_delay = max(min_delay, initial_delay − (level − 1) × step)
```
So speed grows with level, but it never goes below a minimum.

### 🧹 Line Clearing (Filtering)
Keep only the rows that still have an empty cell, then add empty rows on top:
```python
remaining = [row for row in grid if any(c is None for c in row)]
cleared = ROWS - len(remaining)
grid = [[None]*COLS for _ in range(cleared)] + remaining
```
This makes everything above fall down automatically.

### 👻 Ghost Piece & Hard Drop
Move the piece down one row at a time until the next row would collide. The last valid position is the landing spot. The ghost piece draws it, and a hard drop jumps there.

### 🎲 7-Bag Randomizer (Permutation)
All 7 pieces are shuffled into a bag and drawn one by one, then the bag refills. This is **sampling without replacement**, so the same piece can never be missing for long.

### 📈 Scoring & Levels
```
score += line_points[lines_cleared] × level      # 100 / 300 / 500 / 800
level  = total_lines // 10 + 1
```
Clearing several lines at once is worth much more than clearing them separately.

### 🧭 State Machine
The game is always in exactly one state, and each key press can only move it along allowed paths:
```
MENU → PLAYING ⇄ PAUSED
          ↓
      GAME OVER → PLAYING
```

### 🔁 Game Loop
```
handle input → update (gravity, locking, clearing) → render → cap at 60 FPS
```

## 🛠️ Built With
Python 🐍 · Pygame 🎮 · OOP · 2D grid algorithms
