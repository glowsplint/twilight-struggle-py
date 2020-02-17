import math
import random

from functools import partial
from itertools import chain
from typing import Sequence

from twilight_map import GameMap, CountryInfo, Country
from twilight_enums import Side, MapRegion, InputType, CardAction
from twilight_cards import GameCards, CardInfo, Card


class Game:

    # this is the currently active game. One may refer to this as
    # Game.main. The point is to have a globally accessible game
    # object for the active game, but still allow for other game
    # objects to deal with hypothetical future/past game states
    # which would be useful for non-committed actions and possibly
    # the AI depending on how you do it.
    main = None
    ars_by_turn = [None, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7]

    class Input:

        OPTION_DO_NOT_DISCARD = 'Do Not Discard'

        def __init__(self, side: Side, state: InputType, callback: Callable[[str], bool],
                     options: Iterable[str], prompt: str = '',
                     reps=1, reps_unit: str = '', max_per_option=-1):
            self.side = side
            self.state = state
            self.callback = callback
            self.prompt = prompt
            self.reps = reps
            self.reps_unit = reps_unit
            self.max_per_option = reps if max_per_option == -1 else max_per_option
            self.selection = {k: 0 for k in options}
            self.discarded_options = set()

        # Following here are some factory methods for standard required inputs.
        @staticmethod
        def DiceRoll(side: Side, callback: Callable[[str], bool]):
            return Game.Input(side, InputType.DICE_ROLL, callback,
                              ['Yes', 'No'],
                              'Commit your actions and roll the dice?')

        def recv(self, input_str):
            if input_str not in self.available_options:
                return False
            if self.callback(input_str):
                self.selection[input_str] += 1
                return True
            else:
                return False

        def remove_option(self, option):
            if option not in self.selection:
                raise KeyError('Option was never present!')
            self.discarded_options.add(option)

        @property
        def available_options(self):
            return map(
                lambda item: item[0],
                filter(
                    lambda item: item[0] not in self.discarded_options and item[1] < self.max_per_option,
                    self.selection.items()
                )
            )

        @property
        def complete(self):
            return not self.reps or len(self.selection) == len(self.discarded_options)

    class Output:

        def __init__(self, turn, ar, ar_side=None, input=None, prompt=''):
            self.turn = turn
            self.ar = ar
            self.ar_side = ar_side
            self.prompt = prompt
            if input:
                self.in_prompt = input.prompt
                self.in_selection = input.selection

    def __init__(self):
        self.vp_track = 0  # positive for ussr
        self.turn_track = 0
        self.ar_track = 0
        self.ar_side = None
        self.defcon_track = 0
        self.milops_track = [0, 0]  # ussr first
        self.space_track = [0, 0]  # 0 is start, 1 is earth satellite etc
        self.spaced_turns = [0, 0]
        self.extra_turn = [False, False]

        self.map = None
        self.cards = None

        # interfacing with the UI
        self.input_state = None
        self.output_queue = [[], []]

        self.hand = [[], []]  # ussr, us hands; list of 2 lists of Card objects
        self.removed_pile = []
        self.discard_pile = []
        self.draw_pile = []
        # ussr, us baskets; list of 2 lists of Card objects
        self.basket = [[], []]
        self.headline_bin = ['', '']

        # For new set the first created game to be the actual ongoing game.
        if Game.main is None:
            Game.main = self

    '''
    Starts a new game.
    '''

    def start(self, handicap=-2):

        self.started = True
        self.vp_track = 0  # positive for ussr
        self.turn_track = 1
        self.ar_track = 0
        self.ar_side = Side.USSR
        self.defcon_track = 5
        self.milops_track = [0, 0]  # ussr first
        self.space_track = [0, 0]  # 0 is start, 1 is earth satellite etc
        self.spaced_turns = [0, 0]
        self.extra_turn = [False, False]
        self.map = GameMap()
        self.cards = GameCards()
        self.handicap = handicap  # positive in favour of ussr

        self.stage_list = [
            self.put_start_USSR,
            self.put_start_US,
            self.put_start_extra,
            self.process_headline,
        ]
        self.stage_list.reverse()

        self.map.build_standard()
        self.deal()

        self.stage_complete()

    '''
    self.current returns current game stage.
    self.stage_list returns the full list of stages. The list starts with the
    last possible event, and ends with the current event. We pop items off the
    list when they are resolved.
    '''
    @property
    def current(self):
        return self.stage_list[-1]

    def stage_complete(self):
        self.stage_list.pop()()

    '''Output functions'''

    def output_both(self, out: Output):
        self.output_queue[Side.USSR].append(out)
        self.output_queue[Side.US].append(out)

    '''Here are functions used to manipulate the various tracks.'''

    def change_space(self, side: Side, n: int):
        '''
        Changes a player's advancement on the space track. This should be used
        instead of self.space_track[side] += n because it provides the correct VPs.

        Parameters
        ----------
        side : Side
            Player side. Can be Side.US or Side.USSR.
        n : int
            Number of steps on the space race to change by.
        '''

        y = side.vp_mult  # multiplier for VP - gives 1 for USSR and -1 for US
        self.space_track[side] += n

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

    # to add game terminate functionality EndGame()

    def change_vp(self, n: int):  # positive for ussr
        '''
        Changes the number of VPs. Positive values are in favour of the USSR player.

        Parameters
        ----------
        n : int
            Number of VPs to change by.
        '''
        self.vp_track += n
        if self.vp_track >= 20:
            print('USSR victory')
            # EndGame()
        if self.vp_track <= -20:
            print('US victory')
            # EndGame()
        print(f'Current VP: {self.vp_track}')

    def change_defcon(self, n: int):
        '''
        Changes the current DEFCON level. Keeps DEFCON level between 1-5.
        If DEFCON level goes below 2, the game ends.

        Parameters
        ----------
        n : int
            Number of levels to change by.
        '''
        previous_defcon = self.defcon_track
        self.defcon_track += min(n, 5 - self.defcon_track)
        if self.defcon_track < 2:
            print('Game ended by thermonuclear war')
            # EndGame()
        if previous_defcon > 2 and self.defcon_track == 2 and self.ar_track != 0 and 'NORAD' in self.basket[Side.US]:
            self.norad_influence()
        if n > 0:
            print(f'DEFCON level improved to {self.defcon_track}.')
        else:
            print(f'DEFCON level degraded to {self.defcon_track}.')

        # EndGame()

    def change_milops(self, side, n: int):
        '''
        Changes the level of military operations (milops) for a given side. Keeps milops level between 0-5.

        Parameters
        ----------
        side : Side
            Player side. Can be Side.US or Side.USSR.
        n : int
            Number of levels to change by.
        '''
        self.milops_track[side] += min(n, 5 - self.milops_track[side])

    # Here, we have the game initialisation stages.
    def put_start_USSR(self):
        '''
        Stage for USSR player to place starting influence anywhere in Eastern Europe.
        '''
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE],
            prompt='Place starting influence.',
            reps=1,  # TODO: FOR TESTING ONLY
            reps_unit='influence'
        )

    def put_start_US(self):
        '''
        Stage for US player to place starting influence anywhere in Western Europe.
        '''
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.US),
            CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE],
            prompt='Place starting influence.',
            reps=1,  # TODO: FOR TESTING ONLY
            reps_unit='influence'
        )

    def put_start_extra(self):
        '''
        Stage for player with handicap to place starting handicap influence in
        any country in which they currently have influence.
        '''
        if self.handicap == 0:
            self.stage_complete()
            return

        if self.handicap < 0:
            side = Side.US
        elif self.handicap > 0:
            side = Side.USSR

        self.input_state = Game.Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, side),
            self.map.has_influence(side),
            prompt='Place additional starting influence.',
            reps=side.vp_mult * self.handicap,
            reps_unit='influence'
        )

    def headline_callback(self, side: Side, name: str):
        self.input_state.reps -= 1
        self.hand[side].remove(name)
        self.headline_bin[side] = name
        return True

    def choose_headline(self, side: Side):
        self.input_state = Game.Input(
            side, InputType.SELECT_CARD_IN_HAND,
            partial(self.headline_callback, side),
            filter(lambda c: self.cards[c].info.can_headline, self.hand[side]),
            prompt='Select headline.'
        )

    def process_headline(self):
        '''
        Stage for both players to simultaneously choose their headline card.
        Due to UI constraints, USSR player chooses first, then the US player.
        All choices are then displayed.
        '''
        # TODO account for space race!
        # must append triggers in backwards order
        self.stage_list.append(self.ar_complete)
        self.stage_list.append(self.resolve_headline_order)
        self.stage_list.append(partial(self.choose_headline, Side.US))
        self.stage_list.append(partial(self.choose_headline, Side.USSR))

        # continue
        self.stage_complete()

    def resolve_headline_order(self):
        '''
        Stage to resolve the headline order.
        '''

        self.output_both(Game.Output(
            self.turn_track, self.ar_track,
            prompt=f'USSR selected {self.headline_bin[Side.USSR]} for headline.'
        ))
        self.output_both(Game.Output(
            self.turn_track, self.ar_track,
            prompt=f'US selected {self.headline_bin[Side.US]} for headline.'
        ))

        ussr_hl = self.headline_bin[Side.USSR]
        us_hl = self.headline_bin[Side.US]

        if us_hl == 'Defectors' or self.cards[us_hl].info.ops >= self.cards[ussr_hl].info.ops:
            # must append triggers in backwards order
            self.stage_list.append(partial(self.resolve_headline, Side.USSR))
            self.stage_list.append(partial(self.resolve_headline, Side.US))

        else:
            # must append triggers in backwards order
            self.stage_list.append(partial(self.resolve_headline, Side.US))
            self.stage_list.append(partial(self.resolve_headline, Side.USSR))

        self.stage_complete()

    def resolve_headline(self, side: Side):
        '''
        Stage to resolve the headline order.

        Parameters
        ----------
        side : Side
            Player side of the headline we are resolving.
        '''
        card_name = self.headline_bin[side]
        if card_name:
            self.stage_list.append(
                partial(self.dispose_card, side, card_name, event=True))
            self.stage_list.append(
                partial(self.trigger_event, side, card_name))
            self.headline_bin[side] = ''
        self.stage_complete()

    def ar_complete(self):
        if self.ar_track == Game.ars_by_turn[self.turn_track]:
            # TODO do next turn
            self.stage_list.append(self.end_of_turn)
        else:
            if self.ar_track == 0:
                self.ar_track = 1
                self.ar_side = Side.USSR
            else:
                if self.ar_side == Side.US:
                    self.ar_track += 1
                self.ar_side = self.ar_side.opp

            self.stage_list.append(self.ar_complete)
            self.stage_list.append(partial(self.select_card_and_action))

        self.stage_complete()

    def can_play_event(self, side: Side, card_name: str, resolve_check=False):
        '''
        Checks if all the prerequisites for the Event are fulfilled. Returns True
        if all prerequisites are fulfilled and the Event if not prevented, and False
        otherwise.

        Parameters
        ----------
        side : Side
            Side of the phasing player.
        card_name : str
            String representation of the card.
        resolve_check : bool, default=False
            True only when used in can_resolve_event_first below. Ensures that
            'Resolve Event first' does not appear as an option when the Event's
            prerequisites are not fulfilled.
        '''
        hand = self.hand[side]
        if card_name == 'Blank_4_Op_Card':
            return False
        elif card_name == 'The_China_Card':
            return False
        elif card_name == 'UN_Intervention':
            return any(
                map(lambda c: self.cards[c].info.owner == side.opp, hand))
        elif card_name == 'Defectors':
            return False
        elif card_name == 'Special_Relationship':
            return True if self.map['UK'].control == Side.US else False
        elif card_name == 'NATO':
            return True if 'Warsaw_Pact_Formed' in self.basket[
                Side.US] or 'Marshall_Plan' in self.basket[Side.US] else False
        elif card_name == 'Kitchen_Debates':
            us_count = [1 for n in CountryInfo.ALL if self.map[n].control ==
                        Side.US and self.map[n].info.battleground == True]
            ussr_count = [1 for n in CountryInfo.ALL if self.map[n].control ==
                          Side.USSR and self.map[n].info.battleground == True]
            return True if us_count > ussr_count else False
        elif card_name == 'Arab_Israeli_War':
            return False if 'Camp_David_Accords' in self.basket[Side.US] else True
        elif card_name == 'The_Cambridge_Five':
            return False if self.turn_track >= 8 else True
        elif card_name == 'Socialist_Governments':
            return False if 'The_Iron_Lady' in self.basket[Side.US] else True
        elif card_name == 'One_Small_Step':
            return True if self.space_track[side] < self.space_track[side.opp] else False
        elif card_name == 'Muslim_Revolution':
            return False if 'AWACS_Sale_to_Saudis' in self.basket[Side.US] else True
        elif card_name == 'OPEC':
            return False if 'North_Sea_Oil' in self.basket[Side.US] or 'North_Sea_Oil' in self.removed_pile else True
        elif card_name == 'Willy_Brandt':
            return False if 'Tear_Down_This_Wall' in self.basket[Side.US] else True
        elif card_name == 'Solidarity':
            return False if 'John_Paul_II_Elected_Pope' in self.basket[Side.US] else True
        elif card_name == 'Star_Wars':
            return True if self.space_track[Side.US] > self.space_track[Side.USSR] else False
        elif card_name == 'Wargames':
            return True if self.defcon_track == 2 else False
        else:
            if resolve_check:
                return False if self.cards[card_name].info.owner == Side.NEUTRAL else True
            else:
                return True if self.cards[card_name].info.owner != side.opp else False

    def can_resolve_event_first(self, side: Side, card_name: str):
        '''
        Checks if the phasing player can resolve the card's Event first.
        True if:
        1. Card is opponent-owned.
        2. All the prerequisites for the event are fulfilled.

        Parameters
        ----------
        side : Side
            Side of the player who plays the card.
        card_name : str
            Card itself, or string representation of the card.
        '''
        return False if self.cards[card_name].info.owner != side.opp else self.can_play_event(side, card_name, resolve_check=True)

    def can_place_influence(self, side: Side, card_name: str):
        '''
        Checks if the phasing player can place influence using the card.
        False for scoring cards and True otherwise.
        '''
        return False if self.cards[card_name].info.ops == 0 else True

    def can_realign_at_all(self, side: Side):
        '''
        Checks if the player of <side> can use realignment on any country.
        True if there is at least 1 country suitable for realignment.
        '''
        return any(map(
            lambda n: self.map.can_realignment(self, n, side), CountryInfo.ALL))

    def can_coup_at_all(self, side: Side):
        '''
        Checks if the player of <side> can coup in any country.
        True if there is at least 1 country suitable for coup.
        '''
        return any(map(
            lambda n: self.map.can_coup(self, n, side), CountryInfo.ALL))

    def can_space(self, side: Side, card_name: str):
        '''
        Checks if the player of <side> can use their selected <card> to advance
        their space race marker.
        '''
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
        def enough_ops(self, side: Side, card_name: str):
            if self.space_track[side] == 8:
                return False
            if self.space_track[side] == 7 and self.get_global_effective_ops(side, card.info.ops) == 4:
                return True
            elif self.space_track[side] >= 5 and self.get_global_effective_ops(side, card.info.ops) >= 3:
                return True
            elif self.get_global_effective_ops(side, self.cards[card_name].info.ops) >= 2:
                return True
            else:
                return False

        return available_space_turn(self, side) and enough_ops(self, side, card_name)

    def select_card_and_action(self, side: Side = Side.NEUTRAL):
        '''
        Stage for a single player to choose a card in hand to play.

        Parameters
        ----------
        side : Side
            Side of the choosing player.
        '''

        if side == Side.NEUTRAL:
            side = self.ar_side

        self.input_state = Game.Input(
            side, InputType.SELECT_CARD_IN_HAND,
            partial(self.card_callback, side),
            filter(lambda c: self.cards[c].is_playable, self.hand[side]),
            prompt='Select a card in hand to play.'
        )

    def card_callback(self, side: Side, card_name: str):
        if self.cards[card_name].info.type == 'Scoring':
            self.input_state.reps -= 1
            self.stage_list.append(
                partial(self.resolve_card_action, side,
                        card_name, CardAction.PLAY_EVENT.name)
            )
        else:
            self.select_action(side, card_name, False)
        return True

    def action_callback(self, side: Side, card_name: str, action_name: str):
        self.input_state.reps -= 1
        self.stage_list.append(
            partial(self.resolve_card_action, side, card_name, action_name)
        )
        return True

    def select_action(self, side: Side, card_name: str, is_event_resolved: bool = False):
        '''
        Stage where the player has already chosen a card and now chooses an action to do with the card.
        Checks are made to ensure that the actions made available to the player are feasible actions,
        before displaying them to the player as possible actions.

        Parameters
        ----------
        side : Side
            Side of the player who plays the card.
        card_name : str
            String representation of the card.
        is_event_resolved : bool, default=False
            True if the opponent event has already been resolved.

        Notes
        -----
        If the player chooses the resolve the opponent's Event first, the Event will be triggered,
        and this stage will be triggered again with the 'Resolve Event first' removed.
        '''
        bool_arr = [
            not is_event_resolved and self.can_play_event(side, card_name),
            not is_event_resolved and self.can_resolve_event_first(
                side, card_name),
            self.can_place_influence(side, card_name),
            self.can_realign_at_all(side),
            self.can_coup_at_all(side),
            self.can_space(side, card_name)
        ]

        self.input_state = Game.Input(
            side, InputType.SELECT_CARD_IN_HAND,
            partial(self.action_callback, side, card_name),
            map(lambda e: CardAction(e[0]).name,
                filter(lambda e: e[1], enumerate(bool_arr))),
            prompt=f'Select an action for {card_name}.'
        )

    def resolve_card_action(self, side: Side, card_name: str, action_name: str):
        '''
         This function should lead to card_operation_realignment, card_operation_coup,
         or card_operation_influence, or a space race function.
         '''

        action = CardAction[action_name]
        card = self.cards[card_name]
        opp_event = card.info.owner == side.opp

        if action == CardAction.PLAY_EVENT:

            self.stage_list.append(
                partial(self.dispose_card, side, card_name, event=True))
            self.stage_list.append(
                partial(self.trigger_event, side, card_name))

        elif action == CardAction.RESOLVE_EVENT_FIRST:

            self.stage_list.append(
                partial(self.dispose_card, side, card_name, event=True))
            self.stage_list.append(
                partial(self.select_action, side, card_name, is_event_resolved=True))
            self.stage_list.append(
                partial(self.trigger_event, side, card_name))

        elif action == CardAction.SPACE:

            self.stage_list.append(partial(self.dispose_card, side, card_name))
            self.stage_list.append(partial(self.space, side, card_name))

        elif action == CardAction.INFLUENCE:

            self.stage_list.append(
                partial(self.dispose_card, side, card_name, event=opp_event))
            if opp_event:
                self.stage_list.append(
                    partial(self.trigger_event, side, card_name))
            self.stage_list.append(
                partial(self.card_operation_influence, side, card_name))

        elif action == CardAction.REALIGNMENT:

            self.stage_list.append(
                partial(self.dispose_card, side, card_name, event=opp_event))
            if opp_event:
                self.stage_list.append(
                    partial(self.trigger_event, side, card_name))
            self.stage_list.append(
                partial(self.card_operation_realignment, side, card_name))

        elif action == CardAction.COUP:

            self.stage_list.append(
                partial(self.dispose_card, side, card_name, event=opp_event))
            if opp_event:
                self.stage_list.append(
                    partial(self.trigger_event, side, card_name))
            self.stage_list.append(
                partial(self.card_operation_coup, side, card_name))

        self.stage_complete()

    # Utility functions used in stages

    def dispose_card(self, side, card_name: str, event=False):
        '''
        Stage that deals with the card after it has been used.
        Calls to this function should come after the event / use of operations / space race.

        Parameters
        ----------
        side : Side
            Side of the player who plays the card.
        card_name : str
            Card itself, or string representation of the card.
        event : bool, default=False
            True if the event has been resolved.
        '''
        card = self.cards[card_name]
        if card_name == 'The_China_Card':
            self.move_china_card(side)
        elif event and card.info.event_unique:
            self.removed_pile.append(card_name)
        else:
            self.discard_pile.append(card_name)

        self.stage_complete()

    def move_china_card(self, side: Side):
        '''
        Moves and flips the China Card after it has been used.

        Parameters
        ----------
        side : Side
            Side of the player who plays the China Card.
        '''
        receipient = self.hand[side.opp]
        receipient.append('The China Card')
        self.cards['The China Card'].is_playable = False

    def get_global_effective_ops(self, side: Side, raw_ops: int):
        '''
        Gets the effective operations value of the card, bound to [1,4]. Accounts for
        only global effects like Containment, Brezhnev_Doctrine and Red_Scare_Purge.

        Does not account for local effects like additional operations points from the use
        of the China Card in Asia, or the use of operations points in SEA when Vietnam Revolts
        is active.

        Parameters
        ----------
        side : Side
            Side of the player who plays the China Card.
        raw_ops : int
            Unmodified operations value of the card.
        '''
        modifier = 0
        if side == Side.USSR and 'Brezhnev_Doctrine' in self.basket[side]:
            modifier += 1
        if side == Side.US and 'Containment' in self.basket[side]:
            modifier += 1
        if 'Red_Scare_Purge' in self.basket[side.opp]:
            modifier -= 1
        return min(max([raw_ops + modifier, 1]), 4)

    def calculate_nato_countries(self):
        '''
        Calculates which countries are affected by NATO. Accounts for cancellations
        like De_Gaulle_Leads_France and Willy_Brandt. Returns a list of country name
        strings with NATO effect protection.
        '''
        europe = list(CountryInfo.REGION_ALL[MapRegion.EUROPE])
        if 'NATO' in self.basket[Side.US]:
            if 'De_Gaulle_Leads_France' in self.basket[Side.USSR]:
                europe.remove('France')
            if 'Willy_Brandt' in self.basket[Side.USSR]:
                europe.remove('West_Germany')
        return europe

    def trigger_event(self, side: Side, card_name: str):
        '''
        Wrapper for triggering an event. Takes in a card_name and runs the associated
        card event function.

        Parameters
        ----------
        side : Side
            Side of the player who plays the card.
        card_name : str
            String representation of the card.
        '''
        Game.card_function_mapping[card_name](self, side)

    def choose_random_card(self, side: Side):
        '''
        Wrapper for choosing a random card from a player's hand.
        Used in Terrorism, Grain_Sales_to_Soviets, Five_Year_Plan card Events.
        Returns a random Card object which needs to be placed.

        Parameters
        ----------
        side : Side
            Side of the player whose hand we pick the card from.
        '''
        return self.hand[side].pop(random.randint(1, len(self.hand[side])))

    '''
    Here we have different stages for card uses. These include the use of influence,
    operations points for coup or realignment, and also on the space race.
    '''

    def ops_influence_callback(self, side, name):
        c = self.map[name]

        # may no longer need this eventually if we ensure options are always correct
        if self.input_state.reps == 1 and c.control == side.opp:
            return False

        if c.control == side.opp:
            self.input_state.reps -= 2
        else:
            self.input_state.reps -= 1
        c.increment_influence(side)

        if self.input_state.reps == 1:
            for n in self.input_state.selection:
                if self.map[n].control == side.opp:
                    self.input_state.remove_option(n)

        return True

    def card_operation_influence(self, side: Side, card_name: str):
        '''
        Stage when a player is given the opportunity to place influence. Provides a list
        of countries where influence can be placed into and waits for player input.

        TODO: Does not currently check the player baskets for China Card and Vietnam effects.

        Parameters
        ----------
        side : Side
            Side of the player who is placing influence.
        card_name : str
            String representation of the card used for influence operations.
        '''

        card = self.cards[card_name]
        effective_ops = self.get_global_effective_ops(side, card.info.ops)

        self.input_state = Game.Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.ops_influence_callback, side),
            filter(lambda n: self.map.can_place_influence(
                n, side, effective_ops), CountryInfo.ALL),
            prompt=f'Place operations from {card_name} as influence.',
            reps=effective_ops,
            reps_unit='operations'
        )

    def realignment_callback(self, side, name):

        self.input_state.reps -= 1
        self.map.realignment(self, name, side)

        return True

    def card_operation_realignment(self, side: Side, card_name: str):
        '''
        Stage when a player is given the opportunity to use realignment. Provides a list
        of countries where realignment can take place and waits for player input.

        TODO: Does not currently check the player baskets for China Card and Vietnam effects.

        Parameters
        ----------
        side : Side
            Side of the player who is placing influence.
        card_name : str
            String representation of the card used for the realignment operations.
        '''
        card = self.cards[card_name]
        effective_ops = self.get_global_effective_ops(side, card.info.ops)

        self.input_state = Game.Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.realignment_callback, side),
            filter(lambda n: self.map.can_realignment(
                self, n, side), self.map.ALL),
            prompt=f'Select a country for realignment using operations from {card_name}.',
            reps=effective_ops,
            reps_unit='operations'
        )

    def coup_callback(self, side, effective_ops, name):
        '''
        TODO: Does not currently check the player baskets for China Card and Vietnam effects.
        TODO: Latin American DS, Iran-contra
        '''
        self.input_state.reps -= 1
        self.map.coup(self, name, side, effective_ops, random.randint(1, 6))
        return True

    def card_operation_coup(self, side: Side, card_name: str, restricted_list: Sequence[str] = None):
        '''
        Stage when a player is given the opportunity to coup. Provides a list
        of countries which can be couped and waits for player input.

        TODO: Does not currently check the player baskets for China Card and Vietnam effects.
        TODO: Latin American DS, Iran-contra

        Parameters
        ----------
        side : Side
            Side of the player who is placing influence.
        card_name : str
            String representation of the card used for the coup.
        restricted_list : Sequence[str], default=None
            Further restricts the available_list via intersection of two sets.
            It should be a list of country_names. Use of restricted_list is intended
            for cards like Junta, Che, Ortega where there are further restrictions.
        '''
        card = self.cards[card_name]
        effective_ops = self.get_global_effective_ops(
            side, card.info.ops)
        if restricted_list is None:
            restricted_list = CountryInfo.ALL

        self.input_state = Game.Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.coup_callback, side, effective_ops),
            filter(lambda n: self.map.can_coup(self, n, side)
                   and n in restricted_list, CountryInfo.ALL),
            prompt=f'Select a country to coup using operations from {card_name}.',
        )

    def space(self, side: Side, card_name: str):
        '''
        The action of spacing a card after you have selected a card.

        Parameters
        ----------
        side : Side
            Side of the player who has chosen to advance on the space race.
        card_name : str
            Card object used in the advacement of the space race.
        '''

        if self.space_track[side] in [0, 2, 4, 6]:
            modifier = 0
        elif self.space_track[side] in [1, 3, 5]:
            modifier = -1
        else:
            modifier = 1
        roll = random.randint(1, 6)

        if roll + modifier <= 3:
            self.change_space(side, 1)
            print(f'Success with roll of {roll}.')
        else:
            print(f'Failure with roll of {roll}.')

        self.spaced_turns[side] += 1

        self.stage_complete()  # TODO the die roll in the UI

    def event_influence_callback(self, country_function, side: Side, name: str) -> bool:
        '''
        event_influence_callback is used as the callback function for modifying influence.
        This is mostly used for card events where the player has to choose
        which regions in which to directly insert influence.

        Examples of cards that use this function are: VOA, Decolonization, OAS_Founded, Junta.
        See examples in the card functions.

        country_function is the function that the country will apply.
        For example, for cards like COMECON / Decolonization,
            use partial(Country.increment_influence, Side.USSR)
        For Voice Of America, specify max_per_option in input_state as 2, then
            use partial(Country.decrement_influence, Side.USSR).
        For a card like Junta you want to get an increment by 2 function, so
            use partial(Country.increment_influence, side, amt=2).
        For a card like Warsaw Pact / Muslim_Revolution / Truman Doctrine
            use partial(Country.remove_influence, Side.US).
        '''
        self.input_state.reps -= 1
        return country_function(self.map[name], side)

    # TODO eventually, deprecate
    def event_influence(self, side: Side, ops: int, available_list: list, can_split: bool, positive: bool, limit: int = None, all: bool = False, EEU: bool = False):
        '''
        Stage where a player is given the opportunity to modify influence via an Event.
        Examples of cards that use this function: VOA, Decolonization, OAS_Founded, Junta.

        Parameters
        ----------
        side : Side
            Side of the player who has the opportunity to choose which countries to modify influence.
        ops : int
            Number of influence to be modified.
        available_list : list
            The list of country name strings that can be manipulated by the effect.
        can_split : bool
            True where the influence adjustment can affect multiple countries.
            False where the influence adjustment can only affect one chosen country.
        positive: bool
            True for adding influence.
            False for removing influence.
        limit : int, default=None
            The maximum influence adjustment that can be made to a single country.
        all : bool, default=False
            True where influence affects all the influence of a side in the country.
            Cards that have all=True: Warsaw_Pact_Formed, Muslim_Revolution, Truman_Doctrine
        EEU : bool, default=False
            True only for EEU. Hardcoded for EEU's changing {ops} parameter from Early War to Late War.

        Notes
        -----
        This function is tremendously huge and is used in up to 15% of all card Events.
        It is currently still buggy (see google sheet for more information).
        '''

        available_list_values = [
            str(self.map[n].info.country_index) for n in available_list]
        late_war = self.turn_track >= 8
        verb = 'add' if positive else 'remove'
        guide_msg = f'You may {verb} {(late_war*EEU+1) * ops} influence in these countries. Type in their country indices, separated by commas (no spaces).'
        guide_msg_all = f'You may remove influence completely in {ops} of these countries. Type in their country indices, separated by commas (no spaces).'
        limit_msg = f'You are limited to modifying {limit} influence per country.'
        rejection_msg = f'Please key in {ops} comma-separated values.'

        while True:
            self.prompt_side(side)
            if all:
                print(guide_msg_all)
            else:
                print(guide_msg)
            if limit != None:
                print(limit_msg)
            for available_name in available_list:
                print(
                    f'{self.map[available_name].info.country_index}\t{self.map[available_name].info.name}')

            user_choice = UI.ask_for_input(ops, rejection_msg, can_be_less=all)
            if user_choice == None:
                break

            is_input_all_available = (
                len(set(user_choice) - set(available_list_values)) == 0)
            is_input_not_singular = True if can_split else (
                len(set(user_choice)) == 1)
            is_input_not_limited = True if limit == None else max(
                user_choice.count(x) for x in set(user_choice)) <= limit

            if all:
                if is_input_all_available:
                    for country_index in user_choice:
                        name = self.map.index_country_mapping[int(
                            country_index)]
                        if ops in [2, 4]:  # this is total countries we can remove from, not card ops
                            self.map[name].set_influence(
                                self.map[name].influence[Side.USSR], 0)  # hardcoded for warsaw and muslim revolution
                        elif ops == 1:
                            self.map[name].set_influence(
                                0, self.map[name].influence[Side.US])  # hardcoded for truman
                    break

            elif is_input_all_available and is_input_not_singular and is_input_not_limited:
                for country_index in user_choice:
                    name = self.map.index_country_mapping[int(country_index)]
                    if side == Side.USSR:
                        if positive:
                            self.map[name].change_influence(1, 0)
                        else:
                            self.map[name].change_influence(0, -1)
                    elif side == Side.US:
                        if positive:
                            self.map[name].change_influence(0, 1)
                        else:
                            if EEU and late_war:
                                self.map[name].change_influence(-2, 0)
                            else:
                                self.map[name].change_influence(-1, 0)
                break
            else:
                print('\nYour input cannot be accepted.')

    # The following stages tend to be for cards that are a little more specific.

    def select_multiple(self, side: Side, statements: list, values: list = None):
        '''
        Stage where a player is given the opportunity to select from multiple choices.

        Parameters
        ----------
        side : Side
            Side of the player who has chosen to advance on the space race.
        statements : list
            List of strings to be displayed to the player. Statements are automatically
            enumerated if {values} is NoneType.
        values : list, default=None
            List of accompanying values that match statements one-for-one. Usually allows
            every item in {statements} to be uniquely identified; in the case of cards --
            their card indices; or countries -- their country indices.
        '''
        guide_msg = f'Type in a single value.'
        rejection_msg = f'Please key in a single value.'

        available_list = statements
        available_list_values = [str(i) for i in range(len(statements))]

        if values == None:
            while True:
                self.prompt_side(side)
                print(guide_msg)
                for i, available_name in enumerate(available_list):
                    print(f'{i}\t{available_name}')

                user_choice = UI.ask_for_input(1, rejection_msg)
                if user_choice == None:
                    break

                if len(set(user_choice) - set(available_list_values)) == 0:
                    return int(user_choice[0])
                else:
                    print('\nYour input cannot be accepted.')
        else:
            while True:
                self.prompt_side(side)
                print(guide_msg)
                for (available_name, i) in zip(available_list, values):
                    print(f'{i}\t{available_name}')

                user_choice = UI.ask_for_input(1, rejection_msg)
                if user_choice == None:
                    break

                if len(set(user_choice) - set(values)) == 0:
                    return int(user_choice[0])
                else:
                    print('\nYour input cannot be accepted.')

    def may_discard_callback(self, side: Side, opt: str, did_not_discard_fn: Callable[[], None] = lambda: None):

        if opt == Game.Input.OPTION_DO_NOT_DISCARD:
            did_not_discard_fn()
            self.input_state.reps -= 1
            return True

        if opt not in self.hand[side]:
            return False

        self.hand[side].remove(opt)
        self.discard_pile.append(opt)
        self.input_state.reps -= 1
        return True

    def may_discard_card(self, side: Side, blockade=False):
        '''
        Stage where a player is given the opportunity to discard a single card.
        Used in the Blockade discard, Latin_American_Debt_Crisis discard, and also the space race buff.

        # TODO: the space race buff has not yet been coded

        Parameters
        ----------
        side : Side
            Side of the player who is to discard.
        blockade : bool, default=True
            True if the condition to discard has to be 3 operations value or higher.
        '''
        guide_msg = f'You may discard a card. Type in the card index.'
        rejection_msg = f'Please key in a single value.'

        hand = self.hand[side]
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

    def pick_from_discarded(self, side: Side):
        '''
        Stage where a player is given the opportunity to pick a card from the discard pile.
        Used in the Star_Wars (event happens immediately) and Salt_Negotiations.
        Returns selected card which has to be placed somewhere.

        # TODO: not sure if the interpretation for Star_Wars is a 'may' or a 'must'

        Parameters
        ----------
        side : Side
            Side of the player who is to pick from the discard pile.
        '''
        hand = self.hand[Side.US]
        available_list = ['Do not take a card.']
        available_list_values = ['0']
        available_list.extend(
            card.info.name for card in self.discard_pile if card.info.type != 'Scoring')
        available_list_values.extend(
            [str(self.cards[n].info.card_index) for n in available_list[1:]])
        choice = self.select_multiple(
            side, available_list, values=available_list_values)
        if choice == 0:
            return None
        else:
            name = self.cards.index_card_mapping[choice]
            return hand.pop(hand.index(name))

    def forced_to_missile_envy(self):
        # check first if the player has as many scoring cards as turns
        # if True, then player is given choice as to which scoring card they
        # can play. this stage is then triggered again at a later stage.
        pass

    def select_take_8_rounds(self):
        pass

    def quagmire_discard(self):
        # '''
        # The player must discard a card if they are holding suitable discards.
        # Player is given a list of suitable discards. Card has to be at least
        # 2 effective ops. If there are only scoring cards left..
        # '''
        # available_list = [
        #     card.info.name for card in hand if self.get_global_effective_ops(side, card.info.ops) >= 2]
        #
        # if 'The_China_Card' in available_list:
        #     available_list.pop(available_list.index('The_China_Card'))
        # if len(available_list) == 0:
        #     pass  # may only play scoring cards ```
        #
        # available_list_values = [
        #     str(self.cards[n].info.card_index) for n in available_list]
        #
        # while True:
        #     self.prompt_side(side)
        #     print(guide_msg)
        #     for available_name in available_list:
        #         print(
        #             f'{self.cards[available_name].info.card_index}\t{self.cards[available_name].info.name}')
        #
        #     user_choice = UI.ask_for_input(1, rejection_msg)
        #     if user_choice == None:
        #         break
        #
        #     if len(set(user_choice) - set(available_list_values)) == 0:
        #         name = self.cards.index_card_mapping[int(user_choice[0])]
        #         self.discard_pile.append(hand.pop(hand.index(name)))
        #         break
        #     else:
        #         print('\nYour input cannot be accepted.')
        # return 'discard successful'
        pass

    def norad_influence(self):
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.US),
            self.map.has_us_influence,
            prompt="Place NORAD influence.",
            reps_unit="influence"
        )

    def cuba_missile_remove(self):
        pass

    def headline(self):
        # decide if it is going to be joint_choose_headline or separated
        # modify top to use this function instead
        pass

    def deal(self):

        # if turn 4, add mid war cards into draw pile and shuffle, same for turn 8 for late war cards
        if self.turn_track == 1:
            # self.hand[Side.USSR].append(self.cards.early_war.pop(
            # self.cards.early_war.index('Asia_Scoring')))  # for testing of specific cards
            self.draw_pile.extend(self.cards.early_war)
            self.cards.early_war = []
            random.shuffle(self.draw_pile)
        if self.turn_track == 4:
            self.draw_pile.extend(self.cards.mid_war)
            self.cards.mid_war = []
            random.shuffle(self.draw_pile)
        if self.turn_track == 8:
            self.draw_pile.extend(self.cards.late_war)
            self.cards.late_war = []
            random.shuffle(self.draw_pile)

        if 1 <= self.turn_track <= 3:
            handsize_target = [8, 8]
        else:
            handsize_target = [9, 9]

        # TODO: FOR TESTING ONLY
        if self.turn_track == 1:
            handsize_target = [12, 12]

        # Ignore China Card if it is in either hand
        if 'The_China_Card' in self.hand[Side.USSR]:
            handsize_target[Side.USSR] += 1
        elif 'The_China_Card' in self.hand[Side.US]:
            handsize_target[Side.US] += 1

        next_side = Side.USSR
        while not list(map(len, self.hand)) == handsize_target:
            if len(self.hand[next_side]) == handsize_target[next_side]:
                next_side = next_side.opp
                continue

            self.hand[next_side].append(self.draw_pile.pop())
            next_side = next_side.opp

            if not self.draw_pile:
                # if draw pile exhausted, shuffle the discard pile and put it as the new draw pile
                self.draw_pile = self.discard_pile
                self.discard_pile = []
                random.shuffle(self.draw_pile)

    # need to make sure next_turn is only called after all extra rounds
    def end_of_turn(self):
        # 0. Clear all events that only last until the end of turn.
        def clear_baskets(self):
            us_clearing = ['Containment', 'Nuclear_Subs',
                           'Chernobyl', 'Iran_Contra_Scandal']
            ussr_clearing = ['Vietnam_Revolts', 'Brezhnev_Doctrine',
                             'Yuri_and_Samantha', 'Iran_Contra_Scandal']
            either_clearing = ['Red_Scare_Purge',
                               'Cuban_Missile_Crisis', 'Salt_Negotiations', 'Latin_American_Death_Squads']
            for item in ussr_clearing:
                if item in self.basket[Side.USSR]:
                    self.removed_pile.append(self.basket[Side.US].pop(
                        self.basket[Side.US].index(item)))
            for item in us_clearing:
                if item in self.basket[Side.US]:
                    self.removed_pile.append(self.basket[Side.US].pop(
                        self.basket[Side.US].index(item)))
            for item in either_clearing:
                if item in self.basket[Side.USSR]:
                    self.removed_pile.append(self.basket[Side.USSR].pop(
                        self.basket[Side.US].index(item)))
                elif item in self.basket[Side.US]:
                    self.removed_pile.append(self.basket[Side.US].pop(
                        self.basket[Side.US].index(item)))

        # 1. Check milops
        def check_milops(self):
            milops_vp_change = map(
                lambda x: x - self.defcon_track if x < self.defcon_track else 0,
                self.milops_track
            )
            swing = 0
            for s in [Side.USSR, Side.US]:
                swing += s.vp_mult * milops_vp_change[s]
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
                    'The_China_Card')].is_playable = True
            elif 'The_China_Card' in self.hand[Side.US]:
                self.hand[Side.US][self.hand[Side.US].index(
                    'The_China_Card')].is_playable = True

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
        clear_baskets(self)
        check_milops(self)
        check_for_scoring_cards(self)
        flip_china_card(self)
        advance_turn_marker(self)  # turn marker advanced before final scoring
        final_scoring(self)
        self.change_defcon(1)
        self.deal()  # turn marker advanced before dealing
        self.process_headline()

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

    card_event_functions should return the next location of the card.
    This can be one of the following:
    ['self.basket[Side.USSR]', 'self.basket[Side.US]', 'self.discard_pile', 'self.removed_pile']
    '''

    def _Asia_Scoring(self, side):
        # TODO: ADD SHUTTLE DIPLOMACY AND FORMOSAN RESOLUTION
        self.score(MapRegion.ASIA, 3, 7, 9)
        self.stage_complete()

    def _Europe_Scoring(self, side):
        self.score(MapRegion.EUROPE, 3, 7, 120)
        self.stage_complete()

    def _Middle_East_Scoring(self, side):
        self.score(MapRegion.MIDDLE_EAST, 3, 5, 7)
        self.stage_complete()

    def _Duck_and_Cover(self, side):
        self.change_defcon(-1)
        self.change_vp(-(5 - self.defcon_track))
        self.stage_complete()

    def _Five_Year_Plan(self, side):
        pass

    def _The_China_Card(self, side):
        'No event.'
        pass

    def _Socialist_Governments(self, side):
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.decrement_influence, Side.US),
            filter(lambda n: self.map[n].has_us_influence,
                   CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]),
            prompt='Place influence from Socialist Governments.',
            reps=3,
            reps_unit='influence',
            max_per_option=2
        )

    def _Fidel(self, side):
        cuba = self.map['Cuba']
        cuba.set_influence(max(3, cuba.influence[Side.USSR]), 0)
        self.stage_complete()

    def _Vietnam_Revolts(self, side):
        # TODO
        self.stage_complete()

    def _Blockade(self, side):
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_DISCARD_OPTIONAL,
            partial(self.may_discard_callback, Side.US,
                    did_not_discard_fn=partial(self.map['West_Germany'].remove_influence, Side.US)),
            chain(
                filter(
                    lambda n: n != 'The_China_Card' and self.get_global_effective_ops(
                        side, self.cards[n].info.ops) >= 3,
                    self.hand[Side.US]
                ),
                [Game.Input.OPTION_DO_NOT_DISCARD]),
            prompt='You may discard a card. If you choose not to discard a card, US loses all influence in West Germany.',
        )

    def _Korean_War(self, side):
        self._War('South_Korea', Side.USSR)

    def _Romanian_Abdication(self, side):
        romania = self.map['Romania']
        romania.set_influence(max(3, romania.influence[Side.USSR]), 0)
        self.stage_complete()

    def _War(self, country_name: str, side: Side, lower: int = 4, win_vp: int = 2, win_milops: int = 2):
        country = self.map[country_name]
        roll = random.randint(1, 6)
        modifier = sum([self.map[adjacent_country].control ==
                        side.opp for adjacent_country in country.info.adjacent_countries])
        if roll - modifier >= lower:
            self.change_vp(win_vp * side.vp_mult)
            self.change_milops(side, win_milops)
            if side == Side.US:
                country.change_influence(
                    -country.influence[side.opp], country.influence[side.opp])
            if side == Side.USSR:
                country.change_influence(
                    country.influence[side.opp], -country.influence[side.opp])
            print(f'Success with roll of {roll}.')
        else:
            print(f'Failure with roll of {roll}.')

    def _Arab_Israeli_War(self, side):
        is_event_playable = False if 'Camp_David_Accords' in self.basket[Side.US] else True
        if is_event_playable:
            self._War('Israel', Side.USSR)
        return self.discard_pile

    def _COMECON(self, side):
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            filter(lambda n: self.map[n].control != Side.US,
                   CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]),
            prompt='Place influence from COMECON.',
            reps=4,
            reps_unit='influence',
            max_per_option=1
        )

    def _Nasser(self, side):
        egypt = self.map['Egypt']
        egypt.change_influence(2, -math.ceil(egypt.influence[Side.US] / 2))
        self.stage_complete()

    def _Warsaw_Pact_Formed(self, side):
        # will not offer the first option if there is no US influence
        eastern_europe = CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]
        available_list = [
            name for name in eastern_europe if self.map[name].has_us_influence]
        if len(available_list) == 0:
            binary_outcome = 1
        else:
            statements = ['Remove all US influence from 4 countries in Eastern Europe',
                          'Add 5 USSR Influence to any countries in Eastern Europe']
            binary_outcome = self.select_multiple(Side.USSR, statements)
        if binary_outcome == 0:
            self.event_influence(Side.USSR, 4, available_list,
                                 can_split=True, positive=False, limit=1, all=True)
        elif binary_outcome == 1:
            available_list = [
                n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]]
            self.event_influence(Side.USSR, 5, available_list,
                                 can_split=True, positive=True, limit=2)

        return self.basket[Side.US]

    def _De_Gaulle_Leads_France(self, side):
        self.map['France'].change_influence(1, -2)
        # for NATO cancellation effect
        self.basket[Side.USSR].append('De Gaulle Leads France')
        self.stage_complete()

    def _Captured_Nazi_Scientist(self, side):
        self.change_space(side, 1)
        self.stage_complete()

    def _Truman_Doctrine(self, side):
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.remove_influence, Side.USSR),
            filter(
                lambda n: self.map[n].control == Side.NEUTRAL and self.map[n].has_ussr_influence,
                CountryInfo.REGION_ALL[MapRegion.EUROPE]
            ),
            prompt="Truman Doctrine: Select a country in which to remove all USSR influence."
        )

    def _Olympic_Games(self, side):
        statements = [
            'Participate and sponsor has modified die roll (+2).',
            'Boycott: DEFCON level degrades by 1 and sponsor may conduct operations as if they played a 4 op card.']
        binary_outcome = self.select_multiple(side.opp, statements)
        if binary_outcome == 0:
            # probability of eventer eventually winning
            if random.uniform(0, 1) < 13 / 16:
                self.change_vp(2 * side.vp_mult)
            else:
                self.change_vp(-2 * side.vp_mult)
        elif binary_outcome == 1:
            self.change_defcon(-1)
            self.select_action(side, Card('Blank_4_Op_Card'))
        return self.discard_pile

    def _NATO(self, side):
        return self.basket[Side.US] if self.can_play_event(side, 'NATO') else self.discard_pile

    def _Independent_Reds(self, side):
        base = ['Yugoslavia', 'Romania',
                'Bulgaria', 'Hungary', 'Czechoslovakia']
        available_list = [
            n for n in base if self.map[n].has_ussr_influence]
        available_list_values = [
            str(self.map[n].info.country_index) for n in available_list]

        guide_msg = f'You may add influence in these countries to equal USSR influence. Type in the country index.'
        rejection_msg = f'Please key in a single appropriate value.'

        pass

    def _Marshall_Plan(self, side):

        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.US),
            filter(lambda n: self.map[n].control != Side.USSR,
                   CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]),
            prompt='Place influence from Marshall Plan.',
            reps=7,
            reps_unit='influence',
            max_per_option=1
        )
        self.basket[Side.US].append('Marshall Plan')

    def _Indo_Pakistani_War(self, side):
        statements = ['India',
                      'Pakistan']
        choice = self.select_multiple(side, statements)
        if choice == 0:
            self._War('India', side)
        elif choice == 1:
            self._War('Pakistan', side)
        return self.discard_pile

    def _Containment(self, side):
        self.basket[Side.US].append('Containment')
        self.stage_complete()

    def _CIA_Created(self, side):
        pass

    def _US_Japan_Mutual_Defense_Pact(self, side):
        japan = self.map['Japan']
        japan.set_influence(japan.influence[Side.USSR], max(
            japan.influence[Side.USSR] + 4, japan.influence[Side.US]))
        return self.basket[Side.US]

    def _Suez_Crisis(self, side):
        suez = ['France', 'UK', 'Israel']

        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.decrement_influence, Side.USSR),
            filter(lambda n: self.map[n].has_us_influence, suez),
            prompt='Remove US influence using Suez Crisis.',
            reps=4,
            reps_unit='influence',
            max_per_option=2
        )

    def _East_European_Unrest(self, side):

        if 8 <= self.turn_track <= 10:
            dec = 2
        else:
            dec = 1

        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback, partial(
                Country.decrement_influence, amt=dec), Side.USSR),
            filter(lambda n: self.map[n].has_ussr_influence,
                   CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]),
            prompt='Remove USSR influence using East European Unrest.',
            reps=3,
            reps_unit='influence',
            max_per_option=1
        )

    def _Decolonization(self, side):

        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            chain(CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA],
                  CountryInfo.REGION_ALL[MapRegion.AFRICA]),
            prompt='Place influence using Decolonization.',
            reps=4,
            reps_unit='influence',
            max_per_option=1
        )

    def _Red_Scare_Purge(self, side):
        self.basket[side].append('Red_Scare_Purge')
        self.stage_complete()

    def _UN_Intervention(self, side):
        pass

    def _De_Stalinization(self, side):
        gather_list = [*self.map.has_ussr_influence()]
        # cannot accept input if you are trying to remove more influence than you have
        # also gathering influence needs to accept less than 4
        # maybe need to write a less_than=False kwarg
        # TODO need to split this into two functions.
        self.event_influence(Side.USSR, 4, gather_list,
                             can_split=True, positive=False)
        spread_list = [
            name for name in self.map.ALL if self.map[name].control != Side.US]
        self.event_influence(Side.USSR, 4, spread_list,
                             can_split=True, positive=True, limit=2)
        return self.removed_pile

    def _Nuclear_Test_Ban(self, side):
        self.change_vp((self.defcon_track - 2) * side.vp_mult)
        self.change_defcon(2)
        self.stage_complete()

    def _Formosan_Resolution(self, side):
        pass

    def _Defectors(self, side):
        # checks to see if headline bin is empty i.e. in action round
        if self.headline_bin[Side.USSR]:  # check if there's a headline
            self.discard_pile.append(self.headline_bin[Side.USSR])
            self.headline_bin[Side.USSR] = ''
        if side == Side.USSR and self.ar_track > 0:
            self.change_vp(1)
        self.stage_complete()

    def _The_Cambridge_Five(self, side):
        pass

    def _Special_Relationship(self, side):
        if self.can_play_event(Side.US, 'Special_Relationship'):
            if 'NATO' in self.basket[Side.US]:
                available_list = CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]
                incr = 2
                self.change_vp(2 * Side.US.vp_mult)
            else:
                available_list = self.map['UK'].info.adjacent_countries
                incr = 1

            self.input_state = Game.Input(
                Side.US, InputType.SELECT_COUNTRY,
                partial(self.event_influence_callback, partial(
                    Country.increment_influence, amt=incr), Side.US),
                available_list,
                prompt=f"Place {incr} influence in a single country using Special Relationship.",
            )

    def _NORAD(self, side):
        pass

    def _Brush_War(self, side):
        # check NATO
        all = [n for n in self.map.ALL]
        available_list = [n for n in all if self.map[n].info.stability <=
                          2 and n not in self.calculate_nato_countries()]
        return available_list

    def _Central_America_Scoring(self, side):
        self.score(MapRegion.CENTRAL_AMERICA, 1, 3, 5)
        self.stage_complete()

    def _Southeast_Asia_Scoring(self, side):
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
        self.stage_complete()

    def _Arms_Race(self, side):
        if self.milops_track[side] > self.milops_track[side.opp]:
            if self.milops_track >= self.defcon_track:
                if side == Side.USSR:
                    self.change_vp(3)
                elif side == Side.US:
                    self.change_vp(-3)
            else:
                if side == Side.USSR:
                    self.change_vp(1)
                elif side == Side.US:
                    self.change_vp(-1)
        return self.discard_pile

    def _Cuban_Missile_Crisis(self, side):
        pass

    def _Nuclear_Subs(self, side):
        return self.basket[Side.US]

    def _Quagmire(self, side):
        # need to insert and replace the US Action round with the quagmire_discard stage
        pass

    def _Salt_Negotiations(self, side):
        pass

    def _Bear_Trap(self, side):
        pass

    def _Summit(self, side):
        pass

    def _How_I_Learned_to_Stop_Worrying(self, side):
        # multiple choice = 5
        statements = [f'DEFCON 1 - Thermonuclear War. {side.opp} victory!',
                      'DEFCON 2', 'DEFCON 3', 'DEFCON 4', 'DEFCON 5']
        new_defcon_level = self.select_multiple(side, statements) + 1
        self.change_defcon(new_defcon_level - self.defcon_track)
        self.change_milops(side, 5)
        return self.removed_pile

    def _Junta(self, side):
        pass

    def _Kitchen_Debates(self, side):
        if self.can_play_event(side, 'Kitchen_Debates'):
            print('USSR poked in the chest by US player!')
            self.change_vp(-2)
        return self.removed_pile

    def _Missile_Envy(self, side):
        # if the other player is only holding scoring cards, this effect needs to be pushed
        pass

    def _We_Will_Bury_You(self, side):
        pass

    def _Brezhnev_Doctrine(self, side):
        return self.basket[Side.USSR]

    def _Portuguese_Empire_Crumbles(self, side):
        self.map.change_influence('Angola', Side.USSR, 2)
        self.map.change_influence('SE_African_States', Side.USSR, 2)
        return self.removed_pile

    def _South_African_Unrest(self, side):
        statements = ['Add 2 Influence to South Africa', 'Add 1 Influence to South Africa and 2 Influence to Angola',
                      'Add 1 Influence to South Africa and 2 Influence to Botswana']
        choice = self.select_multiple(side, statements)
        # using alternate syntax
        if choice == 0:
            self.map.change_influence('South_Africa', Side.USSR, 2)
        elif choice == 1:
            self.map.change_influence('South_Africa', Side.USSR, 1)
            self.map.change_influence('Angola', Side.USSR, 2)
        elif choice == 2:
            self.map.change_influence('South_Africa', Side.USSR, 1)
            self.map.change_influence('Botswana', Side.USSR, 2)
        return self.discard_pile

    def _Allende(self, side):
        self.map['Chile'].change_influence(2, 0)
        return self.removed_pile

    def _Willy_Brandt(self, side):
        # interaction with nato not implemented
        pass

    def _Muslim_Revolution(self, side):
        mr = ['Sudan', 'Iran', 'Iraq', 'Egypt',
              'Libya', 'Saudi_Arabia', 'Syria', 'Jordan']
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.remove_influence, Side.US),
            filter(lambda n: self.map[n].has_us_influence, mr),
            prompt='Muslim Revolution: Select countries in which to remove all US influence.',
            reps=2,
            reps_unit='countries',
            max_per_option=1
        )

    def _ABM_Treaty(self, side):
        pass

    def _Cultural_Revolution(self, side):
        pass

    def _Flower_Power(self, side):
        pass

    def _U2_Incident(self, side):
        pass

    def _OPEC(self, side):
        opec = ['Egypt', 'Iran', 'Libya', 'Saudi_Arabia',
                'Iraq', 'Gulf_States', 'Venezuela']
        swing = sum(
            [1 for country in opec if self.map[country].control == Side.USSR])
        self.change_vp(swing)
        return self.basket[Side.US]

    def _Lone_Gunman(self, side):
        pass

    def _Colonial_Rear_Guards(self, side):
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.US),
            chain(CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA],
                  CountryInfo.REGION_ALL[MapRegion.AFRICA]),
            prompt='Place influence using Colonial Real Guards.',
            reps=4,
            reps_unit='influence',
            max_per_option=1
        )

    def _Panama_Canal_Returned(self, side):
        countries = ['Panama', 'Costa_Rica', 'Venezuela']
        for country in countries:
            self.map[country].change_influence(0, 1)
        return self.removed_pile

    def _Camp_David_Accords(self, side):
        self.change_vp(-1)
        countries = ['Israel', 'Jordan', 'Egypt']
        for country in countries:
            self.map[country].change_influence(0, 1)
        return self.basket[Side.US]

    def _Puppet_Governments(self, side):
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.US),
            filter(
                lambda n: not self.map[n].has_us_influenc and not self.map[n].has_ussr_influence, CountryInfo.ALL),
            prompt='Place influence using Puppet Governments.',
            reps=3,
            reps_unit='influence',
            max_per_option=1
        )

    def _Grain_Sales_to_Soviets(self, side):
        pass

    def _John_Paul_II_Elected_Pope(self, side):
        self.map['Poland'].change_influence(-2, 1)
        return self.basket[Side.US]

    def _Latin_American_Death_Squads(self, side):
        return self.discard_pile

    def _OAS_Founded(self, side):
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.US),
            chain(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA],
                  CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA]),
            prompt='Place influence using OAS_Founded.',
            reps=2,
            reps_unit='influence',
            max_per_option=1
        )

    def _Nixon_Plays_The_China_Card(self, side):
        pass

    def _Sadat_Expels_Soviets(self, side):
        self.map.set_influence('Egypt', Side.USSR, 0)  # using alternate syntax
        self.map['Egypt'].change_influence(0, 1)
        return self.removed_pile

    def _Shuttle_Diplomacy(self, side):
        pass

    def _The_Voice_Of_America(self, side):
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.decrement_influence, Side.USSR),
            filter(
                lambda n: n not in CountryInfo.REGION_ALL[MapRegion.EUROPE] and self.map[n].has_ussr_influence,
                CountryInfo.ALL
            ),
            prompt='Remove USSR influence using The Voice Of America.',
            reps=4,
            reps_unit='influence',
            max_per_option=2
        )

    def _Liberation_Theology(self, side):
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA],
            prompt='Place influence using Liberation Theology.',
            reps=3,
            reps_unit='influence',
            max_per_option=2
        )

    def _Ussuri_River_Skirmish(self, side):
        pass

    def _Ask_Not_What_Your_Country_Can_Do_For_You(self, side):
        pass

    def _Alliance_for_Progress(self, side):
        ca = list(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA])
        sa = list(CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA])
        ca.extend(sa)
        swing = sum([-1 for n in ca if self.map[n].control == Side.US])
        self.change_vp(swing)
        return self.removed_pile

    def _Africa_Scoring(self, side):
        self.score(MapRegion.AFRICA, 1, 4, 6)
        return self.discard_pile

    def _One_Small_Step(self, side):
        if self.can_play_event(side, 'One_Small_Step'):
            self.change_space(side, 2)
        return self.discard_pile

    def _South_America_Scoring(self, side):
        self.score(MapRegion.SOUTH_AMERICA, 2, 5, 6)
        return self.discard_pile

    def _Che(self, side):
        pass

    def _Our_Man_In_Tehran(self, side):
        pass

    def _Iranian_Hostage_Crisis(self, side):
        # uses alternate syntax
        self.map.set_influence('Iran', Side.US, 0)
        self.map.change_influence('Iran', Side.USSR, 2)
        return self.basket[Side.USSR]

    def _The_Iron_Lady(self, side):
        # uses alternate syntax
        self.map.change_influence('Argentina', Side.USSR, 1)
        self.map.set_influence('UK', Side.USSR, 0)
        self.change_vp(-1)
        return self.basket[Side.US]

    def _Reagan_Bombs_Libya(self, side):
        swing = math.floor(self.map['Libya'].influence[Side.USSR] / 2)
        self.change_vp(swing)
        return self.discard_pile

    def _Star_Wars(self, side):
        if self.can_play_event(side, 'Star_Wars'):
            self.pick_from_discarded(side)
            # return self.removed_pile
            return 1
        else:
            # return self.discard_pile
            return 0

    def _North_Sea_Oil(self, side):
        return self.basket[Side.US]

    def _The_Reformer(self, side):
        pass

    def _Marine_Barracks_Bombing(self, side):
        self.map.set_influence('Lebanon', Side.US, 0)
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.decrement_influence, Side.US),
            filter(lambda n: self.map[n].has_us_influence,
                   CountryInfo.REGION_ALL[MapRegion.MIDDLE_EAST]),
            prompt='Remove US influence using Marine_Barracks_Bombing.',
            reps=2,
            reps_unit='influence',
        )

    def _Soviets_Shoot_Down_KAL(self, side):
        pass

    def _Glasnost(self, side):
        pass

    def _Ortega_Elected_in_Nicaragua(self, side):
        pass

    def _Terrorism(self, side):
        pass

    def _Iran_Contra_Scandal(self, side):
        return self.basket[Side.USSR]

    def _Chernobyl(self, side):
        pass

    def _Latin_American_Debt_Crisis(self, side):
        def double_inf_ussr_callback(country_name: str) -> bool:
            if self.map[country_name].get_ussr_influence == 0:
                return False
            self.map[country_name].influence[Side.USSR] *= 2
            return True

        def did_not_discard_fn():
            self.input_state = Game.Input(
                Side.USSR, InputType.SELECT_COUNTRY,
                double_inf_ussr_callback,
                filter(lambda n: self.map[n].has_ussr_influence,
                       CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA]),
                prompt="Select countries to double USSR influence",
                reps=2,
                reps_unit="countries",
                max_per_option=1
            )

        self.input_state = Game.Input(
            Side.US, InputType.SELECT_DISCARD_OPTIONAL,
            partial(self.may_discard_callback, Side.US,
                    did_not_discard_fn=did_not_discard_fn),
            chain(
                filter(
                    lambda n: n != 'The_China_Card' and self.get_global_effective_ops(
                        side, self.cards[n].info.ops) >= 3,
                    self.hand[Side.US]
                ),
                [Game.Input.OPTION_DO_NOT_DISCARD]),
            prompt='You may discard a card. If you choose not to discard a card, US loses all influence in West Germany.',
        )

    def _Tear_Down_This_Wall(self, side):
        if 'Willy_Brandt' in self.basket[Side.USSR]:
            self.removed_pile.append(self.basket[Side.USSR].pop(
                self.basket[Side.USSR].index('Willy_Brandt')))
        self.change_vp(1)
        self.map['West_Germany'].change_influence(1, 0)
        pass
        # coup/realignment not done

    def _An_Evil_Empire(self, side):
        self.change_vp(-1)
        if 'Flower_Power' in self.basket[Side.USSR]:
            self.removed_pile.append(self.basket[Side.USSR].pop(
                self.basket[Side.USSR].index('Flower_Power')))
        return self.basket[Side.US]

    def _Aldrich_Ames_Remix(self, side):
        pass

    def _Pershing_II_Deployed(self, side):
        self.change_vp(Side.USSR.vp_mult)
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.decrement_influence, Side.US),
            filter(lambda n: self.map[n].has_us_influence,
                   CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]),
            prompt='Remove US influence using Pershing II Deployed.',
            reps=3,
            reps_unit='influence',
            max_per_option=1
        )

    def _Wargames(self, side):
        if self.can_play_event(side, 'Wargames'):
            pass
        pass

    def _Solidarity(self, side):
        if 'John_Paul_II_Elected_Pope' in self.basket[Side.US]:
            self.map['Poland'].change_influence(0, 3)
            self.removed_pile.append(self.basket[Side.US].pop(
                self.basket[Side.US].index('John_Paul_II_Elected_Pope')))
        return self.removed_pile

    def _Iran_Iraq_War(self, side):
        pass

    def _Yuri_and_Samantha(self, side):
        return self.basket[Side.USSR]

    def _AWACS_Sale_to_Saudis(self, side):
        self.map.change_influence('Saudi_Arabia', Side.US, 2)
        return self.basket[Side.US]

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
