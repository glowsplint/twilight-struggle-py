"""
Core MCTS (Monte Carlo Tree Search) implementation.

Uses PUCT (Predictor + Upper Confidence bounds applied to Trees) selection
with neural network priors for expansion and value estimation.
"""

import math
import random

import numpy as np

from ai.action_encoder import (
    TOTAL_ACTIONS,
    decode_action,
    encode_action,
    get_action_mask,
    masked_action_probs,
)
from ai.state_encoder import TOTAL_FEATURES, encode_state
from enums import Side


class MCTSNode:
    """A node in the MCTS search tree."""

    __slots__ = [
        "parent", "action_idx", "children", "visit_count",
        "value_sum", "prior", "is_expanded", "input_type",
    ]

    def __init__(self, parent=None, action_idx: int = -1, prior: float = 0.0):
        self.parent = parent
        self.action_idx = action_idx
        self.children = {}  # action_idx -> MCTSNode
        self.visit_count = 0
        self.value_sum = 0.0
        self.prior = prior
        self.is_expanded = False
        self.input_type = None

    @property
    def value(self) -> float:
        """Mean value estimate Q(s,a)."""
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count

    def select_child(self, c_puct: float = 1.4) -> "MCTSNode":
        """Select child with highest PUCT score."""
        total_visits = sum(c.visit_count for c in self.children.values())
        sqrt_total = math.sqrt(total_visits + 1)

        best_score = -float("inf")
        best_child = None

        for child in self.children.values():
            q_value = child.value
            u_value = c_puct * child.prior * sqrt_total / (1 + child.visit_count)
            score = q_value + u_value
            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def expand(self, action_priors: np.ndarray, legal_mask: np.ndarray):
        """
        Expand this node with children for all legal actions.

        Parameters
        ----------
        action_priors : np.ndarray
            Prior probabilities for each action from the policy network.
        legal_mask : np.ndarray
            Boolean mask of legal actions.
        """
        self.is_expanded = True
        for action_idx in np.where(legal_mask)[0]:
            self.children[action_idx] = MCTSNode(
                parent=self,
                action_idx=int(action_idx),
                prior=float(action_priors[action_idx]),
            )

    def backpropagate(self, value: float):
        """Propagate value estimate back up the tree."""
        node = self
        while node is not None:
            node.visit_count += 1
            node.value_sum += value
            value = -value  # Flip for opponent's perspective
            node = node.parent


class MCTSSearch:
    """
    MCTS search engine.

    Parameters
    ----------
    network : callable or None
        Neural network that takes (state_vector, legal_mask) and returns
        (policy_logits, value). If None, uses uniform priors and random rollouts.
    num_simulations : int
        Number of MCTS simulations per search.
    c_puct : float
        Exploration constant for PUCT formula.
    temperature : float
        Temperature for action selection from visit counts.
    """

    def __init__(self, network=None, num_simulations: int = 200,
                 c_puct: float = 1.4, temperature: float = 1.0):
        self.network = network
        self.num_simulations = num_simulations
        self.c_puct = c_puct
        self.temperature = temperature

    def search(self, game, perspective_side: Side) -> dict:
        """
        Run MCTS from the current game state.

        Parameters
        ----------
        game : Game
            The game state to search from.
        perspective_side : Side
            The side making the decision.

        Returns
        -------
        dict
            Mapping of action_idx -> visit_count for root children.
        """
        if not game.input_state:
            return {}

        root = MCTSNode()
        legal_mask = get_action_mask(game.input_state)

        if not legal_mask.any():
            return {}

        # Evaluate root
        policy, value = self._evaluate(game, perspective_side, legal_mask)
        root.expand(policy, legal_mask)

        # Run simulations
        for _ in range(self.num_simulations):
            node = root
            sim_game = None

            # Selection: traverse tree to leaf
            while node.is_expanded and node.children:
                node = node.select_child(self.c_puct)

            # We need a copy of the game to simulate moves
            # For efficiency, we only copy when we need to go beyond root
            if node != root:
                from copy import deepcopy
                sim_game = deepcopy(game)
                # Replay moves from root to this node
                path = []
                trace = node
                while trace.parent is not None:
                    path.append(trace)
                    trace = trace.parent
                path.reverse()

                for step_node in path:
                    if sim_game.input_state:
                        option = decode_action(step_node.action_idx, sim_game.input_state)
                        sim_game.input_state.recv(option)
                        if sim_game.input_state.complete and sim_game.stage_list:
                            sim_game.input_state = None
                            sim_game.stage_list.pop()()
                            while sim_game.stage_list and not sim_game.input_state:
                                sim_game.stage_list.pop()()

                # Expansion
                if sim_game.input_state and sim_game.stage_list:
                    sim_legal_mask = get_action_mask(sim_game.input_state)
                    if sim_legal_mask.any():
                        sim_policy, sim_value = self._evaluate(
                            sim_game, perspective_side, sim_legal_mask
                        )
                        node.expand(sim_policy, sim_legal_mask)
                        node.backpropagate(sim_value)
                        continue

                # Terminal or no legal moves - rollout value
                value = self._terminal_value(sim_game, perspective_side)
                node.backpropagate(value)
            else:
                # Root node only - use network value
                node.backpropagate(value)

        return {idx: child.visit_count for idx, child in root.children.items()}

    def select_action(self, visit_counts: dict, temperature: float = None) -> int:
        """
        Select action from visit counts using temperature.

        Parameters
        ----------
        visit_counts : dict
            action_idx -> visit_count.
        temperature : float
            Temperature parameter. 0 = greedy, 1 = proportional.

        Returns
        -------
        int
            Selected action index.
        """
        if temperature is None:
            temperature = self.temperature

        if not visit_counts:
            raise ValueError("No visit counts to select from")

        actions = list(visit_counts.keys())
        counts = np.array([visit_counts[a] for a in actions], dtype=np.float64)

        if temperature == 0:
            # Greedy
            return actions[np.argmax(counts)]

        # Temperature-scaled probabilities
        counts = counts ** (1.0 / temperature)
        total = counts.sum()
        if total == 0:
            return random.choice(actions)
        probs = counts / total
        return actions[np.random.choice(len(actions), p=probs)]

    def get_policy(self, visit_counts: dict) -> np.ndarray:
        """
        Convert visit counts to a policy vector.

        Returns
        -------
        np.ndarray
            Policy distribution over full action space.
        """
        policy = np.zeros(TOTAL_ACTIONS, dtype=np.float32)
        total = sum(visit_counts.values())
        if total > 0:
            for idx, count in visit_counts.items():
                policy[idx] = count / total
        return policy

    def _evaluate(self, game, perspective_side: Side,
                  legal_mask: np.ndarray) -> tuple:
        """
        Evaluate game state using the neural network or uniform priors.

        Returns
        -------
        tuple
            (policy_probs, value) where policy_probs is masked and normalized.
        """
        if self.network is not None:
            state = encode_state(game, perspective_side)
            policy_logits, value = self.network.predict(state, legal_mask)
            policy = masked_action_probs(policy_logits, legal_mask)
            return policy, float(value)

        # Uniform priors as fallback
        num_legal = legal_mask.sum()
        policy = np.zeros(TOTAL_ACTIONS, dtype=np.float32)
        if num_legal > 0:
            policy[legal_mask] = 1.0 / num_legal
        return policy, 0.0

    def _terminal_value(self, game, perspective_side: Side) -> float:
        """Estimate value of a terminal or near-terminal state."""
        vp = game.vp_track * perspective_side.vp_mult
        # Normalize to [-1, 1]
        return max(-1.0, min(1.0, vp / 20.0))
