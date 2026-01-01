import sys
import os
from random import randint
import pygame
from car_spawner import Spawn

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 60
LEFT_BORDER = 215
RIGHT_BORDER = SCREEN_WIDTH - 474
PLAYER_START_Y = SCREEN_HEIGHT - 5
PLAYER_Y_LIMIT = SCREEN_HEIGHT - 250
CAR_SPAWN_INTERVAL = 2000
SCORE_INCREMENT_INTERVAL = 1000
INITIAL_LIVES = 3
INITIAL_SPEED = 12
BACKGROUND_ANIMATION_FRAMES = 12


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource for PyInstaller compatibility."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def load_image(path: str) -> pygame.Surface:
    """Load and convert image with alpha channel."""
    return pygame.image.load(resource_path(path)).convert_alpha()


class Game:
    def __init__(self):
        """Initialize game components and state."""
        pygame.init()
        pygame.mixer.init()

        # Setup display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_icon(load_image("images/Car_2.png"))
        pygame.display.set_caption("Avoid cars!")

        # Setup music
        pygame.mixer.music.load(resource_path("music/Music.mp3"))
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.2)

        # Setup timer for car spawning
        pygame.time.set_timer(pygame.USEREVENT, CAR_SPAWN_INTERVAL)

        # Game clock
        self.clock = pygame.time.Clock()

        # Load sounds
        self.hit_sound = pygame.mixer.Sound(resource_path("music/hit.mp3"))

        # Load background frames
        self.bg_frames = [
            load_image('images/frame_1.png'),
            load_image('images/frame_2.png'),
            load_image('images/frame_3.png'),
            load_image('images/frame_4.png'),
            load_image('images/frame_5.png'),
            load_image('images/frame_6.png')
        ]

        # Load car images
        self.cars_surf = [
            load_image('images/Car_2.png'),
            load_image('images/Car_3.png'),
            load_image('images/Car_4.png')
        ]

        # Load UI elements
        self.score_image = load_image('images/Score.png')
        self.player_car = load_image('images/Car_1.png')

        # Setup fonts
        self.font_small = pygame.font.SysFont('IMPACT', 30)
        self.font_large = pygame.font.SysFont('IMPACT', 200)

        # Player setup
        self.player_rect = self.player_car.get_rect(
            centerx=SCREEN_WIDTH // 2,
            bottom=PLAYER_START_Y
        )

        # Game state
        self.lives = INITIAL_LIVES
        self.anim_count = 0
        self.car_score = 0
        self.score_timer = 0
        self.speed = INITIAL_SPEED

        # Sprite groups
        self.cars_group = pygame.sprite.Group()
        self.create_car()

    def create_car(self) -> None:
        """Spawn a new car with random properties."""
        index = randint(0, len(self.cars_surf) - 1)
        x = randint(340, SCREEN_WIDTH - 340)
        speedx = randint(5, 10)
        Spawn(x, speedx, self.cars_surf[index], self.cars_group)

    def draw_background(self) -> None:
        """Draw animated background."""
        if self.lives > 0:
            if self.anim_count + 1 >= BACKGROUND_ANIMATION_FRAMES:
                self.anim_count = 0
            else:
                self.screen.blit(self.bg_frames[self.anim_count // 2], (0, 0))
                self.anim_count += 1
        else:
            self.screen.blit(self.bg_frames[0], (0, 0))

    def draw_ui(self) -> None:
        """Draw score and lives UI elements."""
        self.screen.blit(self.score_image, (0, 0))

        if self.lives > 0:
            score_text = self.font_small.render(
                f"Score: {self.car_score}",
                True,
                pygame.Color('black')
            )
            lives_text = self.font_small.render(
                f"Lives: {self.lives}",
                True,
                pygame.Color('black')
            )
            self.screen.blit(score_text, (50, 100))
            self.screen.blit(lives_text, (50, 140))

    def draw_game_over(self) -> None:
        """Draw game over scree n."""
        if self.lives <= 0:
            game_over_text = self.font_large.render(
                "GAME OVER",
                True,
                pygame.Color('red')
            )
            restart_text = self.font_small.render(
                "Press 'R' to play again",
                True,
                pygame.Color('orange')
            )
            self.screen.blit(game_over_text, (50, 140))
            self.screen.blit(restart_text, (350, 350))
            pygame.mixer.music.stop()

    def handle_restart(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Handle game restart."""
        if keys[pygame.K_r] and self.lives <= 0:
            self.car_score = 0
            self.lives = INITIAL_LIVES
            self.speed = INITIAL_SPEED
            self.cars_group.empty()
            self.create_car()
            pygame.mixer.music.play(-1)

    def check_collisions(self) -> None:
        """Check for collisions between player and cars."""
        for car in self.cars_group:
            if self.player_rect.collidepoint(car.rect.center):
                self.lives -= 1
                pygame.mixer.Sound.play(self.hit_sound)
                car.kill()
                if self.lives == 0:
                    self.speed = 0

    def handle_player_movement(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Handle player car movement."""
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_rect.x -= self.speed
            self.player_rect.x = max(self.player_rect.x, LEFT_BORDER)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_rect.x += self.speed
            self.player_rect.x = min(self.player_rect.x, RIGHT_BORDER)

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_rect.y -= self.speed
            self.player_rect.y = max(self.player_rect.y, 0)

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_rect.y += self.speed
            self.player_rect.y = min(self.player_rect.y, PLAYER_Y_LIMIT)

    def update_score(self) -> None:
        """Update score based on time."""
        self.score_timer += self.clock.get_time()
        if self.score_timer > SCORE_INCREMENT_INTERVAL:
            self.car_score += randint(1, 5)
            self.score_timer = 0

    def handle_events(self) -> bool:
        """Handle pygame events. Returns False if game should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.USEREVENT:
                if self.speed != 0:
                    self.create_car()
        return True

    def run(self) -> None:
        """Main game loop."""
        running = True

        while running:
            # Handle events
            running = self.handle_events()
            if not running:
                break

            # Handle input
            keys = pygame.key.get_pressed()

            if keys[pygame.K_ESCAPE]:
                break

            self.handle_player_movement(keys)
            self.handle_restart(keys)

            # Update game state
            self.check_collisions()
            self.update_score()

            # Draw everything
            self.draw_background()
            self.draw_ui()

            # Draw cars and player only if game is active
            if self.lives > 0:
                self.cars_group.draw(self.screen)
                self.screen.blit(self.player_car, self.player_rect)

            self.draw_game_over()

            # Update display
            pygame.display.update()
            self.clock.tick(FPS)
            self.cars_group.update(SCREEN_HEIGHT)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()