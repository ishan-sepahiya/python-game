import pygame
import random

# Initialize Pygame
pygame.init()
# Initialize the mixer for sound effects
pygame.mixer.init()

# Get screen info for fullscreen
infoObject = pygame.display.Info()
screen_width = 1500
screen_height = 800

# Set up the game window to be fullscreen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dodge the Needles")

# Colors
BALLOON_RED = (255, 69, 0)
# Changed the needle color to gray
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
player_speed = 1.5

# Enemy settings (Needles)
# Increased the length of the needles and added a pinhead
enemy_width = 10
enemy_height = 80
pinhead_radius = 6
enemies = []

# Game variables
score = 0
base_enemy_speed = 0.5
base_spawn_rate = 200
# The game now starts at the 'start_menu'
game_state = 'start_menu'

# Fonts
score_font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)
title_font = pygame.font.Font(None, 90) # Font for the title
button_font = pygame.font.Font(None, 50)

# Load the sound file
# NOTE: The file name has been updated to use '.mp3'
try:
    pop_sound = pygame.mixer.Sound('pop.wav.mp3')
except pygame.error as e:
    print(f"Warning: Could not load sound file 'pop.wav.mp3': {e}")
    pop_sound = None

# Load the background image
# NOTE: The background image 'cloud.jpg' is now loaded here
try:
    background_image = pygame.image.load('cloud.jpg')
    # Scale the background image to fit the screen
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
except pygame.error as e:
    print(f"Warning: Could not load background image 'cloud.jpg': {e}")
    background_image = None

def reset_game():
    """Resets all game variables to their initial state."""
    global player_x, player_y, score, enemies, base_enemy_speed, base_spawn_rate, game_state
    # CORRECTED LINE: Used player_width instead of player_size
    player_x = (screen_width / 2) - (player_width / 2)
    player_y = screen_height - player_height - 30
    score = 0
    enemies.clear()
    base_enemy_speed = 0.5
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
    # The collision rect for the needle is based on its new width and height
    needle_rect = pygame.Rect(enemy_x - enemy_width / 2, enemy_y + pinhead_radius, enemy_width, enemy_height - pinhead_radius)
    pinhead_rect = pygame.Rect(enemy_x - pinhead_radius, enemy_y, pinhead_radius * 2, pinhead_radius)
    
    return balloon_rect.colliderect(needle_rect) or balloon_rect.colliderect(pinhead_rect)

# Game loop
running = True
last_spawn_time = pygame.time.get_ticks()
last_difficulty_increase_time = pygame.time.get_ticks()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle mouse clicks for different game states
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if game_state == 'start_menu':
                if start_button_rect.collidepoint(mouse_pos):
                    game_state = 'playing'
                elif quit_button_rect.collidepoint(mouse_pos):
                    running = False
            elif game_state == 'game_over':
                if retry_button_rect.collidepoint(mouse_pos):
                    if pop_sound:
                        pop_sound.stop()
                    reset_game()
                elif quit_button_rect.collidepoint(mouse_pos):
                    if pop_sound:
                        pop_sound.stop()
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
        if current_time - last_difficulty_increase_time > 10000:
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
                # Play the pop sound when a collision occurs
                if pop_sound:
                    pop_sound.play()
                game_state = 'game_over'
            if enemy[1] > screen_height:
                enemies_to_remove.append(enemy)

        for enemy in enemies_to_remove:
            enemies.remove(enemy)
            score += 1
        
        # Draw the background image instead of filling the screen with a color
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((135, 206, 250)) # Fallback to sky blue if image is not loaded
            
        draw_balloon(player_x, player_y, player_width, player_height, BALLOON_RED)
        for enemy in enemies:
            # Pass the new color to the drawing function
            draw_downward_triangle(enemy[0], enemy[1], enemy_width, enemy_height, NEEDLE_GRAY)
        
        score_text = score_font.render(f"Score: {score}", True, TEXT_WHITE)
        screen.blit(score_text, (10, 10))
    
    elif game_state == 'start_menu':
        # Draw background for the start menu
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((135, 206, 250))
        
        #Title shadow
        TEXT_BLACK = (0, 0, 0)
        shadow_text = title_font.render("Dodge the Needles", True, TEXT_BLACK)
        shadow_rect = shadow_text.get_rect(center=(screen_width/2 + 3, screen_height/2 - 150 + 3)) # Offset by 3 pixels
        screen.blit(shadow_text, shadow_rect)

        # Draw Title
        title_text = title_font.render("Dodge the Needles", True, TEXT_WHITE)
        title_rect = title_text.get_rect(center=(screen_width/2, screen_height/2 - 150))
        screen.blit(title_text, title_rect)
        
        # Start Button
        start_button_text = button_font.render("Start", True, TEXT_WHITE)
        start_button_rect = pygame.Rect(screen_width/2 - 100, screen_height/2, 200, 60)
        pygame.draw.rect(screen, BUTTON_GREEN, start_button_rect)
        start_text_rect = start_button_text.get_rect(center=start_button_rect.center)
        screen.blit(start_button_text, start_text_rect)
        
        # Quit Button
        quit_button_text = button_font.render("Quit", True, TEXT_WHITE)
        quit_button_rect = pygame.Rect(screen_width/2 - 100, screen_height/2 + 80, 200, 60)
        pygame.draw.rect(screen, BUTTON_RED, quit_button_rect)
        quit_text_rect = quit_button_text.get_rect(center=quit_button_rect.center)
        screen.blit(quit_button_text, quit_text_rect)

    elif game_state == 'game_over':
        screen.fill(BACKGROUND_BLACK)
        
        game_over_text = game_over_font.render("Game Over", True, TEXT_WHITE)
        game_over_rect = game_over_text.get_rect(center=(screen_width/2, screen_height/2 - 100))
        screen.blit(game_over_text, game_over_rect)
        
        final_score_text = score_font.render(f"Final Score: {score}", True, TEXT_WHITE)
        final_score_rect = final_score_text.get_rect(center=(screen_width/2, screen_height/2 - 20))
        screen.blit(final_score_text, final_score_rect)
        
        # Retry Button
        retry_button_text = button_font.render("Retry", True, TEXT_WHITE)
        retry_button_rect = pygame.Rect(screen_width/2 - 100, screen_height/2 + 50, 200, 60)
        pygame.draw.rect(screen, BUTTON_GREEN, retry_button_rect)
        retry_text_rect = retry_button_text.get_rect(center=retry_button_rect.center)
        screen.blit(retry_button_text, retry_text_rect)
        
        # Quit Button
        quit_button_text = button_font.render("Quit", True, TEXT_WHITE)
        quit_button_rect = pygame.Rect(screen_width/2 - 100, screen_height/2 + 130, 200, 60)
        pygame.draw.rect(screen, BUTTON_RED, quit_button_rect)
        quit_text_rect = quit_button_text.get_rect(center=quit_button_rect.center)
        screen.blit(quit_button_text, quit_text_rect)

    pygame.display.update()

pygame.quit()
