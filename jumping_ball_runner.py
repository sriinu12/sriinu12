import pygame
import random
import numpy as np

# Game constants
WIDTH, HEIGHT = 800, 400
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -12

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jumping Ball Runner")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)


def load_sound(freq=440, duration=0.15):
    """Generate a simple tone for comical sound effects."""
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = (np.sin(freq * 2 * np.pi * t) * 32767).astype(np.int16)
    stereo_wave = np.repeat(wave[:, np.newaxis], 2, axis=1)
    return pygame.sndarray.make_sound(stereo_wave)


jump_sound = load_sound()
crash_sound = load_sound(220)
high_score_sound = load_sound(880)

# Background layers for parallax effect
bg1 = pygame.Surface((WIDTH, HEIGHT))
bg1.fill((135, 206, 250))  # sky blue
bg2 = pygame.Surface((WIDTH, HEIGHT))
bg2.fill((100, 149, 237))  # cornflower blue
bg1_x = 0
bg2_x = 0

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (20, 20), 20)  # red cartoon ball
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT - 30
        self.rect.left = 50
        self.velocity = 0

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += self.velocity
        if self.rect.bottom >= HEIGHT - 30:
            self.rect.bottom = HEIGHT - 30
            self.velocity = 0

    def jump(self):
        if self.rect.bottom >= HEIGHT - 30:
            self.velocity = JUMP_STRENGTH
            jump_sound.play()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((20, 40))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT - 30
        self.rect.x = WIDTH + random.randint(0, 300)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

ball = Ball()
all_sprites = pygame.sprite.Group(ball)
obstacles = pygame.sprite.Group()

speed = 5
score = 0
high_score = 0
running = True
game_active = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                ball.jump()
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # retry game
                game_active = True
                speed = 5
                score = 0
                ball.rect.bottom = HEIGHT - 30
                ball.velocity = 0
                obstacles.empty()

    if game_active:
        # spawn obstacles
        if random.random() < 0.02:
            obstacle = Obstacle(speed)
            obstacles.add(obstacle)
            all_sprites.add(obstacle)

        # increase speed over time
        speed += 0.001

        all_sprites.update()

        if pygame.sprite.spritecollide(ball, obstacles, False):
            crash_sound.play()
            game_active = False
            if score > high_score:
                high_score = score
                high_score_sound.play()

        score += 1

        # parallax background
        bg1_x = (bg1_x - 1) % WIDTH
        bg2_x = (bg2_x - 2) % WIDTH

        screen.blit(bg1, (bg1_x - WIDTH, 0))
        screen.blit(bg1, (bg1_x, 0))
        screen.blit(bg2, (bg2_x - WIDTH, 0))
        screen.blit(bg2, (bg2_x, 0))
        all_sprites.draw(screen)

        score_surf = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_surf, (10, 10))
        high_score_surf = font.render(f"High Score: {high_score}", True, (0, 0, 0))
        screen.blit(high_score_surf, (10, 40))
    else:
        msg = font.render("Game Over - Press R to Retry", True, (255, 0, 0))
        rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(msg, rect)

    pygame.display.flip()

pygame.quit()
