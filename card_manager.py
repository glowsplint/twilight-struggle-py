from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from enums import InputType, Side
from interfacing import Input

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from cards import GameCards
    from game_mechanics import Game
    from game_state import GameState
    from interfacing import Output
    from player_view import PlayerView


class CardManager:
    """Manages card-related operations: deck building, dealing, shuffling, ops calculation."""

    def __init__(self, state: GameState, cards: GameCards) -> None:
        self._state = state
        self._cards = cards

    def expand_deck(
        self,
        players: list[PlayerView],
        shuffle_draw_pile_stage_fn: Callable[[], None],
    ) -> None:

        if self._state.turn_track == 1:
            self._state.draw_pile.extend(reversed(self._cards.early_war))
            self._cards.in_play.update(self._cards.early_war)
            self._state.hand[Side.USSR].append(
                self._state.draw_pile.pop(
                    self._state.draw_pile.index("The_China_Card")
                )
            )
            if "The_China_Card" in self._state.hand[Side.USSR]:
                players[Side.US].opp_hand.update(["The_China_Card"])
            else:
                players[Side.USSR].opp_hand.update(["The_China_Card"])
        elif self._state.turn_track == 4:
            self._state.draw_pile.extend(reversed(self._cards.mid_war))
            self._cards.in_play.update(self._cards.mid_war)
            self._cards.mid_war = []
            shuffle_draw_pile_stage_fn()
        elif self._state.turn_track == 8:
            self._state.draw_pile.extend(reversed(self._cards.late_war))
            self._cards.in_play.update(self._cards.late_war)
            self._cards.late_war = []
            shuffle_draw_pile_stage_fn()

    def deal(
        self,
        players: list[PlayerView],
        stage_list: list[Callable[[], None]],
        shuffle_draw_pile_stage_fn: Callable[[], None],
        deal_fn: Callable[[Side], None],
        first_side: Side = Side.USSR,
    ) -> None:

        if first_side == Side.NEUTRAL:
            handsize_target = [3, 2]  # hardcoded for Ask Not..
        elif 1 <= self._state.turn_track <= 3:
            handsize_target = [8, 8]
        else:
            handsize_target = [9, 9]

        # Ignore China Card if it is in either hand
        if "The_China_Card" in self._state.hand[Side.USSR]:
            handsize_target[Side.USSR] += 1
        elif "The_China_Card" in self._state.hand[Side.US]:
            handsize_target[Side.US] += 1

        next_side = first_side
        while any(
            len(h) < t for h, t in zip(self._state.hand, handsize_target)
        ):
            if len(self._state.hand[next_side]) >= handsize_target[next_side]:
                next_side = next_side.opp
                continue

            if not self._state.draw_pile:
                # if draw pile exhausted, shuffle the discard pile and put it as the new draw pile
                self._state.draw_pile += self._state.discard_pile
                self._state.discard_pile = []
                stage_list.append(partial(deal_fn, next_side))
                shuffle_draw_pile_stage_fn()
                return

            self._state.hand[next_side].append(self._state.draw_pile.pop())
            next_side = next_side.opp

        for s in [Side.USSR, Side.US]:
            players[s].opp_hand_no_scoring_cards = False

    def shuffle_callback(
        self, card_name: str
    ) -> None:
        """Append a card to the draw pile. Reps management is handled by the Game wrapper."""
        self._state.draw_pile.append(card_name)

    def shuffle_draw_pile_stage(
        self,
        set_input_state_fn: Callable[[Input], None],
        shuffle_callback_fn: Callable[[str], bool],
    ) -> None:
        shuffler_pile = self._state.draw_pile
        self._state.draw_pile = []

        set_input_state_fn(
            Input(
                Side.NEUTRAL,
                InputType.SELECT_CARD,
                shuffle_callback_fn,
                shuffler_pile,
                "Shuffle the deck.  Select the next card.",
                reps=len(shuffler_pile),
                reps_unit="cards",
                max_per_option=1,
            )
        )

    def get_global_effective_ops(
        self,
        game: Game,
        side: Side,
        raw_ops: int,
        output_state: Output,
    ) -> int:
        """
        Gets the effective operations value of the card, bound to [1,4]. Accounts for
        only global effects like Containment, Brezhnev_Doctrine and Red_Scare_Purge.

        Does not account for local effects like additional operations points from the use
        of the China Card in Asia, or in SEA when Vietnam Revolts is active.

        Parameters
        ----------
        game : Game
            The game instance (passed to effect methods).
        side : Side
            Side of the player.
        raw_ops : int
            Unmodified operations value of the card.
        output_state : Output
            The output state for notifications.
        """
        for effect_side, effect_name in (
            (s, eff) for s in Side for eff in self._state.basket[s]
        ):
            mod = self._cards[effect_name].effect_global_ops(
                game, effect_side, side
            )
            if mod is not None:
                raw_ops += mod
                output_state.prompt += f"{effect_name}: {mod:+} ops."

        return min(max(raw_ops, 1), 4)
