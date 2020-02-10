import math
import random
import numpy as np

from twilight_enums import *
from twilight_map import *
from twilight_cards import *
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
        self.spaced_turns = np.array([0, 0])
        self.extra_turn = [False, False]

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
        self.headline_bin = []

        self.stage_list = [self.map.build_standard, self.deal, self.put_start_USSR, self.put_start_US, self.put_start_extra, self.joint_choose_headline]
        self.ar6 = [self.select_card_and_action for i in range(12)]
        self.ar6.append(self.end_of_turn)
        self.ar7 = [self.select_card_and_action for i in range(14)]
        self.ar7.append(self.end_of_turn)
        self.stage_list.extend([*self.ar6*3, *self.ar7*4])
        self.stage_list.reverse()

        # For new set the first created game to be the actual ongoing game.
        if Game.main is None: Game.main = self

        '''Use only for testing, comment out otherwise.'''
        # self.us_basket.append(self.cards.early_war.pop(self.cards.early_war.index('Warsaw_Pact_Formed')))
        # self.us_basket.append(self.cards.early_war.pop(self.cards.early_war.index('Marshall_Plan')))

    '''
    self.current returns current game stage.
    self.stage_list returns the full list of stages. The list starts with the
    last possible event, and ends with the current event. We pop items off the
    list when they are resolved.
    '''
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
    def card_operation_influence(self, side: Side, card: Card, hand):

        effective_ops = card.info.ops

        '''Generates the list of all possible countries that influence can be placed in.'''
        filter = np.array([self.map.can_place_influence(name, side, effective_ops) for name in self.map.ALL])
        all_countries = np.array([name for name in self.map.ALL])
        available_list = all_countries[filter]
        available_list_values = [str(self.map[n].info.country_index) for n in available_list]
        guide_msg = f'You may add {effective_ops} influence in these countries. Type in their country indices, separated by commas (no spaces).'
        rejection_msg = f'Please key in {effective_ops} comma-separated values.'

        while True:
            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(f'{self.map[available_name].info.country_index}\t{self.map[available_name].info.name}')

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

        if side == card.info.owner:
            self.discard_pile(hand.pop(card))
        elif side == card.info.owner.opp:
            card_treatment = self.trigger_event(card.info.name)
            if card_treatment == 'discard':
                self.discard_pile.append(hand.pop(hand.index(card)))
            elif card_treatment == 'remove':
                self.removed_pile.append(hand.pop(hand.index(card)))
            elif card_treatment == 'us_basket':
                self.us_basket.append(hand.pop(hand.index(card)))
            elif card_treatment == 'ussr_basket':
                self.ussr_basket.append(hand.pop(hand.index(card)))


    '''
    event_influence is the generic stage where a side is given the opportunity to modify influence.
    Unlike card_operation_add_influence, this is mostly used for card events where the player has to choose
    which regions in which to directly insert influence.

    Examples of cards that use this function are: VOA, Decolonization, OAS_Founded, Junta.
    See put_start_USSR below for an example of how to use this function.
    available_list is the list of names that can be manipulated by the effect.
    can_split is True for cards where the influence adjustment can be split like VOA. False for cards like Junta.
    limit is the maximum influence adjustment that can be made to a single country. 2 for VOA, 1 for COMECON.
    positive is True for positive adjustments like Decolonization, False for VOA.
    '''
    def event_influence(self, side: Side, effective_ops: int, available_list: list, can_split: bool, positive: bool, limit: int=None):

        available_list_values = [str(self.map[n].info.country_index) for n in available_list]
        guide_msg = f'You may modify {effective_ops} influence in these countries. Type in their country indices, separated by commas (no spaces).'
        rejection_msg = f'Please key in {effective_ops} comma-separated values.'

        while True:
            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(f'{self.map[available_name].info.country_index}\t{self.map[available_name].info.name}')

            user_choice = UI.ask_for_input(effective_ops, rejection_msg)
            if user_choice == None:
                break

            is_input_all_available = (len(set(user_choice) - set(available_list_values)) == 0)
            is_input_singular = True if can_split else (len(set(user_choice)) == 1)
            is_input_limited = True if limit == None else max(user_choice.count(x) for x in set(user_choice)) > limit

            if is_input_all_available and is_input_singular and is_input_limited:
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
        self.choose_headline(Side.USSR)
        self.choose_headline(Side.US)
        self.resolve_headline(type = Side.NEUTRAL)


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
                print(f'{self.cards[available_name].info.card_index}\t{self.cards[available_name].info.name}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                name = self.cards.index_card_mapping[int(user_choice[0])]
                self.headline_bin.append(hand.pop(hand.index(name)))
                break
            else:
                print('\nYour input cannot be accepted.')


    def resolve_headline(self, type:Side = Side.NEUTRAL):

        def trigger(self, side: Side):
            player = 'US' if side == Side.US else 'USSR'
            print(f'\n{player} selected {self.headline_bin[side].info.name} for headline.')
            card_treatment = self.trigger_event(self.headline_bin[side].info.name)
            if card_treatment == 'discard':
                self.discard_pile.append(self.headline_bin.pop(side))
            elif card_treatment == 'remove':
                self.removed_pile.append(self.headline_bin.pop(side))
            elif card_treatment == 'us_basket':
                self.us_basket.append(self.headline_bin.pop(side))
            elif card_treatment == 'ussr_basket':
                self.ussr_basket.append(self.headline_bin.pop(side))

        if type == Side.NEUTRAL:
            '''
            Side.NEUTRAL : Joint resolution of headline
            Side.US : Resolve US headline, then USSR headline
            Side.USSR : Resolve USSR headline, then US headline
            '''
            if self.headline_bin[1] == 'Defectors':
                return 'Defectors cancellation of headline phase.'
            if self.headline_bin[0].info.ops > self.headline_bin[1].info.ops:
                trigger(self, Side.USSR)
                trigger(self, Side.US)
            else:
                trigger(self, Side.US)
                trigger(self, Side.USSR)

        elif type == Side.US:
            trigger(self, Side.US)
            trigger(self, Side.USSR)

        elif type == Side.USSR:
            trigger(self, Side.USSR)
            trigger(self, Side.US)

        self.headline_bin.pop()




    def select_card_and_action(self):
        '''
        This function should lead to card_operation_realignment, card_operation_coup,
        or card_operation_influence, or a space race function. It serves as a place
        where all possible actions are revealed to the player.
        '''
        # figure out who is the phasing player
        def determine_side(self):
            # TODO: account for extra turns
            return Side.USSR if self.ar_track % 2 == 1 else Side.US

        side = determine_side(self)
        if side == Side.USSR:
            hand = self.ussr_hand
        elif side == Side.US:
            hand = self.us_hand

        def select_card(self, side: Side):

            guide_msg = f'You may play a card. Type in the card index.'
            rejection_msg = f'Please key in a single value.'

            while True:
                available_list = [card.info.name for card in hand]
                available_list_values = [str(self.cards[n].info.card_index) for n in available_list]

                self.prompt_side(side)
                print(guide_msg)
                for available_name in available_list:
                    print(f'{self.cards[available_name].info.card_index}\t{self.cards[available_name].info.name}')

                user_choice = UI.ask_for_input(1, rejection_msg)
                if user_choice == None:
                    break

                if len(set(user_choice) - set(available_list_values)) == 0:
                    name = self.cards.index_card_mapping[int(user_choice[0])]
                    return hand[hand.index(name)]
                else:
                    print('\nYour input cannot be accepted.')

        card = select_card(self, side)

        '''
        Assume you have selected a card.
        We want to know what options can be available to the player.
        '''
        def can_play_event(self, side: Side, card: Card):
            return True if card.info.owner == side else False

        def can_resolve_event_first(self, side: Side, card: Card):
            return True if card.info.owner == side.opp else False

        def can_place_influence(self, side: Side, card: Card):
            return False if card.info.ops == 0 else True

        def can_realign_at_all(self):
            filter = np.array([self.map.can_realignment(self, name, side, self.defcon_track) for name in self.map.ALL])
            return filter.sum() > 0

        def can_coup_at_all(self):
            filter = np.array([self.map.can_coup(self, name, side, self.defcon_track) for name in self.map.ALL])
            return filter.sum() > 0

        def can_space(self, side: Side, card: Card):
            # first check that player can still space
            def available_space_turn(self, side: Side):
                if self.spaced_turns[side] == 2:
                    return False
                elif self.spaced_turns[side] == 0:
                    return True
                elif self.space_track[side.opp] < 2 and self.space_track[side] >= 2:
                    return True
                else:
                    return False

            # then check if the card ops fulfills space criterion
            def enough_ops(self, side: Side, card: Card):
                if self.space_track[side] == 8:
                    return False
                if self.space_track[side] == 7 and card.info.ops == 4:
                    return True
                elif self.space_track[side] >= 5 and card.info.ops >= 3:
                    return True
                elif card.info.ops >= 2:
                    return True
                else:
                    return False

            return available_space_turn(self, side) and enough_ops(self, side, card)

        action = {
            'PlayEvent' : 0,
            'ResolveEventFirst' : 1,
            'PlaceInfluence' : 2,
            'Realignment' : 3,
            'Coup' : 4,
            'Space' : 5,
        }

        def select_action(self, side: Side, card: Card, hand: list):
            filter = np.array([can_play_event(self, side, card),
            can_resolve_event_first(self, side, card), can_place_influence(self, side, card),
            can_realign_at_all(self), can_coup_at_all(self), can_space(self, side, card)])
            all_actions = np.array(list(action.keys()))
            available_list = all_actions[filter]
            available_list_values = [str(action[n]) for n in available_list]
            guide_msg = 'Choose an action and type in the corresponding value.'
            rejection_msg = 'Please key in a single value.'

            while True:

                self.prompt_side(side)
                print(guide_msg)
                for available_name in available_list:
                    print(f'{available_name}, {action[available_name]}')

                user_choice = UI.ask_for_input(1, rejection_msg)
                if user_choice == None:
                    break

                if len(set(user_choice) - set(available_list_values)) == 0:
                    if int(user_choice[0]) == 0 or int(user_choice[0]) == 1:
                        self.trigger_event(card.info.name)
                    elif int(user_choice[0]) == 2:
                        self.card_operation_influence(side, card, hand)
                    elif int(user_choice[0]) == 3:
                        self.card_operation_realignment(side, card, hand)
                    elif int(user_choice[0]) == 4:
                        self.card_operation_coup(side, card, hand)
                    elif int(user_choice[0]) == 5:
                        self.space(side, card, hand)
                    break
                else:
                    print('\nYour input cannot be accepted.')

        select_action(self, side, card, hand)
        self.ar_track += 1
        pass

    def forced_to_missile_envy(self):
        # check first if the player has as many scoring cards as turns
        # if True, then player is given choice as to which scoring card they
        # can play. this stage is then triggered again at a later stage.
        pass

    def trigger_event(self, card_name: str) -> str:
        '''Takes in a card_name and runs the associated card event function.
        Returns the appropriate treatment of the card.'''
        return Game.card_function_mapping[card_name](self)

    def card_event(self):
        # can only be used if the event is yours
        pass

    def card_operation_realignment(self, side: Side, card: Card, hand):
        '''
        Generates the list of all possible countries that can be realigned.
        Adjusts for DEFCON status only.
        TODO: Does not currently check the player baskets for continuous effects.
        TODO: Does not currently check for The_China_Card realignment bonus in Asia.
        TODO: Does not currently check for Vietnam_Revolts in ussr_basket for realignment bonus in Asia
        '''
        current_effective_ops = card.info.ops
        guide_msg = f'You may attempt realignment in these countries. Type in the target country index.'
        rejection_msg = f'Please key in a single value.'

        while current_effective_ops > 0:
            filter = np.array([self.map.can_realignment(self, name, side, self.defcon_track) for name in self.map.ALL])
            all_countries = np.array([name for name in self.map.ALL])
            available_list = all_countries[filter]
            available_list_values = [str(self.map[n].info.country_index) for n in available_list]

            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(f'{self.map[available_name].info.country_index}\t{self.map[available_name].info.name}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                name = self.map.index_country_mapping[int(user_choice[0])]
                self.map.realignment(self, name, side, self.defcon_track)
                current_effective_ops -= 1
            else:
                print('\nYour input cannot be accepted.')
        self.discard_pile.append(hand.pop(hand.index(card)))


    def card_operation_coup(self, side: Side, card: Card, hand):
        '''
        Generates the list of all possible countries that can be couped.
        Adjusts for DEFCON status only.
        TODO: Does not currently check the player baskets for continuous effects.
        '''
        effective_ops = card.info.ops

        filter = np.array([self.map.can_coup(self, name, side, self.defcon_track) for name in self.map.ALL])
        all_countries = np.array([name for name in self.map.ALL])
        available_list = all_countries[filter]
        available_list_values = [str(self.map[n].info.country_index) for n in available_list]
        guide_msg = f'You may coup these countries. Type in the country index.'
        rejection_msg = f'Please key in a single value.'

        while True:
            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(f'{self.map[available_name].info.country_index}\t{self.map[available_name].info.name}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                name = self.map.index_country_mapping[int(user_choice[0])]
                self.map.coup(self, name, side, effective_ops, self.defcon_track)
                break
            else:
                print('\nYour input cannot be accepted.')
        self.discard_pile.append(hand.pop(hand.index(card)))

    '''
    The player is given here an option to discard a card.
    This would be be used for the Blockade discard, and also the space race buff.
    Not originally intended for Ask Not..
    '''
    def may_discard_card(self, side: Side, blockade=False):

        guide_msg = f'You may discard a card. Type in the card index.'
        rejection_msg = f'Please key in a single value.'

        if blockade:
            hand = self.us_hand
            available_list = [card.info.name for card in hand if card.info.ops > 2]

        else:
            if side == Side.USSR:
                hand = self.ussr_hand
            elif side == Side.US:
                hand = self.us_hand
            available_list = hand

        available_list_values = [str(self.cards[n].info.card_index) for n in available_list]

        while True:
            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(f'{self.cards[available_name].info.card_index}\t{self.cards[available_name].info.name}')

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
        In this stage, the player must discard a card if they are holding suitable
        discards. Player is given a list of suitable discards. Card has to be at least
        2 effective ops.
        '''
        pass

    def norad_influence(self):
        # this stage is triggered because norad is in us_basket
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

    def space(self, side: Side, card: Card, hand):
        if self.space_track[side] in [0,2,4,6]:
            modifier = 0
        elif self.space_track[side] in [1,3,5]:
            modifier = -1
        else:
            modifier = 1

        y = side.vp_mult # multiplier for VP - gives 1 for USSR and -1 for US
        roll = random.randint(1,6)
        if roll + modifier <= 3:
            self.space_track[side] += 1
            print(f'Success with roll of {roll}.')

            if self.space_track[side] == 1:
                if self.space_track[side.opp] < 1:
                    self.change_vp(2*y)
                else:
                    self.change_vp(y)

            elif self.space_track[side] == 3:
                if self.space_track[side.opp] < 3:
                    self.change_vp(2*y)

            elif self.space_track[side] == 5:
                if self.space_track[side.opp] < 5:
                    self.change_vp(3*y)
                else:
                    self.change_vp(y)

            elif self.space_track[side] == 7:
                if self.space_track[side.opp] < 7:
                    self.change_vp(4*y)
                else:
                    self.change_vp(2*y)

            elif self.space_track[side] == 8:
                if self.space_track[side.opp] < 8:
                    self.change_vp(2*y)

        else:
            print(f'Failure with roll of {roll}.')

        self.spaced_turns[side] += 1
        self.discard_pile.append(hand.pop(hand.index(card)))

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
            self.ussr_hand.append(self.cards.early_war.pop(self.cards.early_war.index('The_China_Card')))
            self.ussr_hand.append(self.cards.early_war.pop(self.cards.early_war.index('Asia_Scoring'))) # for testing of specific cards
            self.us_hand.append(self.cards.early_war.pop(self.cards.early_war.index('Europe_Scoring'))) # for testing of specific cards
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
        # TODO: Add 1 VP for China Card holder
        def final_scoring(self):
            if self.turn_track == 10 and (self.ar_track in [15,16,17]):
                self._Asia_Scoring()
                self._Europe_Scoring()
                self._Middle_East_Scoring()
                self._Central_America_Scoring()
                self._South_America_Scoring()
                self._Africa_Scoring()
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
    underscore prefix. Every time a card's event is triggered, the dictionary
    lookup will be used to access the function.

    card_event_functions should return 'ussr_basket' if the card should enter the USSR basket.
    card_event_functions should return 'us_basket' if the card should enter the US basket.
    card_event_functions should return 'discard' if the card should be discarded.
    card_event_functions should return 'remove' if the card should be removed.
    '''

    def _Asia_Scoring(self):
        # TODO: ADD SHUTTLE DIPLOMACY AND FORMOSAN RESOLUTION
        self.score(MapRegion.ASIA, 3, 7, 9)
        return 'discard'

    def _Europe_Scoring(self):
        self.score(MapRegion.EUROPE, 3, 7, 120)

    def _Middle_East_Scoring(self):
        self.score(MapRegion.MIDDLE_EAST, 3, 5, 7)

    def _Duck_and_Cover(self):
        pass

    def _Five_Year_Plan(self):
        pass

    def _The_China_Card(self):
        pass

    def _Socialist_Governments(self):
        pass

    def _Fidel(self):
        def RemoveAllOpponentInfluenceInCuba(_):
            Cuba.set_influence(0, max(3, Cuba.ussr_influence))
        pass

    def _Vietnam_Revolts(self):
        pass

    def _Blockade(self):
        may_discard_card(self, Side.US, blockade=True)
        return 'remove'

    def _Korean_War(self):
        pass

    def _Romanian_Abdication(self):
        def RemoveAllOpponentInfluenceInRomania(_):
            Romania.set_influence(0, max(3, Romania.ussr_influence))
        pass

    def _Arab_Israeli_War(self):
        pass

    def _COMECON(self):
        pass

    def _Nasser(self):
        def GainInfluenceInEgypt(_):
            Egypt.adjust_influence(-math.ceil(Egypt.us_influence/2), 2)
        pass

    def _Warsaw_Pact_Formed(self):
        pass

    def _De_Gaulle_Leads_France(self):
        def RemoveOpponentInfluenceInFrance(_):
            France.adjust_influence(-2, 1)
        pass

    def _Captured_Nazi_Scientist(self):
        pass

    def _Truman_Doctrine(self):
        pass

    def _Olympic_Games(self):
        pass

    def _NATO(self):
        is_event_playable = True if 'Warsaw_Pact_Formed' in self.us_basket or 'Marshall_Plan' in self.us_basket else False
        if is_event_playable:
            return 'us_basket'
        else:
            return 'discard'

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
        def GainInfluenceForControlInJapan(_):
            Japan.set_influence(Japan.ussr_influence + 4, Japan.ussr_influence)
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
        self.score(MapRegion.CENTRAL_AMERICA, 1, 3, 5)

    def _Southeast_Asia_Scoring(self):
        country_count = [0,0]
        for n in CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]:
            x = Game.main.map[n]
            country_count[Side.USSR] += (x.control == Side.USSR)
            country_count[Side.US] += (x.control == Side.US)
        swing = country_count[Side.USSR] - country_count[Side.US]

        if Game.main.map['Thailand'].control == Side.USSR:
            swing += 1
        if Game.main.map['Thailand'].control == Side.US:
            swing -= 1
        self.change_vp(swing)
        print(f'Southeast Asia scores for {swing} VP')

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
        # if the other player is only holding scoring cards, this effect needs to be pushed
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
        self.score(MapRegion.AFRICA, 1, 4, 6)

    def _One_Small_Step(self):
        pass

    def _South_America_Scoring(self):
        self.score(MapRegion.SOUTH_AMERICA, 2, 5, 6)

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
