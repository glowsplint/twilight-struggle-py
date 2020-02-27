import math

from functools import partial
from itertools import chain
from typing import Sequence, Iterable, Callable, Tuple
from twilight_map import GameMap, CountryInfo, Country
from twilight_enums import Side, MapRegion, InputType, CardAction
from twilight_cards import GameCards, Card
from twilight_input_output import Input, Output


class Game:

    class Default:
        ARS_BY_TURN = (None, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7)
        AR_ORDER = [Side.USSR, Side.US]
        SPACE_ROLL_MAX = (3, 4, 3, 4, 3, 4, 3, 2)
        SPACE_VPS = ((2, 1), (0, 0), (2, 0), (0, 0),
                     (3, 1), (0, 0), (4, 2), (2, 0))
        SCORING = {
            MapRegion.ASIA: (3, 7, 9),
            MapRegion.EUROPE: (3, 7, 120),
            MapRegion.MIDDLE_EAST: (3, 5, 7),
            MapRegion.CENTRAL_AMERICA: (1, 3, 5),
            MapRegion.SOUTH_AMERICA: (2, 5, 6),
            MapRegion.AFRICA: (1, 4, 6)
        }

    def __init__(self):

        self.vp_track = 0
        self.turn_track = 0
        self.ar_track = 0
        self.ar_side = None
        self.ars_by_turn: Tuple[Sequence[int], Sequence[int]] = ([], [])
        self.ar_side_done: Sequence[bool] = [False, False]
        self.defcon_track = 0
        self.milops_track = [0, 0]
        self.space_track = [0, 0]  # 0 is start, 1 is earth satellite etc
        self.spaced_turns = [0, 0]

        self.map = None
        self.cards = None

        self.input_state = None
        self.output_queue = [[], []]

        self.hand = [[], [], []]  # neutral hand necessary
        self.removed_pile = []
        self.discard_pile = []
        self.draw_pile = []
        self.limbo = []  # strictly for shuttle_diplomacy
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
        self.ars_by_turn = [list(Game.Default.ARS_BY_TURN),
                            list(Game.Default.ARS_BY_TURN)]
        self.ar_side_done: Sequence[bool] = [False, False]
        self.defcon_track = 5
        self.milops_track = [0, 0]  # ussr first
        self.space_track = [0, 0]  # 0 is start, 1 is earth satellite etc
        self.spaced_turns = [0, 0]
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

    def stage_complete(self):
        self.input_state = None
        self.stage_list.pop()()

    def terminate(self, side: Side = Side.NEUTRAL):
        '''
        Terminates the game prematurely, due to DEFCON 1, held scoring cards, or Wargames.

        Parameters
        ----------
        side : Side, optional
            Side of the winner - used only when holding scoring cards, by default Side.NEUTRAL
            If side is Side.NEUTRAL, determine winner as the player with more VPs.
        '''
        self.stage_list.clear()
        if side != Side.NEUTRAL:
            winner = side.toStr()
        else:
            winner = 'USSR' if self.vp_track > 0 else 'US'
        print(f'{winner} victory!')

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

        for i in (1, 3, 5, 7, 8):
            if self.space_track[side] == i:
                if self.space_track[side.opp] < i:
                    self.change_vp(Game.Default.SPACE_VPS[i-1][0] * y)
                else:
                    self.change_vp(Game.Default.SPACE_VPS[i-1][1] * y)

            if self.space_track[side] == 8:
                self.ars_by_turn[side][self.turn_track] = 8

    def change_vp(self, n: int):
        '''
        Changes the number of VPs. Positive values are in favour of the USSR player.

        Parameters
        ----------
        n : int
            Number of VPs to change by.
        '''
        self.vp_track += n
        if self.vp_track >= 20 or self.vp_track <= -20:
            self.terminate()
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
            self.terminate()
        if previous_defcon > 2 and self.defcon_track == 2 and self.ar_track != 0 and 'NORAD' in self.basket[Side.US]:
            self.norad_influence()

        verb = 'improved' if n > 0 else 'degraded'
        print(f'DEFCON level {verb} to {self.defcon_track}.')

    def change_milops(self, side: Side, n: int):
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

    def reset_milops(self):
        self.milops_track = [0, 0]

    # Here, we have the game initialisation stages.
    def put_start_USSR(self):
        '''
        Stage for USSR player to place starting influence anywhere in Eastern Europe.
        '''
        self.input_state = Input(
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
        self.input_state = Input(
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

        self.input_state = Input(
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
        self.input_state = Input(
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
        special_case = False
        for s in [Side.USSR, Side.US]:
            if self.space_track[s] >= 4 and self.space_track[s.opp] < 4:
                self.stage_list.append(self.ar_complete)
                self.stage_list.append(self.resolve_headline_order)
                self.stage_list.append(partial(self.show_headline, s))
                self.stage_list.append(partial(self.choose_headline, s))
                self.stage_list.append(partial(self.show_headline, s.opp))
                self.stage_list.append(partial(self.choose_headline, s.opp))
                special_case = True
                break

        if not special_case:
            self.stage_list.append(self.ar_complete)
            self.stage_list.append(self.resolve_headline_order)
            self.stage_list.append(partial(self.show_headline, Side.US))
            self.stage_list.append(partial(self.show_headline, Side.USSR))
            self.stage_list.append(partial(self.choose_headline, Side.US))
            self.stage_list.append(partial(self.choose_headline, Side.USSR))

    def show_headline(self, side: Side):
        '''
        Stage to show the headline to the other player.

        Parameters
        ----------
        side : Side, optional
            Side's headline is displayed
        '''
        print(
            f'{side.toStr()} selected {self.headline_bin[side]} for headline.')

    def resolve_headline_order(self):
        '''
        Stage to trigger the headlines.
        '''
        ussr_hl = self.headline_bin[Side.USSR]
        us_hl = self.headline_bin[Side.US]

        if us_hl == 'Defectors' or self.cards[us_hl].ops >= self.cards[ussr_hl].info.ops:
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
                partial(self.dispose_headline, side))
            self.stage_list.append(
                partial(self.trigger_event, side, card_name))
            self.headline_bin[side] = ''

    def dispose_headline(self, side):
        if self.headline_bin[side]:
            c = self.headline_bin[side]
            if self.cards[c].info.unique_event:
                self.removed_pile.append(c)
            else:
                self.discard_pile.append(c)
            self.headline_bin[side] = ''

    def ars_remaining(self, side):
        '''
        This gets the number of ARs remaining in the current turn for a side,
        Is inclusive of the current AR.
        '''
        return max(0, self.ars_by_turn[side][self.turn_track] - self.ar_track + 1 - self.ar_side_done[side])

    def ar_complete(self):

        if self.ar_track > 0:
            self.ar_side_done[self.ar_side] = True
            self.ar_side = Side(self.ar_side + 1)
        while True:
            if not self.ar_track or self.ar_side == len(Game.Default.AR_ORDER):
                # check if just ended headline or
                # if AR should be incremented
                self.ar_track += 1  # ars increase from 0(HL), 1, 1.5, 2..
                self.ar_side_done = [not self.ars_remaining(
                    s) for s in Game.Default.AR_ORDER]
                self.ar_side = Game.Default.AR_ORDER[0]
                if all(self.ar_side_done):
                    # End the turn since all players have no more ARs
                    self.stage_list.append(self.end_of_turn)
                    return
            if not self.ar_side_done[self.ar_side]:
                break
            self.ar_side = Side(self.ar_side + 1)

        self.stage_list.append(self.ar_complete)
        if self.ar_side == Side.US and 'Quagmire' in self.basket[Side.US]:
            self.stage_list.append(
                partial(self.qbt_discard, Side.US, 'Quagmire'))
        elif self.ar_side == Side.USSR and 'Bear_Trap' in self.basket[Side.USSR]:
            self.stage_list.append(
                partial(self.qbt_discard, Side.USSR, 'Bear_Trap'))
        else:
            self.stage_list.append(self.select_card)

    def can_play_event(self, side: Side, card_name: str):
        '''
        Checks if all the prerequisites for the Event are fulfilled.
        True if:
        1. All prerequisites are fulfilled (including event prevention), and
        2. The card is owned by you

        Parameters
        ----------
        side : Side
            Side of the phasing player.
        card_name : str
            String representation of the card.
        '''
        return self.cards[card_name].can_event(self, side) and side != self.cards[card_name].owner.opp

    def can_resolve_event_first(self, side: Side, card_name: str):
        '''
        Checks if the phasing player can resolve the card's Event first.
        True if:
        1. Card is opponent-owned, and
        2. All the prerequisites for the event are fulfilled.

        Parameters
        ----------
        side : Side
            Side of the player who plays the card.
        card_name : str
            String representation of the card.
        '''
        return side == self.cards[card_name].owner.opp and self.cards[card_name].can_event(self, side.opp)

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

        def available_space_turn(self, side: Side):
            if self.spaced_turns[side] == 2:
                return False
            elif self.spaced_turns[side] == 0:
                return True
            elif self.space_track[side.opp] < 2 and self.space_track[side] >= 2:
                return True
            else:
                return False

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

        self.input_state = Input(
            side, InputType.SELECT_CARD,
            partial(self.card_callback, side),
            (c for c in self.hand[side] if self.cards[c].is_playable),
            prompt='Select a card in hand to play.'
        )

    def card_callback(self, side: Side, card_name: str):
        self.input_state.reps -= 1
        if self.cards[card_name].info.card_type == 'Scoring':
            self.stage_list.append(
                partial(self.resolve_card_action, side,
                        card_name, CardAction.PLAY_EVENT.name)
            )
        else:
            if card_name == 'The_China_Card' and side == Side.US and 'Formosan_Resolution' in self.basket[Side.US]:
                self.basket[Side.US].remove('Formosan_Resolution')
            if card_name == 'UN_Intervention' and 'U2_Incident' in self.basket[Side.USSR]:
                self.change_vp(1)
            self.stage_list.append(
                partial(self.select_action, side, card_name))
        return True

    def action_callback(self, side: Side, card_name: str, action_name: str,
                        is_event_resolved: bool = False, un_intervention: bool = False, grain_sales: bool = False):
        self.input_state.reps -= 1
        self.stage_list.append(
            partial(self.resolve_card_action, side,
                    card_name, action_name, is_event_resolved=is_event_resolved,
                    un_intervention=un_intervention, grain_sales=grain_sales)
        )
        return True

    def select_action(self, side: Side, card_name: str, is_event_resolved: bool = False,
                      un_intervention: bool = False, grain_sales: bool = False, can_coup=True, free_coup_realignment=False):
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
            not un_intervention and not is_event_resolved and self.can_play_event(
                side, card_name),
            not un_intervention and not is_event_resolved and self.can_resolve_event_first(
                side, card_name),
            self.can_place_influence(side, card_name),
            self.can_realign_at_all(side),
            self.can_coup_at_all(side) and can_coup,
            not is_event_resolved and self.can_space(side, card_name)
        ]

        self.input_state = Input(
            side, InputType.SELECT_CARD_ACTION,
            partial(self.action_callback, side, card_name,
                    is_event_resolved=is_event_resolved,
                    un_intervention=un_intervention,
                    grain_sales=grain_sales),
            (CardAction(i).name for i, b in enumerate(bool_arr) if b),
            prompt=f'Select an action for {card_name}.'
        )

    def resolve_card_action(self, side: Side, card_name: str, action_name: str,
                            is_event_resolved: bool = False, un_intervention: bool = False, grain_sales: bool = False):
        '''
        This function should lead to card_operation_realignment, card_operation_coup,
        or card_operation_influence, or a space race function.
        '''

        action = CardAction[action_name]
        card = self.cards[card_name]
        opp_event = (card.info.owner == side.opp)

        if 'We_Will_Bury_You' in self.basket[Side.USSR]:
            if card_name != 'UN_Intervention' and action == CardAction.PLAY_EVENT:
                self.change_vp(3)
            self.basket[Side.USSR].remove('We_Will_Bury_You')

        if action == CardAction.PLAY_EVENT:

            if grain_sales:
                self.stage_list.append(
                    partial(self.dispose_card, Side.USSR, card_name, event=True))
            else:
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

            if grain_sales:
                self.stage_list.append(
                    partial(self.dispose_card, Side.USSR, card_name))
            else:
                self.stage_list.append(
                    partial(self.dispose_card, side, card_name))
            self.stage_list.append(partial(self.space, side, card_name))

        elif action == CardAction.INFLUENCE:

            if grain_sales:
                self.stage_list.append(
                    partial(self.dispose_card, Side.USSR, card_name, event=opp_event))
            else:
                self.stage_list.append(
                    partial(self.dispose_card, side, card_name, event=opp_event))
            if opp_event and not is_event_resolved and not un_intervention:
                self.stage_list.append(
                    partial(self.trigger_event, side, card_name))
            self.stage_list.append(
                partial(self.card_operation_influence, side, card_name))

        elif action == CardAction.REALIGNMENT:

            if grain_sales:
                self.stage_list.append(
                    partial(self.dispose_card, Side.USSR, card_name, event=opp_event))
            else:
                self.stage_list.append(
                    partial(self.dispose_card, side, card_name, event=opp_event))
            if opp_event and not is_event_resolved and not un_intervention:
                self.stage_list.append(
                    partial(self.trigger_event, side, card_name))
            self.stage_list.append(
                partial(self.card_operation_realignment, side, card_name))

        elif action == CardAction.COUP:

            side = Side.USSR if grain_sales else side
            self.stage_list.append(
                partial(self.dispose_card, side, card_name, event=opp_event))
            if opp_event and not is_event_resolved and not un_intervention:
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
        elif card_name == 'Shuttle_Diplomacy':
            self.limbo.append('Shuttle_Diplomacy')
            self.hand[side].remove(card_name)
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
        receipient.append('The_China_Card')
        self.cards['The_China_Card'].is_playable = made_playable

    def get_global_effective_ops(self, side: Side, raw_ops: int):
        '''
        Gets the effective operations value of the card, bound to [1,4]. Accounts for
        only global effects like Containment, Brezhnev_Doctrine and Red_Scare_Purge.

        Does not account for local effects like additional operations points from the use
        of the China Card in Asia, or in SEA when Vietnam Revolts is active.

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
        self.cards[card_name].use_event(self, side)

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

        self.input_state = Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.ops_influence_callback, side),
            (n for n in CountryInfo.ALL
                if self.map.can_place_influence(self, n, side, effective_ops)),
            prompt=f'Place operations from {card_name} as influence.',
            reps=effective_ops,
            reps_unit='operations'
        )

    def realign_dice_callback(self, name, side, num: tuple):
        self.input_state.reps -= 1
        self.map.realignment(self, name, side, *num)
        return True

    def realignment_callback(self, side: Side, name: str, card_name: str, reps: int = None) -> bool:
        reps -= 1
        self.input_state.reps -= 1

        if reps:
            self.stage_list.append(
                partial(self.card_operation_realignment, side, card_name=card_name, reps=reps))

        self.stage_list.append(partial(
            self.dice_stage,
            partial(self.realign_dice_callback, name, side),
            two_dice=True
        ))
        return True

    def card_operation_realignment(self, side: Side, card_name: str, reps: int = None, restricted_list: Sequence[str] = None, free=False):
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
            can_stop_now = ''
        else:
            effective_ops = reps
            can_stop_now = 'Stop realignments.'

        if restricted_list is None:
            restricted_list = CountryInfo.ALL

        self.input_state = Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.realignment_callback, side,
                    card_name=card_name, reps=effective_ops),
            (n for n in CountryInfo.ALL if self.map.can_realignment(
                self, n, side) and n in restricted_list),
            prompt=f'Select a country for realignment using operations from {card_name}. {effective_ops} realignments remaining.',
            option_stop_early=can_stop_now
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

        self.input_state = Input(
            Side.NEUTRAL, InputType.ROLL_DICE,
            fn,
            options,
            prompt=prompt,
        )

    def coup_dice_callback(self, name, side, ops, free, num: str, che=False):
        self.input_state.reps -= 1

        if che:
            before_us_inf = self.map[name].influence[Side.US]
            ca_sa_af = chain(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA],
                             CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA],
                             CountryInfo.REGION_ALL[MapRegion.AFRICA])

        self.map.coup(self, name, side, ops, int(num), free=free)

        if che and self.map[name].influence[Side.US] < before_us_inf:
            print('You are allowed a second coup from Che.')
            self.card_operation_coup(Side.USSR, 'Che', restricted_list=[
                n for n in ca_sa_af if not self.map[n].info.battleground], che=False)

        return True

    def coup_callback(self, side: Side, effective_ops: int, card_name: str, country_name: str, free=False, che=False) -> bool:
        self.input_state.reps -= 1

        local_ops_modifier = 0
        if card_name == 'The_China_Card' and country_name in CountryInfo.REGION_ALL[MapRegion.ASIA]:
            local_ops_modifier += 1
        if 'Vietnam_Revolts' in self.basket[Side.USSR] and country_name in CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]:
            local_ops_modifier += 1

        self.stage_list.append(partial(
            self.dice_stage,
            partial(self.coup_dice_callback, country_name, side,
                    effective_ops + local_ops_modifier, free, che=che)
        ))

        return True

    def card_operation_coup(self, side: Side, card_name: str, restricted_list: Sequence[str] = None, free=False, che=False):
        '''
        Stage when a player is given the opportunity to coup. Provides a list
        of countries which can be couped and waits for player input.

        TODO: Does not currently check the player baskets for China Card and Vietnam effects.

        Parameters
        ----------
        side : Side
            Side of the player who is couping.
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

        # Cuban Missile Crisis
        if 'Cuban_Missile_Crisis' in self.basket[side.opp]:
            self.cuban_missile_remove(side)

        def choose_coup_country():
            self.input_state = Input(
                side, InputType.SELECT_COUNTRY,
                partial(self.coup_callback, side,
                        effective_ops, card_name, che=che),
                (n for n in CountryInfo.ALL
                    if self.map.can_coup(self, n, side) and n in restricted_list),
                prompt=f'Select a country to coup using operations from {card_name}.',
            )

        self.stage_list.append(choose_coup_country)

    def space_dice_callback(self, side, num: str):
        self.input_state.reps -= 1
        curr_stage = self.space_track[side]

        outcome = 'Success' if int(
            num) <= Game.Default.SPACE_ROLL_MAX[curr_stage] else 'Failure'
        if outcome == 'Success':
            self.change_space(side, 1)
        print(f'{outcome} with roll of {num}.')
        self.spaced_turns[side] += 1
        return True

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

        self.stage_list.append(partial(
            self.dice_stage,
            partial(self.space_dice_callback, side)
        ))
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
            partial(Country.increment_influence, amt=2).
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

    def war_dice_callback(self, name, side, modifier, min_roll, win_vp, win_milops, num: str):

        self.input_state.reps -= 1
        if int(num) - modifier >= min_roll:
            self.change_vp(win_vp * side.vp_mult)
            self.change_milops(side, win_milops)

            influence = self.map[name].influence[side.opp]
            self.map[name].remove_influence(side.opp)
            self.map[name].increment_influence(side, influence)
            print(f'Success with roll of {num}.')
        else:
            print(f'Failure with roll of {num}.')

        return True

    def war(self, country_name: str, side: Side, country_itself: bool = False,
            lower: int = 4, win_vp: int = 2, win_milops: int = 2):
        country = self.map[country_name]

        modifier = sum(self.map[adjacent_country].control == side.opp
                       for adjacent_country in country.info.adjacent_countries)

        if country_itself and country.control == side.opp:  # For Arab-Israeli War
            modifier += 1

        self.stage_list.append(partial(
            self.dice_stage,
            partial(self.war_dice_callback, country_name, side,
                    modifier, lower, win_vp, win_milops))
        )

    def war_country_callback(self, side: Side, country_name: str, country_itself: bool = False,
                             lower: int = 4, win_vp: int = 2, win_milops: int = 2):
        self.input_state.reps -= 1
        self.war(country_name, side, country_itself=country_itself,
                 lower=lower, win_vp=win_vp, win_milops=win_milops)
        return True

    def norad_influence(self):
        self.input_state = Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    Country.increment_influence, Side.US),
            self.map.has_us_influence,
            prompt='Place NORAD influence.',
            reps_unit='influence'
        )

    def forced_to_missile_envy(self):
        # check first if the player has as many scoring cards as turns
        # if True, then player is given choice as to which scoring card they
        # can play. this stage is then triggered again at a later stage.
        pass

    def select_take_8_rounds(self):
        pass

    def qbt_dice_callback(self, side: Side, trap_name: str, num: str):
        self.input_state.reps -= 1
        if int(num) <= 4:
            self.basket[side].remove(trap_name)
        return True

    def qbt_discard_callback(self, side: Side, trap_name: str, card_name: str):
        self.input_state.reps -= 1
        self.stage_list.append(partial(self.dice_stage, partial(
            self.qbt_dice_callback, side, trap_name)))
        return True

    def qbt_discard(self, side: Side, trap_name: str):
        '''
        Discarding stage for Quagmire/Bear Trap.

        Parameters
        ----------
        side : Side
            Side of the player who is encountering the discard stage.
        trap_name: str
            Name of the basket effect. Can be either 'Quagmire' or 'Bear_Trap'.

        Returns
        -------
        bool
            True if there was a suitable discard/scoring card played, false if not.
        '''

        suitable_cards = [n for n in self.hand[side]
                          if n != 'The_China_Card'
                          and self.get_global_effective_ops(side, self.cards[n].info.ops) >= 2]

        scoring_cards = [n for n in self.hand[side]
                         if self.cards[n].info.card_type == 'Scoring']

        # If we have as many scoring cards as action rounds, then we must play
        # a scoring card. Q/BT stays in basket.
        if len(scoring_cards) == self.ars_remaining(side):
            self.input_state = Input(
                side, InputType.SELECT_CARD,
                partial(self.trigger_event, side),
                scoring_cards,
                prompt='You must play a scoring card.',
            )

        # Otherwise, if there are discardable cards, you have to discard from these.
        elif suitable_cards:
            self.input_state = Input(
                side, InputType.SELECT_CARD,
                partial(self.qbt_discard_callback, side, trap_name),
                suitable_cards,
                prompt='You must discard a card to be released.',
            )
        # If you don't have suitable discards, then you can't play anything.
        else:
            print('AR skipped due to lack of suitable cards.')

    def cuban_missile_remove(self, side: Side):
        '''
        Gives an opportunity to the couping player to remove 2 influence from
        Cuba/(West Germany/Turkey) if USSR/US respectively. This stage triggers
        only when a coup is initiated, rather than 'any time' as mentioned by the
        card event text.

        Parameters
        ----------
        side : Side
            Side of couping player
        '''
        if side == Side.USSR:
            countries = ['Cuba']
        elif side == Side.US:
            countries = ['West_Germany', 'Turkey']
        options = [n for n in countries if self.map[n].influence[side] >= 2]

        if len(options) == 0:
            return False

        def cuban_callback(self, opt: str):
            if opt != self.input_state.option_stop_early:
                self.event_influence_callback(
                    partial(Country.decrement_influence, amt=2), side, opt)
                self.basket[side.opp].remove('Cuban_Missile_Crisis')
            else:
                self.input_state.reps -= 1
            return True

        self.input_state = Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(cuban_callback, self),
            options,
            prompt='Cuban Missile Crisis: Remove 2 influence to de-escalate.',
            reps_unit='influence',
            option_stop_early='Do not remove influence.'
        )

    def shuffle_callback(self, card_name):
        self.input_state.reps -= 1
        self.draw_pile.append(card_name)
        return True

    def shuffle_draw_pile_stage(self):
        shuffler_pile = self.draw_pile
        self.draw_pile = []

        self.input_state = Input(
            Side.NEUTRAL, InputType.SELECT_CARD,
            self.shuffle_callback,
            shuffler_pile,
            'Shuffle the deck.  Select the next card.',
            reps=len(shuffler_pile),
            reps_unit='cards',
            max_per_option=1
        )

    def expand_deck(self):

        if self.turn_track == 1:
            # TEST CODE BELOW -- remove when done
            '''For testing early-war cards'''
            self.hand[Side.USSR].extend([self.cards.early_war.pop(i)
                                         for i in range(20)])
            self.hand[Side.US].extend([self.cards.early_war.pop(0)
                                       for i in range(19)])
            '''For testing mid-war cards'''
            self.hand[Side.US].extend([self.cards.mid_war.pop(i)
                                       for i in range(24)])
            self.hand[Side.USSR].extend([self.cards.mid_war.pop(0)
                                         for i in range(24)])
            '''For testing late-war cards'''
            self.hand[Side.US].extend([self.cards.late_war.pop(i)
                                       for i in range(12)])
            self.hand[Side.USSR].extend([self.cards.late_war.pop(0)
                                         for i in range(11)])
            # TEST CODE ABOVE -- remove when done
            self.draw_pile.extend(self.cards.early_war)
            # # WORKING CODE BELOW -- uncomment if not using test code
            # self.hand[Side.USSR].append(self.draw_pile.pop(
            #     self.draw_pile.index('The_China_Card')))
            # # WORKING CODE ABOVE -- uncomment if not using test code
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

        if first_side == Side.NEUTRAL:
            handsize_target = [3, 2]
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
                self.stage_list.append(
                    partial(self.deal, first_side=next_side))
                self.shuffle_draw_pile_stage()
                return

    # need to make sure next_turn is only called after all extra rounds
    def end_of_turn(self):

        print('-------------------- End of turn --------------------')
        # -2. Check for held scoring card (originally #2. but moved up to prevent held scoring cards)

        def check_for_scoring_cards(self):
            scoring_list = ['Asia_Scoring', 'Europe_Scoring', 'Middle_East_Scoring',
                            'Central_America_Scoring', 'Southeast_Asia_Scoring',
                            'Africa_Scoring', 'South_America_Scoring']
            scoring_cards = [self.cards[y] for y in scoring_list]
            if any(True for x in scoring_cards if x in self.hand[Side.US]):
                self.terminate(Side.USSR)
            elif any(True for x in scoring_cards if x in self.hand[Side.USSR]):
                self.terminate(Side.US)

        # -1. Check if any player may discard held cards, also resets space turns
        def space_discard(self):
            # Will hardcode to prevent discarding The China Card via Eagle/Bear has landed
            for s in [Side.USSR, Side.US]:
                if self.space_track[s] >= 6 and self.space_track[s.opp] < 6:
                    self.input_state = Input(
                        s, InputType.SELECT_CARD,
                        partial(self.may_discard_callback, s),
                        (n for n in self.hand[s] if n != 'The_China_Card'),
                        prompt='You may discard a held card via Eagle/Bear has landed.',
                        option_stop_early='Do not discard.'
                    )
                    break
            self.spaced_turns = [0, 0]

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
            self.reset_milops()

        # 3. Flip China Card
        def flip_china_card(self):
            self.cards['The_China_Card'].is_playable = True

        # 4. Advance turn marker
        def advance_turn_marker(self):
            self.turn_track += 1
            self.ar_track = 0  # headline phase

        # 5. Final scoring (end T10)
        def final_scoring(self):
            if self.turn_track == 10 and (self.ar_track in [15, 16, 17]):
                self._Asia_Scoring()
                self._Europe_Scoring()
                self._Middle_East_Scoring()
                self._Central_America_Scoring()
                self._South_America_Scoring()
                self._Africa_Scoring()
            for s in [Side.USSR, Side.US]:
                if 'The_China_Card' in self.hand[s]:
                    self.change_vp(s.vp_mult)
            print(f'Final scoring complete.')
            self.terminate()

        # 6. Increase DEFCON status
        # 7. Deal Cards -- written outside the next_turn function
        # 8. Headline Phase

        # 9. Action Rounds (advance round marker) -- action rounds are not considered between turns
        check_for_scoring_cards(self)
        clear_baskets(self)
        space_discard(self)
        check_milops(self)
        flip_china_card(self)
        advance_turn_marker(self)  # turn marker advanced before final scoring
        final_scoring(self)
        self.change_defcon(1)
        self.expand_deck()
        self.deal()  # turn marker advanced before dealing
        self.process_headline()

    def score(self, region: MapRegion, check_only=False):

        (presence_vps, domination_vps,
         control_vps) = Game.Default.SCORING[region]

        if 'Formosan_Resolution' in self.basket[Side.US]:
            self.map['Taiwan'].info.battleground = True

        shuttle_modifier = 1 if 'Shuttle_Diplomacy' in self.basket[Side.US] else 0

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

        if region in [MapRegion.ASIA, MapRegion.MIDDLE_EAST]:
            bg_count[Side.USSR] -= shuttle_modifier
            country_count[Side.USSR] -= shuttle_modifier

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

        if not check_only:
            swing = vps[Side.USSR] * Side.USSR.vp_mult + \
                vps[Side.US] * Side.US.vp_mult
            print(f'{region.name} scores for {swing} VP')
            self.change_vp(swing)
        else:
            print(
                f'USSR:US = {vps[Side.USSR]}:{vps[Side.US]}')

        if self.map['Taiwan'].info.battleground:
            self.map['Taiwan'].info.battleground = False
