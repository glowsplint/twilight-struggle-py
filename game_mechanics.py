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
                    name = self.map.index_country_mapping[int(country_index)]
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
                    name = self.map.index_country_mapping[int(country_index)]
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
                name = self.cards.index_card_mapping[int(user_choice[0])]
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
                name = self.map.index_country_mapping[int(user_choice[0])]
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
                name = self.map.index_country_mapping[int(user_choice[0])]
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
                name = self.cards.index_card_mapping[int(user_choice[0])]
                self.discard_pile.append(hand.pop(hand.index(name)))
                break
            else:
                print('\nYour input cannot be accepted.')


    def select_take_8_rounds(self):
        pass

    def quagmire_discard(self):
        '''
        Player is given a list of suitable discards. Card has to be at least 2
        effective ops.
        '''
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
    Card functions will come here. We also create a card dictionary, which ties
    every card_name to their card_function. The card functions are named with an
    underscore prefix.
    '''
    def _Asia_Scoring(self):
        pass

    def _Europe_Scoring(self):
        pass

    def _Middle_East_Scoring(self):
        pass

    def _Duck_and_Cover(self):
        pass

    def _Five_Year_Plan(self):
        pass

    def _The_China_Card(self):
        pass

    def _Socialist_Governments(self):
        pass

    def _Fidel(self):
        pass

    def _Vietnam_Revolts(self):
        pass

    def _Blockade(self):
        pass

    def _Korean_War(self):
        pass

    def _Romanian_Abdication(self):
        pass

    def _Arab_Israeli_War(self):
        pass

    def _COMECON(self):
        pass

    def _Nasser(self):
        pass

    def _Warsaw_Pact_Formed(self):
        pass

    def _De_Gaulle_Leads_France(self):
        pass

    def _Captured_Nazi_Scientist(self):
        pass

    def _Truman_Doctrine(self):
        pass

    def _Olympic_Games(self):
        pass

    def _NATO(self):
        pass

    def _Independent_Reds(self):
        pass

    def _Marshall_Plan(self):
        pass

    def _Indo_Pakistani_War(self):
        pass

    def _Containment(self):
        pass

    def _CIA_Created(self):
        pass

    def _US_Japan_Mutual_Defense_Pact(self):
        pass

    def _Suez_Crisis(self):
        pass

    def _East_European_Unrest(self):
        pass

    def _Decolonization(self):
        pass

    def _Red_Scare_Purge(self):
        pass

    def _UN_Intervention(self):
        pass

    def _De_Stalinization(self):
        pass

    def _Nuclear_Test_Ban(self):
        pass

    def _Formosan_Resolution(self):
        pass

    def _Defectors(self):
        pass

    def _The_Cambridge_Five(self):
        pass

    def _Special_Relationship(self):
        pass

    def _NORAD(self):
        pass

    def _Brush_War(self):
        pass

    def _Central_America_Scoring(self):
        pass

    def _Southeast_Asia_Scoring(self):
        pass

    def _Arms_Race(self):
        pass

    def _Cuban_Missile_Crisis(self):
        pass

    def _Nuclear_Subs(self):
        pass

    def _Quagmire(self):
        pass

    def _Salt_Negotiations(self):
        pass

    def _Bear_Trap(self):
        pass

    def _Summit(self):
        pass

    def _How_I_Learned_to_Stop_Worrying(self):
        pass

    def _Junta(self):
        pass

    def _Kitchen_Debates(self):
        pass

    def _Missile_Envy(self):
        pass

    def _We_Will_Bury_You(self):
        pass

    def _Brezhnev_Doctrine(self):
        pass

    def _Portuguese_Empire_Crumbles(self):
        pass

    def _South_African_Unrest(self):
        pass

    def _Allende(self):
        pass

    def _Willy_Brandt(self):
        pass

    def _Muslim_Revolution(self):
        pass

    def _ABM_Treaty(self):
        pass

    def _Cultural_Revolution(self):
        pass

    def _Flower_Power(self):
        pass

    def _U2_Incident(self):
        pass

    def _OPEC(self):
        pass

    def _Lone_Gunman(self):
        pass

    def _Colonial_Rear_Guards(self):
        pass

    def _Panama_Canal_Returned(self):
        pass

    def _Camp_David_Accords(self):
        pass

    def _Puppet_Governments(self):
        pass

    def _Grain_Sales_to_Soviets(self):
        pass

    def _John_Paul_II_Elected_Pope(self):
        pass

    def _Latin_American_Death_Squads(self):
        pass

    def _OAS_Founded(self):
        pass

    def _Nixon_Plays_The_China_Card(self):
        pass

    def _Sadat_Expels_Soviets(self):
        pass

    def _Shuttle_Diplomacy(self):
        pass

    def _The_Voice_Of_America(self):
        pass

    def _Liberation_Theology(self):
        pass

    def _Ussuri_River_Skirmish(self):
        pass

    def _Ask_Not_What_Your_Country_Can_Do_For_You(self):
        pass

    def _Alliance_for_Progress(self):
        pass

    def _Africa_Scoring(self):
        pass

    def _One_Small_Step(self):
        pass

    def _South_America_Scoring(self):
        pass

    def _Che(self):
        pass

    def _Our_Man_In_Tehran(self):
        pass

    def _Iranian_Hostage_Crisis(self):
        pass

    def _The_Iron_Lady(self):
        pass

    def _Reagan_Bombs_Libya(self):
        pass

    def _Star_Wars(self):
        pass

    def _North_Sea_Oil(self):
        pass

    def _The_Reformer(self):
        pass

    def _Marine_Barracks_Bombing(self):
        pass

    def _Soviets_Shoot_Down_KAL(self):
        pass

    def _Glasnost(self):
        pass

    def _Ortega_Elected_in_Nicaragua(self):
        pass

    def _Terrorism(self):
        pass

    def _Iran_Contra_Scandal(self):
        pass

    def _Chernobyl(self):
        pass

    def _Latin_American_Debt_Crisis(self):
        pass

    def _Tear_Down_This_Wall(self):
        pass

    def _An_Evil_Empire(self):
        pass

    def _Aldrich_Ames_Remix(self):
        pass

    def _Pershing_II_Deployed(self):
        pass

    def _Wargames(self):
        pass

    def _Solidarity(self):
        pass

    def _Iran_Iraq_War(self):
        pass

    def _Yuri_and_Samantha(self):
        pass

    def _AWACS_Sale_to_Saudis(self):
        pass

    card_function_mapping = {
        'Asia_Scoring': _Asia_Scoring,
        'Europe_Scoring': _Europe_Scoring,
        'Middle_East_Scoring': _Middle_East_Scoring,
        'Duck_and_Cover': _Duck_and_Cover,
        'Five_Year_Plan': _Five_Year_Plan,
        'The_China_Card': _The_China_Card,
        'Socialist_Governments': _Socialist_Governments,
        'Fidel': _Fidel,
        'Vietnam_Revolts': _Vietnam_Revolts,
        'Blockade': _Blockade,
        'Korean_War': _Korean_War,
        'Romanian_Abdication': _Romanian_Abdication,
        'Arab_Israeli_War': _Arab_Israeli_War,
        'COMECON': _COMECON,
        'Nasser': _Nasser,
        'Warsaw_Pact_Formed': _Warsaw_Pact_Formed,
        'De_Gaulle_Leads_France': _De_Gaulle_Leads_France,
        'Captured_Nazi_Scientist': _Captured_Nazi_Scientist,
        'Truman_Doctrine': _Truman_Doctrine,
        'Olympic_Games': _Olympic_Games,
        'NATO': _NATO,
        'Independent_Reds': _Independent_Reds,
        'Marshall_Plan': _Marshall_Plan,
        'Indo_Pakistani_War': _Indo_Pakistani_War,
        'Containment': _Containment,
        'CIA_Created': _CIA_Created,
        'US_Japan_Mutual_Defense_Pact': _US_Japan_Mutual_Defense_Pact,
        'Suez_Crisis': _Suez_Crisis,
        'East_European_Unrest': _East_European_Unrest,
        'Decolonization': _Decolonization,
        'Red_Scare_Purge': _Red_Scare_Purge,
        'UN_Intervention': _UN_Intervention,
        'De_Stalinization': _De_Stalinization,
        'Nuclear_Test_Ban': _Nuclear_Test_Ban,
        'Formosan_Resolution': _Formosan_Resolution,
        'Defectors': _Defectors,
        'The_Cambridge_Five': _The_Cambridge_Five,
        'Special_Relationship': _Special_Relationship,
        'NORAD': _NORAD,
        'Brush_War': _Brush_War,
        'Central_America_Scoring': _Central_America_Scoring,
        'Southeast_Asia_Scoring': _Southeast_Asia_Scoring,
        'Arms_Race': _Arms_Race,
        'Cuban_Missile_Crisis': _Cuban_Missile_Crisis,
        'Nuclear_Subs': _Nuclear_Subs,
        'Quagmire': _Quagmire,
        'Salt_Negotiations': _Salt_Negotiations,
        'Bear_Trap': _Bear_Trap,
        'Summit': _Summit,
        'How_I_Learned_to_Stop_Worrying': _How_I_Learned_to_Stop_Worrying,
        'Junta': _Junta,
        'Kitchen_Debates': _Kitchen_Debates,
        'Missile_Envy': _Missile_Envy,
        'We_Will_Bury_You': _We_Will_Bury_You,
        'Brezhnev_Doctrine': _Brezhnev_Doctrine,
        'Portuguese_Empire_Crumbles': _Portuguese_Empire_Crumbles,
        'South_African_Unrest': _South_African_Unrest,
        'Allende': _Allende,
        'Willy_Brandt': _Willy_Brandt,
        'Muslim_Revolution': _Muslim_Revolution,
        'ABM_Treaty': _ABM_Treaty,
        'Cultural_Revolution': _Cultural_Revolution,
        'Flower_Power': _Flower_Power,
        'U2_Incident': _U2_Incident,
        'OPEC': _OPEC,
        'Lone_Gunman': _Lone_Gunman,
        'Colonial_Rear_Guards': _Colonial_Rear_Guards,
        'Panama_Canal_Returned': _Panama_Canal_Returned,
        'Camp_David_Accords': _Camp_David_Accords,
        'Puppet_Governments': _Puppet_Governments,
        'Grain_Sales_to_Soviets': _Grain_Sales_to_Soviets,
        'John_Paul_II_Elected_Pope': _John_Paul_II_Elected_Pope,
        'Latin_American_Death_Squads': _Latin_American_Death_Squads,
        'OAS_Founded': _OAS_Founded,
        'Nixon_Plays_The_China_Card': _Nixon_Plays_The_China_Card,
        'Sadat_Expels_Soviets': _Sadat_Expels_Soviets,
        'Shuttle_Diplomacy': _Shuttle_Diplomacy,
        'The_Voice_Of_America': _The_Voice_Of_America,
        'Liberation_Theology': _Liberation_Theology,
        'Ussuri_River_Skirmish': _Ussuri_River_Skirmish,
        'Ask_Not_What_Your_Country_Can_Do_For_You': _Ask_Not_What_Your_Country_Can_Do_For_You,
        'Alliance_for_Progress': _Alliance_for_Progress,
        'Africa_Scoring': _Africa_Scoring,
        'One_Small_Step': _One_Small_Step,
        'South_America_Scoring': _South_America_Scoring,
        'Che': _Che,
        'Our_Man_In_Tehran': _Our_Man_In_Tehran,
        'Iranian_Hostage_Crisis': _Iranian_Hostage_Crisis,
        'The_Iron_Lady': _The_Iron_Lady,
        'Reagan_Bombs_Libya': _Reagan_Bombs_Libya,
        'Star_Wars': _Star_Wars,
        'North_Sea_Oil': _North_Sea_Oil,
        'The_Reformer': _The_Reformer,
        'Marine_Barracks_Bombing': _Marine_Barracks_Bombing,
        'Soviets_Shoot_Down_KAL': _Soviets_Shoot_Down_KAL,
        'Glasnost': _Glasnost,
        'Ortega_Elected_in_Nicaragua': _Ortega_Elected_in_Nicaragua,
        'Terrorism': _Terrorism,
        'Iran_Contra_Scandal': _Iran_Contra_Scandal,
        'Chernobyl': _Chernobyl,
        'Latin_American_Debt_Crisis': _Latin_American_Debt_Crisis,
        'Tear_Down_This_Wall': _Tear_Down_This_Wall,
        'An_Evil_Empire': _An_Evil_Empire,
        'Aldrich_Ames_Remix': _Aldrich_Ames_Remix,
        'Pershing_II_Deployed': _Pershing_II_Deployed,
        'Wargames': _Wargames,
        'Solidarity': _Solidarity,
        'Iran_Iraq_War': _Iran_Iraq_War,
        'Yuri_and_Samantha': _Yuri_and_Samantha,
        'AWACS_Sale_to_Saudis': _AWACS_Sale_to_Saudis,
    }

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
