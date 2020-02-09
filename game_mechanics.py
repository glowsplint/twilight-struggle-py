import math
import random
import numpy as np

from twilight_enums import *
from twilight_map import *
from twilight_cards import GameCards
from twilight_ui import *

class Game:

    # this is the currently active game. One may refer to this as
    # Game.main. The point is to have a globally accessible game
    # object for the active game, but still allow for other game
    # objects to deal with hypothetical future/past game states
    # which would be useful for non-committed actions and possibly
    # the AI depending on how you do it.
    main = None

    '''VP, AR, Milops, Space tracks'''
    def __init__(self):
        self.handicap = -2 # positive in favour of ussr
        self.vp_track = 0 # positive for ussr
        self.turn_track = 1
        self.ar_track = 1 # increment by 1 for each side's action round
        self.defcon_track = 5
        self.milops_track = np.array([0, 0]) # ussr first
        self.space_track = np.array([0, 0]) # 0 is start, 1 is earth satellite etc
        self.has_spaced = [False, False]

        self.realignment_modifier = np.array([0, 0]) # ussr first
        self.coup_modifier = np.array([0, 0]) # ussr first

        self.map = GameMap()
        self.cards = GameCards()
        self.ui = UI(self)

        self.us_hand = []
        self.ussr_hand = []
        self.removed_pile = []
        self.discard_pile = []
        self.draw_pile = []

        self.us_basket = []
        self.ussr_basket = []

        self.stage_list = [self.map.build_standard, self.deal, self.put_start_USSR, self.put_start_US, self.put_start_extra, self.joint_choose_headline, self.resolve_headline]

        self.ar6 = [self.select_card_and_action for i in range(6)]
        self.ar6.append(self.end_of_turn)
        self.ar7 = [self.select_card_and_action for i in range(7)]
        self.ar7.append(self.end_of_turn)
        self.stage_list.extend([*self.ar6*3, *self.ar7*4])
        self.stage_list.reverse()

        # For new set the first created game to be the actual ongoing game.
        if Game.main is None: Game.main = self

    '''
    self.current returns current game stage.
    self.stage_list returns the full list of stages. The list starts with the
    last possible event, and ends with the current event. We pop items off the
    list when they are resolved.
    '''
    # 6 AR in t1-t3, 7 AR in t4-t10

    @property
    def current(self):
        return self.stage_list[-1]


    '''
    Here, we define a few utility functions used frequently in the code below.
    prompt_side serves to print the headers ----- USSR/US turn -----.
    '''
    @staticmethod
    def prompt_side(side: Side):
        print()
        if side == Side.USSR:
            print(UI.ussr_prompt)
        elif side == Side.US:
            print(UI.us_prompt)
        else:
            raise ValueError('Side argument invalid.')


    '''
    card_operation_add_influence is the generic stage where a side is given the opportunity to place influence.
    They are provided a list of all possible countries that they can place influence into, and
    must choose from these. During this stage, the UI is waiting for a tuple of country indices.

    This is the actual use of operations to place influence.
    '''
    def card_operation_add_influence(self, side: Side, effective_ops: int):

        '''Generates the list of all possible countries that influence can be placed in.'''

        filter = np.array([self.map.can_place_influence(name, side, effective_ops) for name in self.map.ALL])
        all_countries = np.array([name for name in self.map.ALL])
        available_list = all_countries[filter]
        available_list_values = [str(self.map[n].info.country_index) for n in available_list]
        guide_msg = f'You may modify {effective_ops} influence in these countries. Type in their country indices, separated by commas (no spaces).'
        rejection_msg = f'Please key in {effective_ops} comma-separated values.'

        while True:
            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(f'{self.map[available_name].info.name}, {self.map[available_name].info.country_index}')

            user_choice = UI.ask_for_input(effective_ops, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                for country_index in user_choice:
                    name = self.map.index_country_map[int(country_index)]
                    self.map.place_influence(name, side, 1)
                break
            else:
                print('\nYour input cannot be accepted.')




    '''
    event_influence is the generic stage where a side is given the opportunity to modify influence.
    Unlike card_operation_add_influence, this is mostly used for card events where the player has to choose
    which regions in which to directly insert influence.

    Examples of cards that use this function are: VOA, Decolonization, OAS_Founded, Junta.
    See put_start_USSR below for an example of how to use this function.
    available_list is the list of names that can be manipulated by the effect.
    '''
    def event_influence(self, side: Side, effective_ops: int, available_list: list, can_split: bool, positive: bool):

        available_list_values = [str(self.map[n].info.country_index) for n in available_list]
        guide_msg = f'You may modify {effective_ops} influence in these countries. Type in their country indices, separated by commas (no spaces).'
        rejection_msg = f'Please key in {effective_ops} comma-separated values.'

        while True:
            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(f'{self.map[available_name].info.name}, {self.map[available_name].info.country_index}')

            user_choice = UI.ask_for_input(effective_ops, rejection_msg)
            if user_choice == None:
                break

            if can_split:
                additional_input_check = True
            else:
                additional_input_check = (len(set(user_choice)) == 1)

            if len(set(user_choice) - set(available_list_values)) == 0 and additional_input_check:
                for country_index in user_choice:
                    name = self.map.index_country_map[int(country_index)]
                    if side == Side.USSR:
                        if positive:
                            self.map.change_influence(name, 0, 1)
                        else:
                            self.map.change_influence(name, -1, 0)
                    elif side == Side.US:
                        if positive:
                            self.map.change_influence(name, 1, 0)
                        else:
                            self.map.change_influence(name, 0, -1)
                break
            else:
                print('\nYour input cannot be accepted.')



    def put_start_USSR(self):
        available_list = [n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]]
        self.event_influence(Side.USSR, 6, available_list, can_split=True, positive=True)

    def put_start_US(self):
        available_list = [n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]]
        self.event_influence(Side.US, 7, available_list, can_split=True, positive=True)

    def put_start_extra(self):
        if self.handicap < 0:
            available_list = [*self.map.has_us_influence()]
            self.event_influence(Side.US, -self.handicap, available_list, can_split=True, positive=True)
        elif self.handicap > 0:
            available_list = [*self.map.has_ussr_influence()]
            self.event_influence(Side.USSR, self.handicap, available_list, can_split=True, positive=True)

    def joint_choose_headline(self):
        '''
        Both players are to simultaneously choose their headline card.
        USSR chooses first, then US, then display to both players the other's
        choice.
        '''
        pass

    def choose_headline(self, side: Side):
        if side == Side.USSR:
            hand = self.ussr_hand
        elif side == Side.US:
            hand = self.us_hand

        guide_msg = f'You may headline any of these cards. Type in the card index.'
        rejection_msg = f'Please key in a single value.'

        while True:
            filter = np.array([card.info.can_headline for card in hand])
            cards_in_hand = np.array([card.info.name for card in hand])
            available_list = cards_in_hand[filter]
            available_list_values = [str(self.cards[n].info.card_index) for n in available_list]

            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(f'{self.cards[available_name].info.name}, {self.cards[available_name].info.card_index}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                name = self.cards.index_card_map[int(user_choice[0])]
                hand[hand.index(name)].event()
                hand.pop(hand.index(name))
                break
            else:
                print('\nYour input cannot be accepted.')



    def resolve_headline(self):
        pass

    def select_card_and_action(self):
        '''
        This function should lead to card_operation_realignment, card_operation_coup,
        or card_operation_influence, or a space race function.
        '''
        self.ar_track += 1
        pass

    def forced_to_missile_envy(self):
        pass

    def trigger_event(self):
        pass

    def card_event(self):
        # can only be used if the event is yours
        pass

    def card_operation_realignment(self, side: Side, effective_ops: int):
        '''
        Generates the list of all possible countries that can be realigned.
        Adjusts for DEFCON status only.
        TODO: Does not currently check the player baskets for continuous effects.
        '''
        current_effective_ops = effective_ops
        guide_msg = f'You may attempt realignment in these countries. Type in the target country index.'
        rejection_msg = f'Please key in a single value.'

        while current_effective_ops > 0:
            filter = np.array([self.map.can_realignment(name, side, self.defcon_track) for name in self.map.ALL])
            all_countries = np.array([name for name in self.map.ALL])
            available_list = all_countries[filter]
            available_list_values = [str(self.map[n].info.country_index) for n in available_list]

            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(f'{self.map[available_name].info.name}, {self.map[available_name].info.country_index}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                name = self.map.index_country_map[int(user_choice[0])]
                self.map.realignment(name, side, self.defcon_track)
                current_effective_ops -= 1
            else:
                print('\nYour input cannot be accepted.')



    def card_operation_coup(self, side: Side, effective_ops: int):
        '''
        Generates the list of all possible countries that can be couped.
        Adjusts for DEFCON status only.
        TODO: Does not currently check the player baskets for continuous effects.
        '''
        filter = np.array([self.map.can_coup(name, side, self.defcon_track) for name in self.map.ALL])
        all_countries = np.array([name for name in self.map.ALL])
        available_list = all_countries[filter]

        available_list_values = [str(self.map[n].info.country_index) for n in available_list]
        guide_msg = f'You may coup these countries. Type in the country index.'
        rejection_msg = f'Please key in a single value.'

        while True:
            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(f'{self.map[available_name].info.name}, {self.map[available_name].info.country_index}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                name = self.map.index_country_map[int(user_choice[0])]
                self.map.coup(name, side, effective_ops, self.defcon_track)
                break
            else:
                print('\nYour input cannot be accepted.')


    '''
    The player is given here an option to discard a card at the end of the turn.
    This effect is a buff from the space race.
    '''
    def discard_held_card(self):
        if side == Side.USSR:
            hand = self.ussr_hand
        elif side == Side.US:
            hand = self.us_hand

        guide_msg = f'You may discard a card. Type in the card index.'
        rejection_msg = f'Please key in a single value.'

        while True:
            available_list = hand
            available_list_values = [str(self.cards[n].info.card_index) for n in available_list]

            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(f'{self.cards[available_name].info.name}, {self.cards[available_name].info.card_index}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                name = self.cards.index_card_map[int(user_choice[0])]
                self.discard_pile.append(hand.pop(hand.index(name)))
                break
            else:
                print('\nYour input cannot be accepted.')


    def select_take_8_rounds(self):
        pass

    def quagmire_discard(self):
        pass

    def quagmire_play_scoring_card(self):
        pass

    def norad_influence(self):
        pass

    def cuba_missile_remove(self):
        pass







    # to add game terminate functionality EndGame()

    def change_vp(self, n: int): # positive for ussr
        self.vp_track += n
        if self.vp_track >= 20:
            print('USSR victory')
            # EndGame()
        if self.vp_track <= -20:
            print('US victory')
            # EndGame()

    def change_defcon(self, n: int):
        self.defcon_track += min(n, 5 - self.defcon_track)
        if self.defcon_track < 2:
            print('Game ended by thermonuclear war')
            # EndGame()

    # SPACE (function)
    def space(self, side: Side):
        x = Side.fromStr(side)

        # this one could be something game specific later
        space_track = self.space_track

        if space_track[x] in [0,2,4,6]:
            modifier = 0
        elif space_track[x] in [1,3,5]:
            modifier = -1
        else:
            modifier = 1

        y = x.vp_mult # multiplier for VP - gives 1 for USSR and -1 for US
        roll = random.randint(1,6)
        if roll + modifier <= 3:
            space_track[x] += 1
            print(f'Success with roll of {roll}.')

            if space_track[x] == 1:
                if space_track[x.opp] < 1:
                    self.change_vp(2*y)
                else:
                    self.change_vp(y)

            elif space_track[x] == 3:
                if space_track[x.opp] < 3:
                    self.change_vp(2*y)

            elif space_track[x] == 5:
                if space_track[x.opp] < 5:
                    self.change_vp(3*y)
                else:
                    self.change_vp(y)

            elif space_track[x] == 7:
                if space_track[x.opp] < 7:
                    self.change_vp(4*y)
                else:
                    self.change_vp(2*y)

            elif space_track[x] == 8:
                if space_track[x.opp] < 8:
                    self.change_vp(2*y)

        else:
            print(f'Failure with roll of {roll}.')

    def deal(self):
        def top_up_cards(self, n: int):
            ussr_held = len(self.ussr_hand)
            us_held = len(self.us_hand)

            if 'The_China_Card' in self.ussr_hand: # Ignore China Card if it is in either hand
                ussr_held = len(self.ussr_hand) - 1
            elif 'The_China_Card' in self.ussr_hand:
                us_held = len(self.us_hand) - 1

            # if turn 4, add mid war cards into draw pile and shuffle, same for turn 8 for late war cards
            if self.turn_track == 4:
                self.draw_pile.extend(self.cards.mid_war)
                self.cards.mid_war = []
                random.shuffle(self.draw_pile)
            if self.turn_track == 8:
                self.draw_pile.extend(self.cards.late_war)
                self.cards.late_war = []
                random.shuffle(self.draw_pile)

            # exhaust the draw pile
            while ussr_held < n or us_held < n:
                # if draw pile exhausted, shuffle the discard pile and put it as the new draw pile
                def recreate_draw_pile():
                    if self.draw_pile == []:
                        self.draw_pile = self.discard_pile
                        self.discard_pile = []
                        random.shuffle(self.draw_pile)
                if ussr_held < n:
                    self.ussr_hand.extend([self.draw_pile.pop()])
                    ussr_held += 1
                    recreate_draw_pile()
                if us_held < n:
                    self.us_hand.extend([self.draw_pile.pop()])
                    us_held += 1
                    recreate_draw_pile()

        '''Pre-headline setup'''
        if self.turn_track == 1 and self.ar_track == 1:
            # Move the China card from the early war pile to USSR hand, China card 6th from last
            self.ussr_hand.append(self.cards.early_war.pop(self.cards.early_war.index('The_China_Card')))
            # self.ussr_hand.append(self.cards.early_war.pop(self.cards.early_war.index('The_China_Card')))
            self.ussr_hand.append(self.cards.early_war.pop(self.cards.early_war.index('Asia_Scoring'))) # for testing of specific cards
            self.draw_pile.extend(self.cards.early_war) # Put early war cards into the draw pile
            self.cards.early_war = []
            random.shuffle(self.draw_pile) # Shuffle the draw pile
            top_up_cards(self, 8)
        else:
            if self.turn_track in [1,2,3]:
                top_up_cards(self, 8)
            else:
                top_up_cards(self, 9)
        return

    # need to make sure next_turn is only called after all extra rounds
    def end_of_turn(self):
        # played at the end of last US action round within turn
        # 1. Check milops
        def check_milops(self):
            milops_diff = self.milops_track - self.defcon_track
            milops_vp_change = np.where(milops_diff < 0, milops_diff, 0)
            swing = milops_vp_change[0] - milops_vp_change[1]
            self.change_vp(swing)

        # 2. Check for held scoring card
        def check_for_scoring_cards(self):
            scoring_list = ['Asia_Scoring', 'Europe_Scoring', 'Middle_East_Scoring', 'Central_America_Scoring', 'Southeast_Asia_Scoring', 'Africa_Scoring', 'South_America_Scoring']
            scoring_cards = [self.cards[y] for y in scoring_list]
            if any(True for x in scoring_cards if x in self.us_hand):
                print('USSR Victory!')
                # EndGame()
            elif any(True for x in scoring_cards if x in self.ussr_hand):
                print('US Victory!')
                # EndGame()

        # 3. Flip China Card
        def flip_china_card(self):
            if 'The_China_Card' in self.ussr_hand:
                self.ussr_hand[self.ussr_hand.index('The_China_Card')].can_play = True
            elif 'The_China_Card' in self.us_hand:
                self.us_hand[self.us_hand.index('The_China_Card')].can_play = True

        # 4. Advance turn marker
        def advance_turn_marker(self):
            self.turn_track += 1
            self.ar_track = 1

        # 5. Final scoring (end T10)
        def final_scoring(self):
            if self.turn_track == 10 and (self.ar_track in [15,16,17]):
                ScoreAsia()
                ScoreEurope()
                ScoreMiddleEast()
                ScoreCentralAmerica()
                ScoreAfrica()
                ScoreSouthAmerica()
            print(f'Final scoring complete.')
            # EndGame()

        # 6. Increase DEFCON status
        # 7. Deal Cards -- written outside the next_turn function
        # 8. Headline Phase
        def headline(self):
            pass

        # 9. Action Rounds (advance round marker) -- action rounds are not considered between turns

        check_milops(self)
        check_for_scoring_cards(self)
        flip_china_card(self)
        advance_turn_marker(self) #turn marker advanced before final scoring
        final_scoring(self)
        self.change_defcon(1)
        self.deal() # turn marker advanced before dealing
        headline(self)

    def score(self, region: MapRegion, presence_vps: int, domination_vps: int, control_vps: int):
        bg_count = [0, 0, 0]  # USSR, US, NEUTRAL
        country_count = [0, 0, 0]
        vps = [0, 0]

        for n in CountryInfo.REGION_ALL[region]:
            x = self.map[n]
            if x.info.battleground:
                bg_count[x.control] += 1
            country_count[x.control] += 1
            if x.control.opp.name in x.info.adjacent_countries:
                vps[x.control] += 1

        for s in [Side.USSR, Side.US]:
            vps[s] += bg_count[s]
            if country_count[s] > country_count[s.opp]:
                if bg_count[s] == sum(bg_count):
                    vps[s] += control_vps
                elif bg_count[s] > bg_count[s.opp] and country_count[s] > bg_count[s]:
                    vps[s] += domination_vps
            elif country_count[s] > 0:
                vps[s] += presence_vps

        swing = vps[Side.USSR] - vps[Side.US]
        self.change_vp(swing)
        print(f'{region.name} scores for {swing} VP')

    '''
    Card functions will come here. Here we create a card dictionary, which ties
    every card_name to their card_function. The card functions are named with an
    underscore prefix.
    '''




'''Utility functions'''
def RemoveAllOpponentInfluenceInCuba(_):
    Cuba.set_influence(0, max(3, Cuba.ussr_influence))

def RemoveAllOpponentInfluenceInRomania(_):
    Romania.set_influence(0, max(3, Romania.ussr_influence))

def GainInfluenceInEgypt(_):
    Egypt.adjust_influence(-math.ceil(Egypt.us_influence/2), 2)

def RemoveOpponentInfluenceInFrance(_):
    France.adjust_influence(-2, 1)

def GainInfluenceForControlInJapan(_):
    Japan.set_influence(Japan.ussr_influence + 4, Japan.ussr_influence)


'''Scoring Mechanics'''
# TO ADD SHUTTLE DIPLOMACY AND FORMOSAN RESOLUTION
def ScoreAsia(game):
    score(MapRegion.ASIA, 3, 7, 9)

def ScoreEurope():
    score(MapRegion.EUROPE, 3, 7, 120)

# TO ADD SHUTTLE DIPLOMACY
def ScoreMiddleEast():
    score(MapRegion.MIDDLE_EAST, 3, 5, 7)

def ScoreCentralAmerica():
    score(MapRegion.CENTRAL_AMERICA, 1, 3, 5)

def ScoreAfrica():
    score(MapRegion.AFRICA, 1, 4, 6)

def ScoreSouthAmerica():
    score(MapRegion.SOUTH_AMERICA, 2, 5, 6)

def ScoreSoutheastAsia():
    country_count = [0,0]
    for n in CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]:
        x = Game.main.map[n]
        country_count[Side.USSR] += (x.control == Side.USSR)
        country_count[Side.US] += (x.control == Side.US)
    swing = country_count[Side.USSR] - country_count[Side.US]

    # thailand double VP
    if Game.main.map['Thailand'].control == Side.USSR:
        swing += 1
    if Game.main.map['Thailand'].control == Side.US:
        swing -= 1

    Game.main.change_vp(swing)
    print(f'Southeast Asia scores for {swing} VP')
