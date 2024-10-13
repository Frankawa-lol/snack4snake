import random
import sys
import gymnasium as gym
import numpy as np
import pygame
import os

snake_head_image = pygame.image.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sprite', 'snake_head.png'))
snake_body_image = pygame.image.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sprite', 'snake_body.png'))
snake_corner_image = pygame.image.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sprite', 'snake_corner.png'))
snake_tail_image = pygame.image.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sprite', 'snake_tail.png'))
screen = None
pygame.init()

class SnakeEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 2**32-1}

    action_space = gym.spaces.Discrete(4)
    observation_space = gym.spaces.Box(low=0, high=15,
                                       shape=(256,), dtype=np.int32)
    class SnakePart:
        def draw_rotated_image(self, image, direction, position):
            match direction:
                case "up":
                    angle = 0
                case "left":
                    angle = 90
                case "down":
                    angle = 180
                case "right":
                    angle = 270
                case _:
                    angle = 0
            new_image = pygame.transform.rotate(image, angle)
            screen.blit(new_image, position)
        def __init__(self, direction, position, snake_type, last_direction=None):
            self.direction = direction
            self.position = position
            self.snake_type = snake_type
            self.last_direction = last_direction
        def __eq__(self, value: object) -> bool:
            if isinstance(value, SnakeEnv.SnakePart):
                return self.position == value.position
            else:
                return self.position == value
        def draw(self):
            match self.snake_type:
                case "head":
                    self.draw_rotated_image(snake_head_image, self.direction, self.position)
                case "body":
                    self.draw_rotated_image(snake_body_image, self.direction, self.position)
                case "corner":
                    if {self.last_direction, self.direction} == {"up", "left"}:
                        self.draw_rotated_image(snake_corner_image, "up", self.position)
                    elif {self.last_direction, self.direction} == {"left", "down"}:
                        self.draw_rotated_image(snake_corner_image, "left", self.position)
                    elif {self.last_direction, self.direction} == {"down", "right"}:
                        self.draw_rotated_image(snake_corner_image, "down", self.position)
                    elif {self.last_direction, self.direction} == {"right", "up"}:
                        self.draw_rotated_image(snake_corner_image, "right", self.position)
                    else:
                        print("no possible corner")
                case "tail":
                    self.draw_rotated_image(snake_tail_image, self.direction, self.position)

    def __init__(self, render_mode=None, fps=2**32-1):
        super(SnakeEnv, self).__init__()
        self.last_reward = 0
        self.pos_snake = [self.SnakePart("up", (112, 112), "head"),
                          self.SnakePart("up", (112, 128), "body"),
                          self.SnakePart("up", (112, 144), "corner", "right"),
                          self.SnakePart("left", (128, 144), "body"),
                          self.SnakePart("left", (144, 144), "corner", "down"),
                          self.SnakePart("up", (144, 160), "tail")]
        self.alive = True
        self.score = 0
        self.pos_food = []
        self.current_dir = "up"
        self.fps = fps
        self.render_mode = render_mode
        self.steps = 0
        if render_mode == "human":
            global screen
            screen = pygame.display.set_mode((256, 256))
            pygame.display.set_caption("snack4snake")
            self.clock = pygame.time.Clock()
            
            self.color_bg = pygame.Color(223, 175, 255)
            self.color_snake = pygame.Color(175, 255, 223)
            self.color_item = pygame.Color(255, 223, 175)
            self.deathscreen = pygame.font.Font(None, size=50).render("You Died!", True, "black", self.color_item)
        for i in range(4):
            self.generate_new_food()
        self.food_dis = self.calculate_food_distance()

    def close(self):
        sys.exit()

    def calculate_food_distance(self):
        food_distance = []
        for e in self.pos_food:
            food_distance.append(abs(e[0] - self.pos_snake[0].position[0]) + abs(e[1] - self.pos_snake[1].position[1]))
        return min(food_distance)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.pos_snake = [self.SnakePart("up", (112, 112), "head"),
                          self.SnakePart("up", (112, 128), "body"),
                          self.SnakePart("up", (112, 144), "corner", "right"),
                          self.SnakePart("left", (128, 144), "body"),
                          self.SnakePart("left", (144, 144), "corner", "down"),
                          self.SnakePart("up", (144, 160), "tail")]
        self.alive = True
        print((self.score, self.steps))
        self.score = 0
        self.steps = 0
        self.pos_food = []
        self.current_dir = "up"

        for i in range(4):
            self.generate_new_food()

        if self.render_mode == "human":
            self._render_frame()

        return self._get_obs(), self._get_info()

    def generate_new_food(self):
        valid_food_pos = True
        food = (random.randint(0, 15) * 16, random.randint(0, 15) * 16)
        for e in self.pos_snake:
            if food == e:
                valid_food_pos = False
        if valid_food_pos:
            self.pos_food.append(food)
        else:
            self.generate_new_food()

    def step(self, action):
        reward = 0
        self.steps +=1
        food_eaten = False
        current_food_distance = self.calculate_food_distance()
        if action == 2 and self.current_dir != "down" and self.current_dir != "up":
            self.current_dir = "up"
        elif action == 3 and self.current_dir != "up" and self.current_dir != "down":
            self.current_dir = "down"
        elif action == 0 and self.current_dir != "right" and self.current_dir != "left":
            self.current_dir = "left"
        elif action == 1 and self.current_dir != "left" and self.current_dir != "right":
            self.current_dir = "right"

        match self.current_dir:
            case "up":
                self.pos_snake.insert(0, self.SnakePart(self.current_dir,
                    (self.pos_snake[0].position[0], self.pos_snake[0].position[1] - 16), "head"))
            case "down":
                self.pos_snake.insert(0, self.SnakePart(self.current_dir,
                    (self.pos_snake[0].position[0], self.pos_snake[0].position[1] + 16), "head"))
            case "left":
                self.pos_snake.insert(0, self.SnakePart(self.current_dir,
                    (self.pos_snake[0].position[0] - 16, self.pos_snake[0].position[1]), "head"))
            case "right":
                self.pos_snake.insert(0, self.SnakePart(self.current_dir,
                    (self.pos_snake[0].position[0] + 16, self.pos_snake[0].position[1]), "head"))

        if self.pos_snake[0].position[0] > 240:
            self.pos_snake[0].position = (0, self.pos_snake[0].position[1])
        if self.pos_snake[0].position[0] < 0:
            self.pos_snake[0].position = (240, self.pos_snake[0].position[1])
        if self.pos_snake[0].position[1] > 240:
            self.pos_snake[0].position = (self.pos_snake[0].position[0], 0)
        if self.pos_snake[0].position[1] < 0:
            self.pos_snake[0].position = (self.pos_snake[0].position[0], 240)
        # print(pos_snake[0])

        for e in self.pos_food:
            if self.pos_snake[0] == e:
                food_eaten = True
                self.pos_food.remove(e)
                self.score += 1
                if len(self.pos_snake) < 253:
                    self.generate_new_food()

        if not food_eaten:
            self.pos_snake.pop()
            if current_food_distance >= self.food_dis:
                reward = -0.2
            else:
                reward = 0.2
        else:
            reward = 5.0

        for e in self.pos_snake[1:]:
            if self.pos_snake[0] == e:
                self.alive = False
                print("die!!")


        if not self.alive:
            reward = -1.0

        if self.render_mode == "human":
            self._render_frame()

        self.last_reward = reward

        return self._get_obs(), reward, not self.alive, False, self._get_info()

    def _get_obs(self):
        #print(self.pos_snake, self.pos_food)
        field = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        snake_pos_list = []
        for e in self.pos_snake:
            snake_pos_list.append(e.position)
        for x in range(16):
            for y in range(16):
                if (x*16, y*16) == snake_pos_list[0]:
                    field[x][y] = 1
                elif (x*16, y*16) in snake_pos_list[1:]:
                    field[x][y] = 2
                elif (x*16, y*16) in self.pos_food:
                    field[x][y] = 3
        return [
            x for row in field for x in row
        ]

    def _get_info(self):
        return { "score": self.score, "reward": self.last_reward }

    def _render_frame(self):
        if self.render_mode is None: return
        if self.alive:
            if self.pos_snake[1].direction != self.current_dir:
                self.pos_snake[1].last_direction = self.flip_direction(self.pos_snake[1].direction)
                self.pos_snake[1].direction = self.current_dir
                self.pos_snake[1].snake_type = "corner"
            else:
                self.pos_snake[1].snake_type = "body"
                self.pos_snake[len(self.pos_snake)-1].snake_type = "tail"
                screen.fill(self.color_bg)
            for e in self.pos_food:
                pygame.draw.circle(screen, self.color_item, (e[0] + 8, e[1] + 8), 8)
            for e in self.pos_snake:
                e.draw()
                if self.pos_snake.index(e) == 0:
                    continue
        else:
            screen.fill(self.color_item)
            screen.blit(self.deathscreen, (128 - 79, 128 - 17))

        screen.blit(pygame.font.Font(None, 30).render(str(self.score), True, "black"), (0, 0))

        pygame.display.flip()

        self.clock.tick(self.fps)

    def flip_direction(self, direction):
        match direction:
            case "up":
                return "down"
            case "down":
                return "up"
            case "left":
                return "right"
            case "right":
                return "left"

gym.register("libewa/snack4snake-v0", entry_point=SnakeEnv)
if __name__ == "__main__":
    gym.pprint_registry()
    env = SnakeEnv()
    print(env.reset()[0])