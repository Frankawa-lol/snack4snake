from logic import SnakeEnv
from stable_baselines3 import DQN


model = DQN.load("models/DQN_Snake_final")


num_episodes = 400

# Ausführung
eval_env = SnakeEnv(render_mode="human", fps=10)
obs, _ = eval_env.reset()

for _ in range(num_episodes):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = eval_env.step(action)

    if terminated or truncated:
        obs, _ = eval_env.reset()

eval_env.close()
