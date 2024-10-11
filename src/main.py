import pygame
import random

pygame.init()
screen = pygame.display.set_mode((256, 256))
clock = pygame.time.Clock()
running = True

color_bg = pygame.Color(223, 175, 255)
color_snake = pygame.Color(175, 255, 223)
color_item = pygame.Color(255, 223, 175)

deathscreen = pygame.font.Font(None, size=50).render("You Died!", True, "black", color_item)

pos_snake = [(120, 120), (120, 136), (120, 152), (136, 152), (152, 152), (152, 168)]
alive = True
score = 0

def generate_new_food():
    valid_food_pos = True
    food = (random.randint(0, 15) * 16 + 8, random.randint(0, 15)* 16 + 8)
    for e in pos_snake:
        if food == e:
            valid_food_pos = False
    if valid_food_pos:
        pos_food.append(food)
    else:
        generate_new_food()

pos_food = []
for i in range(4):
    generate_new_food()


food_eaten = False

current_dir = "up"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if alive:
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
        #print(pos_snake[0])

        for e in pos_food:
            if pos_snake[0] == e:
                food_eaten = True
                pos_food.remove(e)
                score += 1
                if len(pos_snake) < 253:
                    generate_new_food()

        if not food_eaten:
            pos_snake.pop()

        food_eaten = False

        screen.fill(color_bg)
        for e in pos_food:
            pygame.draw.circle(screen, color_item, e, 8)
        
        for e in pos_snake:
            if pos_snake.index(e) == 0:
                continue
            pygame.draw.rect(screen, color_snake, (e[0]-8, e[1]-8, 16, 16))
        
        pygame.draw.circle(screen, color_snake, pos_snake[0], 8)
        if pos_snake[0] in pos_snake[1:]:
            alive = False
    else:
        screen.fill(color_item)
        screen.blit(deathscreen, (128 - 79, 128 - 17))

    screen.blit(pygame.font.Font(None, 30).render(str(score), True, "black"), (0, 0))

    pygame.display.flip()

    clock.tick(10)
