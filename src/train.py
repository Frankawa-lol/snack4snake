import argparse
from logic import SnakeEnv
import os
from datetime import datetime
import numpy as np
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback

parser = argparse.ArgumentParser(
                    prog='snack4snake train',
                    description='Train snack4snake AI models')
parser.add_argument('-r', '--render', action='store_true')

human = parser.parse_args().render

TIMESTEPS = 100_000
LEARNING_RATE = 1e-4
gamma = 0.99
EXPLORATION_FRACTION = 0.8
EXPLORATION_INITIAL_EPS = 1.0
EXPLORATION_FINAL_EPS = 0.05
BUFFER_SIZE = 100_000
LEARNING_START = 1000
BATCH_SIZE = 100

TARGET_UPDATE_INTERVAL = 1000
tau = 1.0
TRAIN_FREQ = 4
GRADIENT_STEPS = 1


def safe_mean(arr):
    return np.nan if len(arr) == 0 else np.mean(arr)

# Training
env = SnakeEnv(render_mode="human" if human else None)

current_time = datetime.now()

# Format datetime for file names
#formatted_time = current_time.strftime("%Y-%m-%d_%H-%M")

formatted_time = "new"

models_dir = f"models/{formatted_time}/"
log_dir = f"logs/{formatted_time}/"

os.makedirs(models_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)


class TensorboardCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(TensorboardCallback, self).__init__(verbose)

    def _on_step(self) -> bool:
        # Log epsilon (exploration rate)
        self.logger.record('epsilon', self.model.exploration_rate)

        # Log Q-values
        obs = self.training_env.reset()[0]
        q_values = self.model.q_net(self.model.q_net.obs_to_tensor(obs)[0])
        self.logger.record('q_values/max', q_values.max().item())
        self.logger.record('q_values/min', q_values.min().item())
        self.logger.record('q_values/mean', q_values.mean().item())

        return True

model = DQN('MlpPolicy', env,
            learning_rate=LEARNING_RATE,
            buffer_size=BUFFER_SIZE,
            learning_starts=LEARNING_START,
            batch_size=BATCH_SIZE,
            tau=tau,
            gamma=gamma,
            train_freq=TRAIN_FREQ,
            gradient_steps=GRADIENT_STEPS,
            target_update_interval=TARGET_UPDATE_INTERVAL,
            exploration_fraction=EXPLORATION_FRACTION,
            exploration_initial_eps=EXPLORATION_INITIAL_EPS,
            exploration_final_eps=EXPLORATION_FINAL_EPS,
            tensorboard_log=log_dir,
            verbose=1)

checkpoint_callback = CheckpointCallback(save_freq=1000, save_path=models_dir, name_prefix='dqn_snake')

try:
    model.learn(
        total_timesteps=TIMESTEPS,
        callback=[checkpoint_callback, TensorboardCallback()],
        progress_bar=True
    )
except KeyboardInterrupt:
    print("Training interrupted by user")
finally:
    model.save(f"{models_dir}/DQN_Snake_final")
    print("Final model saved")