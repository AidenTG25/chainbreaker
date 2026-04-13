#!/usr/bin/env python3
import argparse
import asyncio
import numpy as np
from pathlib import Path
from stable_baselines3 import PPO
from sb3_contrib import MaskablePPO
from torch import nn

from backend.agent.kill_chain_env import KillChainEnv
from backend.agent.action_masker import ActionMasker
from backend.utils.config import config
from backend.utils.logger import setup_logger

logger = setup_logger("train_rl")


def make_env():
    def _init():
        env = KillChainEnv()
        return env
    return _init


async def train():
    env = KillChainEnv()
    obs, _ = env.reset()

    ppo_cfg = config.get_section("rl").get("ppo", {})
    env_cfg = config.get_section("rl").get("environment", {})

    policy_kwargs = {
        "net_arch": [256, 256, 128],
        "activation_fn": nn.ReLU,
    }

    model = MaskablePPO(
        "MlpPolicy",
        env,
        verbose=1,
        tensorboard_log="logs/tensorboard/",
        n_steps=ppo_cfg.get("n_steps", 2048),
        batch_size=ppo_cfg.get("batch_size", 64),
        n_epochs=ppo_cfg.get("n_epochs", 10),
        gamma=ppo_cfg.get("gamma", 0.99),
        gae_lambda=ppo_cfg.get("gae_lambda", 0.95),
        clip_range=ppo_cfg.get("clip_range", 0.2),
        ent_coef=ppo_cfg.get("ent_coef", 0.01),
        learning_rate=ppo_cfg.get("learning_rate", 0.0003),
        max_grad_norm=ppo_cfg.get("max_grad_norm", 0.5),
        policy_kwargs=policy_kwargs,
    )

    total_timesteps = config.get_nested("rl", "training", "total_timesteps", default=500000)
    save_freq = config.get_nested("rl", "training", "save_freq", default=10000)
    save_path = config.get_nested("rl", "training", "save_path", default="models/rl_agent.zip")

    logger.info("rl_training_started", total_timesteps=total_timesteps)
    model.learn(
        total_timesteps=total_timesteps,
        callback=None,
        log_interval=100,
        progress_bar=True,
    )

    save_path_obj = Path(save_path)
    save_path_obj.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(save_path_obj))
    logger.info("rl_training_complete", save_path=str(save_path_obj))

    env.close()


async def evaluate():
    from stable_baselines3 import PPO
    model_path = config.get_nested("rl", "training", "save_path", default="models/rl_agent.zip")
    if not Path(model_path).exists():
        logger.warning("model_not_found_skipping_evaluation")
        return
    model = MaskablePPO.load(model_path)
    env = KillChainEnv()

    n_episodes = config.get_nested("rl", "training", "n_eval_episodes", default=10)
    rewards = []
    for ep in range(n_episodes):
        obs, _ = env.reset()
        done = False
        total_reward = 0.0
        steps = 0
        while not done and steps < env.max_steps:
            mask = env.get_action_mask()
            valid_actions = np.where(mask == 1.0)[0]
            if len(valid_actions) == 0:
                break
            action, _ = model.predict(obs, action_masks=mask)
            obs, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            total_reward += reward
            steps += 1
        rewards.append(total_reward)
        logger.info("episode_complete", ep=ep+1, reward=total_reward, steps=steps)

    logger.info("evaluation_complete", mean_reward=float(np.mean(rewards)), std_reward=float(np.std(rewards)))
    env.close()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["train", "evaluate"], default="train")
    args = parser.parse_args()
    if args.mode == "train":
        await train()
    else:
        await evaluate()


if __name__ == "__main__":
    asyncio.run(main())
