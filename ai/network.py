"""
Policy-Value Neural Network for Twilight Struggle AI.

Architecture: Shared trunk with residual blocks, split into policy and value heads.
  - Input: state vector (~756 features)
  - Shared trunk: Linear(756, 512) -> 8 residual blocks
  - Policy head: Linear(512, 256) -> Linear(256, TOTAL_ACTIONS) + masked softmax
  - Value head: Linear(512, 256) -> Linear(256, 1) + tanh
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ai.action_encoder import TOTAL_ACTIONS
from ai.state_encoder import TOTAL_FEATURES


class ResidualBlock(nn.Module):
    """Residual block with two linear layers, batch norm, and skip connection."""

    def __init__(self, hidden_size: int):
        super().__init__()
        self.fc1 = nn.Linear(hidden_size, hidden_size)
        self.bn1 = nn.BatchNorm1d(hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.bn2 = nn.BatchNorm1d(hidden_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        out = F.relu(self.bn1(self.fc1(x)))
        out = self.bn2(self.fc2(out))
        out = F.relu(out + residual)
        return out


class TwilightNet(nn.Module):
    """
    AlphaZero-style policy-value network for Twilight Struggle.

    Parameters
    ----------
    input_size : int
        Size of the state feature vector.
    hidden_size : int
        Size of hidden layers in the trunk and heads.
    num_residual_blocks : int
        Number of residual blocks in the shared trunk.
    num_actions : int
        Size of the action space.
    """

    def __init__(self, input_size: int = TOTAL_FEATURES, hidden_size: int = 512,
                 num_residual_blocks: int = 8, num_actions: int = TOTAL_ACTIONS):
        super().__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_actions = num_actions

        # Input projection
        self.input_fc = nn.Linear(input_size, hidden_size)
        self.input_bn = nn.BatchNorm1d(hidden_size)

        # Shared trunk: residual blocks
        self.trunk = nn.Sequential(
            *[ResidualBlock(hidden_size) for _ in range(num_residual_blocks)]
        )

        # Policy head
        self.policy_fc1 = nn.Linear(hidden_size, 256)
        self.policy_bn = nn.BatchNorm1d(256)
        self.policy_fc2 = nn.Linear(256, num_actions)

        # Value head
        self.value_fc1 = nn.Linear(hidden_size, 256)
        self.value_bn = nn.BatchNorm1d(256)
        self.value_fc2 = nn.Linear(256, 1)

    def forward(self, x: torch.Tensor, legal_mask: torch.Tensor = None):
        """
        Forward pass.

        Parameters
        ----------
        x : torch.Tensor
            State features of shape (batch, input_size).
        legal_mask : torch.Tensor, optional
            Boolean mask of shape (batch, num_actions). True = legal action.

        Returns
        -------
        tuple
            (policy_logits, value) where:
            - policy_logits: (batch, num_actions) masked log-probabilities
            - value: (batch, 1) in range [-1, 1]
        """
        # Shared trunk
        h = F.relu(self.input_bn(self.input_fc(x)))
        h = self.trunk(h)

        # Policy head
        p = F.relu(self.policy_bn(self.policy_fc1(h)))
        policy_logits = self.policy_fc2(p)

        # Apply legal action mask
        if legal_mask is not None:
            policy_logits = policy_logits.masked_fill(~legal_mask, -1e9)

        # Value head
        v = F.relu(self.value_bn(self.value_fc1(h)))
        value = torch.tanh(self.value_fc2(v))

        return policy_logits, value

    def predict(self, state: np.ndarray, legal_mask: np.ndarray) -> tuple:
        """
        Single-state prediction for MCTS (no gradient).

        Parameters
        ----------
        state : np.ndarray
            State vector of shape (TOTAL_FEATURES,).
        legal_mask : np.ndarray
            Boolean mask of shape (TOTAL_ACTIONS,).

        Returns
        -------
        tuple
            (policy_logits_np, value_float)
        """
        self.eval()
        with torch.no_grad():
            state_t = torch.FloatTensor(state).unsqueeze(0)
            mask_t = torch.BoolTensor(legal_mask).unsqueeze(0)

            if next(self.parameters()).is_cuda:
                state_t = state_t.cuda()
                mask_t = mask_t.cuda()

            policy_logits, value = self.forward(state_t, mask_t)

            policy_np = policy_logits.cpu().numpy()[0]
            value_float = value.cpu().item()

        return policy_np, value_float

    def save_checkpoint(self, filepath: str):
        """Save model weights to file."""
        torch.save({
            "model_state_dict": self.state_dict(),
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "num_actions": self.num_actions,
        }, filepath)

    @classmethod
    def load_checkpoint(cls, filepath: str, device: str = "cpu") -> "TwilightNet":
        """Load model from checkpoint file."""
        checkpoint = torch.load(filepath, map_location=device)
        model = cls(
            input_size=checkpoint["input_size"],
            hidden_size=checkpoint["hidden_size"],
            num_actions=checkpoint["num_actions"],
        )
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(device)
        return model
