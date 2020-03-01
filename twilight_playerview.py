from typing import Sequence, Iterable
from twilight_enums import Side, InputType, CardAction
from twilight_map import MapRegion, CountryInfo


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
        self.draw_pile = set()
        self.hand = set()
        self.opp_hand = set()
        self.opp_headline = None  # contains only opposite headline

    def update(self, game):

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

        self.map = game.map
        self.cards = game.cards
        self.removed_pile = game.removed_pile
        self.discard_pile = game.discard_pile
        self.basket = game.basket

        self.hand = game.hand[self.side]

    def update_opp_hand(self, new_known_cards: Iterable[str]):
        '''Adds <opp_hand> to a set of already known information about the other player's cards.'''
        print(f'{self.side.opp.toStr} player reveals: {new_known_cards}')
        self.opp_hand.update(new_known_cards)

    def remove_opp_hand(self, removed_cards: Iterable[str]):
        '''Removes <removed_cards> from known information about the other player's cards.'''
        self.opp_hand.difference_update(removed_cards)

    def update_headline(self, opp_headline):
        self.opp_headline = opp_headline

    def update_draw_pile(self, known_cards: Iterable[str]):
        '''Contains additional information about the draw pile.'''
        self.draw_pile.update(known_cards)

    def remove_draw_pile(self, removed_cards: Iterable[str]):
        '''Removes <removed_cards> from known information about the draw pile.'''
        self.draw_pile.difference_update(removed_cards)

    def reset_draw_pile(self):
        '''Reverting to no additional information about the contents of the draw pile.'''
        self.draw_pile = set()
