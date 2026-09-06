from twilight_enums import Side, InputType, CardAction
from twilight_map import MapRegion, CountryInfo
from copy import deepcopy


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

        self.map = None
        self.cards = None
        self.removed_pile = []
        self.discard_pile = []
        self.basket = [[], []]

        '''
        Information that is mostly private and available only to a specific player.
        May contain other revealed public information as well.

        For instance, the draw pile can contain revealed information from Our_Man_In_Tehran.
        However, we may also want for a player to maintain probabilistic distributions over
        what the draw pile contains, based on what cards have been played.
        '''
        self.draw_pile = []
        self.hand = []
        self.opp_hand = []
        self.opp_hand_revision = 0
        self.opp_hand_observation_mode = ''
        self.opp_hand_observation_cards = []
        self.opp_hand_observation_shuffle_count = None
        self.opp_hand_known_at = {}
        self.opp_hand_excluded_at = {}

    def update(self, game, side):

        self.vp_track = game.vp_track
        self.turn_track = game.turn_track
        self.ar_track = game.ar_track
        self.ar_side = game.ar_side
        self.ars_by_turn = [list(game.ars_by_turn[Side.USSR]), list(game.ars_by_turn[Side.US])]
        self.ar_side_done = list(game.ar_side_done)
        self.defcon_track = game.defcon_track
        self.milops_track = list(game.milops_track)
        self.space_track = list(game.space_track)
        self.spaced_turns = list(game.spaced_turns)

        # Snapshot game state so mutating PlayerView cannot mutate the engine.
        self.map = deepcopy(game.map)
        self.cards = deepcopy(game.cards)
        self.removed_pile = list(game.removed_pile)
        self.discard_pile = list(game.discard_pile)
        self.basket = [list(game.basket[Side.USSR]), list(game.basket[Side.US])]

        self.hand = list(game.hand[self.side])
        if self.side == Side.USSR and 'Aldrich_Ames_Remix' in game.basket[Side.USSR]:
            visible_hand = list(game.hand[Side.US])
            if visible_hand != self.opp_hand:
                self.update_opp_hand(visible_hand)
                self.stamp_opp_hand_observation(game.shuffle_count)

    def update_opp_hand(self, opp_hand: list):
        '''Opponent's hand consists of a list of card strings for known cards.'''
        self.opp_hand = list(opp_hand)
        self.opp_hand_known_at = {card: 0 for card in opp_hand}
        self.opp_hand_excluded_at = {}
        self.opp_hand_revision += 1
        self.opp_hand_observation_mode = 'snapshot'
        self.opp_hand_observation_cards = list(opp_hand)

    def learn_opp_card(self, card_name: str):
        '''Record a card publicly transferred into the opponent's hand.'''
        if card_name not in self.opp_hand:
            self.opp_hand.append(card_name)
        self.opp_hand_known_at[card_name] = 0
        self.opp_hand_revision += 1
        self.opp_hand_observation_mode = 'add'
        self.opp_hand_observation_cards = [card_name]

    def learn_opp_cards(self, card_names: list):
        for card_name in card_names:
            if card_name not in self.opp_hand:
                self.opp_hand.append(card_name)
            self.opp_hand_known_at[card_name] = 0
        self.opp_hand_revision += 1
        self.opp_hand_observation_mode = 'add'
        self.opp_hand_observation_cards = list(card_names)

    def stamp_opp_hand_observation(self, shuffle_count: int):
        self.opp_hand_observation_shuffle_count = shuffle_count
        for card_name in self.opp_hand_observation_cards:
            self.opp_hand_known_at[card_name] = shuffle_count

    def exclude_opp_cards(self, card_names: list,
                          unknown_draw_count: int):
        for card_name in card_names:
            self.opp_hand_excluded_at[card_name] = unknown_draw_count
        self.opp_hand_revision += 1

    def update_draw_pile(self, known_cards: list):
        '''Contains additional information about the draw pile from events.'''
        self.draw_pile += known_cards
