import numpy as np

from typing import Sequence, Iterable
from enums import Side, InputType, CardAction
from world_map import MapRegion, CountryInfo, GameMap
from cards import Card, GameCards


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
        self.draw_pile = DrawPile()
        self.hand = Hand(self.side)
        self.opp_hand = OppHand(self.side.opp)
        self.opp_headline = OppHeadline()  # contains only opposite headline

    def create_links(self, game):
        '''Passes a view of the game attributes to the PlayerView instance.'''
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

        self.cards = Cards(game.cards)
        self.removed_pile = game.removed_pile
        self.discard_pile = game.discard_pile
        self.basket = game.basket

        self.hand._link = game.hand[self.side]


class DrawPile:
    def __init__(self):
        self.info = set()

    def update(self, known_cards: Iterable[str]):
        '''Contains additional information about the draw pile.'''
        self.info.update(known_cards)

    def remove(self, removed_cards: Iterable[str]):
        '''Removes <removed_cards> from known information about the draw pile.'''
        self.info.difference_update(removed_cards)

    def reset(self):
        '''Reverting to no additional information about the contents of the draw pile.'''
        self.info = set()


class OppHeadline:
    def __init__(self):
        self.info = None

    def update(self, opp_headline):
        '''Adds headline information to other player. Used as during the space race buff.'''
        self.info = opp_headline

    def reset(self):
        self.info = None


class Hand:
    def __init__(self, side: Side):
        '''
        Contains the information about a given player's hand.
        Information on the player's own hand will be fully known, but may not be true for opponent's hand.

        Parameters
        ----------
        side : Side
            Side of the hand.
            self.side if own hand, self.side.opp if opponent's hand.

        Attributes / Properties
        ----------
        info : dict
            Dictionary with (card_index, card_name) as (k,v) pairs
        _link : List[str]
            List of card_names
        '''
        self.side = side
        self.no_scoring_cards = False
        self._link = set()

    @property
    def info(self):
        return {Card.ALL[c].card_index: c for c in self._link}


class OppHand(Hand):

    def __init__(self, side: Side):
        super().__init__(side)

    def update(self, new_known_cards: Iterable[str]):
        '''Adds <opp_hand> to known information about the other player's cards.'''
        print(f'{self.side.toStr} player reveals: {new_known_cards}')
        self._link.update(new_known_cards)

    def remove(self, removed_cards: Iterable[str]):
        '''Removes <removed_cards> from known information about the other player's cards.'''
        self._link.difference_update(removed_cards)

    def infer(self, player_view: PlayerView):
        '''Infers the other player's cards based on our own and the exhaustion of the draw pile.'''
        new_known_cards = set(player_view.cards.in_play) - set(player_view.discard_pile) - \
            set(player_view.removed_pile) - set(self.info.items())
        print('By draw pile exhaustion inference..')
        self.update(new_known_cards)


class Map:
    def __init__(self, game_map: GameMap):
        self.info = game_map

    def to_array(self):
        pass
        # for country_name in self.info.ALL.keys():
        #     self.info[country_name].control
        #     self.info[country_name].influence[Side.US]
        #     self.info[country_name].influence[Side.USSR]
        #     self.info[country_name].info.battleground
        #     self.info[country_name].info.stability
        #     self.info[country_name].control
        #     self.info.us_playable
        #     self.info.ussr_playable


class Cards:
    def __init__(self, GameCards: GameCards):
        pass

    def to_array(self):
        pass
