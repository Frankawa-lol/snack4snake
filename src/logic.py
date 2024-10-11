import random

class SnakeEnv:
    pos_snake = [(120, 120), (120, 136), (120, 152), (136, 152), (152, 152), (152, 168)]
    alive = True
    score = 0
    pos_food = []
    current_dir = "up"

    def __init__(self):
        for i in range(4):
            self.generate_new_food()

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

        food_eaten = False