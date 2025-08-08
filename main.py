import pygame
import random
import math
import time
import sys

# Initialize Pygame and game window
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Color Snake")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 48)

# Game Constants
SNAKE_RADIUS = 10
FOOD_RADIUS = 8
STAR_RADIUS = 12
SNAKE_SPEED = 4
FOOD_SCORE = 1
STAR_SCORE = 4

# Fixed color list for food and snake parts
COLOR_LIST = [
    (34, 139, 34),    # Leaf green
    (220, 20, 60),    # Crimson
    (15, 82, 186),    # Sapphire
    (255, 191, 0),    # Amber
    (138, 43, 226),   # Violet
    (64, 224, 208),   # Turquoise
    (255, 127, 80),   # Coral
    (255, 102, 204),  # Rose
]

# Initialize snake
snake = [(WIDTH // 2, HEIGHT // 2)]
snake_colors = [random.choice(COLOR_LIST)]
direction = pygame.Vector2(1, 0)

# Food list
foods = []

# Star variables
star = None
last_star_time = time.time()
star_interval = 10  # First appears after 10s, then adds +10s each time

# Score & game state
score = 0
game_over = False

# Food spawn control
max_food = 5
food_increase_interval = 20  # every 20 seconds
last_food_increase_time = time.time()

# Spawn a food item with fade-in setup
def spawn_food():
    return {
        'pos': (random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)),
        'color': random.choice(COLOR_LIST),
        'alpha': 0  # Fade-in start
    }

# Preload some food
for _ in range(max_food):
    foods.append(spawn_food())

# Drawing the snake
def draw_snake():
    for i, pos in enumerate(snake):
        color = snake_colors[i % len(snake_colors)]
        pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), SNAKE_RADIUS)

# Draw foods with fade-in animation
def draw_foods():
    for food in foods:
        food_surface = pygame.Surface((FOOD_RADIUS*2, FOOD_RADIUS*2), pygame.SRCALPHA)
        r, g, b = food['color']
        alpha = min(food['alpha'], 255)
        pygame.draw.circle(food_surface, (r, g, b, alpha), (FOOD_RADIUS, FOOD_RADIUS), FOOD_RADIUS)
        screen.blit(food_surface, (food['pos'][0] - FOOD_RADIUS, food['pos'][1] - FOOD_RADIUS))

# Draw the star (no animation yet)
def draw_star():
    if star:
        pygame.draw.circle(screen, (255, 255, 0), star['pos'], STAR_RADIUS)

# Move snake forward with wraparound
def move_snake():
    if not snake:
        return
    head_x, head_y = snake[0]

    # Wrap around screen
    new_x = (head_x + direction.x * SNAKE_SPEED) % WIDTH
    new_y = (head_y + direction.y * SNAKE_SPEED) % HEIGHT
    new_head = (new_x, new_y)

    snake.insert(0, new_head)
    snake.pop()  # remove tail

# Simple circular collision detection
def check_collision(pos1, pos2, threshold=5):
    return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1]) < threshold

# Read key input to control direction
def handle_input():
    global direction
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and direction.x != 1:
        direction = pygame.Vector2(-1, 0)
    elif keys[pygame.K_RIGHT] and direction.x != -1:
        direction = pygame.Vector2(1, 0)
    elif keys[pygame.K_UP] and direction.y != 1:
        direction = pygame.Vector2(0, -1)
    elif keys[pygame.K_DOWN] and direction.y != -1:
        direction = pygame.Vector2(0, 1)

# Game over screen
def show_game_over():
    screen.fill((20, 20, 30))
    game_over_text = big_font.render("Game Over", True, (255, 0, 0))
    score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
    exit_text = font.render("Press any key to exit", True, (200, 200, 200))
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 80))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 20))
    screen.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, HEIGHT//2 + 30))
    pygame.display.flip()

    # Wait for any key to exit
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False

# ========== Main Game Loop ==========
running = True
while running:
    if game_over:
        show_game_over()
        running = False
        continue

    screen.fill((25, 25, 35))  # Background

    # Handle inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    handle_input()
    move_snake()

    # === Self-collision detection (head with body) ===
    head = snake[0]
    for segment in snake[4:]:  # Skip early segments to avoid false positives
        if check_collision(head, segment, SNAKE_RADIUS):
            game_over = True
            break

    # === FOOD LIMIT INCsREASE every 20 seconds ===
    if time.time() - last_food_increase_time > food_increase_interval:
        if max_food < 30:
            max_food = min(max_food + 4, 30)
        last_food_increase_time = time.time()

    # === FOOD collision & fade-in ===
    for food in foods[:]:
        if food['alpha'] < 255:
            food['alpha'] += 10  # Increase transparency for animation

        if check_collision(snake[0], food['pos'], SNAKE_RADIUS + FOOD_RADIUS):
            score += FOOD_SCORE
            snake.append(snake[-1])
            snake_colors.append(food['color'])
            foods.remove(food)

    # Maintain food count up to max_food
    while len(foods) < max_food:
        foods.append(spawn_food())

    # === STAR logic ===
    current_time = time.time()
    if star is None and (current_time - last_star_time > star_interval):
        star = {
            'pos': (random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)),
            'spawn_time': current_time
        }
        last_star_time = current_time
        star_interval += 10  # Increase time until next star

    # STAR collision
    if star and check_collision(snake[0], star['pos'], SNAKE_RADIUS + STAR_RADIUS):
        score += STAR_SCORE
        # Shrink snake by 4 segments or reset
        if len(snake) > 4:
            snake = snake[:-4]
            snake_colors = snake_colors[:-4]
        else:
            snake = [snake[0]]
            snake_colors = [random.choice(COLOR_LIST)]
        star = None

    # === Drawing ===
    draw_snake()
    draw_foods()
    draw_star()

    # Show score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

# Exit game
pygame.quit()
