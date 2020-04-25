import numpy as np

from typing import Sequence, Iterable
from enums import Side, InputType, CardAction
from world_map import MapRegion, CountryInfo, GameMap
from cards import Card, GameCards
from interfacing import Output


class PlayerView:

    def __init__(self, side: Side):

        self.side = side

        '''
        Public information that is shared by both players.
        '''
        self.vp_track = 0
        self.turn_track = 0
        self.ar_track = 0
        self.ar_side = None
        self.ars_by_turn = ([], [])
        self.ar_side_done = [False, False]
        self.defcon_track = 0
        self.milops_track = [0, 0]
        self.space_track = [0, 0]
        self.spaced_turns = [0, 0]
        self.handicap = None

        self.player_view = None
        self.map = None
        self.removed_pile = []
        self.discard_pile = []
        self.basket = [[], []]

        '''
        Information that is mostly private and available only to a specific player.
        May contain other revealed public information as well.

        For instance, the draw pile can contain revealed information from Our_Man_In_Tehran.
        '''
        self.draw_pile = set()
        self.hand = set()
        self.opp_hand = set()
        self.opp_hand_no_scoring_cards = False
        self.opp_headline = []

    # might have to run this every game loop
    def link(self, game):
        '''Passes game attributes to the PlayerView instance.'''
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
    def json(self):
        return {
            'vp_track': self.vp_track,
            'turn_track': self.turn_track,
            'ar_track': self.ar_track,
            'ar_side': self.ar_side,
            'ars_by_turn': self.ars_by_turn,
            'ar_side_done': self.ar_side_done,
            'defcon_track': self.defcon_track,
            'milops_track': self.milops_track,
            'space_track': self.space_track,
            'spaced_turns': self.spaced_turns,
            'handicap': self.handicap,

            'map': self.map.json,
            'removed_pile': self.removed_pile,
            'discard_pile': self.discard_pile,
            'basket': self.basket,
            'hand': self.hand,
            'opp_hand_scoring': self.opp_hand_no_scoring_cards,
        }


class Map:
    def __init__(self, game_map: GameMap):
        self.info = game_map

    @property
    def json(self):
        return {
            country_name: {
                'control': self.info[country_name].control,
                'us_influence': self.info[country_name].influence[Side.US],
                'ussr_influence': self.info[country_name].influence[Side.USSR],
                'battleground': self.info[country_name].info.battleground,
                'stability': self.info[country_name].info.stability,
                # 'us_playable': self.info.us_playable,
                # 'ussr_playable': self.info.ussr_playable,
            } for country_name in self.info.ALL.keys()
        }
