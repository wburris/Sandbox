import pygame
import numpy as np
from scipy import signal
import os
from datetime import datetime

WIDTH, HEIGHT = 1900, 1000
#WIDTH, HEIGHT = 1280, 720

CELL_SZ = 10

grid_w = WIDTH // CELL_SZ
grid_h = HEIGHT // CELL_SZ

generation = 0

def create_grid():
    return np.random.choice([0, 1], size=(grid_h, grid_w), p=[0.8, 0.2])

def update(grid):
    # Define the kernel for neighbor counting
    kernel = np.array([[1, 1, 1],
                       [1, 0, 1],
                       [1, 1, 1]])

    neighbors = signal.convolve2d(grid, kernel, mode='same', boundary='wrap')

    new_grid = np.zeros((grid_h, grid_w), dtype=int)
    new_grid[np.logical_and(grid == 1, np.logical_or(neighbors == 2, neighbors == 3))] = 1
    new_grid[np.logical_and(grid == 0, neighbors == 3)] = 1
    return new_grid

def draw_grid(screen, grid):
    for y in range(grid_h):
        for x in range(grid_w):
            color = (0, 0, 0) if grid[y, x] else (255, 255, 255)
            pygame.draw.rect(screen, color, (x * CELL_SZ + 1, y * CELL_SZ + 1, CELL_SZ - 2, CELL_SZ - 2))

def setup():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game of Life")
    return create_grid()

def save_screen(screen):
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    
    current_time = datetime.now()
    time_str = current_time.strftime("%Y%m%d%H%M%S")
    filename = f"screenshots/life_{time_str}.png"
    pygame.image.save(screen, filename)

def main():
    global generation
    grid = setup()
    clock = pygame.time.Clock()
    running = True
    paused = False
    
    font = pygame.font.Font(None, 36)

    LIGHT_GRAY = (200, 200, 200)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_c and paused:
                    grid = np.zeros((grid_h, grid_w), dtype=int)
                    generation = 0
                elif event.key == pygame.K_r and paused:
                    grid = create_grid()
                    generation = 0
                elif event.key == pygame.K_s:
                    save_screen(screen)
            elif event.type == pygame.MOUSEBUTTONDOWN and paused:
                if event.button == 1:  # Left mouse button
                    x, y = event.pos
                    grid_x, grid_y = x // CELL_SZ, y // CELL_SZ
                    grid[grid_y, grid_x] = 1 - grid[grid_y, grid_x]  # Toggle cell state

        if not paused:
            grid = update(grid)
            generation += 1

        screen.fill(LIGHT_GRAY)
        draw_grid(screen, grid)

        gen_text = font.render(f"Generation: {generation}", True, (0, 0, 0))
        screen.blit(gen_text, (10, 10))

        paused_text = font.render("PAUSED" if paused else "RUNNING", True, (255, 0, 0) if paused else (0, 255, 0))
        screen.blit(paused_text, (WIDTH - 120, 10))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
