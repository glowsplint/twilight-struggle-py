import math

from functools import partial
from itertools import chain
from typing import Sequence, Iterable, Callable, Tuple

from twilight_map import GameMap, CountryInfo, Country
from twilight_enums import Side, MapRegion, InputType, CardAction
from twilight_cards import GameCards, Card
from twilight_input_output import Input
from twilight_playerview import PlayerView

# 起始 handicap 补偿: 引擎历史行为给 US 额外 +2 起始影响力(负值偏向 US,
# 正值偏向 USSR,标准规则为 0)。UI、RL env、训练与全部智能体均依赖此
# 默认分布——改动它会整体改变训练分布,调用点应显式传参而非依赖默认值。
DEFAULT_HANDICAP = -2


def _choose_coup_country(game_instance, side, effective_ops, card_name,
                         restricted_list, free, che, event_after_ops=False,
                         ignore_defcon=False):
    """Coup target selection stage (module-level for deepcopy safety:
    game_instance must arrive via partial args so cloned games rebind it —
    a closure over the original game would keep mutating the wrong object)."""
    game_instance.input_state = Input(
        side, InputType.SELECT_COUNTRY,
        partial(game_instance.coup_callback, side,
                effective_ops, card_name, free=free, che=che,
                ignore_defcon=ignore_defcon),
        (n for n in CountryInfo.ALL
            if game_instance.map.can_coup(
                game_instance, n, side, free=free,
                ignore_defcon=ignore_defcon)
            and n in restricted_list),
        prompt=f'Select a country to coup using operations from {card_name}.',
        context={
            'source_card': card_name,
            'event_after_ops': bool(event_after_ops),
        })


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
        self.defcon_reached_two_this_ar = False
        self.milops_track = [0, 0]
        self.space_track = [0, 0]  # 0 is start, 1 is earth satellite etc
        self.spaced_turns = [0, 0]

        self.map = None
        self.cards = None
        self.players = None

        self.input_state = None

        self.hand = [[], [], []]  # neutral hand necessary
        self.unknown_hand_draws = [0, 0]
        self.removed_pile = []
        self.discard_pile = []
        self.draw_pile = []
        self.shuffle_count = 0
        self.card_last_shuffled = {}
        self.limbo = []  # strictly for shuttle_diplomacy
        self.basket = [[], []]
        self.headline_bin = ['', '']
        self.headline_resolving_side = None
        self.end_turn_stage_list = []

        self.started = False
        self.terminated = False
        self.final_scoring_active = False
        self.termination_reason = ''
        self.termination_context = {}
        self.termination_winner = Side.NEUTRAL

    '''
    Starts a new game.
    '''

    def start(self, handicap: int = DEFAULT_HANDICAP):

        self.started = True
        self.terminated = False
        self.final_scoring_active = False
        self.termination_reason = ''
        self.termination_context = {}
        self.termination_winner = Side.NEUTRAL
        self.vp_track = 0  # positive for ussr
        self.turn_track = 1
        self.ar_track = 0
        self.ar_side = Side.USSR
        self.headline_resolving_side = None
        self.ars_by_turn = [list(Game.Default.ARS_BY_TURN),
                            list(Game.Default.ARS_BY_TURN)]
        self.ar_side_done: Sequence[bool] = [False, False]
        self.defcon_track = 5
        self.defcon_reached_two_this_ar = False
        self.milops_track = [0, 0]  # ussr first
        self.space_track = [0, 0]  # 0 is start, 1 is earth satellite etc
        self.spaced_turns = [0, 0]
        self.shuffle_count = 0
        self.card_last_shuffled = {}
        self.map = GameMap()
        self.cards = GameCards()
        self.players = [PlayerView(Side.USSR), PlayerView(Side.US)]
        self.unknown_hand_draws = [0, 0]
        self.handicap = handicap  # positive in favour of ussr

        self.stage_list = [
            self.expand_deck,
            self.deal,
            partial(self.put_start, Side.USSR,
                    CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE], 6),
            partial(self.put_start, Side.US,
                    CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE], 7),
            self.put_start_extra,
            self.process_headline,
        ]
        self.stage_list.reverse()

        self.map.build_standard()

    def stage_complete(self):
        self.input_state = None
        if not self.stage_list:
            raise RuntimeError(
                "stage_complete() called with empty stage_list. "
                "This means the game has terminated but something is still "
                "trying to advance the stage machine. Check for a missing "
                "'done' check in the calling loop."
            )
        self.stage_list.pop()()

    def safe_remove_from_basket(self, side: Side, item: str) -> None:
        """Remove an item from a basket if present — no-op otherwise."""
        try:
            self.basket[side].remove(item)
        except ValueError:
            pass

    def add_turn_effect(self, side: Side, name: str) -> None:
        """Register a persistent effect that lasts until the end of turn.

        Adds ``name`` to the side's basket and schedules its automatic removal
        in ``end_turn_stage_list`` (run by end_of_turn's clear_baskets, which
        tolerates a missing item via ValueError)."""
        self.basket[side].append(name)
        self.end_turn_stage_list.append(
            partial(self.basket[side].remove, name))

    def terminate(self, side: Side = Side.NEUTRAL, reason: str = '', context: dict = None):
        '''
        Terminates the game prematurely, due to DEFCON 1, held scoring cards, or Wargames.

        Parameters
        ----------
        side : Side, optional
            Side of the winner - used only when holding scoring cards, by default Side.NEUTRAL
            If side is Side.NEUTRAL, determine winner as the player with more VPs.
        reason : str, optional
            Structured game-over reason for logging/analysis.
        context : dict, optional
            Additional key-value metadata about the game-over state.
        '''
        self.terminated = True
        self.termination_reason = reason
        self.termination_context = context or {}
        # Hard-stop all pending interaction so callers cannot keep driving the
        # state machine after game over.
        self.input_state = None
        self.stage_list.clear()
        if side != Side.NEUTRAL:
            self.termination_winner = side
            winner = side.toStr()
        else:
            if self.vp_track > 0:
                self.termination_winner = Side.USSR
                winner = self.termination_winner.toStr()
            elif self.vp_track < 0:
                self.termination_winner = Side.US
                winner = self.termination_winner.toStr()
            else:
                self.termination_winner = Side.NEUTRAL
                winner = 'Draw'
        print(f'{winner} victory!')

    '''Here are functions used to manipulate the various tracks.'''

    def change_space(self, side: Side, n: int, score_intermediate: bool = True):
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
        start = self.space_track[side]
        end = max(0, min(8, start + n))

        if end == start:
            return

        self.space_track[side] = end

        if end > start:
            for i in range(start + 1, end + 1):
                if i in (1, 3, 5, 7, 8) and (score_intermediate or i == end):
                    if self.space_track[side.opp] < i:
                        self.change_vp(Game.Default.SPACE_VPS[i - 1][0] * y)
                    else:
                        self.change_vp(Game.Default.SPACE_VPS[i - 1][1] * y)
                    if self.terminated:
                        return

                if i == 8:
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
        if ((self.vp_track >= 20 or self.vp_track <= -20)
            and not self.final_scoring_active):
            self.terminate(reason='vp_autovictory', context={'vp_track': self.vp_track})
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
        if self.terminated:
            raise RuntimeError(
                f"change_defcon({n}) called after termination. "
                f"reason={self.termination_reason}, context={self.termination_context}"
            )

        previous_defcon = self.defcon_track
        self.defcon_track = max(1, min(5, self.defcon_track + n))
        if self.defcon_track < 2:
            print('Game ended by thermonuclear war')
            # Rule 6.3: the phasing player is responsible for all DEFCON
            # degradation and loses. During the Headline Phase the phasing
            # player is the side whose headline event is being resolved,
            # even if the opponent conducts the Operations (e.g. CIA
            # Created / Lone Gunman granted Ops). The headline marker takes
            # precedence because ar_side may hold a stale value here.
            if self.headline_resolving_side in (Side.USSR, Side.US):
                loser = self.headline_resolving_side
            elif self.ar_side in (Side.USSR, Side.US):
                loser = self.ar_side
            else:
                loser = Side.NEUTRAL
            winner = loser.opp if loser is not Side.NEUTRAL else Side.NEUTRAL
            self.terminate(side=winner, reason='thermonuclear_war', context={'defcon': self.defcon_track})
            return
        if (previous_defcon > 2
                and self.defcon_track == 2
                and self.ar_track != 0):
            self.defcon_reached_two_this_ar = True

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
    def put_start(self, side: Side, region, reps: int):
        '''Stage for a player to place starting influence in a region.'''
        self.event_place_influence(
            side, Country.increment_influence, side, region,
            prompt='Place starting influence.', reps=reps,
            context={'decision_kind': 'setup'})

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
            reps_unit='influence',
            context={'decision_kind': 'setup_extra'},
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
            (c for c in self.hand[side]
             if self.cards[c].info.can_headline
             and not (c == 'Missile_Envy'
                      and 'Missile_Envy' in self.basket[side])),
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

        if not ussr_hl:
            raise RuntimeError(
                f"USSR headline is empty at resolve_headline_order. "
                f"headline_bin={self.headline_bin}. "
                f"This means choose_headline(USSR) never ran or its callback was not invoked. "
                f"Check for an earlier exception that skipped the headline selection phase."
            )
        if not us_hl:
            raise RuntimeError(
                f"US headline is empty at resolve_headline_order. "
                f"headline_bin={self.headline_bin}. "
                f"This means choose_headline(US) never ran or its callback was not invoked. "
                f"Check for an earlier exception that skipped the headline selection phase."
            )

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
        if not card_name:
            # Legitimate: Defectors cancels opponent's headline, or the
            # headline phase was skipped because a player had no headlineable
            # cards.  Either way there is nothing to resolve.
            return
        # This side's headline event is now resolving: for DEFCON
        # attribution it is treated as the phasing player (rule 6.3).
        self.headline_resolving_side = side
        self.apply_flower_power(side, card_name)
        if self.terminated:
            return
        self.stage_list.append(
            partial(self.dispose_headline, side))
        self.stage_list.append(
            partial(self.trigger_event, side, card_name))

    def dispose_headline(self, side):
        card_name = self.headline_bin[side]
        if not card_name:
            return
        if card_name not in self.hand[side]:
            self.hand[side].append(card_name)
        self.cards[card_name].dispose(self, side)
        self.headline_bin[side] = ''
        if not self.headline_bin[Side.USSR] and not self.headline_bin[Side.US]:
            # Headline phase fully resolved: clear the attribution marker.
            self.headline_resolving_side = None

    def ars_remaining(self, side):
        '''
        This gets the number of ARs remaining in the current turn for a side.
        Is inclusive of the current AR.
        '''
        return max(0, self.ars_by_turn[side][self.turn_track] - self.ar_track + 1 - self.ar_side_done[side])

    def ar_complete(self):

        # Action rounds must never see a stale headline attribution marker.
        self.headline_resolving_side = None

        if (self.ar_track > 0
                and self.ar_side in Game.Default.AR_ORDER):
            self.ar_side_done[self.ar_side] = True
            self.ar_side = Side(self.ar_side + 1)

        while True:
            if not self.ar_track or self.ar_side == len(Game.Default.AR_ORDER):
                # check if just ended headline or
                # if AR should be incremented
                if self.ar_track > 0 and self.defcon_reached_two_this_ar:
                    self.defcon_reached_two_this_ar = False
                    if ('NORAD' in self.basket[Side.US]
                            and self.map['Canada'].control == Side.US):
                        self.stage_list.append(self.ar_complete)
                        self.cards['NORAD'].place_norad_influence(self)
                        if self.input_state is not None:
                            return
                self.ar_track += 1
                # The old flags refer to the PREVIOUS AR (both sides already
                # completed it). Reset them before recomputing, otherwise
                # ars_remaining() subtracts a stale 1 and the turn ends one
                # AR early (off-by-one: 5 ARs in the Early War instead of 6).
                self.ar_side_done = [False, False]
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
        next_stage = self.select_card
        if self.ar_side == Side.US and 'Quagmire' in self.basket[Side.US]:
            next_stage = partial(self.qbt_discard, Side.US, 'Quagmire')
        elif self.ar_side == Side.USSR and 'Bear_Trap' in self.basket[Side.USSR]:
            next_stage = partial(self.qbt_discard, Side.USSR, 'Bear_Trap')
        self.stage_list.append(next_stage)

        if 'Cuban_Missile_Crisis' in self.basket[self.ar_side.opp]:
            self.stage_list.append(
                partial(self.maybe_cancel_cuban_missile_crisis, self.ar_side))

        if 'Vietnam_Revolts' in self.basket[Side.USSR]:
            self.cards['Vietnam_Revolts'].reset()

    def maybe_cancel_cuban_missile_crisis(self, side: Side):
        if 'Cuban_Missile_Crisis' not in self.basket[side.opp]:
            return
        self.cards['Cuban_Missile_Crisis'].cuban_missile_remove(self, side)

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
            if self.space_track[side] == 7 and self.get_global_effective_ops(side, self.cards[card_name].info.ops) == 4:
                return True
            elif self.space_track[side] >= 5 and self.get_global_effective_ops(side, self.cards[card_name].info.ops) >= 3:
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

        if 'Missile_Envy' in self.basket[side] and 'Missile_Envy' in self.hand[side]:
            playable_cards = ['Missile_Envy']
        else:
            if 'Missile_Envy' in self.basket[side] and 'Missile_Envy' not in self.hand[side]:
                self.safe_remove_from_basket(side, 'Missile_Envy')
            playable_cards = (
                c for c in self.hand[side] if self.cards[c].is_playable)

        self.input_state = Input(
            side, InputType.SELECT_CARD,
            partial(self.card_callback, side),
            playable_cards,
            prompt='Select a card in hand to play.'
        )

    def card_callback(self, side: Side, card_name: str):
        self.input_state.reps -= 1
        if self.cards[card_name].info.card_type == 'Scoring':
            self.stage_list.append(
                partial(self.resolve_card_action, side,
                        card_name, CardAction.PLAY_EVENT.name))

        else:
            if card_name == 'The_China_Card' and side == Side.US and 'Formosan_Resolution' in self.basket[Side.US]:
                self.basket[Side.US].remove('Formosan_Resolution')
                if 'Formosan_Resolution' in self.removed_pile:
                    self.removed_pile.remove('Formosan_Resolution')
                    self.discard_pile.append('Formosan_Resolution')
            self.stage_list.append(
                partial(self.select_action, side, card_name))
        return True

    def action_callback(self, side: Side, card_name: str, action_name: str,
                        no_event: bool = False, un_intervention: bool = False,
                        influence_restriction=None,
                        flower_power_resolved=False):
        self.input_state.reps -= 1
        self.stage_list.append(
            partial(self.resolve_card_action, side,
                    card_name, action_name, no_event=no_event,
                    un_intervention=un_intervention,
                    influence_restriction=influence_restriction,
                    flower_power_resolved=flower_power_resolved)
        )
        return True

    def select_action(self, side: Side, card_name: str, is_event_resolved: bool = False,
                      un_intervention: bool = False, can_coup=True,
                      free_coup_realignment=False,
                      influence_restriction=None,
                      flower_power_resolved=False):
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
        if self.terminated:
            raise RuntimeError(
                f"select_action called after termination for card={card_name}, side={side}. "
                f"reason={self.termination_reason}, context={self.termination_context}"
            )

        can_influence = self.can_place_influence(side, card_name)
        if influence_restriction is not None:
            reps = self.get_global_effective_ops(
                side, self.cards[card_name].info.ops)
            allowed = set(influence_restriction)
            can_influence = any(
                name in allowed
                and self.map.can_place_influence(self, name, side, reps)
                for name in CountryInfo.ALL
            )

        bool_arr = [
            not un_intervention and not is_event_resolved and self.can_play_event(
                side, card_name),
            not un_intervention and not is_event_resolved and self.can_resolve_event_first(
                side, card_name),
            can_influence,
            self.can_realign_at_all(side),
            self.can_coup_at_all(side) and can_coup,
            not is_event_resolved and self.can_space(side, card_name),
            (not is_event_resolved
             and self.ars_by_turn[side][self.turn_track] == 8
             and self.ar_track == 8)
        ]

        self.input_state = Input(
            side, InputType.SELECT_CARD_ACTION,
            partial(self.action_callback, side, card_name,
                    no_event=is_event_resolved,
                    un_intervention=un_intervention,
                    influence_restriction=influence_restriction,
                    flower_power_resolved=flower_power_resolved),
            (CardAction(i).name for i, b in enumerate(bool_arr) if b),
            prompt=f'Select an action for {card_name}.',
            context={
                'source_card': card_name,
                'is_event_resolved': bool(is_event_resolved),
                'un_intervention': bool(un_intervention),
            }
        )

    def resolve_card_action(self, side: Side, card_name: str, action_name: str,
                            no_event: bool = False, un_intervention: bool = False,
                            influence_restriction=None,
                            flower_power_resolved=False):
        '''
        This function should lead to card_operation_realignment, card_operation_coup,
        or card_operation_influence, or a space race function.
        '''

        action = CardAction[action_name]
        card = self.cards[card_name]
        opp_event = (card.info.owner == side.opp)

        # We Will Bury You resolves on the US player's next action round:
        # unless UN Intervention is played as an Event, the USSR gains 3 VP.
        if side == Side.US and 'We_Will_Bury_You' in self.basket[Side.USSR]:
            if not (card_name == 'UN_Intervention' and action == CardAction.PLAY_EVENT):
                self.change_vp(3)
            self.basket[Side.USSR].remove('We_Will_Bury_You')
            if self.terminated:
                return

        if (card_name == 'UN_Intervention'
                and action == CardAction.PLAY_EVENT
                and 'U2_Incident' in self.basket[Side.USSR]):
            self.change_vp(1)
            self.safe_remove_from_basket(Side.USSR, 'U2_Incident')
            if self.terminated:
                return

        if action == CardAction.PLAY_EVENT:

            self.stage_list.append(
                partial(self.cards[card_name].dispose, self, side))
            self.stage_list.append(
                partial(self.trigger_event, side, card_name))

        elif action == CardAction.RESOLVE_EVENT_FIRST:

            if card_name == 'The_Iron_Lady' and side == Side.USSR:
                reps = self.get_global_effective_ops(side, card.info.ops)
                influence_restriction = tuple(
                    name for name in CountryInfo.ALL
                    if self.map.can_place_influence(
                        self, name, side, reps)
                )

            self.stage_list.append(
                partial(
                    self.select_action, side, card_name,
                    is_event_resolved=True,
                    influence_restriction=influence_restriction,
                    flower_power_resolved=True))
            self.stage_list.append(
                partial(self.trigger_event, side, card_name))

        elif action == CardAction.SPACE:

            self.stage_list.append(
                partial(self.cards[card_name].dispose, self, side))
            self.stage_list.append(partial(self.space, side, card_name))

        elif action in (CardAction.INFLUENCE, CardAction.REALIGNMENT,
                        CardAction.COUP):

            self.stage_list.append(
                partial(self.cards[card_name].dispose, self, side))
            if opp_event and not no_event and not un_intervention:
                self.stage_list.append(
                    partial(self.trigger_event, side, card_name))
            if action == CardAction.COUP:
                self.stage_list.append(partial(
                    self.card_operation_coup, side, card_name,
                    event_after_ops=(
                        opp_event and not no_event and not un_intervention)))
            else:
                operation = {
                    CardAction.INFLUENCE: self.card_operation_influence,
                    CardAction.REALIGNMENT: self.card_operation_realignment,
                }[action]
                if action == CardAction.INFLUENCE:
                    self.stage_list.append(partial(
                        operation, side, card_name,
                        restricted_list=influence_restriction))
                else:
                    self.stage_list.append(partial(operation, side, card_name))

        if (not flower_power_resolved
                and action not in (
                    CardAction.SPACE, CardAction.SKIP_OPTIONAL_AR)):
            self.apply_flower_power(side, card_name)
            if self.terminated:
                return

    def apply_flower_power(self, side: Side, card_name: str) -> None:
        if ('Flower_Power' in self.basket[Side.USSR]
                and side == Side.US
                and card_name in {
                    'Arab_Israeli_War', 'Indo_Pakistani_War',
                    'Korean_War', 'Brush_War', 'Iran_Iraq_War',
                }):
            self.change_vp(2)

    # Utility functions used in stages

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
        if 'NATO' not in self.basket[Side.US]:
            return []
        europe = [
            n for n in CountryInfo.REGION_ALL[MapRegion.EUROPE]
            if self.map[n].control == Side.US
        ]
        if 'De_Gaulle_Leads_France' in self.basket[Side.USSR]:
            if 'France' in europe:
                europe.remove('France')
        if 'Willy_Brandt' in self.basket[Side.USSR]:
            if 'West_Germany' in europe:
                europe.remove('West_Germany')
        return europe

    def trigger_event(self, side: Side, card_name: str):
        '''
        Runs the associated card event function with <side> argument.
        '''
        self.cards[card_name].use_event(self, side)

    '''
    Here we have different stages for card uses. These include the use of influence,
    operations points for coup or realignment, and also on the space race.
    '''

    def ops_influence_callback(self, side: Side, card_name: str,
                               allowed: frozenset, name: str) -> bool:
        c = self.map[name]

        # may no longer need this eventually if we ensure options are always correct
        if self.input_state.reps == 1 and c.control == side.opp:
            return False

        if c.control == side.opp:
            self.input_state.reps -= 2
        else:
            self.input_state.reps -= 1

        if card_name == 'The_China_Card':
            self.input_state.reps = self.cards['The_China_Card'].give_rep(
                self, name, self.input_state.reps)
            self.input_state.reps = self.cards['The_China_Card'].remove_rep(
                self, name, self.input_state.reps)
            self.cards['The_China_Card'].modify_selection(self, side)

        if side == Side.USSR and 'Vietnam_Revolts' in self.basket[Side.USSR]:
            self.input_state.reps = self.cards['Vietnam_Revolts'].give_rep(
                self, name, self.input_state.reps)
            self.input_state.reps = self.cards['Vietnam_Revolts'].remove_rep(
                self, name, self.input_state.reps)
            self.cards['Vietnam_Revolts'].modify_selection(
                self, card_name, side)

        c.increment_influence(side)

        if self.input_state.reps > 0:
            for candidate in allowed:
                if (candidate not in self.input_state.selection
                        and self.map.can_place_influence(
                            self, candidate, side, self.input_state.reps)):
                    self.input_state.add_option(candidate)
            # Newly reachable countries must still obey regional bonus-card
            # restrictions already applied to the original option set.
            if card_name == 'The_China_Card':
                self.cards['The_China_Card'].modify_selection(self, side)
            if side == Side.USSR and 'Vietnam_Revolts' in self.basket[Side.USSR]:
                self.cards['Vietnam_Revolts'].modify_selection(
                    self, card_name, side)

        if self.input_state.reps == 1:
            for n in self.input_state.selection:
                if self.map[n].control == side.opp:
                    self.input_state.remove_option(n)

        return True

    def card_operation_influence(self, side: Side, card_name: str,
                                 restricted_list=None):
        '''
        Stage when a player is given the opportunity to place influence. Provides a list
        of countries where influence can be placed into and waits for player input.

        Parameters
        ----------
        side : Side
            Side of the player who is placing influence.
        card_name : str
            String representation of the card used for influence operations.
        '''

        card = self.cards[card_name]
        reps = self.get_global_effective_ops(side, card.info.ops)
        allowed = (set(CountryInfo.ALL) if restricted_list is None
               else set(restricted_list))

        self.input_state = Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.ops_influence_callback, side, card_name,
                    frozenset(allowed)),
            (n for n in CountryInfo.ALL
                if n in allowed
                and self.map.can_place_influence(self, n, side, reps)),
            prompt=f'Place operations from {card_name} as influence.',
            reps=reps,
            reps_unit='operations',
            context={
                'source_card': card_name,
                'effective_ops': reps,
                'decision_kind': 'ops_influence',
                'restricted_countries': tuple(sorted(allowed)),
            },
        )

    def realign_dice_callback(self, name, side, num: tuple, free=False,
                              ignore_defcon=False):
        self.input_state.reps -= 1
        self.map.realignment(
            self, name, side, *num, free=free,
            ignore_defcon=ignore_defcon)
        return True

    def _region_ops_bonus_cards(self, side: Side, card_name: str):
        """Cards granting +1 ops for using all points in a region.

        The China Card always applies when realigning with it; Vietnam Revolts
        applies to USSR realignments while its turn effect is active. New
        region-ops bonus cards only need to be added here — the callbacks
        (realignment_callback etc.) dispatch through this list instead of
        special-casing card names.
        """
        if card_name == 'The_China_Card':
            yield self.cards['The_China_Card']
        if ('Vietnam_Revolts' in self.basket[Side.USSR]
                and side == Side.USSR):
            yield self.cards['Vietnam_Revolts']

    def realignment_callback(self, side: Side, name: str, card_name: str,
                             reps: int = None, free=False,
                             ignore_defcon=False) -> bool:

        if name == self.input_state.option_stop_early:
            self.input_state.reps = 0
            return True

        reps -= 1
        self.input_state.reps -= 1

        for bonus in self._region_ops_bonus_cards(side, card_name):
            reps = bonus.give_rep(self, name, reps)
            reps = bonus.remove_rep(self, name, reps)

        if reps:
            # The restricted region combines both cards' state: when both
            # bonuses are live at reps==2, the China Card's (wider) Asia
            # region wins; at reps==1 the live bonus restricts to its region.
            china = self.cards['The_China_Card']
            vietnam = self.cards['Vietnam_Revolts']
            china_active = card_name == 'The_China_Card'
            vietnam_active = ('Vietnam_Revolts' in self.basket[Side.USSR]
                              and side == Side.USSR)
            if (china_active and vietnam_active and reps == 2
                    and china.all_points_in_region
                    and vietnam.all_points_in_region):
                restricted = china._region
            elif (vietnam_active and reps == 1
                    and vietnam.all_points_in_region):
                restricted = vietnam._region
            elif china_active and reps == 1 and china.all_points_in_region:
                restricted = china._region
            else:
                restricted = None
            self.stage_list.append(
                partial(self.card_operation_realignment, side,
                        card_name=card_name, reps=reps,
                        restricted_list=restricted, free=free,
                        ignore_defcon=ignore_defcon))

        self.stage_list.append(partial(
            self.dice_stage,
            partial(
                self.realign_dice_callback, name, side, free=free,
                ignore_defcon=ignore_defcon),
            two_dice=True))

        return True

    def card_operation_realignment(self, side: Side, card_name: str, reps: int = None,
                                   restricted_list: Sequence[str] = None,
                                   free=False, ignore_defcon=False):
        '''
        Stage when a player is given the opportunity to use realignment. Provides a list
        of countries where realignment can take place and waits for player input.

        Parameters
        ----------
        side : Side
            Side of the player who is placing influence.
        card_name : str
            String representation of the card used for the realignment operations.
        '''
        card = self.cards[card_name]
        if not reps:
            reps = self.get_global_effective_ops(side, card.info.ops)
            can_stop_now = ''
        else:
            can_stop_now = 'Stop realignments.'

        if restricted_list is None:
            restricted_list = CountryInfo.ALL

        self.input_state = Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.realignment_callback, side,
                    card_name=card_name, reps=reps, free=free,
                    ignore_defcon=ignore_defcon),
            (n for n in CountryInfo.ALL if self.map.can_realignment(
                self, n, side, free=free,
                ignore_defcon=ignore_defcon) and n in restricted_list),
            prompt=f'Select a country for realignment using operations from {card_name}. {reps} realignments remaining.',
            option_stop_early=can_stop_now,
            context={
                'source_card': card_name,
                'decision_kind': 'realignment',
                'remaining_realignments': reps,
                'restricted_countries': tuple(sorted(restricted_list)),
                'free': bool(free),
                'ignore_defcon': bool(ignore_defcon),
            },
        )

    def dice_stage(self, fn: Callable[[str], bool] = None, two_dice=False, reroll_ties=False):
        if not two_dice:
            options = (str(i) for i in range(1, 7))
            prompt = '1d6 roll'
        elif not reroll_ties:
            options = ((i, j) for i in range(1, 7) for j in range(1, 7))
            prompt = '2d6 roll (USSR roll, US roll)'
        else:
            options = ((i + 2, j) for i in range(1, 7)
                       for j in range(1, 7) if i + 2 != j)
            prompt = '2d6 roll (Sponsor roll, Participant roll), no ties'

        self.input_state = Input(
            Side.NEUTRAL, InputType.ROLL_DICE,
            fn,
            options,
            prompt=prompt,
        )

    def coup_dice_callback(self, name, side, ops, free, num: str, che=False,
                           ignore_defcon=False):
        self.input_state.reps -= 1

        if che:
            before_us_inf = self.map[name].influence[Side.US]
            ca_sa_af = chain(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA],
                             CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA],
                             CountryInfo.REGION_ALL[MapRegion.AFRICA])

        self.map.coup(
            self, name, side, ops, int(num), free=free,
            ignore_defcon=ignore_defcon)

        if self.terminated:
            return True

        if che and self.map[name].influence[Side.US] < before_us_inf:
            print('You are allowed a second coup from Che.')
            self.card_operation_coup(Side.USSR, 'Che', restricted_list=[
                n for n in ca_sa_af
                if n != name and not self.map[n].info.battleground
            ], che=False)

        return True

    def coup_callback(self, side: Side, effective_ops: int, card_name: str,
                      name: str, free=False, che=False,
                      ignore_defcon=False) -> bool:
        self.input_state.reps -= 1

        local_ops_modifier = 0
        if card_name == 'The_China_Card' and name in self.cards['The_China_Card']._region:
            local_ops_modifier += 1
        if 'Vietnam_Revolts' in self.basket[Side.USSR] and side == Side.USSR and name in self.cards['Vietnam_Revolts']._region:
            local_ops_modifier += 1

        self.stage_list.append(partial(
            self.dice_stage,
            partial(self.coup_dice_callback, name, side,
                    effective_ops + local_ops_modifier, free, che=che,
                    ignore_defcon=ignore_defcon)))

        return True

    def card_operation_coup(self, side: Side, card_name: str,
                            restricted_list: Sequence[str] = None,
                            free=False, che=False, event_after_ops=False,
                            ignore_defcon=False):
        '''
        Stage when a player is given the opportunity to coup. Provides a list
        of countries which can be couped and waits for player input.

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
            self.cards['Cuban_Missile_Crisis'].cuban_missile_remove(self, side)

        # NOTE: game_instance is passed via partial (not a closure) so
        # deepcopy-based lookahead/search clones rebind to the clone.
        self.stage_list.append(partial(
            _choose_coup_country, self, side, effective_ops, card_name,
            restricted_list, free, che, event_after_ops, ignore_defcon))

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
            partial(self.space_dice_callback, side)))
        return True

    def event_place_influence(self, side: Side, country_function,
                              callback_side: Side, options, prompt: str,
                              reps: int = 1, max_per_option: int = -1,
                              option_stop_early: str = '',
                              reps_unit: str = 'influence',
                              context=None) -> None:
        '''Prompt ``side`` to place/remove influence via a card event.

        ``callback_side`` is the side whose influence is modified — usually
        equal to ``side``, but some events (e.g. Socialist Governments) prompt
        one side to remove the other side's influence. Thin wrapper over the
        standard SELECT_COUNTRY + event_influence_callback Input (see
        event_influence_callback for the country_function shapes).'''
        self.input_state = Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.event_influence_callback,
                    country_function, callback_side),
            options, prompt=prompt, reps=reps, reps_unit=reps_unit,
            max_per_option=max_per_option,
            option_stop_early=option_stop_early,
            context=context,
        )

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
        if name == self.input_state.option_stop_early:
            self.input_state.reps = 0
            return True

        self.input_state.reps -= 1
        status = country_function(self.map[name], side)
        # Some callbacks can temporarily drive influence to zero; remove exhausted options.
        if not status:
            return False
        else:
            if not self.map[name].influence[side]:
                self.input_state.remove_option(name)
            return True

    def choose_option(self, side: Side, option_function_mapping: dict,
                      prompt: str) -> None:
        '''Prompt ``side`` to pick one of several options (SELECT_MULTIPLE).'''
        self.input_state = Input(
            side, InputType.SELECT_MULTIPLE,
            partial(self.select_multiple_callback, option_function_mapping),
            option_function_mapping.keys(),
            prompt=prompt,
        )

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
        # War events always satisfy military operations regardless of success.
        self.change_milops(side, win_milops)
        outcome = 'Success' if int(num) - modifier >= min_roll else 'Failure'
        if outcome == 'Success':
            self.change_vp(win_vp * side.vp_mult)
            if self.terminated:
                return True

            influence = self.map[name].influence[side.opp]
            self.map[name].remove_influence(side.opp)
            self.map[name].increment_influence(side, influence)
        print(f'{outcome} with roll of {num}.')

        return True

    def war(self, country_name: str, side: Side, country_itself: bool = False,
            lower: int = 4, win_vp: int = 2, win_milops: int = 2):
        '''
        Generic war stage.

        War with country selection (e.g. Brush) should call war_country_callback.
        War with specified country only (e.g. Korean) should call this directly.
        '''
        country = self.map[country_name]

        modifier = sum(self.map[adjacent_country].control == side.opp
                       for adjacent_country in country.info.adjacent_countries)

        if country_itself and country.control == side.opp:  # For Arab-Israeli War
            modifier += 1

        self.stage_list.append(partial(
            self.dice_stage,
            partial(self.war_dice_callback, country_name, side,
                    modifier, lower, win_vp, win_milops)))

    def war_country_callback(self, side: Side, country_name: str, country_itself: bool = False,
                             lower: int = 4, win_vp: int = 2, win_milops: int = 2):
        self.input_state.reps -= 1
        self.war(country_name, side, country_itself=country_itself,
                 lower=lower, win_vp=win_vp, win_milops=win_milops)
        return True

    def qbt_dice_callback(self, side: Side, trap_name: str, num: str):
        self.input_state.reps -= 1
        if int(num) <= 4:
            self.basket[side].remove(trap_name)
        return True

    def qbt_discard_callback(self, side: Side, trap_name: str, card_name: str):
        self.input_state.reps -= 1
        if card_name not in self.hand[side]:
            raise RuntimeError(
                f"{trap_name} discard selected card not in hand: {card_name}. "
                f"hand={self.hand[side]} basket={self.basket[side]}"
            )
        self.hand[side].remove(card_name)
        if card_name == 'Missile_Envy':
            self.safe_remove_from_basket(side, 'Missile_Envy')
            missile_envy = self.cards['Missile_Envy']
            missile_envy.event_occurred = False
            missile_envy.exchange = False
        self.discard_pile.append(card_name)
        self.stage_list.append(partial(self.dice_stage, partial(
            self.qbt_dice_callback, side, trap_name)))
        return True

    def qbt_play_scoring_callback(self, side: Side, card_name: str):
        self.input_state.reps -= 1
        self.stage_list.append(
            partial(self.resolve_card_action, side, card_name, CardAction.PLAY_EVENT.name)
        )
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
        '''

        scoring_cards = [n for n in self.hand[side]
                         if self.cards[n].info.card_type == 'Scoring']

        if 'Missile_Envy' in self.basket[side] and 'Missile_Envy' not in self.hand[side]:
            self.safe_remove_from_basket(side, 'Missile_Envy')

        suitable_cards = []
        if 'Missile_Envy' in self.basket[side] and 'Missile_Envy' in self.hand[side]:
            me_ops = self.get_global_effective_ops(
                side, self.cards['Missile_Envy'].info.ops)
            if me_ops >= 2:
                suitable_cards = ['Missile_Envy']
            else:
                suitable_cards = [
                    n for n in self.hand[side]
                    if n not in ('The_China_Card', 'Missile_Envy')
                    and self.get_global_effective_ops(side, self.cards[n].info.ops) >= 2
                ]
        else:
            suitable_cards = [
                n for n in self.hand[side]
                if n != 'The_China_Card'
                and self.get_global_effective_ops(side, self.cards[n].info.ops) >= 2
            ]

        # If we have as many scoring cards as action rounds, then we must play
        # a scoring card. Q/BT stays in basket.
        if len(scoring_cards) == self.ars_remaining(side):
            self.input_state = Input(
                side, InputType.SELECT_CARD,
                partial(self.qbt_play_scoring_callback, side),
                scoring_cards,
                prompt='You must play a scoring card.'
            )
            return

        # Otherwise, if there are discardable cards, you have to discard from these.
        if suitable_cards:
            self.input_state = Input(
                side, InputType.SELECT_CARD,
                partial(self.qbt_discard_callback, side, trap_name),
                suitable_cards,
                prompt='You must discard a card to be released.'
            )
        # If there are no valid QBT discards but scoring cards remain, scoring must be played.
        elif scoring_cards:
            self.input_state = Input(
                side, InputType.SELECT_CARD,
                partial(self.qbt_play_scoring_callback, side),
                scoring_cards,
                prompt='You must play a scoring card.'
            )
        # If you don't have suitable discards or scoring cards, then AR is skipped.
        else:
            print('AR skipped due to lack of suitable cards.')

    def shuffle_callback(self, card_name):
        self.input_state.reps -= 1
        self.draw_pile.append(card_name)
        return True

    def shuffle_draw_pile_stage(self):
        self.shuffle_count += 1
        shuffler_pile = self.draw_pile
        for card_name in shuffler_pile:
            self.card_last_shuffled[card_name] = self.shuffle_count
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

    def _expand_era(self, era_list):
        '''Move one era's cards into the draw pile and schedule a shuffle.'''
        self.draw_pile.extend(era_list)
        era_list.clear()
        self.shuffle_draw_pile_stage()

    def _reshuffle_and_continue(self, first_side, trigger_headline: bool):
        '''Reset the draw pile from the discard pile and re-deal after the
        shuffle stage completes.'''
        self.draw_pile = self.discard_pile
        self.discard_pile = []
        self.stage_list.append(
            partial(self.deal, first_side=first_side,
                    trigger_headline=trigger_headline))
        self.shuffle_draw_pile_stage()

    def expand_deck(self):

        if self.turn_track == 1:
            # All Early War cards (including The China Card) go to the draw pile.
            self.draw_pile.extend(self.cards.early_war)
            self.cards.early_war.clear()
            # USSR starts with The China Card — must be drawn before the
            # shuffle stage swaps draw_pile out for the shuffler pile.
            self.hand[Side.USSR].append(self.draw_pile.pop(
                self.draw_pile.index('The_China_Card')))
            self.shuffle_draw_pile_stage()
        elif self.turn_track == 4:
            self._expand_era(self.cards.mid_war)
        elif self.turn_track == 8:
            self._expand_era(self.cards.late_war)

    def deal(self, first_side=Side.USSR, trigger_headline: bool = False):

        if first_side == Side.NEUTRAL:
            # Our_Man_In_Tehran path — draw 5 cards into the neutral hand.
            for _ in range(5):
                if not self.draw_pile:
                    if not self.discard_pile:
                        return
                    self._reshuffle_and_continue(
                        Side.NEUTRAL, trigger_headline)
                    return
                self.hand[Side.NEUTRAL].append(self.draw_pile.pop())
            return

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

            if not self.draw_pile:
                # if draw pile exhausted, shuffle the discard pile and put it as the new draw pile
                if not self.discard_pile:
                    # No cards left to draw while hands are still under target.
                    # End explicitly so callers never observe an unknown termination.
                    self.terminate(
                        reason='deck_exhausted',
                        context={
                            'turn_track': self.turn_track,
                            'ar_track': self.ar_track,
                            'first_side': first_side.toStr() if first_side in (Side.USSR, Side.US) else str(first_side),
                            'handsize_target': handsize_target,
                            'hand_sizes': [len(self.hand[Side.USSR]), len(self.hand[Side.US])],
                        },
                    )
                    return
                self._reshuffle_and_continue(next_side, trigger_headline)
                return

            self.hand[next_side].append(self.draw_pile.pop())
            self.unknown_hand_draws[next_side] += 1
            next_side = next_side.opp

        if trigger_headline:
            self.process_headline()

    # need to make sure next_turn is only called after all extra rounds
    def end_of_turn(self, resume_after_space_discard=False):

        if not resume_after_space_discard:
            print('-------------------- End of turn --------------------')
        # -2. Check for held scoring card (originally #2. but moved up to prevent held scoring cards)

        def check_for_scoring_cards(self):
            scoring_list = ['Asia_Scoring', 'Europe_Scoring', 'Middle_East_Scoring',
                            'Central_America_Scoring', 'Southeast_Asia_Scoring',
                            'Africa_Scoring', 'South_America_Scoring']
            scoring_cards = [self.cards[y] for y in scoring_list]
            if any(True for x in scoring_cards if x in self.hand[Side.US]):
                held = [c for c in scoring_list if c in self.hand[Side.US]]
                self.terminate(Side.USSR, reason='held_scoring_card', context={'loser': 'US', 'held_cards': held})
            elif any(True for x in scoring_cards if x in self.hand[Side.USSR]):
                held = [c for c in scoring_list if c in self.hand[Side.USSR]]
                self.terminate(Side.US, reason='held_scoring_card', context={'loser': 'USSR', 'held_cards': held})

        # -1. Check if any player may discard held cards, also resets space turns
        def space_discard(self):
            # Will hardcode to prevent discarding The China Card via Eagle/Bear has landed
            for s in [Side.USSR, Side.US]:
                if self.space_track[s] >= 6 and self.space_track[s.opp] < 6:
                    eligible_cards = [
                        n for n in self.hand[s]
                        if n != 'The_China_Card'
                        and self.cards[n].info.card_type != 'Scoring'
                    ]
                    if not eligible_cards:
                        continue
                    self.input_state = Input(
                        s, InputType.SELECT_CARD,
                        partial(self.may_discard_callback, s),
                        eligible_cards,
                        prompt='You may discard a held card via Eagle/Bear has landed.',
                        option_stop_early='Do not discard.',
                        context={'hand_exit': 'space_discard'},
                    )
                    return True
            return False

        # 0. Clear all events that only last until the end of turn.
        def clear_baskets(self):
            for function in self.end_turn_stage_list:
                try:
                    function()
                except ValueError:
                    pass
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

        # 5. Final scoring (after turn 10)
        def final_scoring(self):
            # advance_turn_marker already ran, so turn_track is 11
            # when turn 10 just ended.
            if self.turn_track != 11:
                return  # turns 1-9: nothing to do
            # Shuttle Diplomacy explicitly "Does not count for Final Scoring".
            # If neither Asia nor Middle East scoring was played during the
            # game, the card is still in limbo. Clear it now.
            self.limbo.clear()
            self.final_scoring_active = True
            try:
                for region in MapRegion.main_regions():
                    self.score(region)
                for s in [Side.USSR, Side.US]:
                    if 'The_China_Card' in self.hand[s]:
                        self.change_vp(s.vp_mult)
            finally:
                self.final_scoring_active = False
            print('Final scoring complete.')
            self.terminate(reason='final_scoring_complete', context={'turn_track': self.turn_track})

        if not resume_after_space_discard:
            clear_baskets(self)
            check_milops(self)
            if self.terminated:
                return
            if space_discard(self):
                self.spaced_turns = [0, 0]
                self.stage_list.append(partial(
                    self.end_of_turn, resume_after_space_discard=True))
                return
            self.spaced_turns = [0, 0]
        check_for_scoring_cards(self)
        if self.terminated:
            return
        flip_china_card(self)
        advance_turn_marker(self)
        final_scoring(self)
        # Stop only when terminate() has been called.
        if self.terminated:
            return
        self.change_defcon(1)
        self.expand_deck()
        # expand_deck may schedule a neutral shuffle input and temporarily clear
        # draw_pile. Do not deal until that shuffle stage completes.
        if self.input_state is not None:
            self.stage_list.append(partial(self.deal, trigger_headline=True))
            return
        self.deal(trigger_headline=True)

    def score_breakdown(self, region: MapRegion):
        """Return the current public scoring result without mutating the game."""
        if region == MapRegion.SOUTHEAST_ASIA:
            vps = [0, 0, 0]
            country_count = [0, 0, 0]
            for name in CountryInfo.REGION_ALL[region]:
                control = self.map[name].control
                country_count[control] += 1
                vps[control] += 1
            thailand_control = self.map['Thailand'].control
            vps[thailand_control] += 1
            return {
                'region': region.name,
                'sides': {
                    side.name: {
                        'vp': vps[side],
                        'status': 'points' if vps[side] else 'none',
                        'countries': country_count[side],
                        'battlegrounds': 0,
                        'adjacency': 0,
                    }
                    for side in (Side.USSR, Side.US)
                },
                'swing': vps[Side.USSR] - vps[Side.US],
                'modifiers': [],
            }

        (presence_vps, domination_vps,
         control_vps) = Game.Default.SCORING[region]
        formosan_applies = (
            region == MapRegion.ASIA
            and 'Formosan_Resolution' in self.basket[Side.US]
            and self.map['Taiwan'].control == Side.US
        )
        shuttle_applies = (
            'Shuttle_Diplomacy' in self.limbo
            and region in (MapRegion.ASIA, MapRegion.MIDDLE_EAST)
        )

        bg_count = [0, 0, 0]
        country_count = [0, 0, 0]
        vps = [0, 0, 0]
        adjacency_vps = [0, 0, 0]
        statuses = ['none', 'none', 'none']

        for name in CountryInfo.REGION_ALL[region]:
            country = self.map[name]
            effective_battleground = country.info.battleground or (
                formosan_applies and name == 'Taiwan'
            )
            if effective_battleground:
                bg_count[country.control] += 1
            country_count[country.control] += 1
            if country.control.opp.name in country.info.adjacent_countries:
                vps[country.control] += 1
                adjacency_vps[country.control] += 1

            actual_bg_count = list(bg_count)
            total_battlegrounds = sum(actual_bg_count)
        if shuttle_applies:
            bg_count[Side.USSR] = max(0, bg_count[Side.USSR] - 1)

        for side in (Side.USSR, Side.US):
            vps[side] += bg_count[side]
            if country_count[side] > country_count[side.opp]:
                if (total_battlegrounds > 0
                        and bg_count[side] == total_battlegrounds):
                    vps[side] += control_vps
                    statuses[side] = 'control'
                elif bg_count[side] > bg_count[side.opp] \
                        and country_count[side] > actual_bg_count[side]:
                    vps[side] += domination_vps
                    statuses[side] = 'domination'
                elif country_count[side] > 0:
                    vps[side] += presence_vps
                    statuses[side] = 'presence'
            elif country_count[side] > 0:
                vps[side] += presence_vps
                statuses[side] = 'presence'

        modifiers = []
        if formosan_applies:
            modifiers.append('formosan_resolution')
        if shuttle_applies:
            modifiers.append('shuttle_diplomacy')
        return {
            'region': region.name,
            'sides': {
                side.name: {
                    'vp': vps[side],
                    'status': statuses[side],
                    'countries': country_count[side],
                    'battlegrounds': bg_count[side],
                    'adjacency': adjacency_vps[side],
                }
                for side in (Side.USSR, Side.US)
            },
            'swing': vps[Side.USSR] - vps[Side.US],
            'modifiers': modifiers,
        }

    def score(self, region: MapRegion, check_only=False):
        breakdown = self.score_breakdown(region)
        swing = breakdown['swing']
        if not check_only:
            region_name = ('Southeast Asia'
                           if region == MapRegion.SOUTHEAST_ASIA else region.name)
            print(f'{region_name} scores for {swing} VP')
            self.change_vp(swing)
        else:
            print(
                f'US:USSR = {breakdown["sides"]["US"]["vp"]}:'
                f'{breakdown["sides"]["USSR"]["vp"]}')
        return breakdown
