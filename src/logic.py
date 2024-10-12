import random
import gymnasium as gym
import numpy as np
import pygame

color_bg = pygame.Color(223, 175, 255)
color_snake = pygame.Color(175, 255, 223)
color_item = pygame.Color(255, 223, 175)

class SnakeEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 2000}

    action_space = gym.spaces.Discrete(4)
    observation_space = gym.spaces.Box(low=0, high=15,
                                       shape=(11,), dtype=np.int32)

    def __init__(self, render_mode=None, fps=2**32-1):
        super(SnakeEnv, self).__init__()
        self.pos_snake = [(120, 120), (120, 136), (120, 152), (136, 152), (152, 152), (152, 168)]
        self.alive = True
        self.score = 0
        self.pos_food = []
        self.current_dir = "up"
        self.fps = fps
        self.render_mode = "human"
        if render_mode == "human":
            pygame.init()
            self.deathscreen = pygame.font.Font(None, size=50).render("You Died!", True, "black", color_item)
            self.screen = pygame.display.set_mode((256, 256))
            pygame.display.set_caption("snack4snake")
            self.clock = pygame.time.Clock()
        for i in range(4):
            self.generate_new_food()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.__init__()
        if self.render_mode == "human":
            self._render_frame()
        return self._get_obs(), self._get_info()

    def generate_new_food(self):
        valid_food_pos = True
        food = (random.randint(0, 15) * 16 + 8, random.randint(0, 15) * 16 + 8)
        for e in self.pos_snake:
            if food == e:
                valid_food_pos = False
        if valid_food_pos:
            self.pos_food.append(food)
        else:
            self.generate_new_food()

    def step(self, action):
        food_eaten = False
        if action == 2 and self.current_dir != "down":
            self.current_dir = "up"
        if action == 3 and self.current_dir != "up":
            self.current_dir = "down"
        if action == 0 and self.current_dir != "right":
            self.current_dir = "left"
        if action == 1 and self.current_dir != "left":
            self.current_dir = "right"

        match self.current_dir:
            case "up":
                self.pos_snake.insert(0, (self.pos_snake[0][0], self.pos_snake[0][1] - 16))
            case "down":
                self.pos_snake.insert(0, (self.pos_snake[0][0], self.pos_snake[0][1] + 16))
            case "left":
                self.pos_snake.insert(0, (self.pos_snake[0][0] - 16, self.pos_snake[0][1]))
            case "right":
                self.pos_snake.insert(0, (self.pos_snake[0][0] + 16, self.pos_snake[0][1]))

        if self.pos_snake[0][0] > 248:
            self.pos_snake[0] = (8, self.pos_snake[0][1])
        if self.pos_snake[0][1] > 248:
            self.pos_snake[0] = (self.pos_snake[0][0], 8)
        if self.pos_snake[0][0] < 8:
            self.pos_snake[0] = (248, self.pos_snake[0][1])
        if self.pos_snake[0][1] < 8:
            self.pos_snake[0] = (self.pos_snake[0][0], 248)
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
            reward = -0.1
        else:
            reward = 1

        if not self.alive:
            reward = -6e23

        if self.render_mode == "human":
            self._render_frame()

        return self._get_obs(), reward, not self.alive, False, self._get_info()

    def _get_obs(self):
        #print(self.pos_snake, self.pos_food)
        return [
            self.pos_snake[0][0],
            self.pos_snake[0][1],
            self.pos_food[0][0],
            self.pos_food[0][1],
            self.pos_food[1][0],
            self.pos_food[1][1],
            self.pos_food[2][0],
            self.pos_food[2][1],
            self.pos_food[3][0],
            self.pos_food[3][1],
            len(self.pos_snake[1:])
        ]

    def _get_info(self):
        return { "score": self.score }

    def _render_frame(self):
        if self.alive:
            self.screen.fill(color_bg)
            for e in self.pos_food:
                pygame.draw.circle(self.screen, color_item, e, 8)

            for e in self.pos_snake:
                if self.pos_snake.index(e) == 0:
                    continue
                pygame.draw.rect(self.screen, color_snake, (e[0] - 8, e[1] - 8, 16, 16))

            pygame.draw.circle(self.screen, color_snake, self.pos_snake[0], 8)
            if self.pos_snake[0] in self.pos_snake[1:]:
                self.alive = False
        else:
            self.screen.fill(color_item)
            self.screen.blit(self.deathscreen, (128 - 79, 128 - 17))

        self.screen.blit(pygame.font.Font(None, 30).render(str(self.score), True, "black"), (0, 0))

        pygame.display.flip()

        self.clock.tick(self.fps)

gym.register("libewa/snack4snake-v0", entry_point=SnakeEnv)
if __name__ == "__main__":
    gym.pprint_registry()
    env = SnakeEnv()
    print(env.reset()[0])