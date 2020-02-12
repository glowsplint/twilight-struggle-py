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

    def __init__(self):
        self.handicap = -2  # positive in favour of ussr
        self.vp_track = 0  # positive for ussr
        self.turn_track = 1
        self.ar_track = 1  # increment by 1 for each side's action round
        self.defcon_track = 5
        self.milops_track = np.array([0, 0])  # ussr first

        # 0 is start, 1 is earth satellite etc
        self.space_track = np.array([0, 0])
        self.spaced_turns = np.array([0, 0])
        self.extra_turn = [False, False]

        self.map = GameMap()
        self.cards = GameCards()
        self.ui = UI(self)

        self.hand = [[], []]  # ussr, us hands; list of 2 lists of Card objects
        self.removed_pile = []
        self.discard_pile = []
        self.draw_pile = []

        # ussr, us hands; list of 2 lists of Card objects
        self.basket = [[], []]
        self.headline_bin = [[], []]  # the inner lists are placeholders

        self.stage_list = [self.map.build_standard, self.deal, self.put_start_USSR,
                           self.put_start_US, self.put_start_extra, self.joint_choose_headline]

        self.ar6 = [self.select_card_and_action for i in range(12)]
        self.ar6.append(self.end_of_turn)
        self.ar7 = [self.select_card_and_action for i in range(14)]
        self.ar7.append(self.end_of_turn)
        self.stage_list.extend([*self.ar6 * 3, *self.ar7 * 4])
        self.stage_list.reverse()

        # For new set the first created game to be the actual ongoing game.
        if Game.main is None:
            Game.main = self

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
    event_influence is the generic stage where a side is given the opportunity to modify influence.
    Unlike card_operation_add_influence, this is mostly used for card events where the player has to choose
    which regions in which to directly insert influence.

    Examples of cards that use this function are: VOA, Decolonization, OAS_Founded, Junta.
    See put_start_USSR below for an example of how to use this function.
    available_list is the list of names that can be manipulated by the effect.
    can_split is True for cards where the influence adjustment can be split like VOA. False for cards like Junta.
    limit is the maximum influence adjustment that can be made to a single country. 2 for VOA, 1 for COMECON.
    positive is True for positive adjustments like Decolonization, False for VOA.
    all is True for Warsaw Pact removal, and Muslim_Revolution.
    '''

    def event_influence(self, side: Side, ops: int, available_list: list, can_split: bool, positive: bool, limit: int = None, all=False):

        available_list_values = [
            str(self.map[n].info.country_index) for n in available_list]
        verb = 'add' if positive else 'remove'
        guide_msg = f'You may {verb} {ops} influence in these countries. Type in their country indices, separated by commas (no spaces).'
        guide_msg_all = f'You may remove influence completely in these countries. Type in their country indices, separated by commas (no spaces).'
        rejection_msg = f'Please key in {ops} comma-separated values.'

        while True:
            self.prompt_side(side)

            if all:
                print(guide_msg_all)
            else:
                print(guide_msg)
            for available_name in available_list:
                print(
                    f'{self.map[available_name].info.country_index}\t{self.map[available_name].info.name}')

            user_choice = UI.ask_for_input(ops, rejection_msg)
            if user_choice == None:
                break

            is_input_all_available = (
                len(set(user_choice) - set(available_list_values)) == 0)
            is_input_singular = True if can_split else (
                len(set(user_choice)) == 1)
            is_input_limited = True if limit == None else max(
                user_choice.count(x) for x in set(user_choice)) >= limit

            if all:
                if is_input_all_available:
                    self.map.set_influence(
                        name, 0, self.map[name].influence[Side.USSR])
                    break

            elif is_input_all_available and is_input_singular and is_input_limited:
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
        available_list = [
            n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]]
        self.event_influence(Side.USSR, 6, available_list,
                             can_split=True, positive=True)

    def put_start_US(self):
        available_list = [
            n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]]
        self.event_influence(Side.US, 7, available_list,
                             can_split=True, positive=True)

    def put_start_extra(self):
        if self.handicap < 0:
            available_list = [*self.map.has_us_influence()]
            self.event_influence(Side.US, -self.handicap,
                                 available_list, can_split=True, positive=True)
        elif self.handicap > 0:
            available_list = [*self.map.has_ussr_influence()]
            self.event_influence(Side.USSR, self.handicap,
                                 available_list, can_split=True, positive=True)

    def joint_choose_headline(self):
        '''
        Both players are to simultaneously choose their headline card.
        USSR chooses first, then US, then display to both players the other's
        choice.
        '''
        self.choose_headline(Side.USSR)
        self.choose_headline(Side.US)
        self.resolve_headline(type=Side.NEUTRAL)

    def choose_headline(self, side: Side):
        hand = self.hand[side]

        guide_msg = f'You may headline any of these cards. Type in the card index.'
        rejection_msg = f'Please key in a single value.'

        while True:
            filter = np.array([card.info.can_headline for card in hand])
            cards_in_hand = np.array([card.info.name for card in hand])
            available_list = cards_in_hand[filter]
            available_list_values = [
                str(self.cards[n].info.card_index) for n in available_list]

            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(
                    f'{self.cards[available_name].info.card_index}\t{self.cards[available_name]}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                name = self.cards.index_card_mapping[int(user_choice[0])]
                self.headline_bin[side] = hand.pop(hand.index(name))
                break
            else:
                print('\nYour input cannot be accepted.')

    def resolve_headline(self, type: Side = Side.NEUTRAL):

        def trigger(self, side: Side):
            print(
                f'\n{side.toStr} selected {self.headline_bin[side].info.name} for headline.')
            card_treatment = self.trigger_event(
                self.headline_bin[side].info.name)
            if card_treatment == 'discard':
                self.discard_pile.append(self.headline_bin.pop(side))
            elif card_treatment == 'remove':
                self.removed_pile.append(self.headline_bin.pop(side))
            elif card_treatment == 'us_basket':
                self.basket[Side.US].append(self.headline_bin.pop(side))
            elif card_treatment == 'ussr_basket':
                self.basket[Side.USSR].append(self.headline_bin.pop(side))

        if type == Side.NEUTRAL:
            '''
            Side.NEUTRAL : Joint resolution of headline
            Side.US : Resolve US headline, then USSR headline
            Side.USSR : Resolve USSR headline, then US headline
            '''
            if self.headline_bin[Side.US] == 'Defectors':
                for card in self.headline_bin:
                    self.discard_pile.append(self.headline_bin.pop())
                print('Defectors cancellation of headline phase.')
                return
            # how about the case of Grain_Sales_to_Soviets into Five_Year_Plan into Defectors?
            if self.headline_bin[Side.USSR].info.ops > self.headline_bin[Side.US].info.ops:
                trigger(self, Side.USSR)
                trigger(self, Side.US)
            else:
                trigger(self, Side.US)
                trigger(self, Side.USSR)
        else:
            trigger(self, type)
            trigger(self, type.opp)

        self.ar_track = 1

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
        hand = self.hand[side]

        def select_card(self, side: Side):

            guide_msg = f'You may play a card. Type in the card index.'
            rejection_msg = f'Please key in a single value.'

            while True:
                available_list = [card.info.name for card in hand]
                available_list_values = [
                    str(self.cards[n].info.card_index) for n in available_list]

                self.prompt_side(side)
                print(guide_msg)
                for available_name in available_list:
                    print(
                        f'{self.cards[available_name].info.card_index}\t{self.cards[available_name]}')

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
            hand = self.hand[side]
            if card == 'The_China_Card':
                return False
            elif card == 'UN_Intervention':
                my_cards_owners = np.array([item.info.owner for item in hand])
                enemy = np.array([side.opp for item in hand])
                return (my_cards_owners == enemy).sum() != 0
            else:
                return True if card.info.owner == side else False

        def can_resolve_event_first(self, side: Side, card: Card):
            return True if card.info.owner == side.opp else False

        def can_place_influence(self, side: Side, card: Card):
            return False if card.info.ops == 0 else True

        def can_realign_at_all(self):
            filter = np.array([self.map.can_realignment(
                self, name, side) for name in self.map.ALL])
            return filter.sum() > 0

        def can_coup_at_all(self):
            filter = np.array([self.map.can_coup(
                self, name, side) for name in self.map.ALL])
            return filter.sum() > 0

        def can_space(self, side: Side, card: Card):
            # first check that player has an available space slot
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
                if self.space_track[side] == 7 and self.get_global_effective_ops(side, card.info.ops) == 4:
                    return True
                elif self.space_track[side] >= 5 and self.get_global_effective_ops(side, card.info.ops) >= 3:
                    return True
                elif self.get_global_effective_ops(side, card.info.ops) >= 2:
                    return True
                else:
                    return False

            return available_space_turn(self, side) and enough_ops(self, side, card)

        action = {
            'PlayEvent': 0,
            'ResolveEventFirst': 1,
            'PlaceInfluence': 2,
            'Realignment': 3,
            'Coup': 4,
            'Space': 5,
        }

        def select_action(self, side: Side, card: Card, is_event_resolved=False):
            if card.info.type == 'Scoring':
                self.trigger_event(card.info.name)
                self.discard_pile.append(
                    self.hand[side].pop(self.hand[side].index(card)))
            else:
                filter = np.array([can_play_event(self, side, card) and not is_event_resolved,
                                   can_resolve_event_first(
                                       self, side, card) and not is_event_resolved, can_place_influence(self, side, card),
                                   can_realign_at_all(self), can_coup_at_all(self), can_space(self, side, card)])
                all_actions = np.array(list(action.keys()))
                available_list = all_actions[filter]
                available_list_values = [str(action[n])
                                         for n in available_list]
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
                        if int(user_choice[0]) == 0:
                            self.trigger_event(card.info.name)
                        elif int(user_choice[0]) == 1:
                            self.trigger_event(card.info.name)
                            select_action(self, side, card,
                                          is_event_resolved=True)
                        elif int(user_choice[0]) == 2:
                            self.card_operation_influence(side, card)
                        elif int(user_choice[0]) == 3:
                            self.card_operation_realignment(side, card)
                        elif int(user_choice[0]) == 4:
                            self.card_operation_coup(side, card)
                        elif int(user_choice[0]) == 5:
                            self.space(side, card)
                        break
                    else:
                        print('\nYour input cannot be accepted.')

        select_action(self, side, card)
        self.ar_track += 1
        pass

    '''
    card_operation_influence is the generic stage where a side is given the opportunity to place influence.
    They are provided a list of all possible countries that they can place influence into, and
    must choose from these. During this stage, the UI is waiting for a tuple of country indices.

    This is the actual use of operations to place influence.
    '''

    def card_operation_influence(self, side: Side, card: Card):

        effective_ops = card.info.ops

        '''Generates the list of all possible countries that influence can be placed in.'''
        filter = np.array([self.map.can_place_influence(
            name, side, effective_ops) for name in self.map.ALL])
        all_countries = np.array([name for name in self.map.ALL])
        available_list = all_countries[filter]
        available_list_values = [
            str(self.map[n].info.country_index) for n in available_list]
        guide_msg = f'You may add {effective_ops} influence in these countries. Type in their country indices, separated by commas (no spaces).'
        rejection_msg = f'Please key in {effective_ops} comma-separated values.'

        while True:
            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(
                    f'{self.map[available_name].info.country_index}\t{self.map[available_name].info.name}')

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

        self.dispose_card(side, card)

    def dispose_card(self, side: Side, card: Card, space=False):
        hand = self.hand[side]
        if card == 'The_China_Card':
            self.move_china_card(side, card)
        elif space or side != card.info.owner.opp:
            self.discard_pile.append(hand.pop(hand.index(card)))
        elif side == card.info.owner.opp:
            card_treatment = self.trigger_event(card.info.name)
            if card_treatment == 'discard':
                self.discard_pile.append(hand.pop(hand.index(card)))
            elif card_treatment == 'remove':
                self.removed_pile.append(hand.pop(hand.index(card)))
            elif card_treatment == 'us_basket':
                self.basket[Side.US].append(hand.pop(hand.index(card)))
            elif card_treatment == 'ussr_basket':
                self.basket[Side.USSR].append(hand.pop(hand.index(card)))

    def card_operation_realignment(self, side: Side, card: Card):
        '''
        Generates the list of all possible countries that can be realigned.
        Adjusts for DEFCON status only.
        TODO: Does not currently check for The_China_Card realignment bonus in Asia.
        TODO: Does not currently check for Vietnam_Revolts in ussr_basket for realignment bonus in Asia
        '''
        current_effective_ops = self.get_global_effective_ops(
            side, card.info.ops)
        guide_msg = f'You may attempt realignment in these countries. Type in the target country index.'
        rejection_msg = f'Please key in a single value.'

        while current_effective_ops > 0:
            filter = np.array([self.map.can_realignment(
                self, name, side) for name in self.map.ALL])
            all_countries = np.array([name for name in self.map.ALL])
            available_list = all_countries[filter]
            available_list_values = [
                str(self.map[n].info.country_index) for n in available_list]

            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(
                    f'{self.map[available_name].info.country_index}\t{self.map[available_name].info.name}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                name = self.map.index_country_mapping[int(user_choice[0])]
                self.map.realignment(self, name, side)
                current_effective_ops -= 1
            else:
                print('\nYour input cannot be accepted.')

        self.dispose_card(side, card)

    def card_operation_coup(self, side: Side, card: Card, restricted_list: list = None):
        '''
        Generates the list of all possible countries that can be couped.
        restricted_list should be a list of country_names.
        TODO: Does not currently check the player baskets for China Card and Vietnam effects.
        TODO: Latin American DS, Iran-contra
        '''
        current_effective_ops = self.get_global_effective_ops(
            side, card.info.ops)

        filter = np.array([self.map.can_coup(
            self, name, side) for name in self.map.ALL])
        all_countries = np.array([name for name in self.map.ALL])
        available_list = all_countries[filter]

        if restricted_list != None:
            available_list = list(np.intersect1d(
                restricted_list, available_list))

        available_list_values = [
            str(self.map[n].info.country_index) for n in available_list]
        guide_msg = f'You may coup these countries. Type in the country index.'
        rejection_msg = f'Please key in a single value.'

        while True:
            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(
                    f'{self.map[available_name].info.country_index}\t{self.map[available_name].info.name}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                name = self.map.index_country_mapping[int(user_choice[0])]
                self.map.coup(self, name, side, current_effective_ops)
                break
            else:
                print('\nYour input cannot be accepted.')

        self.dispose_card(side, card)

    def forced_to_missile_envy(self):
        # check first if the player has as many scoring cards as turns
        # if True, then player is given choice as to which scoring card they
        # can play. this stage is then triggered again at a later stage.
        pass

    def trigger_event(self, card_name: str) -> str:
        '''
        Wrapper for triggering an event.
        Takes in a card_name and runs the associated card event function.
        Returns the appropriate treatment of the card.
        '''
        return Game.card_function_mapping[card_name](self)

    def move_china_card(self, side: Side, card: Card('The_China_Card')):
        giver = self.hand[side]
        receipient = self.hand[side.opp]
        receipient.append(giver.pop(giver.index(card)))
        receipient[-1].can_play = False

    def get_global_effective_ops(self, side: Side, raw_ops: int):
        modifier = 0
        if side == Side.USSR and 'Brezhnev_Doctrine' in self.basket[side]:
            modifier += 1
        if side == Side.US and 'Containment' in self.basket[side]:
            modifier += 1
        if 'Red_Scare_Purge' in self.basket[side.opp]:
            modifier -= 1
        return min(max([raw_ops + modifier, 1]), 4)

    '''
    The player is given here an option to discard a card (ONLY ONE).
    This would be be used for the Blockade discard, and also the space race buff.
    '''

    def may_discard_card(self, side: Side, blockade=False):
        guide_msg = f'You may discard a card. Type in the card index.'
        rejection_msg = f'Please key in a single value.'

        if blockade:
            hand = self.hand[Side.US]
            available_list = [
                'Do not discard a card. US loses all influence in West Germany.']
            available_list.extend([
                card.info.name for card in hand if self.get_global_effective_ops(side, card.info.ops) >= 3])
            if len(available_list) == 0:
                return 'did not discard'
        else:
            available_list = self.hand[side]

        if 'The_China_Card' in available_list:
            available_list.pop(available_list.index('The_China_Card'))

        available_list_values = ['0']
        available_list_values.extend(
            [str(self.cards[n].info.card_index) for n in available_list[blockade:]])

        while True:
            self.prompt_side(side)
            print(guide_msg)
            for (available_name, available_list_value) in zip(available_list, available_list_values):
                print(
                    f'{available_list_value}\t{available_name}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                if int(user_choice[0]) == 0:
                    return 'did not discard'
                name = self.cards.index_card_mapping[int(user_choice[0])]
                self.discard_pile.append(hand.pop(hand.index(name)))
                break
            else:
                print('\nYour input cannot be accepted.')

        self.discard_pile.append(
            self.hand[side].pop(self.hand[side].index(card)))

    def select_multiple(self, statements: list, side: Side):
        '''
        The player is given a choice of options from statements.
        '''
        guide_msg = f'You may discard a card. Type in the card index.'
        rejection_msg = f'Please key in a single value.'

        available_list = statements
        available_list_values = [str(i) for i in range(len(statements))]

        while True:
            self.prompt_side(side)
            print(guide_msg)
            for i, available_name in enumerate(available_list):
                print(f'{i}\t{available_name}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            print(available_list_values)
            if len(set(user_choice) - set(available_list_values)) == 0:
                return int(user_choice[0])
            else:
                print('\nYour input cannot be accepted.')

    def select_take_8_rounds(self):
        pass

    def quagmire_discard(self):
        '''
        The player must discard a card if they are holding suitable discards.
        Player is given a list of suitable discards. Card has to be at least
        2 effective ops. If there are only scoring cards left..
        '''
        available_list = [
            card.info.name for card in hand if self.get_global_effective_ops(side, card.info.ops) >= 2]

        if 'The_China_Card' in available_list:
            available_list.pop(available_list.index('The_China_Card'))
        if len(available_list) == 0:
            pass  # may only play scoring cards ```

        available_list_values = [
            str(self.cards[n].info.card_index) for n in available_list]

        while True:
            self.prompt_side(side)
            print(guide_msg)
            for available_name in available_list:
                print(
                    f'{self.cards[available_name].info.card_index}\t{self.cards[available_name].info.name}')

            user_choice = UI.ask_for_input(1, rejection_msg)
            if user_choice == None:
                break

            if len(set(user_choice) - set(available_list_values)) == 0:
                name = self.cards.index_card_mapping[int(user_choice[0])]
                self.discard_pile.append(hand.pop(hand.index(name)))
                break
            else:
                print('\nYour input cannot be accepted.')
        return 'discard successful'

    def norad_influence(self):
        available_list = [*self.map.has_us_influence()]
        self.event_influence(side, 1, available_list,
                             can_split=True, positive=True, limit=1)

    def cuba_missile_remove(self):
        pass

    def space(self, side: Side, card: Card):
        if self.space_track[side] in [0, 2, 4, 6]:
            modifier = 0
        elif self.space_track[side] in [1, 3, 5]:
            modifier = -1
        else:
            modifier = 1

        y = side.vp_mult  # multiplier for VP - gives 1 for USSR and -1 for US
        roll = random.randint(1, 6)
        if roll + modifier <= 3:
            self.space_track[side] += 1
            print(f'Success with roll of {roll}.')

            if self.space_track[side] == 1:
                if self.space_track[side.opp] < 1:
                    self.change_vp(2 * y)
                else:
                    self.change_vp(y)

            elif self.space_track[side] == 3:
                if self.space_track[side.opp] < 3:
                    self.change_vp(2 * y)

            elif self.space_track[side] == 5:
                if self.space_track[side.opp] < 5:
                    self.change_vp(3 * y)
                else:
                    self.change_vp(y)

            elif self.space_track[side] == 7:
                if self.space_track[side.opp] < 7:
                    self.change_vp(4 * y)
                else:
                    self.change_vp(2 * y)

            elif self.space_track[side] == 8:
                if self.space_track[side.opp] < 8:
                    self.change_vp(2 * y)

        else:
            print(f'Failure with roll of {roll}.')

        self.spaced_turns[side] += 1
        self.dispose_card(side, card, space=True)

    # to add game terminate functionality EndGame()

    def change_vp(self, n: int):  # positive for ussr
        self.vp_track += n
        if self.vp_track >= 20:
            print('USSR victory')
            # EndGame()
        if self.vp_track <= -20:
            print('US victory')
            # EndGame()
        print(f'Current VP: {self.vp_track}')

    def change_defcon(self, n: int):
        previous_defcon = self.defcon_track
        self.defcon_track += min(n, 5 - self.defcon_track)
        if self.defcon_track < 2:
            print('Game ended by thermonuclear war')
        if previous_defcon > 2 and self.defcon_track == 2 and self.ar_track != 0 and 'NORAD' in self.basket[Side.US]:
            self.norad_influence()
        if n > 0:
            print(f'DEFCON level improved to {self.defcon_track}.')
        else:
            print(f'DEFCON level degraded to {self.defcon_track}.')

        # EndGame()

    def change_milops(self, side, n: int):
        self.milops_track[side] += min(n, 5 - self.milops_track[side])

    def headline(self):
        # decide if it is going to be joint_choose_headline or separated
        # modify top to use this function instead
        pass

    def deal(self):
        def top_up_cards(self, n: int):
            ussr_held = len(self.hand[Side.USSR])
            us_held = len(self.hand[Side.US])

            # Ignore China Card if it is in either hand
            if 'The_China_Card' in self.hand[Side.USSR]:
                ussr_held = len(self.hand[Side.USSR]) - 1
            elif 'The_China_Card' in self.hand[Side.US]:
                us_held = len(self.hand[Side.US]) - 1

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
                    self.hand[Side.USSR].extend([self.draw_pile.pop()])
                    ussr_held += 1
                    recreate_draw_pile()
                if us_held < n:
                    self.hand[Side.US].extend([self.draw_pile.pop()])
                    us_held += 1
                    recreate_draw_pile()

        '''Pre-headline setup'''
        if self.turn_track == 1 and self.ar_track == 1:
            # self.hand[Side.USSR].append(self.cards.early_war.pop(
                # self.cards.early_war.index('Asia_Scoring')))  # for testing of specific cards
            self.hand[Side.USSR].extend([self.cards.early_war.pop(0)
                                         for i in range(18)])
            self.hand[Side.US].extend([self.cards.early_war.pop(0)
                                       for i in range(18)])
            self.draw_pile.extend(self.cards.early_war)
            self.cards.early_war = []
            random.shuffle(self.draw_pile)
            top_up_cards(self, 8)
        else:
            if self.turn_track in [1, 2, 3]:
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
            scoring_list = ['Asia_Scoring', 'Europe_Scoring', 'Middle_East_Scoring',
                            'Central_America_Scoring', 'Southeast_Asia_Scoring', 'Africa_Scoring', 'South_America_Scoring']
            scoring_cards = [self.cards[y] for y in scoring_list]
            if any(True for x in scoring_cards if x in self.hand[Side.US]):
                print('USSR Victory!')
                # EndGame()
            elif any(True for x in scoring_cards if x in self.hand[Side.USSR]):
                print('US Victory!')
                # EndGame()

        # 3. Flip China Card
        def flip_china_card(self):
            if 'The_China_Card' in self.hand[Side.USSR]:
                self.hand[Side.USSR][self.hand[Side.USSR].index(
                    'The_China_Card')].can_play = True
            elif 'The_China_Card' in self.hand[Side.US]:
                self.hand[Side.US][self.hand[Side.US].index(
                    'The_China_Card')].can_play = True

        # 4. Advance turn marker
        def advance_turn_marker(self):
            self.turn_track += 1
            self.ar_track = 0  # headline phase

        # 5. Final scoring (end T10)
        # TODO: Add 1 VP for China Card holder
        def final_scoring(self):
            if self.turn_track == 10 and (self.ar_track in [15, 16, 17]):
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

        # 9. Action Rounds (advance round marker) -- action rounds are not considered between turns
        check_milops(self)
        check_for_scoring_cards(self)
        flip_china_card(self)
        advance_turn_marker(self)  # turn marker advanced before final scoring
        final_scoring(self)
        self.change_defcon(1)
        self.deal()  # turn marker advanced before dealing
        self.headline()

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

    To write a card event:
    1. If there are pre-requisites, add conditions (think: NATO/Solidarity).
    2. Add the event body.
    3. Add what should be done with the card, if the pre-requisites are not fulfilled,
       and also what should be done with the card if they are.
    '''

    def _Asia_Scoring(self):
        # TODO: ADD SHUTTLE DIPLOMACY AND FORMOSAN RESOLUTION
        self.score(MapRegion.ASIA, 3, 7, 9)
        return 'discard'

    def _Europe_Scoring(self):
        self.score(MapRegion.EUROPE, 3, 7, 120)
        return 'discard'

    def _Middle_East_Scoring(self):
        self.score(MapRegion.MIDDLE_EAST, 3, 5, 7)
        return 'discard'

    def _Duck_and_Cover(self):
        self.change_defcon(-1)
        self.change_vp(-(5 - self.defcon_track))
        return 'discard'

    def _Five_Year_Plan(self):
        pass

    def _The_China_Card(self):
        'No event.'
        pass

    def _Socialist_Governments(self):
        western_europe = [
            n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]]
        available_list = [
            self.map[country_name].info.name for country_name in western_europe if self.map[country_name].has_us_influence]
        self.event_influence(Side.USSR, 3, available_list,
                             can_split=True, positive=False, limit=2)

    def _Fidel(self):
        cuba = self.map['Cuba']
        cuba.set_influence(0, max(3, cuba.influence[Side.USSR]))
        return 'remove'

    def _Vietnam_Revolts(self):
        pass

    def _Blockade(self):
        result = self.may_discard_card(Side.US, blockade=True)
        if result == 'did not discard':
            west_germany = self.map['West_Germany']
            west_germany.set_influence(0, west_germany.influence[Side.USSR])
        return 'remove'

    def _Korean_War(self):
        self._War('South_Korea', Side.USSR)
        return 'remove'

    def _Romanian_Abdication(self):
        romania = self.map['Romania']
        romania.set_influence(0, max(3, romania.influence[Side.USSR]))
        return 'remove'

    def _War(self, country_name: str, side: Side, lower: int = 4, win_vp: int = 2, win_milops: int = 2):
        country = self.map[country_name]
        roll = random.randint(1, 6)
        modifier = sum([self.map[adjacent_country].control ==
                        side.opp for adjacent_country in country.info.adjacent_countries])
        if roll - modifier >= lower:
            self.change_vp(win_vp * side.vp_mult)
            self.change_milops(side, win_milops)
            country.change_influence(
                country.influence[side.opp], -country.influence[side.opp])
            print(f'Success with roll of {roll}.')
        else:
            print(f'Failure with roll of {roll}.')

    def _Arab_Israeli_War(self):
        pass

    def _COMECON(self):
        available_list = [
            n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]]
        self.event_influence(Side.USSR, 4, available_list,
                             can_split=True, positive=True)
        return 'remove'

    def _Nasser(self):
        egypt = self.map['Egypt']
        egypt.change_influence(-math.ceil(egypt.influence[Side.US] / 2), 2)
        return 'remove'

    def _Warsaw_Pact_Formed(self):
        statements = ['Remove all US influence from 4 countries in Eastern Europe',
                      'Add 5 USSR Influence to any countries in Eastern Europe']
        binary_outcome = self.select_multiple(statements, Side.USSR)
        if binary_outcome == 0:
            available_list = [
                n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]]
            self.event_influence(Side.USSR, 0, available_list,
                                 can_split=True, positive=False, limit=1, all=True)
        elif binary_outcome == 1:
            available_list = [
                n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]]
            self.event_influence(Side.USSR, 5, available_list,
                                 can_split=True, positive=True, limit=2)

        return 'us_basket'

    def _De_Gaulle_Leads_France(self):
        self.map['France'].change_influence(-2, 1)
        return 'remove'

    def _Captured_Nazi_Scientist(self):
        pass

    def _Truman_Doctrine(self):
        pass

    def _Olympic_Games(self):
        pass

    def _NATO(self):
        is_event_playable = True if 'Warsaw_Pact_Formed' in self.basket[
            Side.US] or 'Marshall_Plan' in self.basket[Side.US] else False
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
        japan = self.map['Japan']
        japan.set_influence(
            japan.influence[Side.USSR] + 4, japan.influence[Side.USSR])
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
        country_count = [0, 0]
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
        # need to insert and replace the US Action round with the quagmire_discard stage
        '''This runs every US action round if quagmire is in ussr_basket.'''
        if 'NORAD' in self.basket[Side.US]:
            self.removed_pile.append(
                self.basket[Side.US].pop(self.basket[Side.US].index('NORAD')))
        discard = self.quagmire_discard()
        if discard == 'discard successful':
            roll = random.randint(1, 6)
            if roll >= 4:
                self.basket[Side.USSR].pop(
                    self.basket[Side.USSR].index('Quagmire'))
                print(f'Roll successful with roll of {roll}. Quagmire lifted.')
            else:
                print(f'Roll failed with roll of {roll}.')

        # ```

        return 'remove'
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
