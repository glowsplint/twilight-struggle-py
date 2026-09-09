import math

from typing import Callable, Optional
from functools import partial
from itertools import chain

from twilight_input_output import Input
from twilight_map import MapRegion, CountryInfo, Country
from twilight_enums import Side, MapRegion, InputType, CardAction


class GameCards:

    def __init__(self):

        self.ALL = dict()
        self.early_war = []
        self.mid_war = []
        self.late_war = []

        for card_name, CardClass in Card.ALL.items():

            self.ALL[card_name] = CardClass()

            if CardClass.stage == 'Early War':
                self.early_war.append(card_name)
            if CardClass.stage == 'Mid War':
                self.mid_war.append(card_name)
            if CardClass.stage == 'Late War':
                self.late_war.append(card_name)

    def __getitem__(self, item):
        return self.ALL[item]


class Card:

    ALL = dict()
    INDEX = dict()

    name = ''
    card_index = 0
    card_type = ''
    stage = ''
    optional = False
    ops = 0
    owner = Side.NEUTRAL
    can_headline = True
    scoring_region = ''
    event_text = ''
    may_be_held = True
    event_unique = False

    @classmethod
    def __init_subclass__(cls):
        # Abstract base classes (no name) must not register as playable cards.
        if not cls.name:
            return
        Card.ALL[cls.name] = cls
        Card.INDEX[cls.card_index] = cls

    def __init__(self):
        self.is_playable = True
        self.event_occurred = False

    @property
    def info(self):
        return self

    def __repr__(self):
        if self.card_type == 'Scoring':
            return self.name
        else:
            return f'{self.name} - {self.ops}'

    def __eq__(self, other: str):
        return self.name == other

    def __hash__(self):
        # __eq__ is name-based, so __hash__ must match it — otherwise Card
        # instances are unhashable (defining __eq__ alone sets __hash__=None).
        return hash(self.name)

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True

    def can_event(self, game_instance, side: Side):
        return True if self.owner != side.opp else False

    def dispose(self, game, side):
        if self.name in game.hand[side]:
            game.hand[side].remove(self.name)
        if self.event_occurred and self.event_unique:
            game.removed_pile.append(self.name)
        else:
            game.discard_pile.append(self.name)
            if self.card_type != 'Scoring':
                self.event_occurred = False

# --
# -- EARLY WAR
# --


class Asia_Scoring(Card):
    name = 'Asia_Scoring'
    card_index = 1
    card_type = 'Scoring'
    stage = 'Early War'
    scoring_region = MapRegion.ASIA
    event_text = 'Both sides score: Presence: 3, Domination: 7, Control: 9. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
    may_be_held = False

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.score(MapRegion.ASIA)
        if 'Shuttle_Diplomacy' in game_instance.limbo:
            game_instance.discard_pile.append('Shuttle_Diplomacy')
            game_instance.limbo.clear()
            game_instance.safe_remove_from_basket(Side.US, 'Shuttle_Diplomacy')


class Europe_Scoring(Card):
    name = 'Europe_Scoring'
    card_index = 2
    card_type = 'Scoring'
    stage = 'Early War'
    scoring_region = MapRegion.EUROPE
    event_text = 'Both sides score: Presence: 3, Domination: 7, Control: VICTORY. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
    may_be_held = False

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.score(MapRegion.EUROPE)


class Middle_East_Scoring(Card):
    name = 'Middle_East_Scoring'
    card_index = 3
    card_type = 'Scoring'
    stage = 'Early War'
    scoring_region = MapRegion.MIDDLE_EAST
    event_text = 'Both sides score: Presence: 3, Domination: 5, Control: 7. +1 per controlled Battleground Country in Region'
    may_be_held = False

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.score(MapRegion.MIDDLE_EAST)
        if 'Shuttle_Diplomacy' in game_instance.limbo:
            game_instance.discard_pile.append('Shuttle_Diplomacy')
            game_instance.limbo.clear()
            game_instance.safe_remove_from_basket(Side.US, 'Shuttle_Diplomacy')


class Duck_and_Cover(Card):
    name = 'Duck_and_Cover'
    card_index = 4
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.US
    event_text = 'Degrade DEFCON one level. Then US player earns VPs equal to 5 minus current DEFCON level.'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.change_defcon(-1)
        if game_instance.terminated:
            return
        game_instance.change_vp(-(5 - game_instance.defcon_track))


class RegionOpsBonusCard(Card):
    """Card granting +1 Operations value when all points are used in one region
    (The China Card: Asia; Vietnam Revolts: Southeast Asia).

    The per-card ``_region`` class attribute drives the shared
    give_rep/remove_rep bookkeeping; subclasses implement their own
    ``modify_selection`` (the two cards filter options differently).
    """

    def __init__(self):
        super().__init__()
        self.all_points_in_region = True
        self.extra_point_given = False
        self.extra_point_taken = False

    def reset(self):
        self.all_points_in_region = True
        self.extra_point_given = False
        self.extra_point_taken = False

    def give_rep(self, game_instance, name, repetitions):
        '''
        Awards additional rep if:
        1. All points in region
        2. Additional rep has not already been given.
        '''
        if name not in self._region:
            self.all_points_in_region = False
        if self.all_points_in_region and not self.extra_point_given:
            repetitions += 1
            game_instance.input_state.change_max_per_option(1)
            self.extra_point_given = True
        return repetitions

    def remove_rep(self, game_instance, name, repetitions):
        '''
        Removes additional rep if:
        1. It was given
        2. Name not in _region
        3. Additional rep has not already been taken.
        '''
        if self.extra_point_given:
            if name not in self._region:
                if not self.extra_point_taken:
                    repetitions -= 1
                    game_instance.input_state.change_max_per_option(-1)
                    self.extra_point_taken = True
        return repetitions


class Five_Year_Plan(Card):
    name = 'Five_Year_Plan'
    card_index = 5
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.US
    event_text = 'USSR player must randomly discard one card. If the card is a US associated Event, the Event occurs immediately. If the card is a USSR associated Event or and Event applicable to both players, then the card must be discarded without triggering the Event.'

    def callback(self, game_instance, card_name: str):
        game_instance.input_state.reps -= 1
        print(f'{card_name} was selected by Five_Year_Plan.')
        if game_instance.cards[card_name].info.owner == Side.US:
            # must append backwards!
            game_instance.stage_list.append(
                partial(game_instance.cards[card_name].dispose, game_instance, Side.USSR))
            game_instance.stage_list.append(
                partial(game_instance.trigger_event, Side.USSR, card_name))
        else:
            game_instance.stage_list.append(
                partial(game_instance.cards[card_name].dispose, game_instance, Side.USSR))
        return True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        eligible_cards = [
            card_name for card_name in game_instance.hand[Side.USSR]
            if card_name not in ('Five_Year_Plan', 'The_China_Card')
        ]
        if not eligible_cards:
            return

        game_instance.input_state = Input(
            Side.NEUTRAL, InputType.SELECT_CARD,
            partial(self.callback, game_instance),
            eligible_cards,
            prompt='Five Year Plan: USSR randomly discards a card.',
            reps=1,
            context={
                'source_card': self.name,
                'hand_exit': 'five_year_target',
            },
        )


class The_China_Card(RegionOpsBonusCard):
    name = 'The_China_Card'
    card_index = 6
    card_type = 'Event'
    stage = 'Early War'
    ops = 4
    owner = Side.NEUTRAL
    can_headline = False
    event_text = 'Begins the game with the USSR player. +1 Operations value when all points are used in Asia. Pass to opponent after play. +1 VP for the player holding this card at the end of Turn 10. Cancels effect of \'Formosan Resolution\' if this card is played by the US player.'
    _region = list(CountryInfo.REGION_ALL[MapRegion.ASIA])

    def can_event(self, game_instance, side):
        return False

    def move_china_card(self, game_instance, side: Side, made_playable=False):
        '''
        Moves and flips the China Card after it has been used.
        Side refers to the player that uses the China card, or whoever the card should move from.
        '''
        if 'The_China_Card' in game_instance.hand[side]:
            game_instance.hand[side].remove('The_China_Card')
        game_instance.hand[side.opp].append('The_China_Card')
        self.is_playable = made_playable
        self.reset()

    def dispose(self, game, side):
        self.move_china_card(game, side)

    def modify_selection(self, game_instance, side):
        if game_instance.input_state.reps == 2 and self.all_points_in_region:
            for n in game_instance.input_state.selection:
                if game_instance.map[n].info.name not in The_China_Card._region and game_instance.map[n].control == side.opp:
                    game_instance.input_state.remove_option(n)

        if game_instance.input_state.reps == 1 and self.all_points_in_region:
            for n in game_instance.input_state.selection:
                if game_instance.map[n].info.name not in The_China_Card._region:
                    game_instance.input_state.remove_option(n)


class Socialist_Governments(Card):
    name = 'Socialist_Governments'
    card_index = 7
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.USSR
    event_text = 'Unplayable as an event if \'The Iron Lady\' is in effect. Remove US Influence in Western Europe by a total of 3 Influence points, removing no more than 2 per country.'

    def can_event(self, game_instance, side):
        return 'The_Iron_Lady' not in game_instance.basket[Side.US]

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, Side.USSR):
            self.event_occurred = True
            game_instance.event_place_influence(
                Side.USSR, Country.decrement_influence, Side.US,
                (n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]
                    if game_instance.map[n].has_us_influence),
                prompt='Socialist Governments: Remove a total of 3 US Influence from any countries in Western Europe (limit 2 per country)',
                reps=3,
                max_per_option=2,
            )


class Fidel(Card):
    name = 'Fidel'
    card_index = 8
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.USSR
    event_text = 'Remove all US Influence in Cuba. USSR gains sufficient Influence in Cuba for Control.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        cuba = game_instance.map['Cuba']
        cuba.set_influence(max(3, cuba.influence[Side.USSR]), 0)


class Vietnam_Revolts(RegionOpsBonusCard):
    name = 'Vietnam_Revolts'
    card_index = 9
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.USSR
    event_text = 'Add 2 USSR Influence in Vietnam. For the remainder of the turn, the Soviet player may add 1 Operations point to any card that uses all points in Southeast Asia.'
    event_unique = True
    _region = list(CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA])

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.map.change_influence('Vietnam', Side.USSR, 2)
        game_instance.add_turn_effect(Side.USSR, 'Vietnam_Revolts')

    def modify_selection(self, game_instance, card_name, side):
        '''
        Modifies the available options.

        Handles the special case where 4 points have been placed in SEA with the China Card. We want to remove
        all options not in ASIA, and also remove the options outside SEA if opponent owned. 
        '''
        if card_name == 'The_China_Card' and game_instance.input_state.reps == 3 and self.all_points_in_region:
            for n in game_instance.input_state.selection:
                if game_instance.map[n].info.name not in The_China_Card._region and game_instance.map[n].control == side.opp:
                    game_instance.input_state.remove_option(n)

        if card_name == 'The_China_Card' and game_instance.input_state.reps == 2 and self.all_points_in_region:
            for n in game_instance.input_state.selection:
                if game_instance.map[n].info.name not in The_China_Card._region or (game_instance.map[n].info.name not in Vietnam_Revolts._region and game_instance.map[n].control == side.opp):
                    game_instance.input_state.remove_option(n)

        elif game_instance.input_state.reps == 2 and self.all_points_in_region:
            for n in game_instance.input_state.selection:
                if game_instance.map[n].info.name not in Vietnam_Revolts._region or game_instance.map[n].control == side.opp:
                    game_instance.input_state.remove_option(n)

        elif game_instance.input_state.reps == 1 and self.all_points_in_region:
            for n in game_instance.input_state.selection:
                if game_instance.map[n].info.name not in Vietnam_Revolts._region:
                    game_instance.input_state.remove_option(n)


class Blockade(Card):
    name = 'Blockade'
    card_index = 10
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.USSR
    event_text = 'Unless US Player immediately discards a \'3\' or more value Operations card, eliminate all US Influence in West Germany.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        eligible_discards = [
            n for n in game_instance.hand[Side.US]
            if n not in ('The_China_Card', self.name)
            and game_instance.get_global_effective_ops(
                Side.US, game_instance.cards[n].info.ops
            ) >= 3
        ]

        if not eligible_discards:
            game_instance.map['West_Germany'].remove_influence(Side.US)
            return

        game_instance.input_state = Input(
            Side.US, InputType.SELECT_CARD,
            partial(game_instance.may_discard_callback, Side.US,
                    did_not_discard_fn=partial(game_instance.map['West_Germany'].remove_influence, Side.US)),
            eligible_discards,
            prompt='You may discard a card. If you choose not to discard a card, US loses all influence in West Germany.',
            option_stop_early='Do not discard.',
            context={
                'source_card': self.name,
                'hand_exit': 'blockade_target',
            },
        )


class WarCard(Card):
    """War event card (Korean/Arab-Israeli/Indo-Pakistani/Brush/Iran-Iraq).

    Fixed-target wars set ``war_target``; player-choice wars set
    ``war_country_options`` (an iterable, or a callable returning one — e.g.
    Brush War's stability-filtered list) plus ``war_prompt``. The remaining
    ``war_*`` fields map onto war()/war_country_callback parameters.
    """

    war_target = None
    war_country_options = None
    war_prompt = ''
    war_country_itself = False
    war_lower = 4
    war_win_vp = 2
    war_win_milops = 2

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        war_side = self.owner if self.owner in (Side.USSR, Side.US) else side
        if self.war_target is not None:
            game_instance.war(
                self.war_target, war_side, country_itself=self.war_country_itself,
                lower=self.war_lower, win_vp=self.war_win_vp,
                win_milops=self.war_win_milops)
            return
        options = self.war_country_options(game_instance) \
            if callable(self.war_country_options) else self.war_country_options
        game_instance.input_state = Input(
            war_side, InputType.SELECT_COUNTRY,
            partial(game_instance.war_country_callback, war_side,
                    lower=self.war_lower, win_vp=self.war_win_vp,
                    win_milops=self.war_win_milops),
            options,
            prompt=self.war_prompt,
            context={
                'source_card': self.name,
                'decision_kind': 'war_target',
                'beneficiary_side': war_side.name,
            },
        )


class Korean_War(WarCard):
    name = 'Korean_War'
    card_index = 11
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.USSR
    event_text = 'North Korea invades South Korea. Roll one die and subtract 1 for every US Controlled country adjacent to South Korea. USSR Victory on modified die roll 4-6. USSR add 2 to Military Ops Track. Effects of Victory: USSR gains 2 VP and replaces all US Influence in South Korea with USSR Influence.'
    event_unique = True
    war_target = 'South_Korea'


class Romanian_Abdication(Card):
    name = 'Romanian_Abdication'
    card_index = 12
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.USSR
    event_text = 'Remove all US Influence in Romania. USSR gains sufficient Influence in Romania for Control.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        romania = game_instance.map['Romania']
        romania.set_influence(max(3, romania.influence[Side.USSR]), 0)


class Arab_Israeli_War(WarCard):
    name = 'Arab_Israeli_War'
    card_index = 13
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.USSR
    event_text = 'A Pan-Arab Coalition invades Israel. Roll one die and subtract 1 for US Control of Israel and for US-controlled country adjacent to Israel. USSR Victory on modified die roll 4-6. USSR adds 2 to Military Ops Track. Effects of Victory: USSR gains 2 VP and replaces all US Influence in Israel with USSR Influence.'
    war_target = 'Israel'
    war_country_itself = True

    def can_event(self, game_instance, side):
        return 'Camp_David_Accords' not in game_instance.basket[Side.US]

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, Side.USSR):
            super().use_event(game_instance, side)


class COMECON(Card):
    name = 'COMECON'
    card_index = 14
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.USSR
    event_text = 'Add 1 USSR Influence in each of four non-US Controlled countries in Eastern Europe.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.event_place_influence(
            Side.USSR, Country.increment_influence, Side.USSR,
            (n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]
                if game_instance.map[n].control != Side.US),
            prompt='COMECON: Add 1 influence to each of 4 non-US controlled countries of Eastern Europe.',
            reps=4,
            max_per_option=1,
        )


class Nasser(Card):
    name = 'Nasser'
    card_index = 15
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.USSR
    event_text = 'Add 2 USSR Influence in Egypt. Remove half (rounded up) of the US Influence in Egypt.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        egypt = game_instance.map['Egypt']
        egypt.change_influence(2, -math.ceil(egypt.influence[Side.US] / 2))


def _warsaw_remove(game_instance):
    game_instance.event_place_influence(
        Side.USSR, Country.remove_influence, Side.US,
        (n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]
            if game_instance.map[n].has_us_influence),
        prompt='Warsaw Pact Formed: Remove all US influence from 4 countries in Eastern Europe.',
        reps=4,
        max_per_option=1,
    )


def _warsaw_add(game_instance):
    game_instance.event_place_influence(
        Side.USSR, Country.increment_influence, Side.USSR,
        CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE],
        prompt='Warsaw Pact Formed: Add 5 USSR Influence to any countries in Eastern Europe.',
        reps=5,
        max_per_option=2,
    )


class Warsaw_Pact_Formed(Card):
    name = 'Warsaw_Pact_Formed'
    card_index = 16
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.USSR
    event_text = 'Remove all US Influence from four countries in Eastern Europe, or add 5 USSR Influence in Eastern Europe, adding no more than 2 per country. Allow play of NATO.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        # NOTE: option callbacks take game_instance via partial (deepcopy-safe,
        # see Olympic_Games comment).
        self.event_occurred = True
        game_instance.basket[Side.US].append('Warsaw_Pact_Formed')
        option_function_mapping = {
            'Remove all US influence from 4 countries in Eastern Europe': partial(_warsaw_remove, game_instance),
            'Add 5 USSR Influence to any countries in Eastern Europe': partial(_warsaw_add, game_instance)
        }

        if len([n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE] if game_instance.map[n].has_us_influence]):
            game_instance.choose_option(
                Side.USSR, option_function_mapping,
                'Warsaw Pact: Choose between two options.',
            )
        else:
            _warsaw_add(game_instance)


class De_Gaulle_Leads_France(Card):
    name = 'De_Gaulle_Leads_France'
    card_index = 17
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.USSR
    event_text = 'Remove 2 US Influence in France, add 1 USSR Influence. Cancels effects of NATO for France.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.map['France'].change_influence(1, -2)
        game_instance.basket[Side.USSR].append('De_Gaulle_Leads_France')


class Captured_Nazi_Scientist(Card):
    name = 'Captured_Nazi_Scientist'
    card_index = 18
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.NEUTRAL
    event_text = 'Advance player\'s Space Race marker one box.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.change_space(side, 1)


class Truman_Doctrine(Card):
    name = 'Truman_Doctrine'
    card_index = 19
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.US
    event_text = 'Remove all USSR Influence markers in one uncontrolled country in Europe.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.event_place_influence(
            Side.US, Country.remove_influence, Side.USSR,
            (n for n in CountryInfo.REGION_ALL[MapRegion.EUROPE]
                if game_instance.map[n].control == Side.NEUTRAL
             and game_instance.map[n].has_ussr_influence),
            prompt='Truman Doctrine: Select a country in which to remove all USSR influence.',
        )


def _olympic_participate_dice_callback(game_instance, side_sponsor, num: tuple):
    game_instance.input_state.reps -= 1
    outcome = 'Success' if num[0] > num[1] else 'Failure'
    if num[0] > num[1]:
        game_instance.change_vp(2 * side_sponsor.vp_mult)
    elif num[0] < num[1]:
        game_instance.change_vp(2 * side_sponsor.opp.vp_mult)
    print(
        f'{outcome} with (Sponsor, Participant) rolls of ({num[0]}, {num[1]}).')
    return True


def _olympic_participate(game_instance, side_sponsor):
    # NOTE: side_sponsor is the event's phasing side (the sponsor).
    game_instance.stage_list.append(
        partial(game_instance.dice_stage,
                partial(_olympic_participate_dice_callback,
                        game_instance, side_sponsor),
                two_dice=True, reroll_ties=True))
    return True


def _olympic_boycott(game_instance, side):
    game_instance.change_defcon(-1)
    if game_instance.terminated:
        return
    game_instance.select_action(
        side, f'Blank_4_Op_Card', is_event_resolved=True)


class Olympic_Games(Card):
    name = 'Olympic_Games'
    card_index = 20
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'Player sponsors Olympics. Opponent may participate or boycott. If Opponent participates, each player rolls one die, with the sponsor adding 2 to his roll. High roll gains 2 VP. Reroll ties If Opponent boycotts, degrade DEFCON one level and the Sponsor may Conduct Operations as if they played a 4 Ops card.'

    def use_event(self, game_instance, side: Side):
        # NOTE: callbacks take game_instance explicitly (bound via partial)
        # instead of closing over it — deepcopy-based lookahead/search clones
        # rebind partial args to the clone, while closures would keep mutating
        # the original game.
        self.event_occurred = True

        option_function_mapping = {
            'Participate and sponsor has modified die roll (+2).': partial(_olympic_participate, game_instance, side),
            'Boycott: DEFCON level degrades by 1 and sponsor may conduct operations as if they played a 4 op card.': partial(_olympic_boycott, game_instance, side)
        }

        game_instance.choose_option(
            side.opp, option_function_mapping,
            'Olympic Games: Choose between two options.',
        )


class NATO(Card):
    name = 'NATO'
    card_index = 21
    card_type = 'Event'
    stage = 'Early War'
    ops = 4
    owner = Side.US
    event_text = 'Play after \'Marshall Plan\' or \'Warsaw Pact\'. USSR player may no longer make Coup or Realignment rolls in any US Controlled countries in Europe. US Controlled countries in Europe may not be attacked by play of the Brush War event.'
    event_unique = True

    def can_event(self, game_instance, side):
        return 'Warsaw_Pact_Formed' in game_instance.basket[Side.US] \
               or 'Marshall_Plan' in game_instance.basket[Side.US]

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, Side.US):
            self.event_occurred = True
            game_instance.basket[Side.US].append('NATO')


class Independent_Reds(Card):
    name = 'Independent_Reds'
    card_index = 22
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.US
    event_text = 'Adds sufficient US Influence in either Yugoslavia, Romania, Bulgaria, Hungary, or Czechoslavakia to equal USSR Influence.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        ireds = ['Yugoslavia', 'Romania',
                 'Bulgaria', 'Hungary', 'Czechoslovakia']
        game_instance.event_place_influence(
            Side.US, Country.match_influence, Side.US,
            (n for n in ireds
             if game_instance.map[n].influence[Side.US] < game_instance.map[n].influence[Side.USSR]),
            prompt='Independent Reds: You may add influence in 1 of these countries to equal USSR influence.',
        )


class Marshall_Plan(Card):
    name = 'Marshall_Plan'
    card_index = 23
    card_type = 'Event'
    stage = 'Early War'
    ops = 4
    owner = Side.US
    event_text = 'Allows play of NATO. Add one US Influence in each of seven non-USSR Controlled Western European countries.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.basket[Side.US].append('Marshall_Plan')
        game_instance.event_place_influence(
            Side.US, Country.increment_influence, Side.US,
            (n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]
                if game_instance.map[n].control != Side.USSR),
            prompt='Marshall Plan: Place influence in 7 non-USSR controlled countries.',
            reps=7,
            max_per_option=1,
        )


class Indo_Pakistani_War(WarCard):
    name = 'Indo_Pakistani_War'
    card_index = 24
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'India or Pakistan invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to the target of the invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track. Effects of Victory: Player gains 2 VP and replaces all opponent\'s Influence in target country with his Influence.'
    war_country_options = ['India', 'Pakistan']
    war_prompt = 'Indo-Pakistani War: Choose target country.'


class Containment(Card):
    name = 'Containment'
    card_index = 25
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.US
    event_text = 'All further Operations cards played by US this turn add one to their value (to a maximum of 4).'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.add_turn_effect(Side.US, 'Containment')


class CIA_Created(Card):
    name = 'CIA_Created'
    card_index = 26
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.US
    event_text = 'USSR reveals hand this turn. Then the US may Conduct Operations as if they played a 1 Op card.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        print(f'USSR player reveals: {game_instance.hand[Side.USSR]}')
        view = game_instance.players[Side.US]
        view.update_opp_hand(game_instance.hand[Side.USSR])
        if hasattr(view, 'stamp_opp_hand_observation'):
            view.stamp_opp_hand_observation(game_instance.shuffle_count)
        self.event_occurred = True
        game_instance.select_action(
            Side.US, f'Blank_1_Op_Card', is_event_resolved=True)


class US_Japan_Mutual_Defense_Pact(Card):
    name = 'US_Japan_Mutual_Defense_Pact'
    card_index = 27
    card_type = 'Event'
    stage = 'Early War'
    ops = 4
    owner = Side.US
    event_text = 'US gains sufficient Influence in Japan for Control. USSR may no longer make Coup or Realignment rolls in Japan.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        japan = game_instance.map['Japan']
        japan.set_influence(japan.influence[Side.USSR], max(
            japan.influence[Side.USSR] + 4, japan.influence[Side.US]))
        game_instance.basket[Side.US].append('US_Japan_Mutual_Defense_Pact')


class Suez_Crisis(Card):
    name = 'Suez_Crisis'
    card_index = 28
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.USSR
    event_text = 'Remove a total of 4 US Influence from France, the United Kingdom or Israel. Remove no more than 2 Influence per country.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        suez = ['France', 'UK', 'Israel']

        game_instance.event_place_influence(
            Side.USSR, Country.decrement_influence, Side.US,
            (n for n in suez if game_instance.map[n].has_us_influence),
            prompt='Remove US influence using Suez Crisis.',
            reps=4,
            max_per_option=2,
        )


class East_European_Unrest(Card):
    name = 'East_European_Unrest'
    card_index = 29
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.US
    event_text = 'In Early or Mid War: Remove 1 USSR Influence from three countries in Eastern Europe. In Late War: Remove 2 USSR Influence from three countries in Eastern Europe.'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        dec = 2 if 8 <= game_instance.turn_track <= 10 else 1

        game_instance.event_place_influence(
            Side.US, partial(Country.decrement_influence, amt=dec), Side.USSR,
            (n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]
                if game_instance.map[n].has_ussr_influence),
            prompt='Remove USSR influence using East European Unrest.',
            reps=3,
            max_per_option=1,
        )


class Decolonization(Card):
    name = 'Decolonization'
    card_index = 30
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.USSR
    event_text = 'Add one USSR Influence in each of any four African and/or SE Asian countries.'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.event_place_influence(
            Side.USSR, Country.increment_influence, Side.USSR,
            chain(CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA],
                  CountryInfo.REGION_ALL[MapRegion.AFRICA]),
            prompt='Place influence using Decolonization.',
            reps=4,
            max_per_option=1,
        )


class Red_Scare_Purge(Card):
    name = 'Red_Scare_Purge'
    card_index = 31
    card_type = 'Event'
    stage = 'Early War'
    ops = 4
    owner = Side.NEUTRAL
    event_text = 'All further Operations cards played by your opponent this turn are -1 to their value (to a minimum of 1 Op).'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.add_turn_effect(side, 'Red_Scare_Purge')


class UN_Intervention(Card):
    name = 'UN_Intervention'
    card_index = 32
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.NEUTRAL
    can_headline = False
    event_text = 'Play this card simultaneously with a card containing your opponent\'s associated Event. The Event is cancelled, but you may use its Operations value to Conduct Operations. The cancelled event returns to the discard pile. May not be played during headline phase.'

    def can_event(self, game_instance, side):
        return any((game_instance.cards[c].info.owner == side.opp for c in game_instance.hand[side]))

    def callback(self, game_instance, side, card_name: str):
        if game_instance.terminated:
            return False
        game_instance.input_state.reps -= 1
        game_instance.select_action(side, f'{card_name}', un_intervention=True)
        return True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.input_state = Input(
            side, InputType.SELECT_CARD,
            partial(self.callback, game_instance, side),
            (n for n in game_instance.hand[side]
             if game_instance.cards[n].info.owner == side.opp),
            prompt=f'You may pick a opponent-owned card from your hand to use with UN Intervention.',
            context={
                'source_card': self.name,
                'hand_exit': 'un_target',
            },
        )


def _destalinization_begin_placement(game_instance, removal_input):
    ops = 4 - removal_input.reps
    if ops <= 0:
        # No influence was moved; clear the pending input so the stage
        # machine can advance past this card instead of looping forever.
        game_instance.input_state = None
        return True

    game_instance.event_place_influence(
        Side.USSR, Country.increment_influence, Side.USSR,
        (n for n in CountryInfo.ALL
            if game_instance.map[n].control != Side.US and not game_instance.map[n].info.superpower),
        prompt=f'Add {ops} influence using De-Stalinization.',
        reps=ops,
        max_per_option=2,
    )
    return True


def _destalinization_remove_callback(game_instance, country_name):
    removal_input = game_instance.input_state
    if country_name != game_instance.input_state.option_stop_early:
        game_instance.event_influence_callback(
            Country.decrement_influence, Side.USSR, country_name)
        if (removal_input.reps
                and any(removal_input.available_options)):
            # Update early-stop text to reflect how many points were moved.
            removal_input.option_stop_early = f'Move {4 - removal_input.reps} influence.'
            return True

    return _destalinization_begin_placement(game_instance, removal_input)


class De_Stalinization(Card):
    name = 'De_Stalinization'
    card_index = 33
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.USSR
    event_text = 'USSR may relocate up to 4 Influence points to non-US controlled countries. No more than 2 Influence may be placed in the same country.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        # NOTE: callbacks take game_instance via partial (deepcopy-safe,
        # see Olympic_Games comment).
        self.event_occurred = True
        game_instance.input_state = Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(_destalinization_remove_callback, game_instance),
            (n for n in CountryInfo.ALL
                if game_instance.map[n].has_ussr_influence and not game_instance.map[n].info.superpower),
            prompt='Remove up to 4 influence using De-Stalinization.',
            reps=4,
            reps_unit='influence',
            option_stop_early='Move no influence.'
        )


class Nuclear_Test_Ban(Card):
    name = 'Nuclear_Test_Ban'
    card_index = 34
    card_type = 'Event'
    stage = 'Early War'
    ops = 4
    owner = Side.NEUTRAL
    event_text = 'Player earns VPs equal to the current DEFCON level minus 2, then improve DEFCON two levels.'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.change_vp(
            (game_instance.defcon_track - 2) * side.vp_mult)
        if game_instance.terminated:
            return
        game_instance.change_defcon(2)


class Formosan_Resolution(Card):
    name = 'Formosan_Resolution'
    card_index = 35
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.US
    event_text = 'Taiwan shall be treated as a Battleground country for scoring purposes, if the US controls Taiwan when the Asia Scoring Card is played or during Final Scoring at the end of Turn 10. Taiwan is not a battleground country for any other game purpose. This card is discarded after US play of \'The China Card\'.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.basket[Side.US].append('Formosan_Resolution')


class Defectors(Card):
    name = 'Defectors'
    card_index = 103
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.US
    event_text = 'Play in Headline Phase to cancel USSR Headline event, including Scoring Card. Cancelled card returns to the Discard Pile. If Defectors played by USSR during Soviet action round, US gains 1 VP (unless played on the Space Race).'

    def can_event(self, game_instance, side):
        return False

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        # checks to see if headline bin is empty i.e. in action round
        # check if there's a headline
        if game_instance.headline_bin[Side.USSR]:
            game_instance.discard_pile.append(
                game_instance.headline_bin[Side.USSR])
            game_instance.headline_bin[Side.USSR] = ''
        if side == Side.USSR and game_instance.ar_side == Side.USSR:
            game_instance.change_vp(Side.US.vp_mult)


class The_Cambridge_Five(Card):
    name = 'The_Cambridge_Five'
    card_index = 104
    card_type = 'Event'
    stage = 'Early War'
    optional = True
    ops = 2
    owner = Side.USSR
    event_text = 'The US player exposes all scoring cards in their hand. The USSR player may then add 1 Influence in any single region named on one of those scoring cards (USSR choice). Cannot be played as an event in Late War.'

    def can_event(self, game_instance, side):
        return game_instance.turn_track < 8

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, Side.USSR):
            us_scoring_cards = [n for n in game_instance.hand[Side.US]
                                if game_instance.cards[n].info.card_type == 'Scoring']
            countries = [CountryInfo.REGION_ALL[k] for k in [
                Card.ALL[n].scoring_region for n in us_scoring_cards]]

            print(f'US player reveals: {us_scoring_cards}')
            view = game_instance.players[Side.USSR]
            if hasattr(view, 'learn_opp_cards'):
                view.learn_opp_cards(us_scoring_cards)
                view.stamp_opp_hand_observation(game_instance.shuffle_count)
                other_scoring_cards = [
                    name for name, card in Card.ALL.items()
                    if card.card_type == 'Scoring'
                    and name not in us_scoring_cards
                ]
                view.exclude_opp_cards(
                    other_scoring_cards,
                    game_instance.unknown_hand_draws[Side.US])
            else:
                view.update_opp_hand(us_scoring_cards)

            self.event_occurred = True
            game_instance.event_place_influence(
                Side.USSR, Country.increment_influence, Side.USSR,
                (item for sublist in countries for item in sublist),
                prompt=f'Place 1 influence in a country named on the revealed scoring cards using The Cambridge Five.',
            )


class Special_Relationship(Card):
    name = 'Special_Relationship'
    card_index = 105
    card_type = 'Event'
    stage = 'Early War'
    optional = True
    ops = 2
    owner = Side.US
    event_text = 'If UK is US controlled but NATO is not in effect, US adds 1 Influence to any country adjacent to the UK. If UK is US controlled and NATO is in effect, US adds 2 Influence to any Western European country and gains 2 VPs.'

    def can_event(self, game_instance, side):
        return game_instance.map['UK'].control == Side.US

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, Side.US):
            self.event_occurred = True
            if 'NATO' in game_instance.basket[Side.US]:
                available_list = CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]
                incr = 2
                game_instance.change_vp(2 * Side.US.vp_mult)
                if game_instance.terminated:
                    return
            else:
                available_list = game_instance.map['UK'].info.adjacent_countries
                incr = 1

            game_instance.event_place_influence(
                Side.US, partial(Country.increment_influence, amt=incr), Side.US,
                available_list,
                prompt=f'Place {incr} influence in a single country using Special Relationship.',
            )


class NORAD(Card):
    name = 'NORAD'
    card_index = 106
    card_type = 'Event'
    stage = 'Early War'
    optional = True
    ops = 3
    owner = Side.US
    event_text = 'If the US controls Canada, the US may add 1 Influence to any country already containing US Influence at the conclusion of any Action Round in which the DEFCON marker moves to the \'2\' box. This event cancelled by \'Quagmire\'.'
    event_unique = True

    def place_norad_influence(self, game_instance):
        if game_instance.map['Canada'].control != Side.US:
            return
        game_instance.event_place_influence(
            Side.US, Country.increment_influence, Side.US,
            game_instance.map.has_us_influence,
            prompt='Place NORAD influence.',
        )

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.basket[Side.US].append('NORAD')

# --
# -- MID WAR
# --
#
#


class Brush_War(WarCard):
    name = 'Brush_War'
    card_index = 36
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.NEUTRAL
    event_text = 'Attack any country with a stability of 1 or 2. Roll a die and subtract 1 for every adjacent enemy controlled country. Success on 3-6. Player adds 3 to his Military Ops Track. Effects of Victory: Player gains 1 VP and replaces all opponent\'s Influence with his Influence.'
    war_lower = 3
    war_win_vp = 1
    war_win_milops = 3
    war_prompt = 'Brush War: Choose a target country.'

    def war_country_options(self, game_instance):
        return (n for n in game_instance.map.ALL
                if game_instance.map[n].info.stability <= 2
                and n not in game_instance.calculate_nato_countries())


class Central_America_Scoring(Card):
    name = 'Central_America_Scoring'
    card_index = 37
    card_type = 'Scoring'
    stage = 'Mid War'
    scoring_region = MapRegion.CENTRAL_AMERICA
    event_text = 'Both sides score: Presence: 1, Domination: 3, Control: 5. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
    may_be_held = False

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.score(MapRegion.CENTRAL_AMERICA)


class Southeast_Asia_Scoring(Card):
    name = 'Southeast_Asia_Scoring'
    card_index = 38
    card_type = 'Scoring'
    stage = 'Mid War'
    scoring_region = MapRegion.SOUTHEAST_ASIA
    event_text = 'Both sides score: 1 VP each for Control of: Burma, Cambodia/Laos, Vietnam, Malaysia, Indonesia, the Phillipines, 2 VP for Control of Thailand'
    may_be_held = False
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.score(MapRegion.SOUTHEAST_ASIA)


class Arms_Race(Card):
    name = 'Arms_Race'
    card_index = 39
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.NEUTRAL
    event_text = 'Compare each player\'s status on the Military Operations Track. If Phasing Player has more Military Operations points, he scores 1 VP. If Phasing Player has more Military Operations points and has met the Required Military Operations amount, he scores 3 VP instead.'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        if game_instance.milops_track[side] > game_instance.milops_track[side.opp]:
            if game_instance.milops_track[side] >= game_instance.defcon_track:
                game_instance.change_vp(3 * side.vp_mult)
            else:
                game_instance.change_vp(1 * side.vp_mult)


class Cuban_Missile_Crisis(Card):
    name = 'Cuban_Missile_Crisis'
    card_index = 40
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.NEUTRAL
    event_text = 'Set DEFCON to Level 2. Any further Coup attempt by your opponent this turn, anywhere on the board, will result in Global Thermonuclear War. Your opponent will lose the game. This event may be cancelled at any time if the USSR player removes two Influence from Cuba or the US player removes 2 Influence from either West Germany or Turkey.'
    event_unique = True

    def cuban_missile_remove(self, game_instance, side: Side):
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
        options = [
            n for n in countries if game_instance.map[n].influence[side] >= 2]

        if len(options) == 0:
            return False

        def cuban_callback(game_instance, opt: str):
            # NOTE: game_instance 走 partial 参数（deepcopy 重绑到克隆）；
            # 函数体不得引用外层作用域的 game_instance —— 否则克隆上触发
            # 回调会改写原游戏（08-16 搜索实弹抓到的泄漏）。
            if opt != game_instance.input_state.option_stop_early:
                game_instance.event_influence_callback(
                    partial(Country.decrement_influence, amt=2), side, opt)
                game_instance.safe_remove_from_basket(side.opp, 'Cuban_Missile_Crisis')
            else:
                game_instance.input_state.reps -= 1
            return True

        game_instance.input_state = Input(
            side, InputType.SELECT_COUNTRY,
            partial(cuban_callback, game_instance),
            options,
            prompt='Cuban Missile Crisis: Remove 2 influence to de-escalate.',
            reps_unit='influence',
            option_stop_early='Do not remove influence.'
        )
        return True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.change_defcon(2 - game_instance.defcon_track)
        game_instance.add_turn_effect(side, 'Cuban_Missile_Crisis')


class Nuclear_Subs(Card):
    name = 'Nuclear_Subs'
    card_index = 41
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'US Coup attempts in Battleground Countries do not affect the DEFCON track for the remainder of the turn (does not affect Cuban Missile Crisis).'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.add_turn_effect(Side.US, 'Nuclear_Subs')


class Quagmire(Card):
    name = 'Quagmire'
    card_index = 42
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.USSR
    event_text = 'On next action round, US player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each US player Action round until successful or no appropriate cards remain. If out of appropriate cards, the US player may only play scoring cards until the next turn.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        if 'NORAD' in game_instance.basket[Side.US]:
            game_instance.basket[Side.US].remove('NORAD')
        game_instance.basket[Side.US].append('Quagmire')


class Salt_Negotiations(Card):
    name = 'Salt_Negotiations'
    card_index = 43
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.NEUTRAL
    event_text = 'Improve DEFCON two levels. Further Coup attempts incur -1 die roll modifier for both players for the remainder of the turn. Player may sort through discard pile and reclaim one non-scoring card, after revealing it to their opponent.'
    event_unique = True

    def callback(self, game_instance, side: Side, option_stop_early: str, card_name: str):
        game_instance.input_state.reps -= 1
        if card_name != option_stop_early:
            game_instance.discard_pile.remove(card_name)
            # Shared state/log visibility means both players can inspect this pickup.
            game_instance.hand[side].append(card_name)
            if game_instance.players[side.opp] is not None:
                view = game_instance.players[side.opp]
                view.learn_opp_card(card_name)
                view.stamp_opp_hand_observation(game_instance.shuffle_count)
        return True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.change_defcon(2)
        game_instance.add_turn_effect(side, 'Salt_Negotiations')

        can_stop_now = 'Do not take a card.'

        game_instance.input_state = Input(
            side, InputType.SELECT_CARD,
            partial(self.callback, game_instance, side, can_stop_now),
            (n for n in game_instance.discard_pile if game_instance.cards[n].info.ops >= 1),
            prompt=f'You may pick a non-scoring card from the discard pile.',
            option_stop_early=can_stop_now,
            context={
                'source_card': self.name,
                'hand_exit': 'salt_target',
            },
        )


class Bear_Trap(Card):
    name = 'Bear_Trap'
    card_index = 44
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.US
    event_text = 'On next action round, USSR player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each USSR player Action Round until successful or no appropriate cards remain. If out of appropriate cards, the USSR player may only play scoring cards until the next turn.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.basket[Side.USSR].append('Bear_Trap')


class Summit(Card):
    name = 'Summit'
    card_index = 45
    card_type = 'Event'
    stage = 'Mid War'
    ops = 1
    owner = Side.NEUTRAL
    event_text = 'Both players roll a die.  Each adds 1 for each Region they Dominate or Control. High roller gains 2 VP and may move DEFCON marker one level in either direction. Do not reroll ties.'

    def choices(self, game_instance, side: Side):
        game_instance.change_vp(2*side.vp_mult)
        if game_instance.terminated:
            return

        option_function_mapping = {
            'DEFCON -1': partial(game_instance.change_defcon, -1),
            'No change': partial(lambda: None),
            'DEFCON +1': partial(game_instance.change_defcon, 1),
        }

        game_instance.choose_option(
            side, option_function_mapping,
            'Summit: You may change DEFCON level by 1 in either direction.',
        )

    def dice_callback(self, game_instance, ussr_advantage: int, num: tuple):
        game_instance.input_state.reps -= 1
        ussr_total = num[Side.USSR] + ussr_advantage
        us_total = num[Side.US]

        if ussr_total > us_total:
            outcome = 'USSR success'
            self.choices(game_instance, Side.USSR)
        elif us_total > ussr_total:
            outcome = 'US success'
            self.choices(game_instance, Side.US)
        else:
            outcome = 'Tie'
        print(
            f'{outcome} with (USSR, US) rolls of ({num[Side.USSR]}, {num[Side.US]}). ussr_advantage is {ussr_advantage}.')
        return True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        dominate_or_control = [0, 0]

        for region in [i for i in MapRegion.main_regions()]:
            bg_count = [0, 0, 0]  # USSR, US, NEUTRAL
            country_count = [0, 0, 0]

            for n in CountryInfo.REGION_ALL[region]:
                x = game_instance.map[n]
                if x.info.battleground:
                    bg_count[x.control] += 1
                country_count[x.control] += 1

            for s in [Side.USSR, Side.US]:
                if country_count[s] > country_count[s.opp]:
                    if bg_count[s] == sum(bg_count):
                        dominate_or_control[s] += 1
                    elif bg_count[s] > bg_count[s.opp] and country_count[s] > bg_count[s]:
                        dominate_or_control[s] += 1

        ussr_advantage = dominate_or_control[Side.USSR] - \
            dominate_or_control[Side.US]

        game_instance.stage_list.append(partial(
            game_instance.dice_stage,
            partial(self.dice_callback, game_instance, ussr_advantage), two_dice=True))


class How_I_Learned_to_Stop_Worrying(Card):
    name = 'How_I_Learned_to_Stop_Worrying'
    card_index = 46
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'Set the DEFCON at any level you want (1-5). This event counts as 5 Military Operations for the purpose of required Military Operations.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        option_function_mapping = {
            f'DEFCON 1: Thermonuclear War. {side.opp} victory!': partial(game_instance.change_defcon, 1 - game_instance.defcon_track),
            f'DEFCON 2': partial(game_instance.change_defcon, 2 - game_instance.defcon_track),
            f'DEFCON 3': partial(game_instance.change_defcon, 3 - game_instance.defcon_track),
            f'DEFCON 4': partial(game_instance.change_defcon, 4 - game_instance.defcon_track),
            f'DEFCON 5': partial(game_instance.change_defcon, 5 - game_instance.defcon_track)
        }

        game_instance.choose_option(
            side, option_function_mapping,
            'How I Learned To Stop Worrying: Set a new DEFCON level.',
        )

        game_instance.change_milops(side, 5)


class Junta(Card):
    name = 'Junta'
    card_index = 47
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'Place 2 Influence in any one Central or South American country. Then you may make a free Coup attempt or Realignment roll in one of these regions (using this card\'s Operations Value).'

    def stage_2(self, game_instance, side, ca_sa):
        def coup(game_instance, side, ca_sa):
            game_instance.card_operation_coup(
                side, 'Junta', restricted_list=ca_sa, free=True)

        def realignment(game_instance, side, ca_sa):
            game_instance.card_operation_realignment(
                side, 'Junta', restricted_list=ca_sa, free=True)

        option_function_mapping = {
            'Free coup attempt': partial(coup, game_instance, side, ca_sa),
            'Free realignment rolls': partial(realignment, game_instance, side, ca_sa)
        }

        game_instance.choose_option(
            side, option_function_mapping,
            'Junta: Player may make free Coup attempts or realignment rolls in Central America or South America.',
        )

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        ca_sa = list(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA]) + list(
            CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA])

        game_instance.event_place_influence(
            side, partial(Country.increment_influence, amt=2), side,
            ca_sa,
            prompt='Junta: Add 2 influence to a single country in Central America or South America.',
        )

        game_instance.stage_list.append(
            partial(self.stage_2, game_instance, side, ca_sa))


class Kitchen_Debates(Card):
    name = 'Kitchen_Debates'
    card_index = 48
    card_type = 'Event'
    stage = 'Mid War'
    ops = 1
    owner = Side.US
    event_text = 'If the US controls more Battleground countries than the USSR, poke opponent in chest and gain 2 VP!'
    event_unique = True

    def can_event(self, game_instance, side):
        us_count = sum(1 for n in CountryInfo.ALL if game_instance.map[n].control ==
                       Side.US and game_instance.map[n].info.battleground)
        ussr_count = sum(1 for n in CountryInfo.ALL if game_instance.map[n].control ==
                         Side.USSR and game_instance.map[n].info.battleground)
        return us_count > ussr_count

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        if self.can_event(game_instance, Side.US):
            print('USSR poked in the chest by US player!')
            game_instance.change_vp(-2)


class Missile_Envy(Card):
    name = 'Missile_Envy'
    card_index = 49
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'Exchange this card for your opponent\'s highest valued Operations card in his hand. If two or more cards are tied, opponent chooses. If the exchanged card contains your event, or an event applicable to both players, it occurs immediately. If it contains opponent\'s event, use Operations value without triggering event. Opponent must use this card for Operations during his next action round.'

    def __init__(self):
        super().__init__()
        self.exchange = False

    def dispose(self, game, side):
        if self.exchange:
            if self.name in game.hand[side]:
                game.hand[side].remove(self.name)
            if self.name not in game.hand[side.opp]:
                game.hand[side.opp].append(self.name)
            self.exchange = False
        else:
            # Missile Envy is placed in opponent's basket by use_event.
            # It may also end up in the player's basket depending on the
            # exchange path, so try both.
            game.safe_remove_from_basket(side, self.name)
            game.safe_remove_from_basket(side.opp, self.name)
            super().dispose(game, side)

    def can_event(self, game, side):
        return not self.event_occurred

    def missile_envy_exchange_callback(self, game, side, card: str):
        game.input_state.reps -= 1
        game.hand[side.opp].remove(card)
        game.hand[side].append(card)
        if game.players[side.opp] is not None:
            view = game.players[side.opp]
            view.learn_opp_card(card)
            view.stamp_opp_hand_observation(game.shuffle_count)

        self.exchange = True

        if game.cards[card].owner == side.opp:
            options = []
            if game.can_place_influence(side, card):
                options.append(CardAction.INFLUENCE.name)
            if game.can_coup_at_all(side):
                options.append(CardAction.COUP.name)
            if game.can_realign_at_all(side):
                options.append(CardAction.REALIGNMENT.name)
            if game.can_space(side, card):
                options.append(CardAction.SPACE.name)

            game.input_state = Input(
                side, InputType.SELECT_CARD_ACTION,
                partial(game.action_callback, side, card,
                        no_event=True),
                options,
                prompt=f'Opponent has traded {card}. Select an action.'
            )

        else:
            # must append backwards
            game.stage_list.append(
                partial(game.cards[card].dispose, game, side))
            game.stage_list.append(partial(game.trigger_event, side, card))

        return True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[side.opp].append(self.name)

        best_ops = 0
        best_cards = []
        for card_name in game.hand[side.opp]:
            card = game.cards[card_name]
            if (card_name == 'The_China_Card'
                    or card.info.card_type == 'Scoring'
                    or card.info.ops <= 0):
                continue
            curr_ops = game.get_global_effective_ops(
                side.opp, card.ops)
            if curr_ops > best_ops:
                best_ops = curr_ops
                best_cards = [card_name]
            elif curr_ops == best_ops:
                best_cards.append(card_name)

        game.input_state = Input(
            side.opp, InputType.SELECT_CARD,
            partial(self.missile_envy_exchange_callback, game, side),
            best_cards,
            prompt='Select card to exchange with Missile Envy.',
            reps=1
        )


class We_Will_Bury_You(Card):
    name = 'We_Will_Bury_You'
    card_index = 50
    card_type = 'Event'
    stage = 'Mid War'
    ops = 4
    owner = Side.USSR
    event_text = 'Unless UN Invervention is played as an Event on the US player\'s next round, USSR gains 3 VP prior to any US VP award. Degrade DEFCON one level.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.change_defcon(-1)
        if game_instance.terminated:
            return
        game_instance.basket[Side.USSR].append('We_Will_Bury_You')


class Brezhnev_Doctrine(Card):
    name = 'Brezhnev_Doctrine'
    card_index = 51
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.USSR
    event_text = 'All further Operations cards played by the USSR this turn increase their Ops value by one (to a maximum of 4).'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.add_turn_effect(Side.USSR, 'Brezhnev_Doctrine')


class Portuguese_Empire_Crumbles(Card):
    name = 'Portuguese_Empire_Crumbles'
    card_index = 52
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.USSR
    event_text = 'Add 2 USSR Influence in both SE African States and Angola.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.map.change_influence('Angola', Side.USSR, 2)
        game_instance.map.change_influence('SE_African_States', Side.USSR, 2)


def _sa_unrest_sa(game_instance):
    game_instance.map.change_influence('South_Africa', Side.USSR, 2)


def _sa_unrest_sa_angola(game_instance):
    game_instance.map.change_influence('South_Africa', Side.USSR, 1)
    game_instance.map.change_influence('Angola', Side.USSR, 2)


def _sa_unrest_sa_botswana(game_instance):
    game_instance.map.change_influence('South_Africa', Side.USSR, 1)
    game_instance.map.change_influence('Botswana', Side.USSR, 2)


class South_African_Unrest(Card):
    name = 'South_African_Unrest'
    card_index = 53
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.USSR
    event_text = 'USSR either adds 2 Influence in South Africa or adds 1 Influence in South Africa and 2 Influence in any countries adjacent to South Africa.'

    def use_event(self, game_instance, side: Side):
        # NOTE: option callbacks take game_instance via partial (deepcopy-safe,
        # see Olympic_Games comment).
        self.event_occurred = True

        option_function_mapping = {
            'Add 2 Influence to South Africa.': partial(_sa_unrest_sa, game_instance),
            'Add 1 Influence to South Africa and 2 Influence to Angola.': partial(_sa_unrest_sa_angola, game_instance),
            'Add 1 Influence to South Africa and 2 Influence to Botswana.': partial(_sa_unrest_sa_botswana, game_instance)
        }

        game_instance.choose_option(
            Side.USSR, option_function_mapping,
            'South African Unrest: Choose an option.',
        )


class Allende(Card):
    name = 'Allende'
    card_index = 54
    card_type = 'Event'
    stage = 'Mid War'
    ops = 1
    owner = Side.USSR
    event_text = 'USSR receives 2 Influence in Chile.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.map['Chile'].change_influence(2, 0)


class Willy_Brandt(Card):
    name = 'Willy_Brandt'
    card_index = 55
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.USSR
    event_text = 'USSR receives gains 1 VP. USSR receives 1 Influence in West Germany. Cancels NATO for West Germany. This event unplayable and/or cancelled by Tear Down This Wall.'
    event_unique = True

    def can_event(self, game_instance, side):
        return 'Tear_Down_This_Wall' not in game_instance.basket[Side.US]

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, Side.USSR):
            self.event_occurred = True
            game_instance.change_vp(1)
            if game_instance.terminated:
                return
            game_instance.map['West_Germany'].change_influence(1, 0)
            game_instance.basket[Side.USSR].append('Willy_Brandt')


class Muslim_Revolution(Card):
    name = 'Muslim_Revolution'
    card_index = 56
    card_type = 'Event'
    stage = 'Mid War'
    ops = 4
    owner = Side.USSR
    event_text = 'Remove all US Influence in two of the following countries: Sudan, Iran, Iraq, Egypt, Libya, Saudi Arabia, Syria, Jordan.'

    def can_event(self, game_instance, side):
        return False if 'AWACS_Sale_to_Saudis' in game_instance.basket[Side.US] else True

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, Side.USSR):
            self.event_occurred = True
            mr = ['Sudan', 'Iran', 'Iraq', 'Egypt',
                  'Libya', 'Saudi_Arabia', 'Syria', 'Jordan']
            game_instance.event_place_influence(
                Side.USSR, Country.remove_influence, Side.US,
                (n for n in mr if game_instance.map[n].has_us_influence),
                prompt='Muslim Revolution: Select countries in which to remove all US influence.',
                reps=2,
                reps_unit='countries',
                max_per_option=1,
            )


class ABM_Treaty(Card):
    name = 'ABM_Treaty'
    card_index = 57
    card_type = 'Event'
    stage = 'Mid War'
    ops = 4
    owner = Side.NEUTRAL
    event_text = 'Improve DEFCON one level. Then player may Conduct Operations as if they played a 4 Ops card.'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.change_defcon(1)
        game_instance.select_action(
            side, f'Blank_4_Op_Card', is_event_resolved=True)


class Cultural_Revolution(Card):
    name = 'Cultural_Revolution'
    card_index = 58
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.USSR
    event_text = 'If the US has \'The China Card\', claim it face up and available for play. If the USSR already had it, USSR gains 1 VP.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        if 'The_China_Card' in game_instance.hand[Side.US]:
            game_instance.cards['The_China_Card'].move_china_card(
                game_instance, Side.US, made_playable=True)
        elif 'The_China_Card' in game_instance.hand[Side.USSR]:
            game_instance.change_vp(1)


class Flower_Power(Card):
    name = 'Flower_Power'
    card_index = 59
    card_type = 'Event'
    stage = 'Mid War'
    ops = 4
    owner = Side.USSR
    event_text = 'USSR gains 2 VP for every subsequently US played \'war card\' (played as an Event or Operations) unless played on the Space Race. War Cards: Arab-Israeli War, Korean War, Brush War, Indo-Pakistani War or Iran-Iraq War. This event cancelled by \'An Evil Empire\'.'
    event_unique = True

    def can_event(self, game_instance, side):
        return 'An_Evil_Empire' not in game_instance.basket[Side.US]

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, Side.USSR):
            self.event_occurred = True
            game_instance.basket[Side.USSR].append('Flower_Power')


class U2_Incident(Card):
    name = 'U2_Incident'
    card_index = 60
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.USSR
    event_text = 'USSR gains 1 VP. If UN Intervention played later this turn as an Event, either by US or USSR, gain 1 additional VP.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.change_vp(1)
        if game_instance.terminated:
            return
        game_instance.add_turn_effect(Side.USSR, 'U2_Incident')


class OPEC(Card):
    name = 'OPEC'
    card_index = 61
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.USSR
    event_text = 'USSR gains 1VP for each of the following countries he controls: Egypt, Iran, Libya, Saudi Arabia, Iraq, Gulf States, and Venezuela. Unplayable as an event if \'North Sea Oil\' is in effect.'

    def can_event(self, game_instance, side):
        return 'North_Sea_Oil' not in game_instance.basket[Side.US]

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, Side.USSR):
            self.event_occurred = True
            opec = ['Egypt', 'Iran', 'Libya', 'Saudi_Arabia',
                    'Iraq', 'Gulf_States', 'Venezuela']
            swing = sum(
                Side.USSR.vp_mult for country in opec if game_instance.map[country].control == Side.USSR)
            game_instance.change_vp(swing)


class Lone_Gunman(Card):
    name = 'Lone_Gunman'
    card_index = 62
    card_type = 'Event'
    stage = 'Mid War'
    ops = 1
    owner = Side.USSR
    event_text = 'US player reveals his hand. Then the USSR may Conduct Operations as if they played a 1 Op card.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        print(f'US player reveals: {game_instance.hand[Side.US]}')
        view = game_instance.players[Side.USSR]
        view.update_opp_hand(game_instance.hand[Side.US])
        if hasattr(view, 'stamp_opp_hand_observation'):
            view.stamp_opp_hand_observation(game_instance.shuffle_count)
        self.event_occurred = True
        game_instance.select_action(
            Side.USSR, f'Blank_1_Op_Card', is_event_resolved=True)


class Colonial_Rear_Guards(Card):
    name = 'Colonial_Rear_Guards'
    card_index = 63
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'Add 1 US Influence in each of four different African and/or Southeast Asian countries.'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.event_place_influence(
            Side.US, Country.increment_influence, Side.US,
            chain(CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA],
                  CountryInfo.REGION_ALL[MapRegion.AFRICA]),
            prompt='Place influence using Colonial Real Guards.',
            reps=4,
            max_per_option=1,
        )


class Panama_Canal_Returned(Card):
    name = 'Panama_Canal_Returned'
    card_index = 64
    card_type = 'Event'
    stage = 'Mid War'
    ops = 1
    owner = Side.US
    event_text = 'Add 1 US Influence in Panama, Costa Rica, and Venezuela.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        countries = ['Panama', 'Costa_Rica', 'Venezuela']
        for country in countries:
            game_instance.map[country].change_influence(0, 1)


class Camp_David_Accords(Card):
    name = 'Camp_David_Accords'
    card_index = 65
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'US gains 1 VP. US receives 1 Influence in Israel, Jordan and Egypt. Arab-Israeli War event no longer playable.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.change_vp(-1)
        if game_instance.terminated:
            return
        countries = ['Israel', 'Jordan', 'Egypt']
        for country in countries:
            game_instance.map[country].change_influence(0, 1)
        game_instance.basket[Side.US].append('Camp_David_Accords')


class Puppet_Governments(Card):
    name = 'Puppet_Governments'
    card_index = 66
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'US may add 1 Influence in three countries that currently contain no Influence from either power.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.event_place_influence(
            Side.US, Country.increment_influence, Side.US,
            (n for n in CountryInfo.ALL
                if not game_instance.map[n].has_us_influence
                and not game_instance.map[n].has_ussr_influence),
            prompt='Place influence using Puppet Governments.',
            reps=3,
            max_per_option=1,
        )


def _grain_sales_return_card(game_instance, card_name: str):
    if card_name in game_instance.hand[Side.US]:
        game_instance.hand[Side.US].remove(card_name)
    if card_name not in game_instance.hand[Side.USSR]:
        game_instance.hand[Side.USSR].append(card_name)
    if game_instance.players[Side.US] is not None:
        view = game_instance.players[Side.US]
        view.learn_opp_card(card_name)
        view.stamp_opp_hand_observation(game_instance.shuffle_count)
    game_instance.select_action(Side.US, 'Blank_2_Op_Card', is_event_resolved=True)


class Grain_Sales_to_Soviets(Card):
    name = 'Grain_Sales_to_Soviets'
    card_index = 67
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'Randomly choose one card from USSR hand. Play it or return it. If Soviet player has no cards, or returned, use this card to conduct Operations normally.'

    def use_un_intervention(self, game_instance, card_name: str):
        # the only exception where UN intervention is used out of place without calling card_callback
        game_instance.stage_list.append(
            partial(game_instance.cards['UN_Intervention'].dispose,
                    game_instance, Side.US))
        game_instance.select_action(Side.US, card_name, un_intervention=True)
        if 'U2_Incident' in game_instance.basket[Side.USSR]:
            game_instance.change_vp(1)
            game_instance.basket[Side.USSR].remove('U2_Incident')

    def action_stage(self, game_instance, card_name: str):
        # if received card is Side.USSR, then offer to use UN intervention if holding
        # NOTE: option callbacks take game_instance via partial (deepcopy-safe,
        # see Olympic_Games comment).
        option_function_mapping = {
            'Use card normally':
                partial(game_instance.select_action, Side.US, card_name),
            'Return card to USSR':
                partial(_grain_sales_return_card, game_instance, card_name)
        }

        if 'UN_Intervention' in game_instance.hand[Side.US] and \
                game_instance.cards[card_name].info.owner == Side.USSR:
            option_function_mapping['Use card with UN Intervention'] = partial(
                self.use_un_intervention, game_instance, card_name)

        game_instance.choose_option(
            Side.US, option_function_mapping,
            'You may use the card selected by Grain Sales to Soviets.',
        )

    def random_card_callback(self, game_instance, card_name: str):
        game_instance.input_state.reps -= 1
        print(f'{card_name} was selected by Grain Sales to Soviets.')
        game_instance.hand[Side.USSR].remove(card_name)
        game_instance.hand[Side.US].append(card_name)
        if game_instance.players[Side.USSR] is not None:
            view = game_instance.players[Side.USSR]
            view.learn_opp_card(card_name)
            view.stamp_opp_hand_observation(game_instance.shuffle_count)
        game_instance.stage_list.append(
            partial(self.action_stage, game_instance, card_name))
        return True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True

        if not any(n for n in game_instance.hand[Side.USSR] if n != 'Grain_Sales_to_Soviets'):
            game_instance.select_action(Side.US, 'Blank_2_Op_Card', is_event_resolved=True)
            return

        game_instance.input_state = Input(
            Side.NEUTRAL, InputType.SELECT_CARD,
            partial(self.random_card_callback, game_instance),
            (n for n in game_instance.hand[Side.USSR]
             if n != 'Grain_Sales_to_Soviets'),
            prompt='Grain Sales to Soviets: US player randomly selects a card from USSR player\'s hand.'
        )


class John_Paul_II_Elected_Pope(Card):
    name = 'John_Paul_II_Elected_Pope'
    card_index = 68
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'Remove 2 USSR Influence in Poland and then add 1 US Influence in Poland. Allows play of \'Solidarity\'.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.map['Poland'].change_influence(-2, 1)
        game_instance.basket[Side.US].append('John_Paul_II_Elected_Pope')


class Latin_American_Death_Squads(Card):
    name = 'Latin_American_Death_Squads'
    card_index = 69
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'All of the player\'s Coup attempts in Central and South America are +1 for the remainder of the turn, while all opponent\'s Coup attempts are -1 for the remainder of the turn.'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.add_turn_effect(side, 'Latin_American_Death_Squads')


class OAS_Founded(Card):
    name = 'OAS_Founded'
    card_index = 70
    card_type = 'Event'
    stage = 'Mid War'
    ops = 1
    owner = Side.US
    event_text = 'Add 2 US Influence in Central America and/or South America.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.event_place_influence(
            Side.US, Country.increment_influence, Side.US,
            chain(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA],
                  CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA]),
            prompt='Place influence using OAS_Founded.',
            reps=2,
        )


class Nixon_Plays_The_China_Card(Card):
    name = 'Nixon_Plays_The_China_Card'
    card_index = 71
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'If US has \'The China Card\', gain 2 VP. Otherwise, US player receives \'The China Card\' now, face down and unavailable for immediate play.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        if 'The_China_Card' in game_instance.hand[Side.USSR]:
            game_instance.cards['The_China_Card'].move_china_card(
                game_instance, Side.USSR)
        elif 'The_China_Card' in game_instance.hand[Side.US]:
            game_instance.change_vp(-2)


class Sadat_Expels_Soviets(Card):
    name = 'Sadat_Expels_Soviets'
    card_index = 72
    card_type = 'Event'
    stage = 'Mid War'
    ops = 1
    owner = Side.US
    event_text = 'Remove all USSR Influence in Egypt and add one US Influence.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.map.set_influence(
            'Egypt', Side.USSR, 0)  # using alternate syntax
        game_instance.map['Egypt'].change_influence(0, 1)


class Shuttle_Diplomacy(Card):
    name = 'Shuttle_Diplomacy'
    card_index = 73
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.US
    event_text = 'Play in front of US player. During the next scoring of the Middle East or Asia (whichever comes first), subtract one Battleground country from USSR total, then put this card in the discard pile. Does not count for Final Scoring at the end of Turn 10.'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.basket[Side.US].append('Shuttle_Diplomacy')

    def dispose(self, game, side):
        if not self.event_occurred:
            super().dispose(game, side)
            return
        if self.name in game.hand[side]:
            game.hand[side].remove(self.name)
        if self.name not in game.limbo:
            game.limbo.append(self.name)
        self.event_occurred = False


class The_Voice_Of_America(Card):
    name = 'The_Voice_Of_America'
    card_index = 74
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'Remove 4 USSR Influence from non-European countries. No more than 2 may be removed from any one country.'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.event_place_influence(
            Side.US, Country.decrement_influence, Side.USSR,
            (n for n in CountryInfo.ALL
                if n not in CountryInfo.REGION_ALL[MapRegion.EUROPE]
                and game_instance.map[n].has_ussr_influence),
            prompt='Remove USSR influence using The Voice Of America.',
            reps=4,
            max_per_option=2,
        )


class Liberation_Theology(Card):
    name = 'Liberation_Theology'
    card_index = 75
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.USSR
    event_text = 'Add 3 USSR Influence in Central America, no more than 2 per country.'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.event_place_influence(
            Side.USSR, Country.increment_influence, Side.USSR,
            CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA],
            prompt='Place influence using Liberation Theology.',
            reps=3,
            max_per_option=2,
        )


class Ussuri_River_Skirmish(Card):
    name = 'Ussuri_River_Skirmish'
    card_index = 76
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.US
    event_text = 'If the USSR has \'The China Card\', claim it face up and available for play. If the US already has \'The China Card\', add 4 US Influence in Asia, no more than 2 per country.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        if 'The_China_Card' in game_instance.hand[Side.USSR]:
            game_instance.cards['The_China_Card'].move_china_card(
                game_instance, Side.USSR, made_playable=True)
        elif 'The_China_Card' in game_instance.hand[Side.US]:
            game_instance.event_place_influence(
                Side.US, Country.increment_influence, Side.US,
                CountryInfo.REGION_ALL[MapRegion.ASIA],
                prompt='Place influence using Ussuri River Skirmish.',
                reps=4,
                max_per_option=2,
            )


class Ask_Not_What_Your_Country_Can_Do_For_You(Card):
    name = 'Ask_Not_What_Your_Country_Can_Do_For_You'
    card_index = 77
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.US
    event_text = 'US player may discard up to entire hand (including Scoring cards) and draw replacements from the deck. The number of cards discarded must be decided prior to drawing any replacements.'
    event_unique = True

    def __init__(self):
        super().__init__()
        self.discarded_count = 0

    def callback(self, game_instance, option_stop_early, card_name: str):
        game_instance.input_state.reps -= 1
        if card_name != option_stop_early:
            game_instance.hand[Side.US].remove(card_name)
            game_instance.discard_pile.append(card_name)
            self.discarded_count += 1
        else:
            game_instance.input_state.reps = 0
        return True

    def draw_replacements(self, game_instance, remaining=None):
        if remaining is None:
            remaining = self.discarded_count
            self.discarded_count = 0

        while remaining > 0:
            if not game_instance.draw_pile:
                if not game_instance.discard_pile:
                    return
                game_instance.draw_pile = game_instance.discard_pile
                game_instance.discard_pile = []
                game_instance.stage_list.append(
                    partial(self.draw_replacements, game_instance, remaining))
                game_instance.shuffle_draw_pile_stage()
                return

            game_instance.hand[Side.US].append(game_instance.draw_pile.pop())
            game_instance.unknown_hand_draws[Side.US] += 1
            remaining -= 1

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        self.discarded_count = 0
        option_stop_early = 'Do not discard.'
        eligible_cards = [
            card_name for card_name in game_instance.hand[Side.US]
            if card_name not in ('The_China_Card', self.name)
        ]

        game_instance.input_state = Input(
            Side.US, InputType.SELECT_CARD,
            partial(self.callback, game_instance, option_stop_early),
            eligible_cards,
            prompt='You may discard any number of cards.',
            reps=len(eligible_cards),
            max_per_option=1,
            option_stop_early=option_stop_early,
            context={
                'source_card': self.name,
                'hand_exit': 'ask_not_target',
            },
        )
        game_instance.stage_list.append(partial(self.draw_replacements, game_instance))


class Alliance_for_Progress(Card):
    name = 'Alliance_for_Progress'
    card_index = 78
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.US
    event_text = 'US gains 1 VP for each US controlled Battleground country in Central America and South America.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        ca = list(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA])
        sa = list(CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA])
        ca.extend(sa)
        swing = sum(
            Side.US.vp_mult for n in ca if game_instance.map[n].control == Side.US and game_instance.map[n].info.battleground)
        game_instance.change_vp(swing)


class Africa_Scoring(Card):
    name = 'Africa_Scoring'
    card_index = 79
    card_type = 'Scoring'
    stage = 'Mid War'
    scoring_region = MapRegion.AFRICA
    event_text = 'Both sides score: Presence: 1, Domination: 4, Control: 6. +1 per controlled Battleground Country in Region'
    may_be_held = False

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.score(MapRegion.AFRICA)


class One_Small_Step(Card):
    name = 'One_Small_Step'
    card_index = 80
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'If you are behind on the Space Race Track, play this card to move your marker two boxes forward on the Space Rack Track, gaining the VP value of the second box only.'

    def can_event(self, game_instance, side):
        return game_instance.space_track[side] < game_instance.space_track[side.opp]

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, side):
            self.event_occurred = True
            game_instance.change_space(side, 2, score_intermediate=False)


class South_America_Scoring(Card):
    name = 'South_America_Scoring'
    card_index = 81
    card_type = 'Scoring'
    stage = 'Mid War'
    scoring_region = MapRegion.SOUTH_AMERICA
    event_text = 'Both sides score: Presence: 2, Domination: 5, Control: 6. +1 per controlled Battleground Country in Region'
    may_be_held = False

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.score(MapRegion.SOUTH_AMERICA)


class Che(Card):
    name = 'Che'
    card_index = 107
    card_type = 'Event'
    stage = 'Mid War'
    optional = True
    ops = 3
    owner = Side.USSR
    event_text = 'USSR may immediately make a Coup attempt using this card\'s Operations value against a non-battleground country in Central America, South America, or Africa. If the Coup removes any US Influence, USSR may make a second Coup attempt against a different target under the same restrictions.'

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        ca_sa_af = chain(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA],
                         CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA],
                         CountryInfo.REGION_ALL[MapRegion.AFRICA])

        game_instance.card_operation_coup(Side.USSR, 'Che', restricted_list=[
            n for n in ca_sa_af if not game_instance.map[n].info.battleground], che=True)


class Our_Man_In_Tehran(Card):
    name = 'Our_Man_In_Tehran'
    card_index = 108
    card_type = 'Event'
    stage = 'Mid War'
    optional = True
    ops = 2
    owner = Side.US
    event_text = 'If the US controls at least one Middle East country, the US player draws the top 5 cards from the draw pile. They may reveal and then discard any or all of these drawn cards without triggering the Event. Any remaining drawn cards are returned to the draw deck, and it is reshuffled.'
    event_unique = True

    def can_event(self, game_instance, side):
        return any(game_instance.map[n].control == Side.US for n in CountryInfo.REGION_ALL[MapRegion.MIDDLE_EAST])

    def stage_2(self, game_instance):
        game_instance.draw_pile.extend(game_instance.hand[Side.NEUTRAL])
        if game_instance.players[Side.US] is not None:
            game_instance.players[Side.US].update_draw_pile(
                game_instance.hand[Side.NEUTRAL])
        game_instance.hand[Side.NEUTRAL] = []
        game_instance.shuffle_draw_pile_stage()
        return True

    def stage_1(self, game_instance):
        options = list(game_instance.hand[Side.NEUTRAL])
        if not options:
            return

        stop_opt = 'Do not discard more cards.'
        game_instance.input_state = Input(
            Side.US, InputType.SELECT_CARD,
            partial(self.callback, game_instance, stop_opt),
            options,
            prompt='Our Man In Tehran: Discard any of these cards.',
            reps=len(options),
            max_per_option=1,
            option_stop_early=stop_opt,
        )

    def callback(self, game_instance, stop_opt: str, opt: str):
        if opt == stop_opt:
            # End optional discards immediately.
            game_instance.input_state.reps = 0
            game_instance.stage_list.append(partial(self.stage_2, game_instance))
            return True

        game_instance.input_state.reps -= 1
        game_instance.discard_pile.append(opt)
        if opt in game_instance.hand[Side.NEUTRAL]:
            game_instance.hand[Side.NEUTRAL].remove(opt)
        if game_instance.input_state.reps <= 0:
            game_instance.stage_list.append(partial(self.stage_2, game_instance))
        return True

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, Side.US):
            self.event_occurred = True
            next_stage = partial(self.stage_1, game_instance)
            game_instance.stage_list.append(next_stage)
            game_instance.deal(first_side=Side.NEUTRAL)
            if game_instance.stage_list[-1] is next_stage:
                game_instance.stage_list.pop()
                self.stage_1(game_instance)


# --
# -- LATE WAR
# --


class Iranian_Hostage_Crisis(Card):
    name = 'Iranian_Hostage_Crisis'
    card_index = 82
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.USSR
    event_text = 'Remove all US Influence in Iran. Add 2 USSR Influence in Iran. Doubles the effect of Terrorism card against US.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.map.set_influence('Iran', Side.US, 0)
        game_instance.map.change_influence('Iran', Side.USSR, 2)
        game_instance.basket[Side.USSR].append('Iranian_Hostage_Crisis')


class The_Iron_Lady(Card):
    name = 'The_Iron_Lady'
    card_index = 83
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.US
    event_text = 'US gains 1 VP. Add 1 USSR Influence in Argentina. Remove all USSR Influence from UK. Socialist Governments event no longer playable.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.map.change_influence('Argentina', Side.USSR, 1)
        game_instance.map.set_influence('UK', Side.USSR, 0)
        game_instance.change_vp(-1)
        if game_instance.terminated:
            return
        game_instance.basket[Side.US].append('The_Iron_Lady')


class Reagan_Bombs_Libya(Card):
    name = 'Reagan_Bombs_Libya'
    card_index = 84
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.US
    event_text = 'US gains 1 VP for every 2 USSR Influence in Libya.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        swing = math.floor(game_instance.map['Libya'].influence[Side.USSR] / 2)
        game_instance.change_vp(-swing)


class Star_Wars(Card):
    name = 'Star_Wars'
    card_index = 85
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.US
    event_text = 'If the US is ahead on the Space Race Track, play this card to search through the discard pile for a non-scoring card of your choice. Event occurs immediately.'
    event_unique = True

    def can_event(self, game_instance, side):
        return game_instance.space_track[Side.US] > game_instance.space_track[Side.USSR]

    def callback(self, game_instance, card_name: str):
        game_instance.input_state.reps -= 1
        if card_name in game_instance.discard_pile:
            game_instance.discard_pile.remove(card_name)
        if card_name not in game_instance.hand[Side.US]:
            game_instance.hand[Side.US].append(card_name)
        game_instance.cards[card_name].event_occurred = False
        game_instance.stage_list.append(partial(game_instance.cards[card_name].dispose, game_instance, Side.US))
        game_instance.stage_list.append(partial(game_instance.trigger_event, Side.US, card_name))
        return True

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, Side.US):
            self.event_occurred = True
            game_instance.input_state = Input(
                Side.US, InputType.SELECT_CARD,
                partial(self.callback, game_instance),
                (n for n in game_instance.discard_pile if game_instance.cards[n].info.card_type != 'Scoring'),
                prompt=f'Pick a non-scoring card from the discard pile for Event use immediately.',
                context={
                    'source_card': self.name,
                    'hand_exit': 'star_wars_target',
                },
            )


class North_Sea_Oil(Card):
    name = 'North_Sea_Oil'
    card_index = 86
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.US
    event_text = 'OPEC event is no longer playable. US may play 8 cards this turn.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.basket[Side.US].append('North_Sea_Oil')
        game_instance.ars_by_turn[Side.US][game_instance.turn_track] = 8


class The_Reformer(Card):
    name = 'The_Reformer'
    card_index = 87
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.USSR
    event_text = 'Add 4 Influence in Europe (no more than 2 per country). If USSR is ahead of US in VP, then 6 Influence may be added instead. USSR may no longer conduct Coup attempts in Europe. Improves effect of Glasnost event.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        reps = 6 if game_instance.vp_track > 0 else 4
        game_instance.event_place_influence(
            Side.USSR, Country.increment_influence, Side.USSR,
            CountryInfo.REGION_ALL[MapRegion.EUROPE],
            prompt=f'The Reformer: Add {reps} influence to Europe.',
            reps=reps,
            max_per_option=2,
        )
        game_instance.basket[Side.USSR].append('The_Reformer')


class Marine_Barracks_Bombing(Card):
    name = 'Marine_Barracks_Bombing'
    card_index = 88
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.USSR
    event_text = 'Remove all US Influence in Lebanon plus remove 2 additional US Influence from anywhere in the Middle East.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.map.set_influence('Lebanon', Side.US, 0)
        game_instance.event_place_influence(
            Side.USSR, Country.decrement_influence, Side.US,
            (n for n in CountryInfo.REGION_ALL[MapRegion.MIDDLE_EAST]
                if game_instance.map[n].has_us_influence),
            prompt='Remove US influence using Marine_Barracks_Bombing.',
            reps=2,
        )


class Soviets_Shoot_Down_KAL_007(Card):
    name = 'Soviets_Shoot_Down_KAL_007'
    card_index = 89
    card_type = 'Event'
    stage = 'Late War'
    ops = 4
    owner = Side.US
    event_text = 'Degrade DEFCON one level. US gains 2 VP. If South Korea is US Controlled, then the US may place Influence or attempt Realignment as if they played a 4 Ops card.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.change_defcon(-1)
        if game_instance.terminated:
            return
        game_instance.change_vp(-2)
        if game_instance.terminated:
            return
        if game_instance.map['South_Korea'].control == Side.US:
            game_instance.select_action(
                Side.US, f'Blank_4_Op_Card', can_coup=False, is_event_resolved=True)


class Glasnost(Card):
    name = 'Glasnost'
    card_index = 90
    card_type = 'Event'
    stage = 'Late War'
    ops = 4
    owner = Side.USSR
    event_text = 'USSR gains 2 VP. Improve DEFCON one level. If The Reformer is in effect, then the USSR may place Influence or attempt Realignments as if they played a 4 Ops card.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        reformer_active = 'The_Reformer' in game_instance.basket[Side.USSR]
        game_instance.change_defcon(1)
        if game_instance.terminated:
            return
        game_instance.change_vp(2)
        if game_instance.terminated:
            return
        if reformer_active:
            game_instance.safe_remove_from_basket(
                Side.USSR, 'The_Reformer')
            game_instance.select_action(
                Side.USSR, f'Blank_4_Op_Card', can_coup=False, is_event_resolved=True)


class Ortega_Elected_in_Nicaragua(Card):
    name = 'Ortega_Elected_in_Nicaragua'
    card_index = 91
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.USSR
    event_text = 'Remove all US Influence from Nicaragua. Then USSR may make one free Coup attempt (with this card\'s Operations value) in a country adjacent to Nicaragua.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.map.set_influence('Nicaragua', Side.US, 0)
        game_instance.card_operation_coup(Side.USSR, 'Ortega_Elected_in_Nicaragua', restricted_list=[
            n for n in game_instance.map['Nicaragua'].info.adjacent_countries], free=True)


class Terrorism(Card):
    name = 'Terrorism'
    card_index = 92
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'Opponent must randomly discard one card. If played by USSR and Iranian Hostage Crisis is in effect, the US player must randomly discard two cards. (Events on discards do not occur.)'

    def callback(self, game_instance, side, card_name: str):
        game_instance.input_state.reps -= 1
        game_instance.hand[side.opp].remove(card_name)
        game_instance.discard_pile.append(card_name)
        return True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        reps = 2 if 'Iranian_Hostage_Crisis' in game_instance.basket[
            Side.USSR] and side == Side.USSR else 1
        eligible_cards = [
            card_name for card_name in game_instance.hand[side.opp]
            if card_name != 'The_China_Card'
        ]
        reps = min(reps, len(eligible_cards))
        if reps <= 0:
            return

        game_instance.input_state = Input(
            Side.NEUTRAL, InputType.SELECT_CARD,
            partial(self.callback, game_instance, side),
            eligible_cards,
            prompt='Randomly discard a card.',
            reps=reps,
            reps_unit='cards to discard',
            max_per_option=1
        )


class Iran_Contra_Scandal(Card):
    name = 'Iran_Contra_Scandal'
    card_index = 93
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.USSR
    event_text = 'All US Realignment rolls have a -1 die roll modifier for the remainder of the turn.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.add_turn_effect(Side.USSR, 'Iran_Contra_Scandal')


def _chernobyl_add(game_instance, effect_name: str):
    # 用 bound-method partial（add_turn_effect 内部）而非 lambda：
    # lambda 捕获 game_instance，deepcopy 不重绑闭包，克隆上的回合结束会改写原游戏。
    game_instance.add_turn_effect(Side.US, effect_name)


class Chernobyl(Card):
    name = 'Chernobyl'
    card_index = 94
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.US
    event_text = 'The US player may designate one Region. For the remainder of the turn the USSR may not add additional Influence to that Region by the play of Operations Points via placing Influence.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        # NOTE: 回调走 partial 传 game_instance（deepcopy 安全，见
        # Olympic_Games 注释）。
        self.event_occurred = True

        option_function_mapping = {
            'Europe': partial(_chernobyl_add, game_instance, 'Chernobyl_Europe'),
            'Middle East': partial(_chernobyl_add, game_instance, 'Chernobyl_Middle_East'),
            'Asia': partial(_chernobyl_add, game_instance, 'Chernobyl_Asia'),
            'Africa': partial(_chernobyl_add, game_instance, 'Chernobyl_Africa'),
            'Central America': partial(_chernobyl_add, game_instance, 'Chernobyl_Central_America'),
            'South America': partial(_chernobyl_add, game_instance, 'Chernobyl_South_America'),
        }

        game_instance.choose_option(
            Side.US, option_function_mapping,
            'Chernobyl: Designate a single Region where USSR cannot place influence using Operations for the rest of the turn.',
        )


def _ladc_double_inf_ussr_callback(game_instance, country_name: str) -> bool:
    if not game_instance.map[country_name].has_ussr_influence:
        return False
    game_instance.input_state.reps -= 1
    game_instance.map[country_name].influence[Side.USSR] *= 2
    return True


def _ladc_did_not_discard(game_instance):
    game_instance.input_state = Input(
        Side.USSR, InputType.SELECT_COUNTRY,
        partial(_ladc_double_inf_ussr_callback, game_instance),
        (n for n in CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA]
            if game_instance.map[n].has_ussr_influence),
        prompt='Select countries to double USSR influence.',
        reps=2,
        reps_unit='countries',
        max_per_option=1
    )


class Latin_American_Debt_Crisis(Card):
    name = 'Latin_American_Debt_Crisis'
    card_index = 95
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.USSR
    event_text = 'Unless the US Player immediately discards a \'3\' or greater Operations card, double USSR Influence in two countries in South America.'

    def use_event(self, game_instance, side: Side):
        # NOTE: 回调走 partial 传 game_instance（deepcopy 安全，见
        # Olympic_Games 注释）。
        self.event_occurred = True

        eligible_discards = [
            n for n in game_instance.hand[Side.US]
            if n not in ('The_China_Card', self.name)
            and game_instance.get_global_effective_ops(
                Side.US, game_instance.cards[n].info.ops
            ) >= 3
        ]

        if not eligible_discards:
            _ladc_did_not_discard(game_instance)
            return

        game_instance.input_state = Input(
            Side.US, InputType.SELECT_CARD,
            partial(game_instance.may_discard_callback, Side.US,
                    did_not_discard_fn=partial(
                        game_instance.stage_list.append,
                        partial(_ladc_did_not_discard, game_instance))),
            eligible_discards,
            prompt='You may discard a card. If you choose not to discard, USSR chooses two countries in South America to double USSR influence.',
            option_stop_early='Do not discard.'
        )


class Tear_Down_This_Wall(Card):
    name = 'Tear_Down_This_Wall'
    card_index = 96
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.US
    event_text = 'Cancels/prevent Willy Brandt. Add 3 US Influence in East Germany. Then US may make a free Coup attempt or Realignment rolls in Europe using this card\'s Ops Value.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        if 'Willy_Brandt' in game_instance.basket[Side.USSR]:
            game_instance.basket[Side.USSR].remove('Willy_Brandt')
        game_instance.map['East_Germany'].change_influence(0, 3)

        def coup(game_instance):
            game_instance.card_operation_coup(Side.US, 'Tear_Down_This_Wall', restricted_list=list(
                CountryInfo.REGION_ALL[MapRegion.EUROPE]), free=True,
                ignore_defcon=True)

        def realignment(game_instance):
            game_instance.card_operation_realignment(Side.US, 'Tear_Down_This_Wall', restricted_list=list(
                CountryInfo.REGION_ALL[MapRegion.EUROPE]), free=True,
                ignore_defcon=True)

        option_function_mapping = {
            'Free coup attempt': partial(coup, game_instance),
            'Free realignment rolls': partial(realignment, game_instance),
            'Do not conduct free operations.': lambda: None,
        }

        game_instance.choose_option(
            Side.US, option_function_mapping,
            'Tear Down This Wall: US player may make free Coup attempts or realignment rolls in Europe.',
        )


class An_Evil_Empire(Card):
    name = 'An_Evil_Empire'
    card_index = 97
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.US
    event_text = 'Cancels/Prevents Flower Power. US gains 1 VP.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.change_vp(-1)
        if game_instance.terminated:
            return
        if 'Flower_Power' in game_instance.basket[Side.USSR]:
            game_instance.basket[Side.USSR].remove('Flower_Power')
        game_instance.basket[Side.US].append('An_Evil_Empire')


class Aldrich_Ames_Remix(Card):
    name = 'Aldrich_Ames_Remix'
    card_index = 98
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.USSR
    event_text = 'US player exposes his hand to USSR player for remainder of turn. USSR then chooses one card from US hand, this card is discarded.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.basket[Side.USSR].append(self.name)
        game_instance.end_turn_stage_list.append(
            partial(game_instance.safe_remove_from_basket, Side.USSR, self.name))
        if game_instance.players[Side.USSR] is not None:
            view = game_instance.players[Side.USSR]
            view.update_opp_hand(game_instance.hand[Side.US])
            if hasattr(view, 'stamp_opp_hand_observation'):
                view.stamp_opp_hand_observation(game_instance.shuffle_count)
        eligible_cards = [
            card_name for card_name in game_instance.hand[Side.US]
            if card_name not in ('The_China_Card', self.name)
        ]
        if not eligible_cards:
            return
        game_instance.input_state = Input(
            Side.USSR, InputType.SELECT_CARD,
            partial(game_instance.may_discard_callback, Side.US),
            eligible_cards,
            prompt='Choose a card to discard from the US hand.'
        )


class Pershing_II_Deployed(Card):
    name = 'Pershing_II_Deployed'
    card_index = 99
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.USSR
    event_text = 'USSR gains 1 VP. Remove 1 US Influence from up to three countries in Western Europe.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.change_vp(1)
        if game_instance.terminated:
            return
        game_instance.event_place_influence(
            Side.USSR, Country.decrement_influence, Side.US,
            (n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]
                if game_instance.map[n].has_us_influence),
            prompt='Pershing II Deployed: Remove 1 US influence from any 3 countries in Western Europe.',
            reps=3,
            max_per_option=1,
            option_stop_early='Do not remove more influence.',
        )


class Wargames(Card):
    name = 'Wargames'
    card_index = 100
    card_type = 'Event'
    stage = 'Late War'
    ops = 4
    owner = Side.NEUTRAL
    event_text = 'If DEFCON Status 2, you may immediately end the game (without Final Scoring Phase) after giving opponent 6 VPs. How about a nice game of chess?'
    event_unique = True
    END_GAME = 'End the game after giving opponent 6 VP.'
    CONTINUE = 'Continue playing.'

    def can_event(self, game_instance, side):
        return game_instance.defcon_track == 2

    @staticmethod
    def end_game(game_instance, side: Side):
        vp_before = game_instance.vp_track
        game_instance.vp_track += 6 * side.opp.vp_mult
        print(f'Current VP: {game_instance.vp_track}')
        game_instance.terminate(
            reason='wargames',
            context={
                'player': side.toStr(),
                'vp_before': vp_before,
                'vp_after': game_instance.vp_track,
            },
        )

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, side):
            self.event_occurred = True
            game_instance.choose_option(
                side,
                {
                    self.END_GAME: partial(
                        self.end_game, game_instance, side),
                    self.CONTINUE: lambda: None,
                },
                'Wargames: End the game after giving the opponent 6 VP?',
            )


class Solidarity(Card):
    name = 'Solidarity'
    card_index = 101
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.US
    event_text = 'Playable as an event only if John Paul II Elected Pope is in effect. Add 3 US Influence in Poland.'
    event_unique = True

    def can_event(self, game_instance, side):
        return 'John_Paul_II_Elected_Pope' in game_instance.basket[Side.US]

    def use_event(self, game_instance, side: Side):
        if self.can_event(game_instance, Side.US):
            self.event_occurred = True
            game_instance.map['Poland'].change_influence(0, 3)
            game_instance.basket[Side.US].remove('John_Paul_II_Elected_Pope')


class Iran_Iraq_War(WarCard):
    name = 'Iran_Iraq_War'
    card_index = 102
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'Iran or Iraq invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to target of invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track Effects of Victory: Player gains 2 VP and replaces opponent\'s Influence in target country with his own.'
    event_unique = True
    war_country_options = ['Iran', 'Iraq']
    war_prompt = 'Iran/Iraq War: Choose target of war.'


class Yuri_and_Samantha(Card):
    name = 'Yuri_and_Samantha'
    card_index = 109
    card_type = 'Event'
    stage = 'Late War'
    optional = True
    ops = 2
    owner = Side.USSR
    event_text = 'USSR receives 1 VP for each US coup attempt made for the remainder of the current turn.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.add_turn_effect(Side.USSR, 'Yuri_and_Samantha')


class AWACS_Sale_to_Saudis(Card):
    name = 'AWACS_Sale_to_Saudis'
    card_index = 110
    card_type = 'Event'
    stage = 'Late War'
    optional = True
    ops = 3
    owner = Side.US
    event_text = 'US receives 2 Influence in Saudi Arabia. Muslim Revolution may no longer be played as an event.'
    event_unique = True

    def use_event(self, game_instance, side: Side):
        self.event_occurred = True
        game_instance.map.change_influence('Saudi_Arabia', Side.US, 2)
        game_instance.basket[Side.US].append('AWACS_Sale_to_Saudis')


class Blank_1_Op_Card(Card):
    name = 'Blank_1_Op_Card'
    card_index = 150
    card_type = 'Template'
    stage = 'Template'
    optional = False
    ops = 1
    owner = Side.NEUTRAL
    event_text = 'This is a blank card worth 1 operations points.'
    event_unique = False

    def dispose(self, game, side):
        pass

    def can_event(self, game_instance, side):
        return False


class Blank_2_Op_Card(Card):
    name = 'Blank_2_Op_Card'
    card_index = 151
    card_type = 'Template'
    stage = 'Template'
    optional = False
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'This is a blank card worth 2 operations points.'
    event_unique = False

    def dispose(self, game, side):
        pass

    def can_event(self, game_instance, side):
        return False


class Blank_3_Op_Card(Card):
    name = 'Blank_3_Op_Card'
    card_index = 152
    card_type = 'Template'
    stage = 'Template'
    optional = False
    ops = 3
    owner = Side.NEUTRAL
    event_text = 'This is a blank card worth 3 operations points.'
    event_unique = False

    def dispose(self, game, side):
        pass

    def can_event(self, game_instance, side):
        return False


class Blank_4_Op_Card(Card):
    name = 'Blank_4_Op_Card'
    card_index = 153
    card_type = 'Template'
    stage = 'Template'
    optional = False
    ops = 4
    owner = Side.NEUTRAL
    event_text = 'This is a blank card worth 4 operations points.'
    event_unique = False

    def dispose(self, game, side):
        pass

    def can_event(self, game_instance, side):
        return False


# 区域 → 计分卡名。从 Card.scoring_region 派生（单一事实源）——此前
# official_ai 与 train_ppo 各自维护一份逐字相同的表，改卡名会三处漂移。
# 必须在所有卡类注册完成后定义，故置于模块末尾。
SCORING_CARD_BY_REGION = {
    card_cls.scoring_region: card_name
    for card_name, card_cls in Card.ALL.items()
    if isinstance(card_cls.scoring_region, MapRegion)
}


# 全部已注册卡名（防拼错卡名静默失效：basket/limbo 引用必须是合法卡名，
# tests/test_card_name_tokens.py 做源码级扫描校验）。
CARD_NAMES = frozenset(Card.ALL)
