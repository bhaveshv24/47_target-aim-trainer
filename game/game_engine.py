import pygame
import random
from .target import Target

# Game Engine

WHITE = (255, 255, 255)
RED = (220, 60, 60)

class GameEngine:
    DIFFICULTIES = {
        "Easy": {"base_radius": 50, "min_radius": 18, "lifespan_frames": 120},
        "Medium": {"base_radius": 40, "min_radius": 12, "lifespan_frames": 90},
        "Hard": {"base_radius": 30, "min_radius": 8, "lifespan_frames": 60},
    }

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.margin = 60
        self.hud_height = 60
        self.current_difficulty = "Medium"
        self.target = self._spawn_target()

        self.round_seconds = 30
        self.time_left_frames = self.round_seconds * 60

        self.hits = 0
        self.misses = 0
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 26)
        self.title_font = pygame.font.SysFont("Arial", 44, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 22)
        self.button_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.hint_font = pygame.font.SysFont("Arial", 15)
        self.game_over = False

        # Setup buttons for Game Over screen
        btn_y = 355
        btn_w = 120
        btn_h = 42
        spacing = 18
        start_x = (self.width - (4 * btn_w + 3 * spacing)) // 2
        self.btn_easy_rect = pygame.Rect(start_x, btn_y, btn_w, btn_h)
        self.btn_medium_rect = pygame.Rect(start_x + btn_w + spacing, btn_y, btn_w, btn_h)
        self.btn_hard_rect = pygame.Rect(start_x + 2 * (btn_w + spacing), btn_y, btn_w, btn_h)
        self.btn_exit_rect = pygame.Rect(start_x + 3 * (btn_w + spacing), btn_y, btn_w, btn_h)

    def _spawn_target(self):
        config = self.DIFFICULTIES.get(self.current_difficulty, self.DIFFICULTIES["Medium"])
        x = random.randint(self.margin, self.width - self.margin)
        y = random.randint(self.margin + self.hud_height, self.height - self.margin)
        return Target(
            x,
            y,
            base_radius=config["base_radius"],
            min_radius=config["min_radius"],
            lifespan_frames=config["lifespan_frames"],
        )

    def restart(self, difficulty="Medium"):
        self.current_difficulty = difficulty
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.time_left_frames = self.round_seconds * 60
        self.game_over = False
        self.target = self._spawn_target()

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_e):
                    self.restart("Easy")
                elif event.key in (pygame.K_2, pygame.K_m):
                    self.restart("Medium")
                elif event.key in (pygame.K_3, pygame.K_h):
                    self.restart("Hard")
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.btn_easy_rect.collidepoint(pos):
                    self.restart("Easy")
                elif self.btn_medium_rect.collidepoint(pos):
                    self.restart("Medium")
                elif self.btn_hard_rect.collidepoint(pos):
                    self.restart("Hard")
                elif self.btn_exit_rect.collidepoint(pos):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)


    def _handle_click(self, pos):
        x, y = pos
        if self.target.contains_point(x, y):
            self.hits += 1
            self.score += 1
            self.target = self._spawn_target()
        else:
            self.misses += 1

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        self.time_left_frames -= 1
        if self.time_left_frames <= 0:
            self.game_over = True
            return

        self.target.update()
        if self.target.expired():
            self.misses += 1  # letting a target time out counts as a miss too
            self.target = self._spawn_target()

    def accuracy(self):
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return round(100 * self.hits / total, 1)

    def _render_game_over(self, screen):
        # Semi-transparent backdrop
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(230)
        overlay.fill((25, 25, 30))
        screen.blit(overlay, (0, 0))

        # Title
        title_surf = self.title_font.render("GAME OVER", True, RED)
        title_rect = title_surf.get_rect(center=(self.width // 2, 110))
        screen.blit(title_surf, title_rect)

        # Final score & accuracy
        score_surf = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_surf.get_rect(center=(self.width // 2, 180))
        screen.blit(score_surf, score_rect)

        acc_surf = self.font.render(f"Final Accuracy: {self.accuracy()}%", True, WHITE)
        acc_rect = acc_surf.get_rect(center=(self.width // 2, 225))
        screen.blit(acc_surf, acc_rect)

        stats_surf = self.subtitle_font.render(
            f"Hits: {self.hits}    |    Misses: {self.misses}", True, (180, 180, 185)
        )
        stats_rect = stats_surf.get_rect(center=(self.width // 2, 270))
        screen.blit(stats_surf, stats_rect)

        # Replay buttons
        mouse_pos = pygame.mouse.get_pos()
        buttons = [
            (self.btn_easy_rect, "Easy [1]", (40, 140, 75), (55, 175, 95)),
            (self.btn_medium_rect, "Medium [2]", (190, 140, 20), (230, 170, 30)),
            (self.btn_hard_rect, "Hard [3]", (190, 50, 50), (230, 70, 70)),
            (self.btn_exit_rect, "Exit [Q]", (85, 85, 95), (115, 115, 125)),
        ]

        for rect, label, base_color, hover_color in buttons:
            is_hover = rect.collidepoint(mouse_pos)
            color = hover_color if is_hover else base_color
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, WHITE if is_hover else (200, 200, 200), rect, width=2, border_radius=8)

            text_surf = self.button_font.render(label, True, WHITE)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

        hint_surf = self.hint_font.render(
            "Select difficulty to replay, or Exit (click button or press 1 / 2 / 3 / Q)",
            True,
            (160, 160, 170),
        )
        hint_rect = hint_surf.get_rect(center=(self.width // 2, 425))
        screen.blit(hint_surf, hint_rect)

    def render(self, screen):
        if self.game_over:
            self._render_game_over(screen)
            return

        r = int(self.target.visual_radius())
        pygame.draw.circle(screen, RED, (self.target.x, self.target.y), r)
        pygame.draw.circle(screen, WHITE, (self.target.x, self.target.y), r, 2)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        seconds_left = max(0, self.time_left_frames // 60)
        timer_text = self.font.render(f"Time: {seconds_left}s", True, WHITE)
        screen.blit(timer_text, (self.width - 140, 10))

        acc_text = self.font.render(f"Accuracy: {self.accuracy()}%", True, WHITE)
        screen.blit(acc_text, (self.width // 2 - 90, 10))

        diff_text = self.subtitle_font.render(f"Difficulty: {self.current_difficulty}", True, (160, 160, 170))
        screen.blit(diff_text, (10, 42))


