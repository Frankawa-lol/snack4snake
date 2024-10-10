import pygame

pygame.init()
screen = pygame.display.set_mode((256, 256))
clock = pygame.time.Clock()
running = True

color_bg = pygame.Color(0xdf, 0xaf, 0xf)
color_snake = pygame.Color(0xff, 0xdf, 0xaf)
color_item = pygame.Color(0xaf, 0xff, 0xdf)

pos_snake = [(120, 120), (120, 136), (120, 152), (136, 152)]

dir = "up"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        dir = "up"
    if keys[pygame.K_DOWN]:
        dir = "down"
    if keys[pygame.K_LEFT]:
        dir = "left"
    if keys[pygame.K_RIGHT]:
        dir = "right"
    
    match dir:
        case "up":
            pos_snake.insert(0, (pos_snake[0][0], pos_snake[0][1] - 16))
        case "down":
            pos_snake.insert(0, (pos_snake[0][0], pos_snake[0][1] + 16))
        case "left":
            pos_snake.insert(0, (pos_snake[0][0] - 16, pos_snake[0][1]))
        case "right":
            pos_snake.insert(0, (pos_snake[0][0] + 16, pos_snake[0][1]))
    
    pos_snake.pop()

    screen.fill(color_bg)
    pygame.draw.circle(screen, color_snake, pos_snake[0], 8)

    pygame.display.flip()

    clock.tick(10)
