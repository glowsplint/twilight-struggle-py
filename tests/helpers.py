"""Shared test helpers (moved out of test_cards.py so other test files can
import them without dragging in the whole card test module)."""

from twilight_enums import Side
from twilight_map import GameMap
from twilight_cards import GameCards
from game_mechanics import Game


def make_game() -> Game:
    """Create a fresh Game with standard setup, bypassing interactive stages."""
    game = Game()
    game.vp_track = 0
    game.turn_track = 1
    game.ar_track = 1
    game.ar_side = Side.USSR
    game.ars_by_turn = [list(Game.Default.ARS_BY_TURN),
                        list(Game.Default.ARS_BY_TURN)]
    game.ar_side_done = [False, False]
    game.defcon_track = 5
    game.milops_track = [0, 0]
    game.space_track = [0, 0]
    game.spaced_turns = [0, 0]
    game.map = GameMap()
    game.cards = GameCards()
    game.players = [None, None]  # not needed for card tests
    game.handicap = 0
    game.stage_list = []
    game.hand = [[], [], []]
    game.removed_pile = []
    game.discard_pile = []
    game.draw_pile = []
    game.limbo = []
    game.basket = [[], []]
    game.headline_bin = ['', '']
    game.end_turn_stage_list = []
    game.map.build_standard()
    return game
