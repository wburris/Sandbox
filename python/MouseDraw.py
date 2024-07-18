import pygame
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Mouse Event Example")

points: List[Tuple[int, int]] = []
rectangles: List[Tuple[int, int, int, int]] = []
mouseDown = False

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            exit()
        # Check for mouse button presses and releases
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                x = int(event.pos[0])
                y = int(event.pos[1])
                dragStart = (x, y)
                mouseDown = True
                #print("Left mouse button pressed at", event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                mouseDown = False
                x = int(event.pos[0])
                y = int(event.pos[1])
                dragEnd = (x, y)
                if abs(dragStart[0] - dragEnd[0]) > 10 and abs(dragStart[1] - dragEnd[1]) > 10:
                    rectangles.append((min(dragStart[0], dragEnd[0]), min(dragStart[1], dragEnd[1]),
                                      abs(dragStart[0] - dragEnd[0]), abs(dragStart[1] - dragEnd[1])))
                else:
                    points.append(dragStart)
                #print("Left mouse button released at", event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                pygame_surface = screen.copy()
                pygame.image.save(pygame_surface, "sketch.png")
                
        # Get the current mouse position
        mouse_pos = pygame.mouse.get_pos()
        #print("Mouse position:", mouse_pos)

    # Clear the screen
    screen.fill((0, 0, 0))

    for point in points:
        pygame.draw.circle(screen, (255, 255, 255), point, 4)

    if mouseDown:
        # Draw the rectangle outline as the mouse is being dragged
        x = min(dragStart[0], mouse_pos[0])
        y = min(dragStart[1], mouse_pos[1])
        width = abs(dragStart[0] - mouse_pos[0])
        height = abs(dragStart[1] - mouse_pos[1])
        pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height), 3)

    for rect in rectangles:
        pygame.draw.rect(screen, (255, 255, 255), rect, 3)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()