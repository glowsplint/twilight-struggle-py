from game_mechanics import Game
from twilight_enums import Side, InputType, CardAction
from twilight_map import MapRegion, CountryInfo
from twilight_cards import CardInfo


class PlayerView:

    def __init__(self):

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
        self.extra_turn = [False, False]

        self.map = None
        self.cards = None

        # contains known information about other player's hand as well
        self.hand = [[], [], []]
        self.removed_pile = []
        self.discard_pile = []
        self.draw_pile = []  # contains known information from Our Man in Tehran, and possibily probabilistic information based on seen cards
        self.basket = [[], []]
        self.headline_bin = ['', '']
        self.end_turn_stage_list = []

    def update(self):
        pass
