from __future__ import annotations

from typing import TYPE_CHECKING

from enums import Side
from world_map import GameMap

if TYPE_CHECKING:
    from game_mechanics import Game


class PlayerView:
    def __init__(self, side: Side) -> None:

        self.side: Side = side

        """
        Public information that is shared by both players.
        """
        self.vp_track: int = 0
        self.turn_track: int = 0
        self.ar_track: int = 0
        self.ar_side: Side | None = None
        self.ars_by_turn: tuple[list[int], list[int]] = ([], [])
        self.ar_side_done: list[bool] = [False, False]
        self.defcon_track: int = 0
        self.milops_track: list[int] = [0, 0]
        self.space_track: list[int] = [0, 0]
        self.spaced_turns: list[int] = [0, 0]
        self.handicap: int | None = None

        self.player_view: PlayerView | None = None
        self.map: Map | None = None
        self.removed_pile: list[str] = []
        self.discard_pile: list[str] = []
        self.basket: list[list[str]] = [[], []]

        """
        Information that is mostly private and available only to a specific player.
        May contain other revealed public information as well.

        For instance, the draw pile can contain revealed information from Our_Man_In_Tehran.
        """
        self.draw_pile: set[str] = set()
        self.hand: set[str] | list[str] = set()
        self.opp_hand: set[str] = set()
        self.opp_hand_no_scoring_cards: bool = False
        self.opp_headline: list[str] = []

    # might have to run this every game loop
    def link(self, game: Game) -> None:
        """Passes game attributes to the PlayerView instance."""
        self.vp_track = game.vp_track
        self.turn_track = game.turn_track
        self.ar_track = game.ar_track
        self.ar_side = game.ar_side
        self.ars_by_turn = game.ars_by_turn
        self.ar_side_done = game.ar_side_done
        self.defcon_track = game.defcon_track
        self.milops_track = game.milops_track
        self.space_track = game.space_track
        self.spaced_turns = game.spaced_turns
        self.handicap = game.handicap
        self.map = Map(game.map)

        self.removed_pile = game.removed_pile
        self.discard_pile = game.discard_pile
        self.basket = game.basket

        self.hand = game.hand[self.side]

    @property
    def json(self) -> dict[str, object]:
        return {
            "vp_track": self.vp_track,
            "turn_track": self.turn_track,
            "ar_track": self.ar_track,
            "ar_side": self.ar_side,
            "ars_by_turn": self.ars_by_turn,
            "ar_side_done": self.ar_side_done,
            "defcon_track": self.defcon_track,
            "milops_track": self.milops_track,
            "space_track": self.space_track,
            "spaced_turns": self.spaced_turns,
            "handicap": self.handicap,
            "map": self.map.json,
            "removed_pile": self.removed_pile,
            "discard_pile": self.discard_pile,
            "basket": self.basket,
            "hand": list(self.hand) if isinstance(self.hand, set) else self.hand,
            "opp_hand_scoring": self.opp_hand_no_scoring_cards,
            "opp_hand": list(self.opp_hand) if isinstance(self.opp_hand, set) else self.opp_hand,
        }


class Map:
    def __init__(self, game_map: GameMap) -> None:
        self.info: GameMap = game_map

    @property
    def json(self) -> dict[str, dict[str, object]]:
        return {
            country_name: {
                "control": self.info[country_name].control,
                "us_influence": self.info[country_name].influence[Side.US],
                "ussr_influence": self.info[country_name].influence[Side.USSR],
                "battleground": self.info[country_name].info.battleground,
                "stability": self.info[country_name].info.stability,
                # 'us_playable': self.info.us_playable,
                # 'ussr_playable': self.info.ussr_playable,
            }
            for country_name in self.info.ALL.keys()
        }
