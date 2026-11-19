# Software Engineering Lab 04: LLM Pair-Programming Log

**Name:** Chinmai A S
**SRN:** PES2UG24AM198
**Game:** #41 Fruit Ninja (Real-Time Fruit Slice Game)
**LLM used:** Claude (Anthropic)

---

## 1. Understanding the starter code

**Me:**
> Here is my Fruit Ninja starter project (`main.py`, `game/game_engine.py`, `game/fruit.py`). Explain how the game loop works and where each of the four README tasks fits in.

**Claude:**
> `main.py` runs a 60 FPS loop. Each frame it sends every pygame event to `engine.handle_event()`, then calls `handle_input()`, `update()` and `render()`.
>
> - `update()` spawns a fruit every `spawn_interval` frames, applies gravity, removes sliced fruit and takes a life when an unsliced fruit falls off the bottom.
> - Slicing happens in `_handle_motion()`. Every `MOUSEMOTION` position is tested with `Fruit.contains_point()`.
> - Game over only sets `self.game_over = True`. `render()` then prints the score to the console once and the window freezes, with no way to restart.
>
> Where the tasks fit:
> 1. **Collision:** `contains_point()` / `_handle_motion()`
> 2. **Game Over screen:** `render()`
> 3. **Replay:** a new reset method plus event handling while `game_over` is set
> 4. **Sound:** play effects in `_slice()` and when the game ends

---

## 2. Task 1: fast swipes pass through fruit

**Me:**
> When I swipe fast, the blade visibly crosses a fruit but it isn't sliced. Why?

**Claude:**
> Pygame only reports the mouse position a few times per frame. On a fast swipe, two consecutive `MOUSEMOTION` positions can be 100+ px apart, for example one on the left of a 28 px fruit and the next on its right. `contains_point()` only checks those two points, and neither is inside the circle, so the slice is missed.
>
> The fix is to treat the blade as a **line segment** from the previous mouse position to the current one and check whether that segment touches the circle:
>
> ```python
> def intersects_segment(self, start, end):
>     x1, y1 = start
>     x2, y2 = end
>     dx, dy = x2 - x1, y2 - y1
>     length_sq = dx * dx + dy * dy
>     if length_sq == 0:
>         return self.contains_point(x1, y1)
>     t = ((self.x - x1) * dx + (self.y - y1) * dy) / length_sq
>     t = max(0.0, min(1.0, t))
>     return self.contains_point(x1 + t * dx, y1 + t * dy)
> ```
>
> Then in `_handle_motion()`, keep `self._last_pos` and test `fruit.intersects_segment(self._last_pos, pos)`.

**Me:**
> I tried it. Fast swipes work now, but sometimes a fruit gets sliced when I wasn't touching it: after I leave the mouse still and then move it somewhere else.

**Claude:**
> That happens because `_last_pos` is never forgotten. After a pause, the next motion event draws an invisible segment from the old position to the new one, and anything along that line is sliced. Count idle frames in `update()`. When the mouse hasn't moved for a few frames, let the trail fade and reset `_last_pos = None`. Then the first new motion event starts a fresh segment.

**Me (review):**
> Checked it: I moved the mouse to the top-left, waited, then moved it to the bottom-right across a fruit. The fruit is no longer sliced. A 400 px horizontal jump over a fruit at (300, 300) now slices it, where the old code missed it.

---

## 3. Task 2: Game Over screen

**Me:**
> Replace the console `print` with a proper Game Over screen that shows the final score and waits for input.

**Claude:**
> Add an `_end_game(reason)` method that sets `game_over`, stores why the game ended ("You sliced a bomb!" / "You ran out of lives!"), clears the trail and plays the game-over sound. It returns early if the game is already over, so the sound can't play twice.
>
> In `render()`, after drawing the play field, draw a translucent overlay using a `pygame.SRCALPHA` surface. Put a large red **GAME OVER**, the reason and the final score on top of it. `update()` already returns early when `game_over` is set, so the game waits for input.

**Me:**
> On the Game Over screen, the bomb I sliced is still drawn under the text.

**Claude:**
> Sliced objects are only removed from `self.fruits` in `update()`, and `update()` stops running once the game is over. Skip `fruit.sliced` objects in `render()` so they disappear immediately.

**Me (review):**
> Fixed. I also clamped `lives` to 0 so the HUD never shows "Lives: -1" when two fruit drop on the same frame.

---

## 4. Task 3: Replay with difficulty

**Me:**
> After Game Over, let the player pick Easy / Medium / Hard and play again, or exit.

**Claude:**
> Put the tunable values in a table so each difficulty is a single source of truth:
>
> ```python
> DIFFICULTIES = {
>     "Easy":   {"spawn_interval": 70, "bomb_chance": 0.08, "speed_scale": 0.9},
>     "Medium": {"spawn_interval": 55, "bomb_chance": 0.15, "speed_scale": 1.0},
>     "Hard":   {"spawn_interval": 35, "bomb_chance": 0.25, "speed_scale": 1.12},
> }
> ```
>
> Move all per-round state (fruits, trail, timer, lives, score, game_over) into a `reset(difficulty)` method and call it from `__init__`. While `game_over` is set, `handle_event()` sends events to a separate handler:
> - Clicking one of four `pygame.Rect` buttons (Easy, Medium, Hard, Exit)
> - Pressing `1`/`2`/`3` (or `E`/`M`/`H`) and `Esc`/`Q`
>
> For Exit, set `engine.quit_requested = True` and have `main.py` leave the loop. Then `pygame.quit()` still runs cleanly.

**Me:**
> Is a `speed_scale` of 1.3 OK for Hard?

**Claude:**
> At 1.3 the fruit are launched at about 20 px/frame. With gravity 0.35 they rise roughly 570 px, which is almost the whole 600 px window, so many fly off the top. Around 1.1 to 1.15 keeps them on screen. I'd use 1.12 and make Hard harder through the spawn interval and bomb chance instead.

**Me (review):**
> Tested all three modes and the Exit button. The current difficulty name is shown at the top of the HUD.

---

## 5. Task 4: Sound feedback

**Me:**
> Add sounds for slicing, hitting a bomb and game over. I'd rather not download audio files.

**Claude:**
> You can synthesise short effects at start-up and wrap them with `pygame.mixer.Sound(buffer=...)`:
> - **Slice:** a quick falling "swish" (900 Hz to 300 Hz, plus some noise, 0.12 s)
> - **Bomb:** a low, noisy rumble (120 Hz to 40 Hz, 0.6 s)
> - **Game over:** two descending tones
>
> Put this in a `SoundBank` class in `game/sounds.py`. Read the mixer's real sample rate and channel count with `pygame.mixer.get_init()` and duplicate each sample per channel. Otherwise a mono buffer on a stereo mixer plays at the wrong pitch and length. Wrap the set-up in `try/except pygame.error` so the game still runs on machines without an audio device.

**Me:**
> It worked, but the slice sound was very high-pitched and short at first.

**Claude:**
> That is the mono/stereo mismatch: the mixer had opened in stereo at 44.1 kHz while the samples were generated for 22.05 kHz mono. Generate the samples at the rate `get_init()` reports, interleave them for every channel, and call `pygame.mixer.pre_init(44100, -16, 2, 512)` before `pygame.init()` in `main.py`. The small buffer also keeps latency low.

**Me (review):**
> Sounds play correctly now. I tested with the audio device disabled: `SoundBank.enabled` is `False` and the game runs silently.

---

## 6. Final verification

**Me:**
> Can you help me write a quick headless test so I can check everything without playing?

**Claude:**
> Set `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy`, create the engine, and test the logic directly:
> 1. Put a fruit at (300, 300), send motion events at (100, 300) and (500, 300), and assert it was sliced and the score is 1.
> 2. Put a bomb in the path, swipe through it, and assert `game_over` is set and the reason mentions the bomb.
> 3. Send a `K_3` keydown and assert the difficulty is Hard, `spawn_interval == 35`, lives are 3 and the score is 0.
> 4. Run `update()` 2000 times without slicing, and assert the game ends with "You ran out of lives!".
> 5. Click the centre of the Exit button and assert `quit_requested`.

**Me:**
> All five checks pass. Summary of changes:
> - `game/fruit.py`: new `intersects_segment()` (segment vs. circle collision)
> - `game/game_engine.py`: `reset()`, a difficulty table, `_end_game()`, the Game Over overlay, replay buttons and keys, an idle trail fade, no drawing of sliced objects, lives clamped to 0
> - `game/sounds.py`: new synthesised `SoundBank`
> - `main.py`: mixer pre-init and exit through `engine.quit_requested`
