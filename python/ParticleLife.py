import pygame
import numpy as np
from numba import jit
import os
from datetime import datetime

# Constants
WIDTH, HEIGHT = 1900, 1000
#WIDTH, HEIGHT = 1280, 720
NUM_TYPES = 6
COLOR_STEP = 360 // NUM_TYPES
NUM_PARTICLES = 2000
K = 0.05
FRICTION = 0.85

@jit(nopython=True)
def update_particles(positions, velocities, types, forces, min_distances, radii):
    num_particles = len(positions)
    new_positions = np.empty_like(positions)
    new_velocities = np.empty_like(velocities)

    for i in range(num_particles):
        total_force_x, total_force_y = 0.0, 0.0
        pos_x, pos_y = positions[i]
        vel_x, vel_y = velocities[i]
        p_type = types[i]
        
        for j in range(num_particles):
            if i != j:
                dir_x = positions[j, 0] - pos_x
                dir_y = positions[j, 1] - pos_y
                
                # Apply periodic boundary conditions
                if dir_x > 0.5 * WIDTH:
                    dir_x -= WIDTH
                if dir_x < -0.5 * WIDTH:
                    dir_x += WIDTH
                if dir_y > 0.5 * HEIGHT:
                    dir_y -= HEIGHT
                if dir_y < -0.5 * HEIGHT:
                    dir_y += HEIGHT
                
                dis = np.sqrt(dir_x**2 + dir_y**2)
                if dis > 0:
                    dir_x, dir_y = dir_x / dis, dir_y / dis # Normalize the direction vector
                    other_type = types[j]
                    if dis < min_distances[p_type, other_type]:
                        force = abs(forces[p_type, other_type]) * -3 * (1 - dis / min_distances[p_type, other_type]) * K
                        total_force_x += dir_x * force
                        total_force_y += dir_y * force
                    if dis < radii[p_type, other_type]:
                        force = forces[p_type, other_type] * (1 - dis / radii[p_type, other_type]) * K
                        total_force_x += dir_x * force
                        total_force_y += dir_y * force

        new_vel_x = vel_x + total_force_x
        new_vel_y = vel_y + total_force_y
        new_pos_x = (pos_x + new_vel_x) % WIDTH
        new_pos_y = (pos_y + new_vel_y) % HEIGHT
        new_vel_x *= FRICTION
        new_vel_y *= FRICTION
        
        new_positions[i] = new_pos_x, new_pos_y
        new_velocities[i] = new_vel_x, new_vel_y

    return new_positions, new_velocities

def set_parameters():
    forces = np.random.uniform(0.3, 1, (NUM_TYPES, NUM_TYPES))
    mask = np.random.random((NUM_TYPES, NUM_TYPES)) < 0.5
    forces[mask] *= -1
    min_distances = np.random.uniform(30, 50, (NUM_TYPES, NUM_TYPES))
    radii = np.random.uniform(70, 250, (NUM_TYPES, NUM_TYPES))
    return forces, min_distances, radii

def save_screen(screen):
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    
    current_time = datetime.now()
    time_str = current_time.strftime("%Y%m%d%H%M%S")
    filename = f"screenshots/particles_{time_str}.png"
    pygame.image.save(screen, filename)

def main():
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Particle Swarm Simulation")
    clock = pygame.time.Clock()

    # Create particles
    positions = np.random.rand(NUM_PARTICLES, 2) * [WIDTH, HEIGHT]
    velocities = np.zeros((NUM_PARTICLES, 2))
    types = np.random.randint(0, NUM_TYPES, NUM_PARTICLES)
    forces, min_distances, radii = set_parameters()

    # Main game loop
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    forces, min_distances, radii = set_parameters()
                elif event.key == pygame.K_s:
                    save_screen(screen)

        screen.fill((0, 0, 0))  # Clear screen with black

        positions, velocities = update_particles(positions, velocities, types, forces, min_distances, radii)

        for i in range(NUM_PARTICLES):
            color = pygame.Color(0)
            color.hsva = (types[i] * COLOR_STEP, 100, 100, 100)
            pygame.draw.circle(screen, color, (int(positions[i, 0]), int(positions[i, 1])), 2)

        pygame.display.flip()

        clock.tick(60)  # Limit to 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
