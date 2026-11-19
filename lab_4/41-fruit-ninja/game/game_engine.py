import pygame
import random
from .fruit import Fruit
from .sounds import SoundBank

# Game Engine

WHITE = (255, 255, 255)
BOMB_BLACK = (30, 30, 30)
FRUIT_COLORS = [(220, 60, 60), (230, 140, 40), (230, 200, 40), (90, 180, 90)]
OVERLAY = (0, 0, 0, 170)
BUTTON_BG = (60, 70, 110)
BUTTON_HOVER = (95, 110, 170)
RED = (230, 70, 70)

# spawn_interval = frames between spawns, bomb_chance = probability a
# spawned object is a bomb, speed_scale = launch speed multiplier.
DIFFICULTIES = {
    "Easy": {"spawn_interval": 70, "bomb_chance": 0.08, "speed_scale": 0.9},
    "Medium": {"spawn_interval": 55, "bomb_chance": 0.15, "speed_scale": 1.0},
    "Hard": {"spawn_interval": 35, "bomb_chance": 0.25, "speed_scale": 1.12},
}
START_LIVES = 3


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont("Arial", 28)
        self.big_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.sounds = SoundBank()

        self.quit_requested = False
        self.difficulty = "Medium"
        self.buttons = self._build_buttons()
        self.reset("Medium")

    # ------------------------------------------------------------------
    # Setup / replay
    # ------------------------------------------------------------------
    def reset(self, difficulty):
        """Start a fresh round with the chosen difficulty settings."""
        settings = DIFFICULTIES[difficulty]
        self.difficulty = difficulty
        self.spawn_interval = settings["spawn_interval"]
        self.bomb_chance = settings["bomb_chance"]
        self.speed_scale = settings["speed_scale"]

        self.fruits = []
        self.trail = []  # recent mouse positions, drawn as the "blade"
        self._spawn_timer = 0
        self.lives = START_LIVES
        self.score = 0
        self.game_over = False
        self.game_over_reason = ""
        self._last_pos = None
        self._idle_frames = 0

    def _build_buttons(self):
        labels = list(DIFFICULTIES) + ["Exit"]
        width, height, gap = 130, 50, 20
        total = len(labels) * width + (len(labels) - 1) * gap
        left = (self.width - total) // 2
        top = self.height // 2 + 70
        return [
            (label, pygame.Rect(left + i * (width + gap), top, width, height))
            for i, label in enumerate(labels)
        ]

    def spawn_fruit(self):
        x = random.randint(60, self.width - 60)
        vy = -random.uniform(13, 16) * self.speed_scale
        vx = random.uniform(-2, 2)
        gravity = 0.35
        kind = "bomb" if random.random() < self.bomb_chance else "fruit"

        fruit = Fruit(x, self.height + 30, vx, vy, gravity, kind=kind)
        fruit.color = BOMB_BLACK if kind == "bomb" else random.choice(FRUIT_COLORS)
        self.fruits.append(fruit)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def handle_event(self, event):
        if self.game_over:
            self._handle_game_over_event(event)
            return

        if event.type == pygame.MOUSEMOTION:
            self._handle_motion(event.pos)

    def _handle_game_over_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for label, rect in self.buttons:
                if rect.collidepoint(event.pos):
                    self._choose(label)
        elif event.type == pygame.KEYDOWN:
            keys = {
                pygame.K_1: "Easy",
                pygame.K_e: "Easy",
                pygame.K_2: "Medium",
                pygame.K_m: "Medium",
                pygame.K_3: "Hard",
                pygame.K_h: "Hard",
                pygame.K_ESCAPE: "Exit",
                pygame.K_q: "Exit",
            }
            if event.key in keys:
                self._choose(keys[event.key])

    def _choose(self, label):
        if label == "Exit":
            self.quit_requested = True
        else:
            self.reset(label)

    def _handle_motion(self, pos):
        # Task 1: test the whole blade segment travelled since the last
        # motion event, not just the newest point, so fast swipes that
        # jump over a fruit between frames still slice it.
        start = self._last_pos if self._last_pos is not None else pos
        for fruit in self.fruits:
            if not fruit.sliced and fruit.intersects_segment(start, pos):
                self._slice(fruit)
                if self.game_over:
                    break

        self._last_pos = pos
        self._idle_frames = 0
        self.trail.append(pos)
        if len(self.trail) > 15:
            self.trail.pop(0)

    def _slice(self, fruit):
        fruit.sliced = True
        if fruit.kind == "bomb":
            self.sounds.play("bomb")
            self._end_game("You sliced a bomb!")
        else:
            self.score += 1
            self.sounds.play("slice")

    def _end_game(self, reason):
        if self.game_over:
            return
        self.game_over = True
        self.game_over_reason = reason
        self.trail = []
        self.sounds.play("game_over")

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    # ------------------------------------------------------------------
    # Update / render
    # ------------------------------------------------------------------
    def update(self):
        if self.game_over:
            return

        # Let the blade trail fade when the mouse stops moving, and forget
        # the last point so a later swipe doesn't connect to a stale one.
        self._idle_frames += 1
        if self._idle_frames > 2 and self.trail:
            self.trail.pop(0)
            if not self.trail:
                self._last_pos = None

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.spawn_fruit()

        still_alive = []
        for fruit in self.fruits:
            fruit.update()
            if fruit.sliced:
                continue
            if fruit.off_screen(self.height):
                if fruit.kind == "fruit":
                    self.lives -= 1
                continue
            still_alive.append(fruit)
        self.fruits = still_alive

        if self.lives <= 0:
            self.lives = 0
            self._end_game("You ran out of lives!")

    def render(self, screen):
        for fruit in self.fruits:
            if fruit.sliced:
                continue
            color = getattr(fruit, "color", WHITE)
            center = (int(fruit.x), int(fruit.y))
            pygame.draw.circle(screen, color, center, fruit.radius)
            if fruit.kind == "bomb":
                pygame.draw.circle(screen, RED, center, fruit.radius, 3)

        if len(self.trail) >= 2:
            pygame.draw.lines(screen, WHITE, False, self.trail, 3)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(lives_text, (self.width - 130, 10))
        mode_text = self.small_font.render(self.difficulty, True, WHITE)
        screen.blit(mode_text, mode_text.get_rect(midtop=(self.width // 2, 14)))

        if self.game_over:
            self._render_game_over(screen)

    def _render_game_over(self, screen):
        # Task 2: proper Game Over screen with the final score.
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        screen.blit(overlay, (0, 0))

        cx = self.width // 2
        title = self.big_font.render("GAME OVER", True, RED)
        screen.blit(title, title.get_rect(center=(cx, self.height // 2 - 110)))
        reason = self.font.render(self.game_over_reason, True, WHITE)
        screen.blit(reason, reason.get_rect(center=(cx, self.height // 2 - 45)))
        final = self.font.render(f"Final score: {self.score}", True, WHITE)
        screen.blit(final, final.get_rect(center=(cx, self.height // 2)))
        prompt = self.small_font.render(
            "Play again - choose a difficulty (1/2/3) or Exit (Esc)", True, WHITE
        )
        screen.blit(prompt, prompt.get_rect(center=(cx, self.height // 2 + 45)))

        # Task 3: replay buttons.
        mouse = pygame.mouse.get_pos()
        for label, rect in self.buttons:
            bg = BUTTON_HOVER if rect.collidepoint(mouse) else BUTTON_BG
            pygame.draw.rect(screen, bg, rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)
            text = self.font.render(label, True, WHITE)
            screen.blit(text, text.get_rect(center=rect.center))
