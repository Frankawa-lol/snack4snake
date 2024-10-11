import pygame

pygame.init()
screen = pygame.display.set_mode((256, 256))
clock = pygame.time.Clock()
running = True

color_bg = pygame.Color(0xdf, 0xaf, 0xf)
color_snake = pygame.Color(0xff, 0xdf, 0xaf)
color_item = pygame.Color(0xaf, 0xff, 0xdf)

pos_snake = [(120, 120), (120, 136), (120, 152), (136, 152), (152, 152)]

current_dir = "up"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and current_dir != "down":
        current_dir = "up"
    if keys[pygame.K_DOWN] and current_dir != "up":
        current_dir = "down"
    if keys[pygame.K_LEFT] and current_dir != "right":
        current_dir = "left"
    if keys[pygame.K_RIGHT] and current_dir != "left":
        current_dir = "right"
    
    match current_dir:
        case "up":
            pos_snake.insert(0, (pos_snake[0][0], pos_snake[0][1] - 16))
        case "down":
            pos_snake.insert(0, (pos_snake[0][0], pos_snake[0][1] + 16))
        case "left":
            pos_snake.insert(0, (pos_snake[0][0] - 16, pos_snake[0][1]))
        case "right":
            pos_snake.insert(0, (pos_snake[0][0] + 16, pos_snake[0][1]))

    if pos_snake[0][0] > 248:
        pos_snake[0] = (8, pos_snake[0][1])
    if pos_snake[0][1] > 248:
        pos_snake[0] = (pos_snake[0][0], 8)
    if pos_snake[0][0] < 8:
        pos_snake[0] = (248, pos_snake[0][1])
    if pos_snake[0][1] < 8:
        pos_snake[0] = (pos_snake[0][0], 248)
    print(pos_snake[0])
    pos_snake.pop()

    screen.fill(color_bg)
    pygame.draw.circle(screen, color_snake, pos_snake[0], 8)
    for e in pos_snake:
        if pos_snake.index(e) == 0:
            continue
        pygame.draw.rect(screen, color_snake, (e[0]-8, e[1]-8, 16, 16))

    pygame.display.flip()

    clock.tick(10)
