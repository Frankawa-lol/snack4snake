import pygame
from logic import SnakeEnv

running = True

moves = {
    "left": 0,
    "right": 1,
    "up": 2,
    "down": 3
}

pygame.init()

env = SnakeEnv(render_mode="human")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if env.alive:
        if keys[pygame.K_UP]:
            env.step(2)
        elif keys[pygame.K_DOWN]:
            env.step(3)
        elif keys[pygame.K_LEFT]:
            env.step(0)
        elif keys[pygame.K_RIGHT]:
            env.step(1)
        else:
            env.step(moves[env.current_dir])
