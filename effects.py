from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING

from enums import CoupEffects, MapRegion, Side

if TYPE_CHECKING:
    from game_mechanics import Game


class Effect:
    def effect_global_ops(self, game: Game, effect_side: Side, ops_side: Side) -> int | None:
        """
        Returns the operations modifier for a player due to the effect.
        :param effect_side: the side which activated the effect (who's basket the effect is in)
        :param ops_side: the side conducting operations
        :return: the change in ops, or None if no change
        """
        pass

    def effect_ar_function(self, game: Game) -> Callable[[], None] | None:
        pass

    def effect_end_turn(self, game: Game, effect_side: Side) -> None:
        pass

    def effect_opsinf_region_ops(
        self, game: Game, effect_side: Side, ops_side: Side
    ) -> tuple[MapRegion, int] | None:
        pass

    def effect_opsinf_country_select(
        self, game: Game, effect_side: Side, ops_side: Side, country_name: str
    ) -> tuple[MapRegion, int] | None:
        pass

    def effect_opsinf_after(self, game: Game, effect_side: Side, ops_side: Side) -> None:
        """
        This function is called after influence has been placed as operations (and been used up).
        :param effect_side: the side which activated the effect (who's basket the effect is in)
        :param ops_side: the side which is conducting operations
        """
        pass

    def effect_realign_country_restrict(self, game: Game, side: Side) -> Iterable[str] | None:
        """
        Returns the countries in which a realignment is not allowed if
        the effect is active.
        :param side: the side that is trying to perform realignments.
        :return: The list of countries a realignment is NOT allowed in, or
            None if no restriction
        """
        pass

    def effect_realign_roll(
        self, game: Game, effect_side: Side, roll_side: Side, country_name: str
    ) -> int | None:
        """
        Returns the realignment roll modifier for roll_side, given that
        the effect is active for effect_side, and the country being realigned.
        :param effect_side: the side which activated the effect (who's basket the effect is in)
        :param roll_side: the side doing the roll
        :param country_name: the country being realigned
        :return: the change to the roll, or None if no change
        """
        pass

    def effect_realign_ops(self, game: Game, effect_side: Side, country_name: str) -> int | None:
        """
        Returns the realignment ops modifier for effect_side, Called after every
        realignment.
        :param effect_side: the side which activated the effect (who's basket the effect is in)
        :param country_name: the country being realigned
        :return: the change to ops, or None if no change.
        """
        pass

    def effect_realign_after(self, game: Game, effect_side: Side) -> None:
        """
        This function is called after a series of realignments has been completed.
        :param effect_side: the side which activated the effect (who's basket the effect is in)
        """
        pass

    def effect_coup_country_restrict(self, game: Game, side: Side) -> Iterable[str] | None:
        """
        Returns the countries in which a coup is not allowed if
        the effect is active.
        :param side: the side that is trying to coup.
        :return: The list of countries a coup is NOT allowed in.
        """
        pass

    def effect_coup_ops(
        self, game: Game, effect_side: Side, coup_side: Side, country_name: str
    ) -> int | None:
        """
        Returns the ops change for a coup if the effect is active.
        :param effect_side: the side which activated the effect (who's basket the effect is in)
        :param coup_side: the side that is trying to coup
        :param country_name: the country being couped
        :return: the change in ops, or None if no change
        """
        pass

    def effect_coup_roll(
        self, game: Game, effect_side: Side, coup_side: Side, country_name: str
    ) -> int | None:
        """
        Returns the die roll modifier for a coup if the effect is active.
        :param effect_side: the side which activated the effect (who's basket the effect is in)
        :param coup_side: the side that is trying to coup
        :param country_name: the country being couped
        :return: the die roll modifier, or None if no change
        """
        pass

    def effect_coup_after(
        self, game: Game, effect_side: Side, coup_side: Side, country_name: str, result: int
    ) -> CoupEffects | None:
        """
        This function is called after a coup is completed.
        :param effect_side: the side which activated the effect (who's basket the effect is in)
        :param coup_side: the side that did the coup
        :param country_name: the country being couped
        :param result: the final result of the coup, positive for success.
        :return: any effects to be applied. They will be all accumulated and
            applied at the same time as the DEFCON reduction and milops change.
            For cards like Cuban Missile Crisis that takes precedence, perform
            the change in this function rather than returning the effect.
        """
        pass
