"""
PIMC (Perfect Information Monte Carlo) wrapper for imperfect information games.

Samples possible opponent hands consistent with known information,
runs MCTS on each determinized world, and aggregates results.
"""

from __future__ import annotations

import random
from collections import defaultdict
from copy import deepcopy
from typing import TYPE_CHECKING

import numpy as np

from ai.mcts import MCTSSearch
from cards import Card
from enums import Side

if TYPE_CHECKING:
    from game_mechanics import Game
    from interfacing import Input


class Determinizer:
    """
    Samples possible opponent hands consistent with known public information.

    Uses the player's view of the game to determine:
    - Cards known to be in own hand
    - Cards known to be discarded or removed
    - Cards known to be in opponent's hand (e.g., from Cambridge Five)
    - All remaining unknown cards to distribute
    """

    def __init__(self, game: Game, perspective_side: Side) -> None:
        self.game: Game = game
        self.side: Side = perspective_side
        self.opp: Side = perspective_side.opp

    def sample_opponent_hand(self) -> list[str]:
        """
        Sample a possible opponent hand consistent with known information.

        Returns
        -------
        list
            A list of card names representing a possible opponent hand.
        """
        # Known information
        my_hand = set(self.game.hand[self.side])
        opp_hand_size = len(self.game.hand[self.opp])
        discard = set(self.game.discard_pile)
        removed = set(self.game.removed_pile)
        headline_cards = set(c for c in self.game.headline_bin if c)

        # Cards known to be in opponent's hand (from game effects)
        player_view = self.game.players[self.side]
        known_opp_cards = set(player_view.opp_hand) if hasattr(player_view, 'opp_hand') else set()

        # All cards in play
        all_cards = set(self.game.cards.in_play)

        # Cards accounted for (not available for sampling)
        accounted = my_hand | discard | removed | headline_cards | known_opp_cards

        # Cards in the draw pile or unknown location
        unknown_cards = list(all_cards - accounted)
        random.shuffle(unknown_cards)

        # Opponent needs (opp_hand_size - known_opp_cards) more unknown cards
        needed = opp_hand_size - len(known_opp_cards)
        needed = max(0, needed)

        sampled = list(known_opp_cards) + unknown_cards[:needed]
        return sampled

    def determinize(self) -> Game:
        """
        Create a determinized copy of the game with a sampled opponent hand.

        Returns
        -------
        Game
            Deep copy of the game with opponent's hand replaced by sample.
        """
        game_copy = deepcopy(self.game)
        sampled_hand = self.sample_opponent_hand()
        game_copy.hand[self.opp] = list(sampled_hand)
        return game_copy


class PIMCSearch:
    """
    Perfect Information Monte Carlo search.

    Runs K determinizations, performs MCTS on each, and aggregates.

    Parameters
    ----------
    network : callable or None
        Neural network for MCTS evaluation.
    num_worlds : int
        Number of determinized worlds to sample.
    num_simulations : int
        MCTS simulations per world.
    c_puct : float
        PUCT exploration constant.
    temperature : float
        Temperature for final action selection.
    """

    def __init__(self, network: object = None, num_worlds: int = 20,
                 num_simulations: int = 200, c_puct: float = 1.4,
                 temperature: float = 1.0) -> None:
        self.network = network
        self.num_worlds: int = num_worlds
        self.num_simulations: int = num_simulations
        self.c_puct: float = c_puct
        self.temperature: float = temperature

    def select_move(self, input_state: Input, game: Game) -> tuple[str, dict[str, object]]:
        """
        Select a move using PIMC + MCTS.

        Parameters
        ----------
        input_state : Input
            Current input state.
        game : Game
            Current game state.

        Returns
        -------
        tuple
            (move_string, explanation_dict)
        """
        perspective_side = input_state.side
        mcts = MCTSSearch(
            network=self.network,
            num_simulations=self.num_simulations,
            c_puct=self.c_puct,
            temperature=self.temperature,
        )

        # Aggregate visit counts across worlds
        aggregated_visits = defaultdict(float)
        aggregated_values = defaultdict(float)
        world_counts = defaultdict(int)

        for _ in range(self.num_worlds):
            # Create determinized world
            determinizer = Determinizer(game, perspective_side)
            det_game = determinizer.determinize()

            # Run MCTS on this world
            visit_counts = mcts.search(det_game, perspective_side)

            # Aggregate
            for action_idx, visits in visit_counts.items():
                aggregated_visits[action_idx] += visits
                world_counts[action_idx] += 1

            # Also track value estimates
            for action_idx, visits in visit_counts.items():
                if visits > 0:
                    # Approximate value from visit proportions
                    total = sum(visit_counts.values())
                    aggregated_values[action_idx] += visits / max(1, total)

        if not aggregated_visits:
            # Fallback: random legal move
            options = list(input_state.available_options)
            if input_state.option_stop_early:
                options.append(input_state.option_stop_early)
            move = random.choice(options)
            return move, {"action": move, "confidence": 0.0, "alternatives": []}

        # Select best action from aggregated visits
        action_idx = mcts.select_action(dict(aggregated_visits), self.temperature)

        # Decode action to game string
        from ai.action_encoder import decode_action
        move = decode_action(action_idx, input_state)

        # Build explanation
        explanation = self._build_explanation(
            aggregated_visits, aggregated_values, world_counts,
            action_idx, move, input_state
        )

        return move, explanation

    def _build_explanation(self, visits: dict[int, float], values: dict[int, float],
                           world_counts: dict[int, int],
                           chosen_idx: int, chosen_move: str, input_state: Input) -> dict[str, object]:
        """Build explanation dict for the AI decision."""
        from ai.action_encoder import decode_action

        total_visits = sum(visits.values())

        # Sort actions by visit count
        sorted_actions = sorted(visits.items(), key=lambda x: -x[1])[:5]

        alternatives = []
        for action_idx, visit_count in sorted_actions:
            try:
                action_name = decode_action(action_idx, input_state)
            except (ValueError, KeyError):
                action_name = f"action_{action_idx}"

            confidence = visit_count / max(1, total_visits)
            avg_value = values.get(action_idx, 0.0) / max(1, world_counts.get(action_idx, 1))

            alternatives.append({
                "action": action_name,
                "visits": int(visit_count),
                "confidence": round(confidence, 3),
                "avg_value": round(avg_value, 3),
            })

        return {
            "chosen_action": chosen_move,
            "confidence": alternatives[0]["confidence"] if alternatives else 0.0,
            "alternatives": alternatives,
            "total_simulations": total_visits,
            "num_worlds": self.num_worlds,
        }
