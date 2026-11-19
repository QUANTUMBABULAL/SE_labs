# Real-Time Fruit Slice Game

This project is a terminal-based Fruit Ninja–style slicing game using **Pygame**. It introduces students to interactive game design using object-oriented principles and real-time graphical rendering.

---

## What’s Provided

A partially working version of a fruit-slicing game with:

- Fruit (and the occasional bomb) launched upward from the bottom of the screen, arcing under gravity
- A mouse-tracked "blade" that slices whatever it touches
- Lives, score, and a game-over condition when a bomb is sliced or too many fruit are missed

You are expected to **analyze**, **interact with an AI assistant**, and **complete/fix** the game to make it fully functional.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**

---

## Getting Started

### Setup

1. Clone the repo or download the project folder.
2. Make sure you have Python 3.10+ installed.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the game:

```bash
python main.py
```


---


## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Refine Collision Detection

> Fast swipes sometimes pass right through a fruit without slicing it, even though the blade visually crossed it. Investigate and enhance slice detection so quick swipes register reliably.


### Task 2: Implement Game Over Condition

> Add a screen that displays the final score once a bomb is sliced or the player runs out of lives, then gracefully waits for input instead of just printing to the console.


### Task 3: Add Replay Option

> After Game Over, allow the user to play again by choosing a difficulty (Easy, Medium, or Hard spawn rate/bomb chance), or exit.


### Task 4: Add Sound Feedback

> Add basic sound effects for slicing a fruit, hitting a bomb, and the game-over moment.


---

## Expected Behavior

- Fruit and bombs launch from the bottom of the screen and arc under gravity
- Moving the mouse across a fruit slices it and increases the score
- Slicing a bomb ends the game immediately
- Letting a fruit fall back off the bottom of the screen without slicing it costs a life
- The game ends when lives reach zero or a bomb is sliced

---

## Folder Structure

```
fruit-ninja-lite-main/
├── main.py
├── requirements.txt
├── game/
│   ├── game_engine.py
│   ├── fruit.py
│   └── sounds.py        # added: synthesised sound effects
├── lab4/
│   ├── CHAT_HISTORY.md  # LLM pair-programming log
│   ├── original_code/   # starter code, used for the "before" video
│   ├── before.mp4
│   └── after.mp4
└── README.md
```

---

## What I Changed

| Task | Status | Where | Summary |
|------|--------|-------|---------|
| 1. Collision detection | Done | `game/fruit.py` → `intersects_segment()`, `game/game_engine.py` → `_handle_motion()` | Slicing now tests the whole blade segment between two mouse events (closest point on segment vs. radius), so fast swipes can no longer skip over a fruit. |
| 2. Game Over screen | Done | `GameEngine._end_game()`, `_render_game_over()` | Translucent overlay with "GAME OVER", the reason (bomb / out of lives) and the final score. The game freezes and waits for input instead of printing to the console. |
| 3. Replay option | Done | `GameEngine.reset()`, `DIFFICULTIES`, `_handle_game_over_event()` | Easy / Medium / Hard / Exit buttons (mouse) or keys `1`/`2`/`3` and `Esc`. Each difficulty changes spawn rate, bomb chance and launch speed. |
| 4. Sound feedback | Done | `game/sounds.py` | Slice, bomb and game-over sounds are synthesised at start-up, so no audio files are needed. If no audio device exists, the game runs silently. |

Extra fixes found during review: sliced objects are no longer drawn on the Game Over screen, lives can't drop below 0, bombs get a red outline, and the blade trail fades when the mouse stops so a new swipe doesn't join up with an old point.

---

## Submission Checklist

Submission is only the following three things:

- [x] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [x] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [x] The Chat/LLM used page link, with the complete chat history
