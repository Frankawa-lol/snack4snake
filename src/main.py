import pygame
from logic import SnakeEnv

pygame.init()
screen = pygame.display.set_mode((256, 256))
pygame.display.set_caption("snack4snake")
clock = pygame.time.Clock()
running = True

color_bg = pygame.Color(223, 175, 255)
color_snake = pygame.Color(175, 255, 223)
color_item = pygame.Color(255, 223, 175)

deathscreen = pygame.font.Font(None, size=50).render("You Died!", True, "black", color_item)

env = SnakeEnv()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if env.alive:
        if keys[pygame.K_UP]:
            env.step(2)
        if keys[pygame.K_DOWN]:
            env.step(3)
        if keys[pygame.K_LEFT]:
            env.step(0)
        if keys[pygame.K_RIGHT]:
            env.step(1)
        screen.fill(color_bg)
        for e in env.pos_food:
            pygame.draw.circle(screen, color_item, e, 8)
        
        for e in env.pos_snake:
            if env.pos_snake.index(e) == 0:
                continue
            pygame.draw.rect(screen, color_snake, (e[0]-8, e[1]-8, 16, 16))
        
        pygame.draw.circle(screen, color_snake, env.pos_snake[0], 8)
        if env.pos_snake[0] in env.pos_snake[1:]:
            env.alive = False
    else:
        screen.fill(color_item)
        screen.blit(deathscreen, (128 - 79, 128 - 17))

    screen.blit(pygame.font.Font(None, 30).render(str(env.score), True, "black"), (0, 0))

    pygame.display.flip()

    clock.tick(7)
