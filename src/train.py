import argparse
import shutil
from stable_baselines3.common.logger import TensorBoardOutputFormat
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

#human = parser.parse_args().render
human = True

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

field_size = (32, 16)

def safe_mean(arr):
    return np.nan if len(arr) == 0 else np.mean(arr)

# Training
env = SnakeEnv(render_mode="human" if human else None, field_size= field_size)

current_time = datetime.now()
# Format datetime for file names
formatted_time = current_time.strftime("%Y-%m-%d_%H-%M")

models_dir = f"models/{formatted_time}/"
log_dir = f"logs/{formatted_time}/"

os.makedirs(models_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)


class TensorboardCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.step_count = 0

    def _on_step(self):
        self.step_count += 1
        if self.step_count % 1000 == 0:
            print(f"Step: {self.step_count}")

        if self.n_calls % 1000 == 0:
            self.logger.record("train/steps", self.n_calls)
            if len(self.model.ep_info_buffer) > 0 and len(self.model.ep_info_buffer[0]) > 0:
                self.logger.record("rollout/ep_rew_mean",
                                   safe_mean([ep_info["r"] for ep_info in self.model.ep_info_buffer]))
                self.logger.record("rollout/ep_len_mean",
                                   safe_mean([ep_info["l"] for ep_info in self.model.ep_info_buffer]))
                self.logger.record("rollout/score",
                                   self.locals['infos'][0]['score'])
                # Log learning rate
                self.logger.record("train/learning_rate", self.model.learning_rate)

        return True

    def _on_training_start(self):
        output_formats = self.logger.output_formats
        self.tb_formatter = next(formatter for formatter in output_formats
                                 if isinstance(formatter, TensorBoardOutputFormat))

class RewardThresholdCallback(BaseCallback):
    def __init__(self, threshold=15, verbose=0):
        super().__init__(verbose)
        self.threshold = threshold

    def _on_step(self):
        if self.locals['dones'][0]:  # Check if episode is done
            episode_reward = self.locals['infos'][0]['score']
            if episode_reward > self.threshold:
                print(f"Reward threshold reached! Stopping training.")
                return False  # Stop training
        return True  # Continue training


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
threshold_callback = RewardThresholdCallback()

try:
    model.learn(
        total_timesteps=TIMESTEPS,
        callback=[checkpoint_callback, TensorboardCallback(), threshold_callback],
        progress_bar=True
    )
except KeyboardInterrupt:
    print("Training interrupted by user")
finally:
    model.save(f"{models_dir}/DQN_Snake_final")
    print("Final model saved")
    if os.name == 'posix':
        os.remove("models/new")
        os.symlink("models/new", models_dir, True)
    else:
        shutil.rmtree("models/new", ignore_errors=True)
        shutil.copytree(models_dir, "models/new")