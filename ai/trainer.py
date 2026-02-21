"""
Training loop and replay buffer for the Twilight Struggle AI.

Components:
- ReplayBuffer: Stores (state, mcts_policy, game_outcome) tuples
- Trainer: Manages training loop with loss computation and optimization
"""

from __future__ import annotations

import random
from collections import deque
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from ai.action_encoder import TOTAL_ACTIONS
from ai.network import TwilightNet
from ai.state_encoder import TOTAL_FEATURES


class ReplayBuffer:
    """
    Experience replay buffer for training data.

    Stores (state, mcts_policy, game_outcome) tuples with a maximum capacity.

    Parameters
    ----------
    max_size : int
        Maximum number of samples to store.
    """

    def __init__(self, max_size: int = 500_000) -> None:
        self.buffer: deque[tuple[np.ndarray, np.ndarray, float]] = deque(maxlen=max_size)

    def add(self, state: np.ndarray, policy: np.ndarray, outcome: float) -> None:
        """Add a single training sample."""
        self.buffer.append((state, policy, outcome))

    def add_batch(self, data: list[tuple[np.ndarray, np.ndarray, float | None]]) -> None:
        """Add a batch of (state, policy, outcome) tuples."""
        for state, policy, outcome in data:
            if outcome is not None:
                self.add(state, policy, outcome)

    def sample(self, batch_size: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Sample a random batch from the buffer.

        Returns
        -------
        tuple
            (states, policies, outcomes) as numpy arrays.
        """
        batch_size = min(batch_size, len(self.buffer))
        batch = random.sample(list(self.buffer), batch_size)

        states = np.array([s for s, _, _ in batch], dtype=np.float32)
        policies = np.array([p for _, p, _ in batch], dtype=np.float32)
        outcomes = np.array([o for _, _, o in batch], dtype=np.float32)

        return states, policies, outcomes

    def __len__(self) -> int:
        return len(self.buffer)

    def save(self, filepath: str) -> None:
        """Save buffer to file."""
        data = list(self.buffer)
        states = np.array([s for s, _, _ in data])
        policies = np.array([p for _, p, _ in data])
        outcomes = np.array([o for _, _, o in data])
        np.savez_compressed(filepath, states=states, policies=policies, outcomes=outcomes)

    def load(self, filepath: str) -> None:
        """Load buffer from file."""
        data = np.load(filepath)
        for s, p, o in zip(data["states"], data["policies"], data["outcomes"]):
            self.add(s, p, float(o))


class Trainer:
    """
    Manages the training loop for TwilightNet.

    Parameters
    ----------
    network : TwilightNet
        The network to train.
    lr : float
        Learning rate.
    weight_decay : float
        L2 regularization strength.
    device : str
        Device to train on ('cpu' or 'cuda').
    """

    def __init__(self, network: TwilightNet, lr: float = 0.001,
                 weight_decay: float = 1e-4, device: str = "cpu") -> None:
        self.network: TwilightNet = network.to(device)
        self.device: str = device
        self.optimizer = optim.Adam(
            network.parameters(), lr=lr, weight_decay=weight_decay
        )
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=1000, eta_min=1e-5
        )
        self.train_step = 0

    def train_on_buffer(self, replay_buffer: ReplayBuffer,
                        batch_size: int = 256, num_steps: int = 1000) -> dict[str, float | int]:
        """
        Train the network on samples from the replay buffer.

        Parameters
        ----------
        replay_buffer : ReplayBuffer
            The experience replay buffer.
        batch_size : int
            Training batch size.
        num_steps : int
            Number of training steps.

        Returns
        -------
        dict
            Training metrics (policy_loss, value_loss, total_loss).
        """
        self.network.train()

        total_policy_loss = 0.0
        total_value_loss = 0.0
        total_loss = 0.0

        for step in range(num_steps):
            states, policies, outcomes = replay_buffer.sample(batch_size)

            states_t = torch.FloatTensor(states).to(self.device)
            policies_t = torch.FloatTensor(policies).to(self.device)
            outcomes_t = torch.FloatTensor(outcomes).unsqueeze(1).to(self.device)

            # Forward pass
            policy_logits, value = self.network(states_t)

            # Policy loss: cross-entropy with MCTS policy
            log_probs = torch.log_softmax(policy_logits, dim=1)
            policy_loss = -torch.mean(torch.sum(policies_t * log_probs, dim=1))

            # Value loss: MSE with game outcome
            value_loss = nn.functional.mse_loss(value, outcomes_t)

            # Total loss
            loss = policy_loss + value_loss

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.network.parameters(), 1.0)
            self.optimizer.step()
            self.scheduler.step()

            total_policy_loss += policy_loss.item()
            total_value_loss += value_loss.item()
            total_loss += loss.item()
            self.train_step += 1

        n = max(1, num_steps)
        return {
            "policy_loss": total_policy_loss / n,
            "value_loss": total_value_loss / n,
            "total_loss": total_loss / n,
            "train_steps": self.train_step,
            "buffer_size": len(replay_buffer),
        }

    def save_checkpoint(self, filepath: str) -> None:
        """Save training state."""
        torch.save({
            "model_state_dict": self.network.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict(),
            "train_step": self.train_step,
        }, filepath)

    def load_checkpoint(self, filepath: str) -> None:
        """Load training state."""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.network.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        self.train_step = checkpoint["train_step"]
