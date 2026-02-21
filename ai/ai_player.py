"""
AIPlayer: Concrete Player implementation using PIMC + MCTS.

Collects (state, mcts_policy, outcome) training data during play.
Stores top-5 actions with visit counts and win rates for explainability.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import numpy as np

from ai.action_encoder import TOTAL_ACTIONS, get_action_mask
from ai.mcts import MCTSSearch
from ai.pimc import PIMCSearch
from ai.state_encoder import encode_state
from enums import Side
from player import Player

if TYPE_CHECKING:
    from ai.network import TwilightNet
    from game_mechanics import Game
    from interfacing import Input


class AIPlayer(Player):
    """
    AI player using PIMC + MCTS for decision making.

    Parameters
    ----------
    side : Side
        Which side this AI plays.
    network : TwilightNet or None
        Neural network for evaluation. None = uniform priors.
    num_worlds : int
        Number of PIMC determinized worlds.
    num_simulations : int
        MCTS simulations per world.
    temperature : float
        Temperature for action selection (0 = greedy, 1 = proportional).
    collect_data : bool
        Whether to collect training data.
    """

    def __init__(self, side: Side, network: TwilightNet | None = None, num_worlds: int = 20,
                 num_simulations: int = 200, temperature: float = 1.0,
                 collect_data: bool = False) -> None:
        super().__init__(side)
        self.network: TwilightNet | None = network
        self.search = PIMCSearch(
            network=network,
            num_worlds=num_worlds,
            num_simulations=num_simulations,
            temperature=temperature,
        )
        self.collect_data: bool = collect_data
        self.training_data: list[list[object]] = []  # List of (state, policy, None) - outcome filled later
        self.last_explanation: dict[str, object] | None = None
        self.temperature: float = temperature

    def get_move(self, input_state: Input, game: Game) -> str:
        """Select a move using PIMC + MCTS."""
        # For dice rolls, just pick randomly
        if input_state.side == Side.NEUTRAL:
            options = list(input_state.available_options)
            return random.choice(options)

        # Collect state before move for training
        if self.collect_data:
            state = encode_state(game, self.side)
        else:
            state = None

        # Run PIMC search
        move, explanation = self.search.select_move(input_state, game)
        self.last_explanation = explanation

        # Store training data (outcome will be filled post-game)
        if self.collect_data and state is not None:
            # Build policy from MCTS visit counts
            policy = np.zeros(TOTAL_ACTIONS, dtype=np.float32)
            for alt in explanation.get("alternatives", []):
                from ai.action_encoder import encode_action
                idx = encode_action(alt["action"], input_state.state)
                policy[idx] = alt["visits"]
            total = policy.sum()
            if total > 0:
                policy /= total
            self.training_data.append([state, policy, None])

        return move

    def set_game_outcome(self, winner: Side) -> None:
        """
        Fill in game outcomes for all collected training data.

        Parameters
        ----------
        winner : Side
            The winning side.
        """
        if winner == self.side:
            outcome = 1.0
        elif winner == self.side.opp:
            outcome = -1.0
        else:
            outcome = 0.0

        for entry in self.training_data:
            entry[2] = outcome

    def get_training_data(self) -> list[list[object]]:
        """Return collected training data and clear buffer."""
        data = self.training_data
        self.training_data = []
        return data

    def set_temperature(self, temperature: float) -> None:
        """Update temperature for action selection."""
        self.temperature = temperature
        self.search.temperature = temperature
