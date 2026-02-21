"""Abstract Player interface and concrete implementations for Twilight Struggle."""

import random
from abc import ABC, abstractmethod

from enums import InputType, Side


class Player(ABC):
    """Abstract base class for all players (human, AI, random)."""

    def __init__(self, side: Side):
        self.side = side

    @abstractmethod
    def get_move(self, input_state, game) -> str:
        """
        Given the current input state and game, return a move string.

        Parameters
        ----------
        input_state : Input
            The current input state with available options and context.
        game : Game
            The game instance (for AI to read state).

        Returns
        -------
        str
            The selected option string.
        """
        raise NotImplementedError


class HumanPlayer(Player):
    """Human player that receives moves from external input (CLI or GUI)."""

    def __init__(self, side: Side):
        super().__init__(side)
        self._pending_move = None

    def set_move(self, move: str):
        """Set the next move to be returned by get_move."""
        self._pending_move = move

    def get_move(self, input_state, game) -> str:
        move = self._pending_move
        self._pending_move = None
        return move


class RandomPlayer(Player):
    """Baseline player that selects uniformly random valid moves."""

    def get_move(self, input_state, game) -> str:
        options = list(input_state.available_options)
        if input_state.option_stop_early:
            options.append(input_state.option_stop_early)
        if not options:
            return None
        return random.choice(options)


class AIPlayer(Player):
    """AI player using PIMC + MCTS. Placeholder until ai/ module is built."""

    def __init__(self, side: Side, search=None):
        super().__init__(side)
        self.search = search  # Will be PIMCSearch instance
        self.last_explanation = None

    def get_move(self, input_state, game) -> str:
        if self.search is None:
            # Fallback to random if no search engine configured
            options = list(input_state.available_options)
            if input_state.option_stop_early:
                options.append(input_state.option_stop_early)
            return random.choice(options)

        move, explanation = self.search.select_move(input_state, game)
        self.last_explanation = explanation
        return move
