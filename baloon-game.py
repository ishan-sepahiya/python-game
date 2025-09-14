import pygame
import random

pygame.init()

# Get screen info for fullscreen
infoObject = pygame.display.Info()
screen_width = 1500
screen_height = 800

# ---------------- CLOUD CLASS ----------------
class Cloud(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed  # Move left
        if self.rect.right < 0:  # If off-screen, reset to the right
            self.rect.left = pygame.display.get_surface().get_width() + random.randint(0, 200)
            self.rect.y = random.randint(0, pygame.display.get_surface().get_height() // 2)

# Set up the game window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dodge the Needles")

# Colors
SKY_BLUE = (135, 206, 250)
BALLOON_RED = (255, 69, 0)
NEEDLE_GRAY = (60, 60, 60)
BUTTON_GREEN = (50, 200, 50)
BUTTON_RED = (200, 50, 50)
TEXT_WHITE = (255, 255, 255)
BACKGROUND_BLACK = (0, 0, 0)
PIN_HEAD_COLOR = (255, 255, 0)

# Player settings (Balloon)
player_width = 40
player_height = 60
player_x = (screen_width / 2) - (player_width / 2)
player_y = screen_height - player_height - 30
player_speed = 2

# Enemy settings (Needles)
enemy_width = 10
enemy_height = 80
pinhead_radius = 6
enemies = []

# Game variables
score = 0
base_enemy_speed = 1
base_spawn_rate = 200
game_state = 'playing'

# Fonts
score_font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)
button_font = pygame.font.Font(None, 50)

# ---------------- CLOUDS SETUP ----------------
cloud_image_original = pygame.image.load('cloud.png').convert_alpha()  # Load original cloud image

cloud_group = pygame.sprite.Group()
for _ in range(5):
    x = random.randint(0, screen_width)
    y = random.randint(0, screen_height // 2)
    speed = random.uniform(0.2, 0.5)
    # Random scale factor between 0.5 and 1.5
    scale_factor = random.uniform(0.5, 1.5)
    cloud_image = pygame.transform.scale(
        cloud_image_original,
        (int(cloud_image_original.get_width() * scale_factor),
         int(cloud_image_original.get_height() * scale_factor))
    )
    cloud = Cloud(cloud_image, x, y, speed)
    cloud_group.add(cloud)

# ---------------- GAME FUNCTIONS ----------------
def reset_game():
    """Resets all game variables to their initial state."""
    global player_x,player_y, score, enemies, base_enemy_speed, base_spawn_rate, game_state
    player_x = (screen_width / 2) - (player_width / 2)
    player_y = screen_height - player_height - 30
    score = 0
    enemies.clear()
    base_enemy_speed = 1
    base_spawn_rate = 200
    game_state = 'playing'

def draw_balloon(x, y, width, height, color):
    """Draws a balloon shape with a string."""
    pygame.draw.ellipse(screen, color, (x, y, width, height))
    knot_points = [(x + width // 2, y + height), (x + width // 2 - 5, y + height + 10), (x + width // 2 + 5, y + height + 10)]
    pygame.draw.polygon(screen, color, knot_points)
    pygame.draw.line(screen, BACKGROUND_BLACK, (x + width // 2, y + height + 10), (x + width // 2, y + height + 30), 2)

def draw_downward_triangle(x, y, width, height, color):
    """Draws a downward-pointing needle-shaped triangle with a pinhead."""
    points = [
        (x - width / 2, y + pinhead_radius),
        (x + width / 2, y + pinhead_radius),
        (x, y + height)
    ]
    pygame.draw.polygon(screen, color, points)
    pygame.draw.circle(screen, PIN_HEAD_COLOR, (x, y + pinhead_radius), pinhead_radius)

def is_collision(player_x, player_y, enemy):
    """Checks for collision using bounding boxes."""
    enemy_x, enemy_y, _ = enemy
    balloon_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    needle_rect = pygame.Rect(enemy_x - enemy_width / 2, enemy_y + pinhead_radius, enemy_width, enemy_height - pinhead_radius)
    pinhead_rect = pygame.Rect(enemy_x - pinhead_radius, enemy_y, pinhead_radius * 2, pinhead_radius)
    return balloon_rect.colliderect(needle_rect) or balloon_rect.colliderect(pinhead_rect)

# ---------------- GAME LOOP ----------------
running = True
last_spawn_time = pygame.time.get_ticks()
last_difficulty_increase_time = pygame.time.get_ticks()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == 'game_over':
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if retry_button_rect.collidepoint(mouse_pos):
                    reset_game()
                elif quit_button_rect.collidepoint(mouse_pos):
                    running = False

    if game_state == 'playing':
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
        if keys[pygame.K_UP]:
            player_y -= player_speed
        if keys[pygame.K_DOWN]:
            player_y += player_speed

        player_x = max(0, min(player_x, screen_width - player_width))
        player_y = max(0, min(player_y, screen_height - player_height))

        current_time = pygame.time.get_ticks()
        if current_time - last_difficulty_increase_time > 1000:
            base_enemy_speed += 0.05
            base_spawn_rate = max(50, base_spawn_rate - 10)
            last_difficulty_increase_time = current_time

        if current_time - last_spawn_time > base_spawn_rate:
            enemy_x = random.randint(0, screen_width - enemy_width)
            enemy_y = 0
            enemies.append([enemy_x, enemy_y, base_enemy_speed])
            last_spawn_time = current_time
            
        enemies_to_remove = []
        for enemy in enemies:
            enemy[1] += enemy[2]
            if is_collision(player_x, player_y, enemy):
                game_state = 'game_over'
            if enemy[1] > screen_height:
                enemies_to_remove.append(enemy)

        for enemy in enemies_to_remove:
            enemies.remove(enemy)
            score += 1
        
        # ---------- DRAW SECTION ----------
        screen.fill(SKY_BLUE)

        # Draw clouds
        cloud_group.update()
        cloud_group.draw(screen)

        # Draw balloon & enemies
        draw_balloon(player_x, player_y, player_width, player_height, BALLOON_RED)
        for enemy in enemies:
            draw_downward_triangle(enemy[0], enemy[1], enemy_width, enemy_height, NEEDLE_GRAY)
        
        # Score
        score_text = score_font.render(f"Score: {score}", True, TEXT_WHITE)
        screen.blit(score_text, (10, 10))
    
    elif game_state == 'game_over':
        screen.fill(BACKGROUND_BLACK)
        
        game_over_text = game_over_font.render("Game Over", True, TEXT_WHITE)
        game_over_rect = game_over_text.get_rect(center=(screen_width/2, screen_height/2 - 100))
        screen.blit(game_over_text, game_over_rect)
        
        final_score_text = score_font.render(f"Final Score: {score}", True, TEXT_WHITE)
        final_score_rect = final_score_text.get_rect(center=(screen_width/2, screen_height/2 - 20))
        screen.blit(final_score_text, final_score_rect)
        
        retry_button_text = button_font.render("Retry", True, TEXT_WHITE)
        retry_button_rect = pygame.Rect(screen_width/2 - 100, screen_height/2 + 50, 200, 60)
        pygame.draw.rect(screen, BUTTON_GREEN, retry_button_rect)
        retry_text_rect = retry_button_text.get_rect(center=retry_button_rect.center)
        screen.blit(retry_button_text, retry_text_rect)
        
        quit_button_text = button_font.render("Quit", True, TEXT_WHITE)
        quit_button_rect = pygame.Rect(screen_width/2 - 100, screen_height/2 + 130, 200, 60)
        pygame.draw.rect(screen, BUTTON_RED, quit_button_rect)
        quit_text_rect = quit_button_text.get_rect(center=quit_button_rect.center)
        screen.blit(quit_button_text, quit_text_rect)

    pygame.display.update()

pygame.quit()
