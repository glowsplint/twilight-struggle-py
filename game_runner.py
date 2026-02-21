"""
GameRunner: Decoupled game orchestrator for running games between Player instances.

Handles the stage_complete loop, auto-rolls dice, detects game end.
Supports fast simulation mode for self-play training.
"""

from __future__ import annotations

import random
from copy import deepcopy

from enums import Side
from game_mechanics import Game
from player import Player


class GameResult:
    """Result of a completed game."""

    def __init__(self, winner: Side, vp: int, turn: int, move_history: list[tuple[Side, str]]) -> None:
        self.winner: Side = winner
        self.vp: int = vp
        self.turn: int = turn
        self.move_history: list[tuple[Side, str]] = move_history

    def __repr__(self) -> str:
        return f"GameResult(winner={self.winner.toStr}, vp={self.vp}, turn={self.turn}, moves={len(self.move_history)})"


class GameRunner:
    """
    Orchestrates a full game between two Player instances.

    Parameters
    ----------
    ussr_player : Player
        Player controlling USSR.
    us_player : Player
        Player controlling US.
    handicap : int
        Starting influence handicap. Negative favors US.
    silent : bool
        If True, suppresses all output (fast simulation mode).
    max_turns : int
        Maximum number of turns before declaring draw.
    """

    MAX_MOVES = 5000  # Safety limit to prevent infinite loops

    def __init__(self, ussr_player: Player, us_player: Player,
                 handicap: int = -2, silent: bool = True, max_turns: int = 10) -> None:
        self.players: dict[Side, Player] = {Side.USSR: ussr_player, Side.US: us_player}
        self.handicap: int = handicap
        self.silent: bool = silent
        self.max_turns: int = max_turns

    def run_game(self) -> GameResult:
        """
        Run a complete game and return the result.

        Returns
        -------
        GameResult
            The outcome of the game.
        """
        game = Game()
        game.start(handicap=self.handicap)
        move_history: list[tuple[Side, str]] = []
        total_steps = 0

        # Advance past initial setup stages until first input needed
        self._advance(game)

        while game.stage_list:
            total_steps += 1
            if total_steps > self.MAX_MOVES:
                # Safety: prevent infinite loops
                break

            input_state = game.input_state
            if input_state is None:
                self._advance(game)
                continue

            side = input_state.side

            # Auto-roll dice for NEUTRAL (RNG) inputs
            if side == Side.NEUTRAL:
                self._handle_rng(game, move_history)
                continue

            # Check if input is already complete
            if input_state.complete:
                self._advance(game)
                continue

            # Get move from appropriate player
            player = self.players[side]
            move = player.get_move(input_state, game)

            if move is None:
                if input_state.complete:
                    self._advance(game)
                    continue
                # Force advance if stuck
                self._advance(game)
                continue

            accepted = input_state.recv(move)
            if accepted:
                move_history.append((side, move))

            # Check if input is complete, then advance
            if input_state.complete:
                self._advance(game)

        # Game is over
        winner = self._determine_winner(game)
        return GameResult(
            winner=winner,
            vp=game.vp_track,
            turn=game.turn_track,
            move_history=move_history,
        )

    def _advance(self, game: Game) -> None:
        """Advance game stages until input is required or game ends."""
        if not game.stage_list:
            return
        game.stage_complete()
        while game.stage_list and not game.input_state:
            game.stage_complete()

    def _handle_rng(self, game: Game, move_history: list[tuple[Side, str]]) -> None:
        """Auto-roll dice for NEUTRAL-side inputs."""
        input_state = game.input_state
        while not input_state.complete:
            choices = list(input_state.available_options)
            if not choices:
                break
            choice = random.choice(choices)
            input_state.recv(choice)
            move_history.append((Side.NEUTRAL, choice))

        if input_state.complete and game.stage_list:
            self._advance(game)

    def _determine_winner(self, game: Game) -> Side:
        """Determine winner from final game state."""
        if game.vp_track > 0:
            return Side.USSR
        elif game.vp_track < 0:
            return Side.US
        else:
            return Side.NEUTRAL

    def get_game_copy(self, game: Game) -> Game:
        """Return a deep copy of the game for PIMC determinization."""
        return deepcopy(game)
