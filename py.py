# ant_simulation.py
import pygame
import random
import math

# Pygame setup
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MAP_WIDTH, MAP_HEIGHT = 1600, 1200
FPS = 60
ANT_COUNT = 50
FOOD_COUNT = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 155, 0)
GRAY = (120, 120, 120)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ant Foraging Simulation")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 24)

# Camera
NEST_POS = (MAP_WIDTH // 2, MAP_HEIGHT // 2)
camera_x = NEST_POS[0] - SCREEN_WIDTH // 2
camera_y = NEST_POS[1] - SCREEN_HEIGHT // 2
dragging = False
last_mouse_pos = (0, 0)

# Ant class
class Ant:
    def __init__(self, x, y, role="worker"):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = 2
        self.has_food = False
        self.role = role

    def move(self):
        if self.role == "queen":
            return

        self.angle += random.uniform(-0.3, 0.3)
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        self.x = max(0, min(MAP_WIDTH, self.x))
        self.y = max(0, min(MAP_HEIGHT, self.y))

    def draw(self, screen, camera_x, camera_y):
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)

        if self.role == "queen":
            color = YELLOW
            size = 8
        elif self.role == "soldier":
            color = BLUE
            size = 6
        else:
            color = RED if self.has_food else BLACK
            size = 4

        pygame.draw.circle(screen, color, (draw_x, draw_y), size)

        if self.role != "queen":
            head_x = draw_x + math.cos(self.angle) * 5
            head_y = draw_y + math.sin(self.angle) * 5
            pygame.draw.circle(screen, GRAY, (int(head_x), int(head_y)), 2)

class Food:
    def __init__(self):
        self.x = random.randint(50, MAP_WIDTH - 50)
        self.y = random.randint(50, MAP_HEIGHT - 50)
        self.amount = 100

    def draw(self, screen, camera_x, camera_y):
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)
        radius = max(4, int(self.amount / 10))
        pygame.draw.circle(screen, DARK_GREEN, (draw_x, draw_y), radius)
        pygame.draw.circle(screen, GREEN, (draw_x, draw_y), radius - 2)

ants = [Ant(*NEST_POS, role="queen")]
ants += [Ant(*NEST_POS, role="soldier") for _ in range(5)]
ants += [Ant(*NEST_POS, role="worker") for _ in range(ANT_COUNT - 6)]

foods = [Food() for _ in range(FOOD_COUNT)]

growth_timer = 0
GROWTH_INTERVAL = 300

colony_size_history = []
food_collected_history = []
stats_timer = 0
STATS_INTERVAL = 60

total_food_collected = 0

running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)
    growth_timer += 1
    stats_timer += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dragging = True
            last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            dx = event.pos[0] - last_mouse_pos[0]
            dy = event.pos[1] - last_mouse_pos[1]
            camera_x -= dx
            camera_y -= dy
            camera_x = max(0, min(MAP_WIDTH - SCREEN_WIDTH, camera_x))
            camera_y = max(0, min(MAP_HEIGHT - SCREEN_HEIGHT, camera_y))
            last_mouse_pos = event.pos

    pygame.draw.circle(screen, BROWN, (NEST_POS[0] - camera_x, NEST_POS[1] - camera_y), 15)
    pygame.draw.circle(screen, WHITE, (NEST_POS[0] - camera_x, NEST_POS[1] - camera_y), 10)

    for food in foods:
        food.draw(screen, camera_x, camera_y)

    for ant in ants:
        ant.move()
        ant.draw(screen, camera_x, camera_y)

        if ant.role == "worker":
            if not ant.has_food:
                for food in foods:
                    if math.hypot(ant.x - food.x, ant.y - food.y) < 10 and food.amount > 0:
                        ant.has_food = True
                        food.amount -= 1
                        break
            else:
                dx, dy = NEST_POS[0] - ant.x, NEST_POS[1] - ant.y
                ant.angle = math.atan2(dy, dx)
                if math.hypot(dx, dy) < 10:
                    ant.has_food = False
                    total_food_collected += 1

    if growth_timer >= GROWTH_INTERVAL:
        growth_timer = 0
        if len(ants) < 150:
            ants.append(Ant(*NEST_POS, role="worker"))

    if stats_timer >= STATS_INTERVAL:
        stats_timer = 0
        colony_size_history.append(len(ants))
        food_collected_history.append(total_food_collected)
        if len(colony_size_history) > 50:
            colony_size_history.pop(0)
            food_collected_history.pop(0)

    stats_x = 10
    stats_y = SCREEN_HEIGHT - 100
    pygame.draw.rect(screen, WHITE, (stats_x, stats_y, 200, 90))
    pygame.draw.rect(screen, BLACK, (stats_x, stats_y, 200, 90), 1)
    for i in range(1, len(colony_size_history)):
        x1 = stats_x + (i - 1) * 4
        y1 = stats_y + 80 - colony_size_history[i - 1] // 2
        x2 = stats_x + i * 4
        y2 = stats_y + 80 - colony_size_history[i] // 2
        pygame.draw.line(screen, RED, (x1, y1), (x2, y2), 2)

    food_graph_x = 220
    pygame.draw.rect(screen, WHITE, (food_graph_x, stats_y, 200, 90))
    pygame.draw.rect(screen, BLACK, (food_graph_x, stats_y, 200, 90), 1)
    for i in range(1, len(food_collected_history)):
        x1 = food_graph_x + (i - 1) * 4
        y1 = stats_y + 80 - food_collected_history[i - 1] // 10
        x2 = food_graph_x + i * 4
        y2 = stats_y + 80 - food_collected_history[i] // 10
        pygame.draw.line(screen, GREEN, (x1, y1), (x2, y2), 2)

    text = font.render(f"Colony Size: {len(ants)}", True, BLACK)
    screen.blit(text, (10, 10))
    food_text = font.render(f"Food Collected: {total_food_collected}", True, BLACK)
    screen.blit(food_text, (10, 35))

    pygame.display.flip()

pygame.quit()
