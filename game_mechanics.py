import math

from functools import partial
from itertools import chain
from typing import Sequence, Iterable, Callable
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
    ars_by_turn = (None, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7)

    class Input:

        def __init__(self, side: Side, state: InputType, callback: Callable[[str], bool],
                     options: Iterable[str], prompt: str = '',
                     reps: int = 1, reps_unit: str = '', max_per_option: int = -1,
                     option_stop_early=''):
            '''
            Creates an input state, which is the interface by which the game engine
            communicates with the user.

            Parameters
            ----------
            side : Side
                The side of the player receiving the prompt. Neutral for rng events.
            state : InputType
                The type of selection expected.
            callback : Callable[[str], bool]
                The function to run on each input received from the player. This
                function should take a string as the user input. It should return
                True if the string was valid, and False otherwise.
                The return value may be deprecated in the future.
            options : Iterable[str]
                The options available to the user. Should match with state.
                Options can be removed before all reps are exhausted, but additional
                options cannot be added. Remove using the method remove_option.
            prompt : str
                The prompt to display to the user.
            reps : int
                The number of times this input is required. Defaults to 1.
            reps_unit : str
                The unit to provide to the user when notifying them about the
                number of input repetitions remaining. Defaults to empty string,
                which means do not inform the user about remaining repetitions.
            max_per_option : int
                The maximum number of times a particular option can be selected.
                Defaults to reps.
            option_stop_early : str
                If the user is allowed to terminate input before the repetitions
                have been exhausted, this the option text for the early stopping
                option.
                Defaults to empty string, which means this options is not available.
            '''
            self.side = side
            self.state = state
            self.callback = callback
            self.prompt = prompt
            self.reps = reps
            self.reps_unit = reps_unit
            self.max_per_option = reps if max_per_option == -1 else max_per_option
            self.option_stop_early = option_stop_early
            self.selection = {k: 0 for k in options}
            self.discarded_options = set()

        def recv(self, input_str):
            '''
            This method is called by the user to select an option.
            Returns True if the selection was accepted, False otherwise.

            Parameters
            ----------
            input_str : str
                The selected option.
            '''
            if (input_str not in self.available_options and
                    (not self.option_stop_early or input_str != self.option_stop_early)):
                return False

            if input_str == self.option_stop_early:
                self.callback(input_str)
                return True

            if self.callback(input_str):
                self.selection[input_str] += 1
                return True
            else:
                return False

        def remove_option(self, option):
            '''
            The game calls this function to remove an existing option from the
            player before reps has been exhausted. Generally used by callback
            functions.

            Parameters
            ----------
            option : str
                The option to remove.
            '''
            if option not in self.selection:
                raise KeyError('Option was never present!')
            self.discarded_options.add(option)

        @property
        def available_options(self):
            '''
            Returns available input options to the user.
            '''
            return (
                item[0] for item in self.selection.items()
                if item[0] not in self.discarded_options
                and item[1] < self.max_per_option)

        @property
        def complete(self):
            '''
            Returns True if no more input is required, False if input is not
            complete.
            '''
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
        self.vp_track = 0
        self.turn_track = 0
        self.ar_track = 0
        self.ar_side = None
        self.defcon_track = 0
        self.milops_track = [0, 0]
        self.space_track = [0, 0]  # 0 is start, 1 is earth satellite etc
        self.spaced_turns = [0, 0]
        self.extra_turn = [False, False]

        self.map = None
        self.cards = None

        # interfacing with the UI
        self.input_state = None
        self.output_queue = [[], []]

        self.hand = [[], []]
        self.removed_pile = []
        self.discard_pile = []
        self.draw_pile = []
        self.basket = [[], []]
        self.headline_bin = ['', '']
        self.end_turn_stage_list = []

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
            self.expand_deck,
            self.deal,
            self.put_start_USSR,
            self.put_start_US,
            self.put_start_extra,
            self.process_headline,
        ]
        self.stage_list.reverse()

        self.map.build_standard()

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
        self.input_state = None
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
            reps=6,
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
            reps=7,
            reps_unit='influence'
        )

    def put_start_extra(self):
        '''
        Stage for player with handicap to place starting handicap influence in
        any country in which they currently have influence.
        '''
        if self.handicap == 0:
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
        self.headline_bin[side] = name
        self.hand[side].remove(name)
        return True

    def choose_headline(self, side: Side):
        self.input_state = Game.Input(
            side, InputType.SELECT_CARD,
            partial(self.headline_callback, side),
            (c for c in self.hand[side] if self.cards[c].info.can_headline),
            prompt='Select headline.'
        )

    def process_headline(self):
        '''
        Stage for both players to simultaneously choose their headline card.
        Due to UI constraints, USSR player chooses first, then the US player.
        All choices are then displayed.
        '''
        # TODO account for space race.
        # must append triggers in backwards order
        self.stage_list.append(self.ar_complete)
        self.stage_list.append(self.resolve_headline_order)
        self.stage_list.append(partial(self.choose_headline, Side.US))
        self.stage_list.append(partial(self.choose_headline, Side.USSR))

        # continue

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
            self.stage_list.append(partial(self.select_card))

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
        if card_name in (f'Blank_{n}_Op_Card' for n in range(1, 5)):
            return False
        elif card_name == 'The_China_Card':
            return False
        elif card_name == 'UN_Intervention':
            return any(
                (self.cards[c].info.owner == side.opp for c in hand))
        elif card_name == 'Defectors' and side == Side.US:
            return False
        elif card_name == 'Special_Relationship':
            return True if self.map['UK'].control == Side.US else False
        elif card_name == 'NATO' and side == Side.US:
            return True if 'Warsaw_Pact_Formed' in self.basket[
                Side.US] or 'Marshall_Plan' in self.basket[Side.US] else False
        elif card_name == 'Kitchen_Debates' and side == Side.US:
            us_count = sum(1 for n in CountryInfo.ALL if self.map[n].control ==
                           Side.US and self.map[n].info.battleground)
            ussr_count = sum(1 for n in CountryInfo.ALL if self.map[n].control ==
                             Side.USSR and self.map[n].info.battleground)
            return us_count > ussr_count
        elif card_name == 'Arab_Israeli_War' and side == Side.USSR:
            return False if 'Camp_David_Accords' in self.basket[Side.US] else True
        elif card_name == 'The_Cambridge_Five' and side == Side.USSR:
            return False if self.turn_track >= 8 else True
        elif card_name == 'Socialist_Governments' and side == Side.USSR:
            return False if 'The_Iron_Lady' in self.basket[Side.US] else True
        elif card_name == 'One_Small_Step':
            return True if self.space_track[side] < self.space_track[side.opp] else False
        elif card_name == 'Muslim_Revolution' and side == Side.USSR:
            return False if 'AWACS_Sale_to_Saudis' in self.basket[Side.US] else True
        elif card_name == 'Flower_Power' and side == Side.USSR:
            return False if 'An_Evil_Empire' in self.basket[Side.US] else True
        elif card_name == 'OPEC' and side == Side.USSR:
            return False if 'North_Sea_Oil' in self.basket[Side.US] or 'North_Sea_Oil' in self.removed_pile else True
        elif card_name == 'Willy_Brandt' and side == Side.USSR:
            return False if 'Tear_Down_This_Wall' in self.basket[Side.US] else True
        elif card_name == 'Solidarity' and side == Side.US:
            return False if 'John_Paul_II_Elected_Pope' in self.basket[Side.US] else True
        elif card_name == 'Star_Wars' and side == Side.US:
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
            String representation of the card.
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
        return any(self.map.can_realignment(self, n, side) for n in CountryInfo.ALL)

    def can_coup_at_all(self, side: Side):
        '''
        Checks if the player of <side> can coup in any country.
        True if there is at least 1 country suitable for coup.
        '''
        return any(self.map.can_coup(self, n, side) for n in CountryInfo.ALL)

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
            if self.space_track[side] == 7 and self.get_global_effective_ops(side, card_name.info.ops) == 4:
                return True
            elif self.space_track[side] >= 5 and self.get_global_effective_ops(side, card_name.info.ops) >= 3:
                return True
            elif self.get_global_effective_ops(side, self.cards[card_name].info.ops) >= 2:
                return True
            else:
                return False

        return available_space_turn(self, side) and enough_ops(self, side, card_name)

    def select_card(self, side: Side = Side.NEUTRAL):
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
            side, InputType.SELECT_CARD,
            partial(self.card_callback, side),
            (c for c in self.hand[side] if self.cards[c].is_playable),
            prompt='Select a card in hand to play.'
        )

    def card_callback(self, side: Side, card_name: str):
        self.input_state.reps -= 1
        if self.cards[card_name].info.type == 'Scoring':
            self.stage_list.append(
                partial(self.resolve_card_action, side,
                        card_name, CardAction.PLAY_EVENT.name)
            )
        else:
            if card_name == 'The_China_Card' and side == Side.US and 'Formosan_Resolution' in self.basket[Side.US]:
                self.basket[Side.US].remove('Formosan_Resolution')
            self.stage_list.append(
                partial(self.select_action, side, card_name))
        return True

    def action_callback(self, side: Side, card_name: str, action_name: str, is_event_resolved=False):
        self.input_state.reps -= 1
        self.stage_list.append(
            partial(self.resolve_card_action, side,
                    card_name, action_name, is_event_resolved)
        )
        return True

    def select_action(self, side: Side, card_name: str, is_event_resolved: bool = False, can_coup=True, free_coup_realignment=False):
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
            self.can_coup_at_all(side) and can_coup,
            not is_event_resolved and self.can_space(side, card_name)
        ]

        self.input_state = Game.Input(
            side, InputType.SELECT_CARD_ACTION,
            partial(self.action_callback, side, card_name,
                    is_event_resolved=is_event_resolved),
            (CardAction(i).name for i, b in enumerate(bool_arr) if b),
            prompt=f'Select an action for {card_name}.'
        )

    def resolve_card_action(self, side: Side, card_name: str, action_name: str, is_event_resolved=False):
        '''
        This function should lead to card_operation_realignment, card_operation_coup,
        or card_operation_influence, or a space race function.
        '''

        action = CardAction[action_name]
        card = self.cards[card_name]
        opp_event = (card.info.owner == side.opp)

        if action == CardAction.PLAY_EVENT:

            self.stage_list.append(
                partial(self.dispose_card, side, card_name, event=True))
            self.stage_list.append(
                partial(self.trigger_event, side, card_name))

        elif action == CardAction.RESOLVE_EVENT_FIRST:

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
            if opp_event and not is_event_resolved:
                self.stage_list.append(
                    partial(self.trigger_event, side, card_name))
            self.stage_list.append(
                partial(self.card_operation_influence, side, card_name))

        elif action == CardAction.REALIGNMENT:

            self.stage_list.append(
                partial(self.dispose_card, side, card_name, event=opp_event))
            if opp_event and not is_event_resolved:
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

        if 'Flower_Power' in self.basket[Side.USSR]:
            if action in [CardAction.PLAY_EVENT, CardAction.INFLUENCE, CardAction.REALIGNMENT, CardAction.COUP]:
                if card_name in ['Arab_Israeli_War', 'Indo_Pakistani_War', 'Korean_War', 'Brush_War', 'Iran_Iraq_War']:
                    self.change_vp(2)

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
            String representation of the card.
        event : bool, default=False
            True if the event has been resolved.
        '''
        if card_name == 'The_China_Card':
            self.move_china_card(side)
        elif card_name in (f'Blank_{n}_Op_Card' for n in range(1, 5)):
            pass
        else:
            if event and self.cards[card_name].info.event_unique:
                self.removed_pile.append(card_name)
            else:
                self.discard_pile.append(card_name)
            self.hand[side].remove(card_name)

    def move_china_card(self, side: Side, made_playable=False):
        '''
        Moves and flips the China Card after it has been used.
        Note: There are card functions that depend on this function.

        Parameters
        ----------
        side : Side
            Side of the player who plays the China Card.
        '''
        receipient = self.hand[side.opp]
        receipient.append('The China Card')
        self.cards['The China Card'].is_playable = made_playable

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
        Returns a string representation of a random card from the player's hand.

        Parameters
        ----------
        side : Side
            Side of the player whose hand we pick the card from.
        '''

        def choose_random_card_callback(card_name: str):
            self.hand[side].remove(card_name)
            self.discard_pile.append(card_name)
            return True

        self.input_state = Game.Input(
            Side.NEUTRAL, InputType.ROLL_DICE,
            choose_random_card_callback,
            self.hand[side],
            prompt='Randomly pick a card to discard',
        )

    '''
    Here we have different stages for card uses. These include the use of influence,
    operations points for coup or realignment, and also on the space race.
    '''

    def ops_influence_callback(self, side: Side, name: str) -> bool:
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
            (n for n in CountryInfo.ALL
                if self.map.can_place_influence(self, n, side, effective_ops)),
            prompt=f'Place operations from {card_name} as influence.',
            reps=effective_ops,
            reps_unit='operations'
        )

    def realignment_callback(self, side: Side, name: str, card_name: str, reps: int = None) -> bool:
        reps -= 1
        self.input_state.reps -= 1

        def realign_dice_callback(num: tuple):
            self.input_state.reps -= 1
            self.map.realignment(self, name, side, *num)
            return True

        if reps:
            self.stage_list.append(
                partial(self.card_operation_realignment, side, card_name=card_name, reps=reps))

        self.stage_list.append(
            partial(self.dice_stage, realign_dice_callback, two_dice=True))
        return True

    def card_operation_realignment(self, side: Side, card_name: str = None, reps: int = None, restricted_list: Sequence[str] = None, free=False):
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
        if not reps:
            effective_ops = self.get_global_effective_ops(side, card.info.ops)
        else:
            effective_ops = reps

        if restricted_list is None:
            restricted_list = CountryInfo.ALL

        self.input_state = Game.Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.realignment_callback, side,
                    card_name=card_name, reps=effective_ops),
            (n for n in CountryInfo.ALL if self.map.can_realignment(
                self, n, side) and n in restricted_list),
            prompt=f'Select a country for realignment using operations from {card_name}.',
        )

    def dice_stage(self, fn: Callable[[str], bool] = None, two_dice=False, reroll_ties=False):
        if not two_dice:
            options = (str(i) for i in range(1, 7))
            prompt = '1d6 roll'
        elif not reroll_ties:
            options = ((i, j) for i in range(1, 7) for j in range(1, 7))
            prompt = '2d6 roll (USSR roll, US roll)'
        else:
            options = ((i+2, j) for i in range(1, 7)
                       for j in range(1, 7) if i+2 != j)
            prompt = '2d6 roll (Sponsor roll, Participant roll), no ties'

        self.input_state = Game.Input(
            Side.NEUTRAL, InputType.ROLL_DICE,
            fn,
            options,
            prompt=prompt,
        )

    def coup_callback(self, side: Side, effective_ops: int, card_name: str, country_name, free=False) -> bool:
        self.input_state.reps -= 1

        local_ops_modifier = 0
        if card_name == 'The_China_Card' and country_name in CountryInfo.REGION_ALL[MapRegion.ASIA]:
            local_ops_modifier += 1
        if 'Vietnam_Revolts' in self.basket[Side.USSR] and country_name in CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]:
            local_ops_modifier += 1

        def coup_dice_callback(num: str):
            self.input_state.reps -= 1
            self.map.coup(self, country_name, side, effective_ops +
                          local_ops_modifier, int(num), free=free)
            return True
        self.stage_list.append(partial(self.dice_stage, coup_dice_callback))

        return True

    def card_operation_coup(self, side: Side, card_name: str, restricted_list: Sequence[str] = None, free=False):
        '''
        Stage when a player is given the opportunity to coup. Provides a list
        of countries which can be couped and waits for player input.

        TODO: Does not currently check the player baskets for China Card and Vietnam effects.

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
            partial(self.coup_callback, side, effective_ops, card_name),
            (n for n in CountryInfo.ALL
                if self.map.can_coup(self, n, side) and n in restricted_list),
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

        def space_dice_callback(num: str):
            self.input_state.reps -= 1

            if self.space_track[side] in [0, 2, 4, 6]:
                modifier = 0
            elif self.space_track[side] in [1, 3, 5]:
                modifier = -1
            else:
                modifier = 1

            outcome = 'Success' if int(num) + modifier <= 3 else 'Failure'
            if outcome == 'Success':
                self.change_space(side, 1)
            print(f'{outcome} with roll of {num}.')

            self.spaced_turns[side] += 1
            return True

        self.stage_list.append(partial(self.dice_stage, space_dice_callback))
        return True

    def event_influence_callback(self, country_function, side: Side, name: str) -> bool:
        '''
        event_influence_callback is used as the callback function for modifying influence.
        This is mostly used for card events where the player has to choose which regions
        in which to directly insert influence.

        country_function is the function that the country will apply.
        For example, for cards like COMECON / Decolonization, use
            partial(Country.increment_influence, Side.USSR)
        For Voice Of America, specify max_per_option in input_state as 2, then use
            partial(Country.decrement_influence, Side.USSR).
        For a card like Junta you want to get an increment by 2 function, so use
            partial(Country.increment_influence, side, amt=2).
        For a card like Warsaw Pact / Muslim_Revolution / Truman Doctrine use
            partial(Country.remove_influence, Side.US).
        '''
        self.input_state.reps -= 1
        status = country_function(self.map[name], side)
        # TODO: this might not be general enough. If bugs happen check here
        if not status:
            return False
        else:
            if not self.map[name].influence[side]:
                self.input_state.remove_option(name)
            return True

    def select_multiple_callback(self, option_function_mapping: dict, selected_option: list):
        '''
        Stage where a player is given the opportunity to select from multiple choices.

        Parameters
        ----------
        side : Side
            Side of the player who has chosen to advance on the space race.
        option_function_mapping : dict
            Dictionary of (keys: str, values: function)
        selected_option: list
            String which the player selected.
        '''
        self.input_state.reps -= 1
        option_function_mapping[selected_option]()
        return True

  # The following stages tend to be for cards that are a little more specific.

    def may_discard_callback(self, side: Side, opt: str, did_not_discard_fn: Callable[[], None] = lambda: None):

        if opt == self.input_state.option_stop_early:
            did_not_discard_fn()
            self.input_state.reps -= 1
            return True

        if opt not in self.hand[side]:
            return False

        self.hand[side].remove(opt)
        self.discard_pile.append(opt)
        self.input_state.reps -= 1
        return True

    def war(self, country_name: str, side: Side, country_itself: bool = False,
            lower: int = 4, win_vp: int = 2, win_milops: int = 2):

        def war_dice_callback(num: str):

            self.input_state.reps -= 1
            country = self.map[country_name]

            modifier = sum(self.map[adjacent_country].control == side.opp
                           for adjacent_country in country.info.adjacent_countries)

            if country_itself and country.control == side.opp:  # For Arab-Israeli War
                modifier += 1

            outcome = 'Success' if int(num) - modifier >= lower else 'Failure'

            if outcome == 'Success':
                self.change_vp(win_vp * side.vp_mult)
                self.change_milops(side, win_milops)

                influence = country.influence[side.opp]
                country.remove_influence(side.opp)
                country.increment_influence(side, influence)

            print(f'{outcome} with roll of {num}.')

            return True

        self.stage_list.append(
            partial(self.dice_stage, war_dice_callback))

    def war_country_callback(self, side: Side, country_name: str, country_itself: bool = False,
                             lower: int = 4, win_vp: int = 2, win_milops: int = 2):
        self.input_state.reps -= 1
        self.war(country_name, side, country_itself=country_itself,
                 lower=lower, win_vp=win_vp, win_milops=win_milops)
        return True

    def norad_influence(self):
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.US),
            self.map.has_us_influence,
            prompt='Place NORAD influence.',
            reps_unit='influence'
        )

    def pick_from_discarded(self):
        pass

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
        pass

    def cuba_missile_remove(self):
        pass

    def shuffle_callback(self, card_name):
        self.input_state.reps -= 1
        self.draw_pile.append(card_name)
        return True

    def shuffle_draw_pile_stage(self):

        shuffler_pile = self.draw_pile
        self.draw_pile = []

        self.input_state = Game.Input(
            Side.NEUTRAL, InputType.SELECT_CARD,
            self.shuffle_callback,
            shuffler_pile,
            'Shuffle the deck.  Select the next card.',
            reps = len(shuffler_pile),
            reps_unit='cards',
            max_per_option=1
        )

    def expand_deck(self):

        if self.turn_track == 1:
            # TEST CODE BELOW -- remove when done
            # '''For testing early-war cards'''
            # self.hand[Side.USSR].extend([self.cards.early_war.pop(i)
            #                              for i in range(20)])
            # self.hand[Side.US].extend([self.cards.early_war.pop(0)
            #                            for i in range(19)])
            # '''For testing mid-war cards'''
            # self.hand[Side.US].extend([self.cards.mid_war.pop(i)
            #                            for i in range(24)])
            # self.hand[Side.USSR].extend([self.cards.mid_war.pop(0)
            #                              for i in range(24)])
            # '''For testing late-war cards'''
            # self.hand[Side.US].extend([self.cards.late_war.pop(i)
            #                            for i in range(12)])
            # self.hand[Side.USSR].extend([self.cards.late_war.pop(0)
            #                              for i in range(11)])
            # TEST CODE ABOVE -- remove when done
            self.draw_pile.extend(self.cards.early_war)
            self.cards.early_war = []
            self.shuffle_draw_pile_stage()
        elif self.turn_track == 4:
            self.draw_pile.extend(self.cards.mid_war)
            self.cards.mid_war = []
            self.shuffle_draw_pile_stage()
        elif self.turn_track == 8:
            self.draw_pile.extend(self.cards.late_war)
            self.cards.late_war = []
            self.shuffle_draw_pile_stage()


    def deal(self, first_side=Side.USSR):

        if 1 <= self.turn_track <= 3:
            handsize_target = [8, 8]
        else:
            handsize_target = [9, 9]

        # Ignore China Card if it is in either hand
        if 'The_China_Card' in self.hand[Side.USSR]:
            handsize_target[Side.USSR] += 1
        elif 'The_China_Card' in self.hand[Side.US]:
            handsize_target[Side.US] += 1

        next_side = first_side
        while any(len(h) < t for h, t in zip(self.hand, handsize_target)):
            if len(self.hand[next_side]) >= handsize_target[next_side]:
                next_side = next_side.opp
                continue

            self.hand[next_side].append(self.draw_pile.pop())
            next_side = next_side.opp

            if not self.draw_pile:
                # if draw pile exhausted, shuffle the discard pile and put it as the new draw pile
                self.draw_pile = self.discard_pile
                self.discard_pile = []
                self.stage_list.append(partial(self.deal, first_side=next_side))
                self.shuffle_draw_pile_stage()
                return

    # need to make sure next_turn is only called after all extra rounds
    def end_of_turn(self):
        # 0. Clear all events that only last until the end of turn.
        def clear_baskets(self):
            for function in self.end_turn_stage_list:
                function()
            self.end_turn_stage_list = []

        # 1. Check milops
        def check_milops(self):

            milops_vp_change = [
                min(milops - self.defcon_track, 0) for milops in self.milops_track
            ]
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
        self.expand_deck()
        self.deal()  # turn marker advanced before dealing
        self.process_headline()

    def score(self, region: MapRegion, presence_vps: int, domination_vps: int, control_vps: int):

        if 'Formosan_Resolution' in self.basket[Side.US]:
            self.map['Taiwan'].info.battleground = True

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

        swing = vps[Side.USSR] * Side.USSR.vp_mult + \
            vps[Side.US] * Side.US.vp_mult
        self.change_vp(swing)

        if self.map['Taiwan'].info.battleground:
            self.map['Taiwan'].info.battleground = False

        print(f'{region.name} scores for {swing} VP')

    '''
    Card functions will come here. We also create a card dictionary, which ties
    every card_name to their card_function. The card functions are named with an
    underscore prefix. Every time a card's event is triggered, the dictionary
    lookup will be used to access the function.
    '''

    def _Asia_Scoring(self, side):
        # TODO: ADD SHUTTLE DIPLOMACY AND FORMOSAN RESOLUTION
        self.score(MapRegion.ASIA, 3, 7, 9)

    def _Europe_Scoring(self, side):
        self.score(MapRegion.EUROPE, 3, 7, 120)

    def _Middle_East_Scoring(self, side):
        self.score(MapRegion.MIDDLE_EAST, 3, 5, 7)

    def _Duck_and_Cover(self, side):
        self.change_defcon(-1)
        self.change_vp(-(5 - self.defcon_track))

    def _Five_Year_Plan_callback(self, card_name: str):
        self.input_state.reps -= 1
        if self.cards[card_name].info.owner == Side.US:
            # must append backwards!
            self.stage_list.append(
                partial(self.dispose_card, Side.USSR, card_name, event=True))
            self.stage_list.append(
                partial(self.trigger_event, Side.USSR, card_name))
        else:
            self.stage_list.append(
                partial(self.dispose_card, Side.USSR, card_name))
        return True

    def _Five_Year_Plan(self, side):

        self.input_state = Game.Input(
            Side.NEUTRAL, InputType.ROLL_DICE,
            self._Five_Year_Plan_callback,
            (n for n in self.hand[Side.USSR] if n != 'Five_Year_Plan'),
            prompt='Five Year Plan: USSR randomly discards a card.'
        )

    def _The_China_Card(self, side):
        'No event.'
        pass

    def _Socialist_Governments(self, side):
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.decrement_influence, Side.US),
            (n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]
                if self.map[n].has_us_influence),
            prompt='Socialist Governments: Remove a total of 3 US Influence from any countries in Western Europe (limit 2 per country)',
            reps=3,
            reps_unit='influence',
            max_per_option=2
        )

    def _Fidel(self, side):
        cuba = self.map['Cuba']
        cuba.set_influence(max(3, cuba.influence[Side.USSR]), 0)

    def _Vietnam_Revolts(self, side):
        # TODO: Continuous effect
        self.basket[Side.USSR].append('Vietnam_Revolts')
        self.end_turn_stage_list.append(
            partial(self.basket[Side.USSR].remove, 'Vietnam_Revolts'))

    def _Blockade(self, side):
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_CARD,
            partial(self.may_discard_callback, Side.US,
                    did_not_discard_fn=partial(self.map['West_Germany'].remove_influence, Side.US)),
            (n for n in self.hand[Side.US]
                if n != 'The_China_Card'
                and self.get_global_effective_ops(side, self.cards[n].info.ops) >= 3),
            prompt='You may discard a card. If you choose not to discard a card, US loses all influence in West Germany.',
            option_stop_early='Do Not Discard'
        )

    def _Korean_War(self, side):
        self.war('South_Korea', Side.USSR)

    def _Romanian_Abdication(self, side):
        romania = self.map['Romania']
        romania.set_influence(max(3, romania.influence[Side.USSR]), 0)

    def _Arab_Israeli_War(self, side):
        if self.can_play_event(side, 'Arab_Israeli_War'):
            self.war('Israel', Side.USSR, country_itself=True)

    def _COMECON(self, side):
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            (n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]
                if self.map[n].control != Side.US),
            prompt='COMECON: Add 1 influence to each of 4 non-US controlled countries of Eastern Europe.',
            reps=4,
            reps_unit='influence',
            max_per_option=1
        )

    def _Nasser(self, side):
        egypt = self.map['Egypt']
        egypt.change_influence(2, -math.ceil(egypt.influence[Side.US] / 2))

    def _Warsaw_Pact_Formed(self, side):
        # TODO: should aim to remove this as an option (_remove) if it's not available
        def remove():
            self.input_state = Game.Input(
                Side.USSR, InputType.SELECT_COUNTRY,
                partial(self.event_influence_callback,
                        Country.remove_influence, Side.US),
                (n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]
                    if self.map[n].has_us_influence),
                prompt='Warsaw Pact Formed: Remove all US influence from 4 countries in Eastern Europe.',
                reps=4,
                reps_unit='influence',
                max_per_option=1
            )

        def add():
            self.input_state = Game.Input(
                Side.USSR, InputType.SELECT_COUNTRY,
                partial(self.event_influence_callback,
                        Country.increment_influence, Side.USSR),
                CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE],
                prompt='Warsaw Pact Formed: Add 5 USSR Influence to any countries in Eastern Europe.',
                reps=5,
                reps_unit='influence',
                max_per_option=2
            )

        self.basket[Side.US].append('Warsaw_Pact_Formed')
        option_function_mapping = {
            'Remove all US influence from 4 countries in Eastern Europe': remove,
            'Add 5 USSR Influence to any countries in Eastern Europe': add
        }

        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_MULTIPLE,
            partial(self.select_multiple_callback, option_function_mapping),
            option_function_mapping.keys(),
            prompt='Warsaw Pact: Choose between two options.'
        )

    def _De_Gaulle_Leads_France(self, side):
        self.map['France'].change_influence(1, -2)
        self.basket[Side.USSR].append('De_Gaulle_Leads_France')

    def _Captured_Nazi_Scientist(self, side):
        self.change_space(side, 1)

    def _Truman_Doctrine(self, side):
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.remove_influence, Side.USSR),
            (n for n in CountryInfo.REGION_ALL[MapRegion.EUROPE]
                if self.map[n].control == Side.NEUTRAL
             and self.map[n].has_ussr_influence),
            prompt='Truman Doctrine: Select a country in which to remove all USSR influence.'
        )

    def _Olympic_Games(self, side):
        def participate(side_opp):
            # NOTE: the _participate inner function receives the opposite side from the main card function
            def participate_dice_callback(num: tuple):
                outcome = 'Success' if num[0] > num[1] else 'Failure'
                if outcome:
                    # side_opp is the sponsor
                    self.change_vp(2 * side_opp.vp_mult)
                else:
                    self.change_vp(2 * side_opp.opp.vp_mult)
                print(
                    f'{outcome} with (Sponsor, Participant) rolls of ({num[0]}, {num[1]}).')

                return True

            self.stage_list.append(
                partial(self.dice_stage, participate_dice_callback, two_dice=True, reroll_ties=True))
            return True

        def boycott(side):
            self.change_defcon(-1)
            global_ops = self.get_global_effective_ops(side, 4)
            self.select_action(side, f'Blank_{global_ops}_Op_Card')

        option_function_mapping = {
            'Participate and sponsor has modified die roll (+2).': partial(participate, side),
            'Boycott: DEFCON level degrades by 1 and sponsor may conduct operations as if they played a 4 op card.': partial(boycott, side)
        }

        self.input_state = Game.Input(
            side.opp, InputType.SELECT_MULTIPLE,
            partial(self.select_multiple_callback, option_function_mapping),
            option_function_mapping.keys(),
            prompt='Olympic Games: Choose between two options.'
        )

    def _NATO(self, side):
        if self.can_play_event(side, 'NATO'):
            self.basket[Side.USSR].append('NATO')

    def _Independent_Reds(self, side):
        ireds = ['Yugoslavia', 'Romania',
                 'Bulgaria', 'Hungary', 'Czechoslovakia']
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.match_influence, Side.US),
            (n for n in ireds if self.map[n].has_ussr_influence),
            prompt='Independent Reds: You may add influence in 1 of these countries to equal USSR influence.'
        )

    def _Marshall_Plan(self, side):

        self.basket[Side.US].append('Marshall_Plan')
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.US),
            (n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]
                if self.map[n].control != Side.USSR),
            prompt='Marshall Plan: Place influence in 7 non-USSR controlled countries.',
            reps=7,
            reps_unit='influence',
            max_per_option=1
        )

    def _Indo_Pakistani_War(self, side):

        self.input_state = Game.Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.war_country_callback, side),
            ['India', 'Pakistan'],
            prompt='Indo-Pakistani War: Choose between two options.'
        )

    def _Containment(self, side):
        self.basket[Side.US].append('Containment')
        self.end_turn_stage_list.append(
            partial(self.basket[Side.US].remove, 'Containment'))

    def _CIA_Created(self, side):
        # TODO: reveal hand
        ops = self.get_global_effective_ops(Side.US, 1)
        self.select_action(side, f'Blank_{ops}_Op_Card')
        pass

    def _US_Japan_Mutual_Defense_Pact(self, side):
        # TODO: coup and realignment in Japan
        japan = self.map['Japan']
        japan.set_influence(japan.influence[Side.USSR], max(
            japan.influence[Side.USSR] + 4, japan.influence[Side.US]))

    def _Suez_Crisis(self, side):
        suez = ['France', 'UK', 'Israel']

        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.decrement_influence, Side.US),
            (n for n in suez if self.map[n].has_us_influence),
            prompt='Remove US influence using Suez Crisis.',
            reps=4,
            reps_unit='influence',
            max_per_option=2
        )

    def _East_European_Unrest(self, side):

        dec = 2 if 8 <= self.turn_track <= 10 else 1

        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback, partial(
                Country.decrement_influence, amt=dec), Side.USSR),
            (n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]
                if self.map[n].has_ussr_influence),
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
        self.end_turn_stage_list.append(
            partial(self.basket[side].remove, 'Red_Scare_Purge'))

    def _UN_Intervention(self, side):
        '''
        self.input_state = Game.Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            (c for c in self.hand[side] if self.cards[c].info.owner == side.opp),
            prompt=f'Select a card with an opponent event to use for operations with UN Intervention.'
        )
        '''
        pass

    def _De_Stalinization(self, side):

        def remove_callback(country_name):
            if country_name != self.input_state.option_stop_early:
                self.event_influence_callback(
                    Country.decrement_influence, Side.USSR, country_name)
                if self.input_state.reps:
                    # TODO make a better prompt
                    self.input_state.option_stop_early = f'Move {4 - self.input_state.reps} influence.'
                    return True

            ops = 4 - self.input_state.reps
            # if we get here, either out of reps or optional prompt
            self.input_state = Game.Input(
                Side.USSR, InputType.SELECT_COUNTRY,
                partial(self.event_influence_callback,
                        Country.increment_influence, Side.USSR),
                (n for n in CountryInfo.ALL
                    if self.map[n].control != Side.US and not self.map[n].info.superpower),
                prompt=f'Add {ops} influence using De-Stalinization.',
                reps=ops,
                reps_unit='influence',
                max_per_option=2
            )
            return True

        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            remove_callback,
            (n for n in CountryInfo.ALL
                if self.map[n].has_ussr_influence and not self.map[n].info.superpower),
            prompt='Remove up to 4 influence using De-Stalinization.',
            reps=4,
            reps_unit='influence',
            option_stop_early='Move no influence.'
        )

    def _Nuclear_Test_Ban(self, side):
        self.change_vp((self.defcon_track - 2) * side.vp_mult)
        self.change_defcon(2)

    def _Formosan_Resolution(self, side):
        self.basket[Side.US].append('Formosan_Resolution')

    def _Defectors(self, side):
        # checks to see if headline bin is empty i.e. in action round
        if self.headline_bin[Side.USSR]:  # check if there's a headline
            self.discard_pile.append(self.headline_bin[Side.USSR])
            self.headline_bin[Side.USSR] = ''
        if side == Side.USSR and self.ar_track > 0:
            self.change_vp(1)

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
                prompt=f'Place {incr} influence in a single country using Special Relationship.',
            )

    def _NORAD(self, side):
        self.basket[Side.US].append('NORAD')

    def _Brush_War(self, side):
        self.input_state = Game.Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.war_country_callback, side,
                    lower=3, win_vp=1, win_milops=3),
            (n for n in self.map.ALL
                if self.map[n].info.stability <= 2
                and n not in self.calculate_nato_countries()),
            prompt='Brush War: Choose a target country.'
        )

    def _Central_America_Scoring(self, side):
        self.score(MapRegion.CENTRAL_AMERICA, 1, 3, 5)

    def _Southeast_Asia_Scoring(self, side):
        vps = [0, 0, 0]
        for n in CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]:
            x = self.map[n]
            vps[x.control] += 1
        swing = vps[Side.USSR] * Side.USSR.vp_mult + \
            vps[Side.US] * Side.US.vp_mult

        swing += self.map['Thailand'].control.vp_mult
        self.change_vp(swing)
        print(f'Southeast Asia scores for {swing} VP')

    def _Arms_Race(self, side):
        if self.milops_track[side] > self.milops_track[side.opp]:
            if self.milops_track >= self.defcon_track:
                self.change_vp(3 * side.vp_mult)
            else:
                self.change_vp(1 * side.vp_mult)

    def _Cuban_Missile_Crisis(self, side):
        self.change_defcon(2 - self.defcon_track)
        self.basket[side].append('Cuban_Missile_Crisis')
        self.end_turn_stage_list.append(
            partial(self.basket[side].remove, 'Cuban_Missile_Crisis'))

    def _Nuclear_Subs(self, side):
        self.basket[Side.US].append('Nuclear_Subs')
        self.end_turn_stage_list.append(
            partial(self.basket[Side.US].remove, 'Nuclear_Subs'))

    def _Quagmire(self, side):
        # need to insert and replace the US Action round with the quagmire_discard stage
        if 'NORAD' in self.basket[Side.US]:
            self.basket[Side.US].remove('NORAD')
        pass

    def _Salt_Negotiations(self, side):
        self.change_defcon(2)
        self.basket[side].append('Salt_Negotiations')
        self.end_turn_stage_list.append(
            partial(self.basket[side].remove, 'Salt_Negotiations'))

    def _Bear_Trap(self, side):
        pass

    def _Summit(self, side):
        pass

    def _How_I_Learned_to_Stop_Worrying(self, side):

        option_function_mapping = {
            f'DEFCON 1: Thermonuclear War. {side.opp} victory!': partial(self.change_defcon, 1 - self.defcon_track),
            f'DEFCON 2': partial(self.change_defcon, 2 - self.defcon_track),
            f'DEFCON 3': partial(self.change_defcon, 3 - self.defcon_track),
            f'DEFCON 4': partial(self.change_defcon, 4 - self.defcon_track),
            f'DEFCON 5': partial(self.change_defcon, 5 - self.defcon_track)
        }

        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_MULTIPLE,
            partial(self.select_multiple_callback, option_function_mapping),
            option_function_mapping.keys(),
            prompt='How I Learned To Stop Worrying: Set a new DEFCON level.'
        )

        self.change_milops(side, 5)

    def _Junta(self, side):
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    partial(Country.increment_influence, side, amt=2), side),
            [n for n in chain(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA],
                              CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA])],
            prompt='Junta: Add 2 influence to a single country in Central America or South America.',
            reps_unit='influence'
        )
        pass

    def _Kitchen_Debates(self, side):
        if self.can_play_event(side, 'Kitchen_Debates'):
            print('USSR poked in the chest by US player!')
            self.change_vp(-2)

    def _Missile_Envy(self, side):
        # if the other player is only holding scoring cards, this effect needs to be pushed
        pass

    def _We_Will_Bury_You(self, side):
        self.change_defcon(-1)
        pass

    def _Brezhnev_Doctrine(self, side):
        self.basket[Side.USSR].append('Brezhnev_Doctrine')
        self.end_turn_stage_list.append(
            partial(self.basket[Side.USSR].remove, 'Brezhnev_Doctrine'))

    def _Portuguese_Empire_Crumbles(self, side):
        self.map.change_influence('Angola', Side.USSR, 2)
        self.map.change_influence('SE_African_States', Side.USSR, 2)

    def _South_African_Unrest(self, side):

        def _sa():
            self.map.change_influence('South_Africa', Side.USSR, 2)

        def _sa_angola():
            self.map.change_influence('South_Africa', Side.USSR, 1)
            self.map.change_influence('Angola', Side.USSR, 2)

        def _sa_botswana():
            self.map.change_influence('South_Africa', Side.USSR, 1)
            self.map.change_influence('Botswana', Side.USSR, 2)

        def _sa_angola_botswana():
            self.map.change_influence('South_Africa', Side.USSR, 1)
            self.map.change_influence('Angola', Side.USSR, 1)
            self.map.change_influence('Botswana', Side.USSR, 1)

        option_function_mapping = {
            'Add 2 Influence to South Africa.': _sa,
            'Add 1 Influence to South Africa and 2 Influence to Angola.': _sa_angola,
            'Add 1 Influence to South Africa and 2 Influence to Botswana.': _sa_botswana,
            'Add 1 Influence each to South Africa, Angola, and Botswana.': _sa_angola_botswana
        }

        self.input_state = Game.Input(
            side, InputType.SELECT_MULTIPLE,
            partial(self.select_multiple_callback, option_function_mapping),
            option_function_mapping.keys(),
            prompt='South African Unrest: Choose an option.'
        )

    def _Allende(self, side):
        self.map['Chile'].change_influence(2, 0)

    def _Willy_Brandt(self, side):
        self.change_defcon(1)
        self.map['West_Germany'].change_influence(1, 0)
        self.basket[Side.USSR].append('Willy_Brandt')

    def _Muslim_Revolution(self, side):
        mr = ['Sudan', 'Iran', 'Iraq', 'Egypt',
              'Libya', 'Saudi_Arabia', 'Syria', 'Jordan']
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.remove_influence, Side.US),
            (n for n in mr if self.map[n].has_us_influence),
            prompt='Muslim Revolution: Select countries in which to remove all US influence.',
            reps=2,
            reps_unit='countries',
            max_per_option=1
        )

    def _ABM_Treaty(self, side):
        self.change_defcon(1)
        global_ops = self.get_global_effective_ops(side, 4)
        self.select_action(side, f'Blank_{global_ops}_Op_Card')

    def _Cultural_Revolution(self, side):
        if 'The_China_Card' in self.hand[Side.US]:
            self.move_china_card(Side.US, made_playable=True)
        elif 'The_China_Card' in self.hand[Side.USSR]:
            self.change_vp(1)

    def _Flower_Power(self, side):
        self.basket[Side.USSR].append('Flower_Power')

    def _U2_Incident(self, side):
        pass

    def _OPEC(self, side):
        opec = ['Egypt', 'Iran', 'Libya', 'Saudi_Arabia',
                'Iraq', 'Gulf_States', 'Venezuela']
        swing = sum(
            Side.USSR.vp_mult for country in opec if self.map[country].control == Side.USSR)
        self.change_vp(swing)

    def _Lone_Gunman(self, side):
        ops = self.get_global_effective_ops(Side.US, 1)
        self.select_action(side, f'Blank_{ops}_Op_Card')
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

    def _Camp_David_Accords(self, side):
        self.change_vp(-1)
        countries = ['Israel', 'Jordan', 'Egypt']
        for country in countries:
            self.map[country].change_influence(0, 1)
        self.basket[Side.US].append('Camp_David_Accords')

    def _Puppet_Governments(self, side):
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.US),
            (n for n in CountryInfo.ALL
                if not self.map[n].has_us_influence
                and not self.map[n].has_ussr_influence),
            prompt='Place influence using Puppet Governments.',
            reps=3,
            reps_unit='influence',
            max_per_option=1
        )

    def _Grain_Sales_to_Soviets(self, side):
        pass

    def _John_Paul_II_Elected_Pope(self, side):
        self.map['Poland'].change_influence(-2, 1)
        self.basket[Side.US].append('John_Paul_II_Elected_Pope')

    def _Latin_American_Death_Squads(self, side):
        self.basket[side].append('Latin_American_Death_Squads')
        self.end_turn_stage_list.append(
            partial(self.basket[side].remove, 'Latin_American_Death_Squads'))

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
        )

    def _Nixon_Plays_The_China_Card(self, side):
        if 'The_China_Card' in self.hand[Side.USSR]:
            self.move_china_card(Side.USSR)
        elif 'The_China_Card' in self.hand[Side.US]:
            self.change_vp(-2)

    def _Sadat_Expels_Soviets(self, side):
        self.map.set_influence('Egypt', Side.USSR, 0)  # using alternate syntax
        self.map['Egypt'].change_influence(0, 1)

    def _Shuttle_Diplomacy(self, side):
        pass

    def _The_Voice_Of_America(self, side):
        self.input_state = Game.Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.decrement_influence, Side.USSR),
            (n for n in CountryInfo.ALL
                if n not in CountryInfo.REGION_ALL[MapRegion.EUROPE]
                and self.map[n].has_ussr_influence),
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
        if 'The_China_Card' in self.hand[Side.USSR]:
            self.move_china_card(Side.USSR, made_playable=True)
        elif 'The_China_Card' in self.hand[Side.US]:
            self.input_state = Game.Input(
                Side.US, InputType.SELECT_COUNTRY,
                partial(self.event_influence_callback,
                        Country.increment_influence, Side.US),
                CountryInfo.REGION_ALL[MapRegion.ASIA],
                prompt='Place influence using Ussuri River Skirmish.',
                reps=4,
                reps_unit='influence',
                max_per_option=2
            )

    def _Ask_Not_What_Your_Country_Can_Do_For_You(self, side):
        pass

    def _Alliance_for_Progress(self, side):
        ca = list(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA])
        sa = list(CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA])
        ca.extend(sa)
        swing = sum(
            Side.US.vp_mult for n in ca if self.map[n].control == Side.US)
        self.change_vp(swing)

    def _Africa_Scoring(self, side):
        self.score(MapRegion.AFRICA, 1, 4, 6)

    def _One_Small_Step(self, side):
        if self.can_play_event(side, 'One_Small_Step'):
            self.change_space(side, 2)

    def _South_America_Scoring(self, side):
        self.score(MapRegion.SOUTH_AMERICA, 2, 5, 6)

    def _Che(self, side):
        ca_sa_af = chain(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA],
                         CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA],
                         CountryInfo.REGION_ALL[MapRegion.AFRICA])

        self.card_operation_coup(side, 'Che', restricted_list=[
                                 n for n in ca_sa_af if self.map[n].info.battleground])
        pass

    def _Our_Man_In_Tehran(self, side):
        pass

    def _Iranian_Hostage_Crisis(self, side):
        self.map.set_influence('Iran', Side.US, 0)
        self.map.change_influence('Iran', Side.USSR, 2)
        self.basket[Side.US].append('Iranian_Hostage_Crisis')

    def _The_Iron_Lady(self, side):
        self.map.change_influence('Argentina', Side.USSR, 1)
        self.map.set_influence('UK', Side.USSR, 0)
        self.change_vp(-1)
        self.basket[Side.US].append('The_Iron_Lady')

    def _Reagan_Bombs_Libya(self, side):
        swing = math.floor(self.map['Libya'].influence[Side.USSR] / 2)
        self.change_vp(-swing)

    def _Star_Wars(self, side):
        if self.can_play_event(side, 'Star_Wars'):
            # self.pick_from_discarded(side)
            pass
        else:
            # return self.discard_pile
            pass

    def _North_Sea_Oil(self, side):
        self.basket[Side.US].append('North_Sea_Oil')
        pass

    def _The_Reformer(self, side):
        reps = 6 if self.vp_track > 0 else 4
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            CountryInfo.REGION_ALL[MapRegion.EUROPE],
            prompt=f'The Reformer: Add {reps} influence to Europe.',
            reps=reps,
            reps_unit='influence',
            max_per_option=2
        )
        self.basket[Side.USSR].append('The_Reformer')

    def _Marine_Barracks_Bombing(self, side):
        self.map.set_influence('Lebanon', Side.US, 0)
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.decrement_influence, Side.US),
            (n for n in CountryInfo.REGION_ALL[MapRegion.MIDDLE_EAST]
                if self.map[n].has_us_influence),
            prompt='Remove US influence using Marine_Barracks_Bombing.',
            reps=2,
            reps_unit='influence',
        )

    def _Soviets_Shoot_Down_KAL_007(self, side):
        self.change_defcon(-1)
        self.change_vp(-2)
        if self.map['South_Korea'].control == Side.US:
            global_ops = self.get_global_effective_ops(side, 4)
            self.select_action(
                Side.US, f'Blank_{global_ops}_Op_Card', can_coup=False)

    def _Glasnost(self, side):
        self.change_defcon(1)
        self.change_vp(2)
        if 'The_Reformer' in self.basket[Side.USSR]:
            global_ops = self.get_global_effective_ops(side, 4)
            self.select_action(
                Side.USSR, f'Blank_{global_ops}_Op_Card', can_coup=False)

    def _Ortega_Elected_in_Nicaragua(self, side):
        self.map.set_influence('Nicaragua', Side.US, 0)
        self.card_operation_coup(side, 'Ortega_Elected_in_Nicaragua', restricted_list=[
                                 n for n in self.map['Nicaragua'].info.adjacent_countries], free=True)

    def _Terrorism(self, side):
        reps = 2 if 'Iranian_Hostage_Crisis' in self.basket[Side.USSR] and side == Side.USSR else 1

        for _ in range(reps):
            card_name = self.choose_random_card(side.opp)
            self.discard_pile.append(self.hand[side.opp].pop(
                self.hand[side.opp].index(card_name)))

    def _Iran_Contra_Scandal(self, side):
        self.basket[Side.USSR].append('Iran_Contra_Scandal')
        self.end_turn_stage_list.append(
            partial(self.basket[Side.USSR].remove, 'Iran_Contra_Scandal'))

    def _Chernobyl(self, side):
        def add_chernobyl(effect_name: str):
            self.basket[Side.US].append('effect_name')
            self.end_turn_stage_list.append(
                lambda: self.basket[Side.US].remove(effect_name))

        option_function_mapping = {
            'Europe': partial(add_chernobyl, 'Chernobyl_Europe'),
            'Middle East': partial(add_chernobyl, 'Chernobyl_Middle_East'),
            'Asia': partial(add_chernobyl, 'Chernobyl_Asia'),
            'Africa': partial(add_chernobyl, 'Chernobyl_Africa'),
            'Central America': partial(add_chernobyl, 'Chernobyl_Central_America'),
            'South America': partial(add_chernobyl, 'Chernobyl_South_America'),
        }

        self.input_state = Game.Input(
            side.opp, InputType.SELECT_MULTIPLE,
            partial(self.select_multiple_callback, option_function_mapping),
            option_function_mapping.keys(),
            prompt='Chernobyl: Designate a single Region where USSR cannot place influence using Operations for the rest of the turn.'
        )

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
                (n for n in CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA]
                    if self.map[n].has_ussr_influence),
                prompt='Select countries to double USSR influence.',
                reps=2,
                reps_unit='countries',
                max_per_option=1
            )

        self.input_state = Game.Input(
            Side.US, InputType.SELECT_CARD,
            partial(self.may_discard_callback, Side.US,
                    did_not_discard_fn=partial(self.stage_list.append, did_not_discard_fn)),
            (n for n in self.hand[Side.US]
                if n != 'The_China_Card'
                and self.get_global_effective_ops(side, self.cards[n].info.ops) >= 3),
            prompt='You may discard a card. If you choose not to discard, USSR chooses two countries in South America to double USSR influence.',
            option_stop_early='Do Not Discard'
        )

    def _Tear_Down_This_Wall(self, side):
        if 'Willy_Brandt' in self.basket[Side.USSR]:
            self.basket[Side.USSR].remove('Willy_Brandt')
        self.change_vp(1)
        self.map['West_Germany'].change_influence(0, 3)

        def _coup(self, side):
            self.card_operation_coup(side, 'Tear_Down_This_Wall', restricted_list=list(
                CountryInfo.REGION_ALL[MapRegion.EUROPE]), free=True)

        def _realignment(self, side):
            self.card_operation_realignment(side, 'Tear_Down_This_Wall', restricted_list=list(
                CountryInfo.REGION_ALL[MapRegion.EUROPE]), free=True)

        option_function_mapping = {
            'Free coup attempt': _coup,
            'Free realignment rolls': _realignment
        }

        self.input_state = Game.Input(
            side.opp, InputType.SELECT_MULTIPLE,
            partial(self.select_multiple_callback, option_function_mapping),
            option_function_mapping.keys(),
            prompt='Tear Down This Wall: US player may make free Coup attempts or realignment rolls in Europe.'
        )

    def _An_Evil_Empire(self, side):
        self.change_vp(-1)
        if 'Flower_Power' in self.basket[Side.USSR]:
            self.basket[Side.USSR].remove('Flower_Power')
        self.basket[Side.US].append('An_Evil_Empire')

    def _Aldrich_Ames_Remix(self, side):
        pass

    def _Pershing_II_Deployed(self, side):
        self.change_vp(1)
        self.input_state = Game.Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.decrement_influence, Side.US),
            (n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]
                if self.map[n].has_us_influence),
            prompt='Pershing II Deployed: Remove 1 US influence from any 3 countries in Western Europe.',
            reps=3,
            reps_unit='influence',
            max_per_option=1
        )

    def _Wargames(self, side):
        if self.can_play_event(side, 'Wargames'):
            pass
        pass

    def _Solidarity(self, side):
        if self.can_play_event(side, 'Solidarity'):
            self.map['Poland'].change_influence(0, 3)
            self.basket[Side.US].remove('John_Paul_II_Elected_Pope')

    def _Iran_Iraq_War(self, side):
        self.input_state = Game.Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.war_country_callback, side),
            ['Iran', 'Iraq'],
            prompt='Iran/Iraq War: Choose target of war.'
        )

    def _Yuri_and_Samantha(self, side):
        self.basket[Side.USSR].append('Yuri_and_Samantha')
        self.end_turn_stage_list.append(
            partial(self.basket[Side.USSR].remove, 'Yuri_and_Samantha'))

    def _AWACS_Sale_to_Saudis(self, side):
        self.map.change_influence('Saudi_Arabia', Side.US, 2)
        self.basket[Side.US].append('AWACS_Sale_to_Saudis')

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
        'Soviets_Shoot_Down_KAL_007': _Soviets_Shoot_Down_KAL_007,
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
