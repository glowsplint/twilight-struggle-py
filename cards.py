import math

from typing import Callable, Optional, Iterable, Tuple
from functools import partial
from itertools import chain

from interfacing import Input
from world_map import CountryInfo, Country
from enums import Side, MapRegion, InputType, CardAction, CoupEffects, RealignState
from effects import Effect


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

    def use_event(self, game, side: Side):
        self.event_occurred = True

    def can_event(self, game, side: Side):
        return True if self.owner != side.opp else False

    def dispose(self, game, side: Side):
        game.hand[side].remove(self.name)
        if self.event_occurred and self.event_unique:
            game.removed_pile.append(self.name)
        else:
            game.discard_pile.append(self.name)
            self.event_occurred = False
        if self.info.name in game.players[side.opp].opp_hand.info.values():
            game.players[side.opp].opp_hand.remove([self.name])

    def available_actions(self, game, side):
        pass

    def use_space(self, side):
        pass

    def use_ops_influence(self, game, side):
        eff_ops = game.get_global_effective_ops(side, self.ops)
        game.operations_influence(side, eff_ops)

    def use_ops_coup(self, game, side):
        eff_ops = game.get_global_effective_ops(side, self.ops)
        game.coup_country_stage(side, eff_ops)

    def use_ops_realignment(self, game, side):
        eff_ops = game.get_global_effective_ops(side, self.ops)
        game.operations_realign(side, eff_ops)


class GameCards:

    # used for global tracking (cf. playerview)
    early_war = []
    mid_war = []
    late_war = []

    for card_name, CardClass in Card.ALL.items():
        if CardClass.stage == 'Early War':
            early_war.append(card_name)
        if CardClass.stage == 'Mid War':
            mid_war.append(card_name)
        if CardClass.stage == 'Late War':
            late_war.append(card_name)

    def __init__(self):

        self.ALL = dict()
        self.early_war = []
        self.mid_war = []
        self.late_war = []
        self.in_play = set()

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

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.score(MapRegion.ASIA)
        if 'Shuttle_Diplomacy' in game.limbo:
            game.discard_pile.append('Shuttle_Diplomacy')
            game.limbo.clear()


class Europe_Scoring(Card):
    name = 'Europe_Scoring'
    card_index = 2
    card_type = 'Scoring'
    stage = 'Early War'
    scoring_region = MapRegion.EUROPE
    event_text = 'Both sides score: Presence: 3, Domination: 7, Control: VICTORY. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
    may_be_held = False

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.score(MapRegion.EUROPE)


class Middle_East_Scoring(Card):
    name = 'Middle_East_Scoring'
    card_index = 3
    card_type = 'Scoring'
    stage = 'Early War'
    scoring_region = MapRegion.MIDDLE_EAST
    event_text = 'Both sides score: Presence: 3, Domination: 5, Control: 7. +1 per controlled Battleground Country in Region'
    may_be_held = False

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.score(MapRegion.MIDDLE_EAST)
        if 'Shuttle_Diplomacy' in game.limbo:
            game.discard_pile.append('Shuttle_Diplomacy')
            game.limbo.clear()


class Duck_and_Cover(Card):
    name = 'Duck_and_Cover'
    card_index = 4
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.US
    event_text = 'Degrade DEFCON one level. Then US player earns VPs equal to 5 minus current DEFCON level.'

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.change_defcon(-1)
        game.change_vp(-(5 - game.defcon_track))


class Five_Year_Plan(Card):
    name = 'Five_Year_Plan'
    card_index = 5
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.US
    event_text = 'USSR player must randomly discard one card. If the card is a US associated Event, the Event occurs immediately. If the card is a USSR associated Event or and Event applicable to both players, then the card must be discarded without triggering the Event.'

    def callback(self, game, card_name: str):
        game.input_state.reps -= 1
        print(f'{card_name} was selected by Five_Year_Plan.')
        if game.cards[card_name].info.owner == Side.US:
            # must append backwards!
            game.stage_list.append(
                partial(game.cards[card_name].dispose, game, Side.USSR))
            game.stage_list.append(
                partial(game.trigger_event, Side.USSR, card_name))
        else:
            game.stage_list.append(
                partial(game.cards[card_name].dispose, game, Side.USSR))
        return True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        # check that USSR player has enough cards
        reps = len(game.hand[Side.USSR]) if len(
            game.hand[Side.USSR]) <= 1 else 1

        game.input_state = Input(
            Side.NEUTRAL, InputType.SELECT_CARD,
            partial(self.callback, game),
            (n for n in game.hand[Side.USSR]
             if not (n == 'Five_Year_Plan' or n == 'The_China_Card')),
            prompt='Five Year Plan: USSR randomly discards a card.',
            reps=reps
        )


class The_China_Card(Card, Effect):
    name = 'The_China_Card'
    card_index = 6
    card_type = 'Event'
    stage = 'Early War'
    ops = 4
    owner = Side.NEUTRAL
    can_headline = False
    event_text = 'Begins the game with the USSR player. +1 Operations value when all points are used in Asia. Pass to opponent after play. +1 VP for the player holding this card at the end of Turn 10. Cancels effect of \'Formosan Resolution\' if this card is played by the US player.'
    _region = list(CountryInfo.REGION_ALL[MapRegion.ASIA])

    def __init__(self):
        super().__init__()
        self.realign_bonus_given = False
        self.opsinf_bonus_lost = False

    def use_ops_influence(self, game, side):
        game.basket[side].append(self.name)
        self.opsinf_bonus_lost = False
        super().use_ops_influence(game, side)

    def use_ops_realignment(self, game, side):
        game.basket[side].append(self.name)
        self.realign_bonus_given = False
        super().use_ops_realignment(game, side)

    def use_ops_coup(self, game, side):
        game.basket[side].append(self.name)
        super().use_ops_coup(game, side)

    def effect_opsinf_region_ops(self, game, effect_side, ops_side):
        return MapRegion.ASIA, 1

    def effect_opsinf_country_select(self, game, effect_side, ops_side, country_name):
        if (not self.opsinf_bonus_lost
                and country_name not in CountryInfo.REGION_ALL[MapRegion.ASIA]):
            self.opsinf_bonus_lost = True
            return MapRegion.ASIA, -1

    def effect_opsinf_after(self, game, effect_side, ops_side):
        game.basket[effect_side].remove(self.name)

    def effect_realign_country_restrict(self, game, side):
        if self.realign_bonus_given:
            return set(CountryInfo.ALL) - CountryInfo.REGION_ALL[MapRegion.ASIA]

    def effect_realign_ops(self, game, effect_side, country_name):
        if (not self.realign_bonus_given
                and not game.realign_state.reps
                and all(c in CountryInfo.REGION_ALL[MapRegion.ASIA]
                        for c in game.realign_state.countries)):
            self.realign_bonus_given = True
            return RealignState(reps=1)

    def effect_realign_after(self, game, effect_side):
        self.realign_bonus_given = False
        game.basket[game.realign_state.side].remove(self.name)

    def effect_coup_ops(self, game, effect_side, coup_side, country_name):
        if country_name in CountryInfo.REGION_ALL[MapRegion.ASIA]:
            return 1

    def effect_coup_after(self, game, effect_side, coup_side, country_name, result):
        game.basket[coup_side].remove(self.name)

    def can_event(self, game, side):
        return False

    def move(self, game, side: Side, made_playable=False):
        '''
        Moves and flips the China Card after it has been used.
        Side refers to the player that uses the China card, or whoever the card should move from.
        '''
        game.hand[side.opp].append('The_China_Card')
        game.hand[side].remove('The_China_Card')
        game.players[side].opp_hand.update(['The_China_Card'])
        game.players[side.opp].opp_hand.remove(['The_China_Card'])
        self.is_playable = made_playable

    def dispose(self, game, side):
        self.move(game, side)


class Socialist_Governments(Card):
    name = 'Socialist_Governments'
    card_index = 7
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.USSR
    event_text = 'Unplayable as an event if \'The Iron Lady\' is in effect. Remove US Influence in Western Europe by a total of 3 Influence points, removing no more than 2 per country.'

    def can_event(self, game, side):
        return The_Iron_Lady.name not in game.basket[Side.US]

    def use_event(self, game, side: Side):
        if self.can_event(game, Side.USSR):
            self.event_occurred = True
            game.input_state = Input(
                Side.USSR, InputType.SELECT_COUNTRY,
                partial(game.event_influence_callback,
                        Country.decrement_influence, Side.US),
                (n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]
                    if game.map[n].has_us_influence),
                prompt='Socialist Governments: Remove a total of 3 US Influence from any countries in Western Europe (limit 2 per country)',
                reps=3,
                reps_unit='influence',
                max_per_option=2
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

    def use_event(self, game, side: Side):
        self.event_occurred = True
        cuba = game.map['Cuba']
        cuba.set_influence(max(3, cuba.influence[Side.USSR]), 0)


class Vietnam_Revolts(Card, Effect):
    name = 'Vietnam_Revolts'
    card_index = 9
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.USSR
    event_text = 'Add 2 USSR Influence in Vietnam. For the remainder of the turn, the Soviet player may add 1 Operations point to any card that uses all points in Southeast Asia.'
    event_unique = True
    _region = list(CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA])

    def __init__(self):
        super().__init__()
        self.realign_bonus_given = False
        self.opsinf_bonus_lost = False

    def effect_end_turn(self, game, effect_side):
        game.basket[self.owner].remove(self.name)

    def effect_opsinf_region_ops(self, game, effect_side, ops_side):
        '''
        By default, the Southeast Asia bonus is included.
        '''

        if ops_side == Side.USSR:
            self.opsinf_bonus_list = False
            return MapRegion.SOUTHEAST_ASIA, 1

    def effect_opsinf_country_select(self, game, effect_side, ops_side, country_name):
        '''
        Check if the bonus should be removed every time the player selects a country for ops.
        '''
        if (ops_side == Side.USSR and
                not self.opsinf_bonus_lost
                and country_name not in CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]):
            self.opsinf_bonus_lost = True
            return MapRegion.SOUTHEAST_ASIA, -1

    def effect_realign_country_restrict(self, game, side):
        if self.realign_bonus_given:
            return set(CountryInfo.ALL) - CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]

    def effect_realign_ops(self, game, effect_side, country_name):
        if (game.realign_state.side == Side.USSR
                and not self.realign_bonus_given  # haven't gotten the bonus
                and not game.realign_state.reps  # finished all the other stuff
                and all(c in CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]
                        for c in game.realign_state.countries)  # all in SEA
                and (The_China_Card.name not in game.basket[game.realign_state.side]  # China not active
                     or game.cards[The_China_Card.name].realign_bonus_given)  # or China bonus is done
            ):
            self.realign_bonus_given = True
            return RealignState(reps=1)

    def effect_realign_after(self, game, effect_side):
        self.realign_bonus_given = False

    def effect_coup_ops(self, game, effect_side, coup_side, country_name):
        if (coup_side == Side.USSR
                and country_name in CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]):
            return 1

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.map.change_influence('Vietnam', Side.USSR, 2)
        game.basket[self.owner].append(self.name)


class Blockade(Card):
    name = 'Blockade'
    card_index = 10
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.USSR
    event_text = 'Unless US Player immediately discards a \'3\' or more value Operations card, eliminate all US Influence in West Germany.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.input_state = Input(
            Side.US, InputType.SELECT_CARD,
            partial(game.may_discard_callback, Side.US,
                    did_not_discard_fn=partial(game.map['West_Germany'].remove_influence, Side.US)),
            (n for n in game.hand[Side.US]
                if n != 'The_China_Card'
                and game.get_global_effective_ops(side, game.cards[n].info.ops) >= 3),
            prompt='You may discard a card. If you choose not to discard a card, US loses all influence in West Germany.',
            option_stop_early='Do not discard.'
        )


class Korean_War(Card):
    name = 'Korean_War'
    card_index = 11
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.USSR
    event_text = 'North Korea invades South Korea. Roll one die and subtract 1 for every US Controlled country adjacent to South Korea. USSR Victory on modified die roll 4-6. USSR add 2 to Military Ops Track. Effects of Victory: USSR gains 2 VP and replaces all US Influence in South Korea with USSR Influence.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.war('South_Korea', Side.USSR)


class Romanian_Abdication(Card):
    name = 'Romanian_Abdication'
    card_index = 12
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.USSR
    event_text = 'Remove all US Influence in Romania. USSR gains sufficient Influence in Romania for Control.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        romania = game.map['Romania']
        romania.set_influence(max(3, romania.influence[Side.USSR]), 0)


class Arab_Israeli_War(Card):
    name = 'Arab_Israeli_War'
    card_index = 13
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.USSR
    event_text = 'A Pan-Arab Coalition invades Israel. Roll one die and subtract 1 for US Control of Israel and for US-controlled country adjacent to Israel. USSR Victory on modified die roll 4-6. USSR adds 2 to Military Ops Track. Effects of Victory: USSR gains 2 VP and replaces all US Influence in Israel with USSR Influence.'

    def can_event(self, game, side):
        return 'Camp_David_Accords' not in game.basket[Side.US]

    def use_event(self, game, side: Side):
        if self.can_event(game, Side.USSR):
            self.event_occurred = True
            game.war('Israel', Side.USSR, country_itself=True)


class COMECON(Card):
    name = 'COMECON'
    card_index = 14
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.USSR
    event_text = 'Add 1 USSR Influence in each of four non-US Controlled countries in Eastern Europe.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.input_state = Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            (n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]
                if game.map[n].control != Side.US),
            prompt='COMECON: Add 1 influence to each of 4 non-US controlled countries of Eastern Europe.',
            reps=4,
            reps_unit='influence',
            max_per_option=1
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

    def use_event(self, game, side: Side):
        self.event_occurred = True
        egypt = game.map['Egypt']
        egypt.change_influence(2, -math.ceil(egypt.influence[Side.US] / 2))


class Warsaw_Pact_Formed(Card, Effect):
    name = 'Warsaw_Pact_Formed'
    card_index = 16
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.USSR
    event_text = 'Remove all US Influence from four countries in Eastern Europe, or add 5 USSR Influence in Eastern Europe, adding no more than 2 per country. Allows play of NATO.'
    event_unique = True

    def event_remove_stage(self, game):
        game.input_state = Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.remove_influence, Side.US),
            (n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]
                if game.map[n].has_influence(Side.US)),
            prompt='Warsaw Pact Formed: Remove all US influence from 4 countries in Eastern Europe.',
            reps=4,
            reps_unit='influence',
            max_per_option=1
        )

    def event_add_stage(self, game):
        game.input_state = Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE],
            prompt='Warsaw Pact Formed: Add 5 USSR Influence to countries in Eastern Europe.',
            reps=5,
            reps_unit='influence',
            max_per_option=2
        )

    def use_event(self, game, side):
        self.event_occurred = True
        game.basket[Side.US].append('Warsaw_Pact_Formed')
        option_function_mapping = {
            'Remove all US influence from 4 countries in Eastern Europe':
                partial(game.stage_list.append, partial(
                    self.event_remove_stage, game)),
            'Add 5 USSR Influence to countries in Eastern Europe':
                partial(game.stage_list.append, partial(
                    self.event_add_stage, game))
        }

        game.input_state = Input(
            Side.USSR, InputType.SELECT_MULTIPLE,
            partial(game.select_multiple_callback,
                    option_function_mapping),
            option_function_mapping.keys(),
            prompt='Warsaw Pact: Choose between two options.'
        )


class De_Gaulle_Leads_France(Card, Effect):
    name = 'De_Gaulle_Leads_France'
    card_index = 17
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.USSR
    event_text = 'Remove 2 US Influence in France, add 1 USSR Influence. Cancels effects of NATO for France.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.map['France'].change_influence(1, -2)
        game.basket[Side.USSR].append('De_Gaulle_Leads_France')


class Captured_Nazi_Scientist(Card):
    name = 'Captured_Nazi_Scientist'
    card_index = 18
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.NEUTRAL
    event_text = 'Advance player\'s Space Race marker one box.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.change_space(side, 1)


class Truman_Doctrine(Card):
    name = 'Truman_Doctrine'
    card_index = 19
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.US
    event_text = 'Remove all USSR Influence markers in one uncontrolled country in Europe.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.input_state = Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.remove_influence, Side.USSR),
            (n for n in CountryInfo.REGION_ALL[MapRegion.EUROPE]
                if game.map[n].control == Side.NEUTRAL
             and game.map[n].has_ussr_influence),
            prompt='Truman Doctrine: Select a country in which to remove all USSR influence.'
        )


class Olympic_Games(Card):
    name = 'Olympic_Games'
    card_index = 20
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'Player sponsors Olympics. Opponent may participate or boycott. If Opponent participates, each player rolls one die, with the sponsor adding 2 to his roll. High roll gains 2 VP. Reroll ties. If opponent boycotts, degrade DEFCON one level and the Sponsor may Conduct Operations as if they played a 4 Ops card.'

    def event_participate_dice_callback(self, game, side, rolls):
        game.input_state.reps -= 1
        if rolls[0] > rolls[1]:  # sponsor wins
            game.change_vp(2 * side.vp_mult)
        else:
            game.change_vp(2 * side.opp.vp_mult)

    def event_participate_stage(self, game, side):
        game.input_state = Input(
            Side.NEUTRAL, InputType.ROLL_DICE,
            partial(self.event_participate_dice_callback, game, side),
            ((i+2, j) for i in range(1, 7) for j in range(1, 7) if i+2 != j),
            prompt='2d6 roll (Sponsor roll, Participant roll), no ties'
        )

    def event_boycott(self, game, side):
        game.change_defcon(-1)
        game.select_action(
            side, 'Blank_4_Op_Card', is_event_resolved=True)

    def use_event(self, game, side: Side):
        self.event_occurred = True

        option_function_mapping = {
            'Participate: Sponsor has +2 die roll.': partial(game.stage_list.append, partial(self.event_participate_stage, game, side)),
            'Boycott: DEFCON level degrades by 1. Sponsor may conduct operations as if they played a 4 op card.': partial(game.stage_list.append, partial(self.event_boycott, game, side))
        }

        game.input_state = Input(
            side.opp, InputType.SELECT_MULTIPLE,
            partial(game.select_multiple_callback,
                    option_function_mapping),
            option_function_mapping.keys(),
            prompt='Olympic Games: Choose between two options.'
        )


class NATO(Card, Effect):
    name = 'NATO'
    card_index = 21
    card_type = 'Event'
    stage = 'Early War'
    ops = 4
    owner = Side.US
    event_text = 'Play after \'Marshall Plan\' or \'Warsaw Pact\'. USSR player may no longer make Coup or Realignment rolls in any US Controlled countries in Europe. US Controlled countries in Europe may not be attacked by play of the Brush War event.'
    event_unique = True

    def can_event(self, game, side):
        return Warsaw_Pact_Formed.name in game.basket[Side.US] \
            or Marshall_Plan.name in game.basket[Side.US]

    def use_event(self, game, side: Side):
        if self.can_event(game, Side.US):
            self.event_occurred = True
            game.basket[self.owner].append(self.name)

    def effect_countries(self, game):
        cancelled = set()
        if Willy_Brandt.name in game.basket[Side.USSR]:
            cancelled.add('West_Germany')
        if De_Gaulle_Leads_France.name in game.basket[Side.USSR]:
            cancelled.add('France')
        return (c for c in CountryInfo.REGION_ALL[MapRegion.EUROPE]
                if game.map[c].control == Side.US
                and c not in cancelled)

    def effect_realign_country_restrict(self, game, side):
        if side == Side.USSR:
            return self.effect_countries(game)

    def effect_coup_country_restrict(self, game, side):
        if side == Side.USSR:
            return self.effect_countries(game)


class Independent_Reds(Card):
    name = 'Independent_Reds'
    card_index = 22
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.US
    event_text = 'Adds sufficient US Influence in either Yugoslavia, Romania, Bulgaria, Hungary, or Czechoslavakia to equal USSR Influence.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        ireds = ['Yugoslavia', 'Romania',
                 'Bulgaria', 'Hungary', 'Czechoslovakia']
        game.input_state = Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.match_influence, Side.US),
            (n for n in ireds if game.map[n].has_ussr_influence),
            prompt='Independent Reds: You may add influence in 1 of these countries to equal USSR influence.'
        )


class Marshall_Plan(Card, Effect):
    name = 'Marshall_Plan'
    card_index = 23
    card_type = 'Event'
    stage = 'Early War'
    ops = 4
    owner = Side.US
    event_text = 'Allows play of NATO. Add one US Influence in each of seven non-USSR Controlled Western European countries.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[Side.US].append('Marshall_Plan')
        game.input_state = Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.increment_influence, Side.US),
            (n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]
                if game.map[n].control != Side.USSR),
            prompt='Marshall Plan: Place influence in 7 non-USSR controlled countries.',
            reps=7,
            reps_unit='influence',
            max_per_option=1
        )


class Indo_Pakistani_War(Card):
    name = 'Indo_Pakistani_War'
    card_index = 24
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'India or Pakistan invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to the target of the invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track. Effects of Victory: Player gains 2 VP and replaces all opponent\'s Influence in target country with his Influence.'

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.input_state = Input(
            side, InputType.SELECT_COUNTRY,
            partial(game.war_country_callback, side),
            ['India', 'Pakistan'],
            prompt='Indo-Pakistani War: Choose target country.'
        )


class Containment(Card, Effect):
    name = 'Containment'
    card_index = 25
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.US
    event_text = 'All further Operations cards played by US this turn add one to their value (to a maximum of 4).'
    event_unique = True

    def effect_end_turn(self, game, effect_side):
        game.basket[self.owner].remove(self.name)

    def effect_global_ops(self, game, effect_side, ops_side):
        if ops_side == self.owner:
            return 1

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[self.owner].append(self.name)


class CIA_Created(Card):
    name = 'CIA_Created'
    card_index = 26
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.US
    event_text = 'USSR reveals hand this turn. Then the US may Conduct Operations as if they played a 1 Op card.'
    event_unique = True

    def use_event(self, game, side: Side):
        game.players[Side.US].opp_hand.update(
            game.hand[Side.USSR])
        self.event_occurred = True
        game.select_action(
            Side.US, f'Blank_1_Op_Card', is_event_resolved=True)


class US_Japan_Mutual_Defense_Pact(Card, Effect):
    name = 'US_Japan_Mutual_Defense_Pact'
    card_index = 27
    card_type = 'Event'
    stage = 'Early War'
    ops = 4
    owner = Side.US
    event_text = 'US gains sufficient Influence in Japan for Control. USSR may no longer make Coup or Realignment rolls in Japan.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        japan = game.map['Japan']
        japan.set_influence(japan.influence[Side.USSR], max(
            japan.influence[Side.USSR] + 4, japan.influence[Side.US]))
        game.basket[self.owner].append(self.name)

    def effect_realign_country_restrict(self, game, side):
        if side == Side.USSR:
            return ['Japan']

    def effect_coup_country_restrict(self, game, side):
        if side == Side.USSR:
            return ['Japan']


class Suez_Crisis(Card):
    name = 'Suez_Crisis'
    card_index = 28
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.USSR
    event_text = 'Remove a total of 4 US Influence from France, the United Kingdom or Israel. Remove no more than 2 Influence per country.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        suez = ['France', 'UK', 'Israel']

        game.input_state = Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.decrement_influence, Side.US),
            (n for n in suez if game.map[n].has_us_influence),
            prompt='Remove US influence using Suez Crisis.',
            reps=4,
            reps_unit='influence',
            max_per_option=2
        )


class East_European_Unrest(Card):
    name = 'East_European_Unrest'
    card_index = 29
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.US
    event_text = 'In Early or Mid War: Remove 1 USSR Influence from three countries in Eastern Europe. In Late War: Remove 2 USSR Influence from three countries in Eastern Europe.'

    def use_event(self, game, side: Side):
        self.event_occurred = True
        dec = 2 if 8 <= game.turn_track <= 10 else 1

        game.input_state = Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback, partial(
                Country.decrement_influence, amt=dec), Side.USSR),
            (n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]
                if game.map[n].has_ussr_influence),
            prompt='Remove USSR influence using East European Unrest.',
            reps=3,
            reps_unit='influence',
            max_per_option=1
        )


class Decolonization(Card):
    name = 'Decolonization'
    card_index = 30
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.USSR
    event_text = 'Add one USSR Influence in each of any four African and/or SE Asian countries.'

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.input_state = Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            chain(CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA],
                  CountryInfo.REGION_ALL[MapRegion.AFRICA]),
            prompt='Place influence using Decolonization.',
            reps=4,
            reps_unit='influence',
            max_per_option=1
        )


class Red_Scare_Purge(Card, Effect):
    name = 'Red_Scare_Purge'
    card_index = 31
    card_type = 'Event'
    stage = 'Early War'
    ops = 4
    owner = Side.NEUTRAL
    event_text = 'All further Operations cards played by your opponent this turn are -1 to their value (to a minimum of 1 Op).'

    def effect_end_turn(self, game, effect_side):
        game.basket[effect_side].remove(self.name)

    def effect_global_ops(self, game, effect_side, ops_side):
        if ops_side == effect_side.opp:
            return -1

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[side].append(self.name)


class UN_Intervention(Card):
    name = 'UN_Intervention'
    card_index = 32
    card_type = 'Event'
    stage = 'Early War'
    ops = 1
    owner = Side.NEUTRAL
    can_headline = False
    event_text = 'Play this card simultaneously with a card containing your opponent\'s associated Event. The Event is cancelled, but you may use its Operations value to Conduct Operations. The cancelled event returns to the discard pile. May not be played during headline phase.'

    def can_event(self, game, side):
        return any((game.cards[c].info.owner == side.opp for c in game.hand[side]))

    def callback(self, game, side, card_name: str):
        game.input_state.reps -= 1
        game.select_action(side, f'{card_name}', un_intervention=True)
        return True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.input_state = Input(
            side, InputType.SELECT_CARD,
            partial(self.callback, game, side),
            (n for n in game.hand[side]
             if game.cards[n].info.owner == side.opp),
            prompt=f'You may pick a opponent-owned card from your hand to use with UN Intervention.',
        )


class De_Stalinization(Card):
    name = 'De_Stalinization'
    card_index = 33
    card_type = 'Event'
    stage = 'Early War'
    ops = 3
    owner = Side.USSR
    event_text = 'USSR may relocate up to 4 Influence points to non-US controlled countries. No more than 2 Influence may be placed in the same country.'
    event_unique = True

    def __init__(self):
        super().__init__()
        self.ops_removed = 0

    def event_add_stage(self, game):
        game.input_state = Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            (n for n in CountryInfo.ALL
                if game.map[n].control != Side.US
                and not game.map[n].info.superpower),
            prompt=f'Add {self.ops_removed} influence using De-Stalinization.',
            reps=self.ops_removed,
            reps_unit='influence',
            max_per_option=2
        )

    def event_remove_callback(self, game, side, country_name):
        if country_name == game.input_state.option_stop_early:
            game.input_state.reps = 0
        else:
            self.ops_removed += 1
            game.event_influence_callback(
                Country.decrement_influence, Side.USSR, country_name)

        return True

    def use_event(self, game, side: Side):

        self.event_occurred = True
        self.ops_removed = 0

        game.input_state = Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(self.event_remove_callback, game, side),
            (n for n in CountryInfo.ALL
                if game.map[n].has_influence(Side.USSR)
                and not game.map[n].info.superpower),
            prompt='Remove up to 4 influence using De-Stalinization.',
            reps=4,
            reps_unit='influence',
            option_stop_early='Stop removing influence and proceed to relocate influence.'
        )
        game.stage_list.append(partial(self.event_add_stage, game))


class Nuclear_Test_Ban(Card):
    name = 'Nuclear_Test_Ban'
    card_index = 34
    card_type = 'Event'
    stage = 'Early War'
    ops = 4
    owner = Side.NEUTRAL
    event_text = 'Player earns VPs equal to the current DEFCON level minus 2, then improve DEFCON two levels.'

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.change_vp(
            (game.defcon_track - 2) * side.vp_mult)
        game.change_defcon(2)


class Formosan_Resolution(Card, Effect):
    name = 'Formosan_Resolution'
    card_index = 35
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.US
    event_text = 'Taiwan shall be treated as a Battleground country for scoring purposes, if the US controls Taiwan when the Asia Scoring Card is played or during Final Scoring at the end of Turn 10. Taiwan is not a battleground country for any other game purpose. This card is discarded after US play of \'The China Card\'.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[Side.US].append('Formosan_Resolution')


class Defectors(Card):
    name = 'Defectors'
    card_index = 103
    card_type = 'Event'
    stage = 'Early War'
    ops = 2
    owner = Side.US
    event_text = 'Play in Headline Phase to cancel USSR Headline event, including Scoring Card. Cancelled card returns to the Discard Pile. If Defectors played by USSR during Soviet action round, US gains 1 VP (unless played on the Space Race).'

    def can_event(self, game, side):
        return False

    def use_event(self, game, side: Side):
        self.event_occurred = True
        # checks to see if headline bin is empty i.e. in action round
        # check if there's a headline
        if game.headline_bin[Side.USSR]:
            game.discard_pile.append(
                game.headline_bin[Side.USSR])
            game.headline_bin[Side.USSR] = ''
        if side == Side.USSR and game.ar_side == Side.USSR:
            game.change_vp(Side.US.vp_mult)


class The_Cambridge_Five(Card):
    name = 'The_Cambridge_Five'
    card_index = 104
    card_type = 'Event'
    stage = 'Early War'
    optional = True
    ops = 2
    owner = Side.USSR
    event_text = 'The US player exposes all scoring cards in their hand. The USSR player may then add 1 Influence in any single region named on one of those scoring cards (USSR choice). Cannot be played as an event in Late War.'

    def can_event(self, game, side):
        return game.turn_track < 8

    def use_event(self, game, side: Side):
        if self.can_event(game, Side.USSR):
            us_scoring_cards = [n for n in game.hand[Side.US]
                                if game.cards[n].info.card_type == 'Scoring']
            countries = chain(
                *(CountryInfo.REGION_ALL[Card.ALL[n].scoring_region] for n in us_scoring_cards))

            if len(us_scoring_cards):
                game.players[Side.USSR].opp_hand.update(us_scoring_cards)
            else:
                print('US player has no scoring cards.')
                game.players[Side.USSR].opp_hand.no_scoring_cards = True

            self.event_occurred = True
            game.input_state = Input(
                Side.USSR, InputType.SELECT_COUNTRY,
                partial(game.event_influence_callback,
                        Country.increment_influence, Side.US),
                countries,
                prompt=f'The Cambridge Five: Place 1 influence in a country named on the revealed scoring cards.',
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

    def can_event(self, game, side):
        return game.map['UK'].control == Side.US

    def use_event(self, game, side: Side):
        if self.can_event(game, Side.US):
            self.event_occurred = True
            if 'NATO' in game.basket[Side.US]:
                available_list = CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]
                incr = 2
                game.change_vp(2 * Side.US.vp_mult)
            else:
                available_list = game.map['UK'].info.adjacent_countries
                incr = 1

            game.input_state = Input(
                Side.US, InputType.SELECT_COUNTRY,
                partial(game.event_influence_callback, partial(
                    Country.increment_influence, amt=incr), Side.US),
                available_list,
                prompt=f'Special Relationship: Place {incr} influence in a single country.',
            )


class NORAD(Card, Effect):
    name = 'NORAD'
    card_index = 106
    card_type = 'Event'
    stage = 'Early War'
    optional = True
    ops = 3
    owner = Side.US
    event_text = 'If the US controls Canada, the US may add 1 Influence to any country already containing US Influence at the conclusion of any Action Round in which the DEFCON marker moves to the \'2\' box. This event cancelled by \'Quagmire\'.'
    event_unique = True

    def place_norad_influence(self, game):
        game.input_state = Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.increment_influence, Side.US),
            game.map.has_us_influence,
            prompt='Place NORAD influence.',
            reps_unit='influence'
        )

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[Side.US].append('NORAD')

# --
# -- MID WAR
# --
#
#


class Brush_War(Card):
    name = 'Brush_War'
    card_index = 36
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.NEUTRAL
    event_text = 'Attack any country with a stability of 1 or 2. Roll a die and subtract 1 for every adjacent enemy controlled country. Success on 3-6. Player adds 3 to his Military Ops Track. Effects of Victory: Player gains 1 VP and replaces all opponent\'s Influence with his Influence.'

    def use_event(self, game, side: Side):
        self.event_occurred = True

        options = {n for n in game.map.ALL
                   if game.map[n].info.stability <= 2}

        if NATO.name in game.basket[NATO.owner]:
            options -= game.cards[NATO.name].effect_countries(game)

        game.input_state = Input(
            side, InputType.SELECT_COUNTRY,
            partial(game.war_country_callback, side,
                    lower=3, win_vp=1, win_milops=3),
            options,
            prompt='Brush War: Choose a target country.'
        )


class Central_America_Scoring(Card):
    name = 'Central_America_Scoring'
    card_index = 37
    card_type = 'Scoring'
    stage = 'Mid War'
    scoring_region = MapRegion.CENTRAL_AMERICA
    event_text = 'Both sides score: Presence: 1, Domination: 3, Control: 5. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
    may_be_held = False

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.score(MapRegion.CENTRAL_AMERICA)


class Southeast_Asia_Scoring(Card):
    name = 'Southeast_Asia_Scoring'
    card_index = 38
    card_type = 'Scoring'
    stage = 'Mid War'
    scoring_region = MapRegion.SOUTHEAST_ASIA
    event_text = 'Both sides score: 1 VP each for Control of: Burma, Cambodia/Laos, Vietnam, Malaysia, Indonesia, the Phillipines, 2 VP for Control of Thailand'
    may_be_held = False
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        vps = [0, 0, 0]
        for n in CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]:
            x = game.map[n]
            vps[x.control] += 1
        swing = vps[Side.USSR] * Side.USSR.vp_mult + \
            vps[Side.US] * Side.US.vp_mult

        swing += game.map['Thailand'].control.vp_mult
        print(f'Southeast Asia scores for {swing} VP')
        game.change_vp(swing)


class Arms_Race(Card):
    name = 'Arms_Race'
    card_index = 39
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.NEUTRAL
    event_text = 'Compare each player\'s status on the Military Operations Track. If Phasing Player has more Military Operations points, he scores 1 VP. If Phasing Player has more Military Operations points and has met the Required Military Operations amount, he scores 3 VP instead.'

    def use_event(self, game, side: Side):
        self.event_occurred = True
        if game.milops_track[side] > game.milops_track[side.opp]:
            if game.milops_track >= game.defcon_track:
                game.change_vp(3 * side.vp_mult)
            else:
                game.change_vp(1 * side.vp_mult)


class Cuban_Missile_Crisis(Card, Effect):
    name = 'Cuban_Missile_Crisis'
    card_index = 40
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.NEUTRAL
    event_text = 'Set DEFCON to Level 2. Any further Coup attempt by your opponent this turn, anywhere on the board, will result in Global Thermonuclear War. Your opponent will lose the game. This event may be cancelled at any time if the USSR player removes two Influence from Cuba or the US player removes 2 Influence from either West Germany or Turkey.'
    event_unique = True

    def effect_end_turn(self, game, effect_side):
        game.basket[effect_side].remove(self.name)

    def effect_coup_after(self, game, effect_side, coup_side, country_name, result):
        if coup_side != effect_side:
            print('Cuban Missile Crisis: game ends.')
            game.set_defcon(1)

    def cmc_remove_callback(self, game, side: Side, opt: str):
        game.input_state.reps -= 1
        if opt != game.input_state.option_stop_early:
            game.map[opt].decrement_influence(side, amt=2)
            game.basket[side.opp].remove(self.name)

    def cmc_remove_stage(self, game, side: Side):
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
            n for n in countries if game.map[n].influence[side] >= 2]

        if len(options) == 0:
            return False

        game.input_state = Input(
            side, InputType.SELECT_COUNTRY,
            partial(self.cmc_remove_callback, game, side),
            options,
            prompt='Cuban Missile Crisis: Remove 2 influence to de-escalate.',
            reps_unit='influence',
            option_stop_early='Do not remove influence.'
        )

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.change_defcon(2 - game.defcon_track)
        game.basket[side].append(self.name)


class Nuclear_Subs(Card, Effect):
    name = 'Nuclear_Subs'
    card_index = 41
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'US Coup attempts in Battleground Countries do not affect the DEFCON track for the remainder of the turn (does not affect Cuban Missile Crisis).'
    event_unique = True

    def effect_end_turn(self, game, effect_side):
        game.basket[self.owner].remove(self.name)

    def effect_coup_after(self, game, effect_side, coup_side, country_name, result):
        if coup_side == Side.US and game.map[country_name].info.battleground:
            return CoupEffects(no_defcon_bg=True)

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[self.owner].append(self.name)


class Quagmire(Card, Effect):
    name = 'Quagmire'
    card_index = 42
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.USSR
    event_text = 'On next action round, US player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each US player Action round until successful or no appropriate cards remain. If out of appropriate cards, the US player may only play scoring cards until the next turn.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        if 'NORAD' in game.basket[Side.US]:
            game.basket[Side.US].remove('NORAD')
        game.basket[Side.US].append('Quagmire')


class Salt_Negotiations(Card, Effect):
    name = 'Salt_Negotiations'
    card_index = 43
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.NEUTRAL
    event_text = 'Improve DEFCON two levels. Further Coup attempts incur -1 die roll modifier for both players for the remainder of the turn. Player may sort through discard pile and reclaim one non-scoring card, after revealing it to their opponent.'
    event_unique = True

    def effect_end_turn(self, game, effect_side):
        game.basket[effect_side].remove(self.name)

    def callback(self, game, side: Side, card_name: str):
        game.input_state.reps -= 1
        if card_name != game.input_state.option_stop_early:
            game.discard_pile.remove(card_name)
            # TODO: reveal card to opponent
            game.hand[side].append(card_name)
        return True

    def effect_coup_roll(self, game, effect_side, coup_side, country_name):
        return -1

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.change_defcon(2)
        game.basket[side].append(self.name)
        game.input_state = Input(
            side, InputType.SELECT_CARD,
            partial(self.callback, game, side),
            (n for n in game.discard_pile if game.cards[n].info.ops >= 1),
            prompt=f'You may pick a non-scoring card from the discard pile.',
            option_stop_early='Do not take a card.'
        )


class Bear_Trap(Card, Effect):
    name = 'Bear_Trap'
    card_index = 44
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.US
    event_text = 'On next action round, USSR player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each USSR player Action Round until successful or no appropriate cards remain. If out of appropriate cards, the USSR player may only play scoring cards until the next turn.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[Side.USSR].append('Bear_Trap')


class Summit(Card):
    name = 'Summit'
    card_index = 45
    card_type = 'Event'
    stage = 'Mid War'
    ops = 1
    owner = Side.NEUTRAL
    event_text = 'Both players roll a die.  Each adds 1 for each Region they Dominate or Control. High roller gains 2 VP and may move DEFCON marker one level in either direction. Do not reroll ties.'

    def choices(self, game, side: Side):
        game.change_vp(2*side.vp_mult)

        option_function_mapping = {
            'DEFCON -1': partial(game.change_defcon, -1),
            'No change': partial(lambda: None),
            'DEFCON +1': partial(game.change_defcon, 1),
        }

        game.input_state = Input(
            side, InputType.SELECT_MULTIPLE,
            partial(game.select_multiple_callback,
                    option_function_mapping),
            option_function_mapping.keys(),
            prompt='Summit: You may change DEFCON level by 1 in either direction.'
        )

    def dice_callback(self, game, ussr_advantage: int, num: tuple):
        game.input_state.reps -= 1
        if num[Side.USSR] + ussr_advantage > num[Side.US]:
            outcome = 'USSR success'
        elif num[Side.USSR] + ussr_advantage < num[Side.US]:
            outcome = 'US success'
        else:
            outcome = 'Tie'

        if outcome == 'USSR success':
            self.choices(game, Side.USSR)
        elif outcome == 'US success':
            self.choices(game, Side.US)
        print(
            f'{outcome} with (USSR, US) modified rolls of ({num[Side.USSR]}, {num[Side.US]}). ussr_advantage is {ussr_advantage}.')
        return True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        dominate_or_control = [0, 0]

        for region in [i for i in MapRegion.main_regions()]:
            bg_count = [0, 0, 0]  # USSR, US, NEUTRAL
            country_count = [0, 0, 0]

            for n in CountryInfo.REGION_ALL[region]:
                x = game.map[n]
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

        game.stage_list.append(partial(
            game.dice_stage,
            partial(self.dice_callback, game, ussr_advantage), two_dice=True))


class How_I_Learned_to_Stop_Worrying(Card):
    name = 'How_I_Learned_to_Stop_Worrying'
    card_index = 46
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'Set the DEFCON at any level you want (1-5). This event counts as 5 Military Operations for the purpose of required Military Operations.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        option_function_mapping = {
            # is there any way to directly refer to the
            f'DEFCON 1: Thermonuclear War. {side.opp} victory!': partial(game.set_defcon, 1),
            f'DEFCON 2': partial(game.set_defcon, 2),
            f'DEFCON 3': partial(game.set_defcon, 3),
            f'DEFCON 4': partial(game.set_defcon, 4),
            f'DEFCON 5': partial(game.set_defcon, 5)
        }

        game.input_state = Input(
            Side.USSR, InputType.SELECT_MULTIPLE,
            partial(game.select_multiple_callback,
                    option_function_mapping),
            option_function_mapping.keys(),
            prompt='How I Learned To Stop Worrying: Set a new DEFCON level.'
        )

        game.change_milops(side, 5)


class Junta(Card, Effect):
    name = 'Junta'
    card_index = 47
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'Place 2 Influence in any one Central or South American country. Then you may make a free Coup attempt or Realignment roll in one of these regions (using this card\'s Operations Value).'

    def __init__(self):
        super().__init__()
        self.event_active = False

    def effect_coup_after(self, game, effect_side, coup_side, country_name, result):
        game.basket[coup_side].remove(self.name)
        return CoupEffects(no_milops=True)

    def event_coup_stage(self, game, side):
        eff_ops = game.get_global_effective_ops(side, self.ops)
        game.input_state = Input(
            side, InputType.SELECT_COUNTRY,
            partial(game.coup_country_callback, side, eff_ops),
            (n for n in game.can_coup_all(side, defcon=5)
             if n in CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA]
             or n in CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA]),
            prompt=f'Select a country to coup using {eff_ops} operations points.'
        )

    def event_coup_callback(self, game, side):
        game.basket[side].append(self.name)
        game.stage_list.append(partial(self.event_coup_stage, game, side))
        return True

    def effect_realign_after(self, game, effect_side):
        game.basket[effect_side].remove(self.name)

    def effect_realign_country_restrict(self, game, side):
        return set(CountryInfo.ALL) - (
            CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA] |
            CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA]
        )

    def event_realign_callback(self, game, side):
        game.basket[side].append(self.name)
        eff_ops = game.get_global_effective_ops(self.owner, self.ops)
        game.realign_state = RealignState(side, reps=eff_ops, defcon=5)
        game.stage_list.append(game.realign_country_stage)

    def event_stage_2(self, game, side):

        option_function_mapping = {
            'Free coup attempt': partial(self.event_coup_callback, game, side),
            'Free realignment rolls': partial(self.event_realign_callback, game, side)
        }

        game.input_state = Input(
            side, InputType.SELECT_MULTIPLE,
            partial(game.select_multiple_callback,
                    option_function_mapping),
            option_function_mapping.keys(),
            prompt='Junta: Player may make free Coup attempt or realignment rolls in Central America or South America.'
        )

    def use_event(self, game, side: Side):
        self.event_occurred = True

        game.input_state = Input(
            side, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    partial(Country.increment_influence, amt=2), side),
            chain(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA],
                  CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA]),
            prompt='Junta: Add 2 influence to a single country in Central America or South America.',
            reps_unit='influence'
        )

        game.stage_list.append(
            partial(self.event_stage_2, game, side))


class Kitchen_Debates(Card):
    name = 'Kitchen_Debates'
    card_index = 48
    card_type = 'Event'
    stage = 'Mid War'
    ops = 1
    owner = Side.US
    event_text = 'If the US controls more Battleground countries than the USSR, poke opponent in chest and gain 2 VP!'
    event_unique = True

    def can_event(self, game, side):
        us_count = sum(1 for n in CountryInfo.ALL if game.map[n].control ==
                       Side.US and game.map[n].info.battleground)
        ussr_count = sum(1 for n in CountryInfo.ALL if game.map[n].control ==
                         Side.USSR and game.map[n].info.battleground)
        return us_count > ussr_count

    def use_event(self, game, side: Side):
        self.event_occurred = True
        if self.can_event(game, Side.US):
            print('USSR poked in the chest by US player!')
            game.change_vp(-2)


class Missile_Envy(Card, Effect):
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
            game.hand[side].remove(self.name)
            game.hand[side.opp].append(self.name)
            game.players[side].opp_hand.update([self])
            self.exchange = False
        else:
            game.basket[side].remove(self.name)
            super().dispose(game, side)

    def can_event(self, game, side):
        return not self.event_occurred

    def missile_envy_exchange_callback(self, game, side, card: str):
        game.input_state.reps -= 1
        game.hand[side.opp].remove(card)
        game.hand[side].append(card)

        self.exchange = True

        if game.cards[card].owner == side.opp:

            options = [CardAction.INFLUENCE, CardAction.COUP,
                       CardAction.REALIGNMENT, CardAction.SPACE]

            game.input_state = Input(
                side, InputType.SELECT_CARD_ACTION,
                partial(game.action_callback, side, card,
                        no_event=True),
                (opt.name for opt in options),
                prompt=f'Opponent has traded {card}. Select an action.'
            )

        else:
            # must append backwards
            game.stage_list.append(
                partial(game.cards[card].dispose, game, side))
            game.stage_list.append(partial(game.trigger_event, side, card))

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[side.opp].append(self.name)

        best_ops = 0
        best_cards = []
        for card_name in game.hand[side.opp]:
            if card_name == 'The_China_Card':
                continue
            curr_ops = game.get_global_effective_ops(
                side.opp, game.cards[card_name].ops)
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


class We_Will_Bury_You(Card, Effect):
    name = 'We_Will_Bury_You'
    card_index = 50
    card_type = 'Event'
    stage = 'Mid War'
    ops = 4
    owner = Side.USSR
    event_text = 'Unless UN Invervention is played as an Event on the US player\'s next round, USSR gains 3 VP prior to any US VP award. Degrade DEFCON one level.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.change_defcon(-1)
        game.basket[self.owner].append(self.name)


class Brezhnev_Doctrine(Card, Effect):
    name = 'Brezhnev_Doctrine'
    card_index = 51
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.USSR
    event_text = 'All further Operations cards played by the USSR this turn increase their Ops value by one (to a maximum of 4).'
    event_unique = True

    def effect_end_turn(self, game, effect_side):
        game.basket[self.owner].remove(self.name)

    def effect_global_ops(self, game, effect_side, ops_side):
        if ops_side == self.owner:
            return 1

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[self.owner].append(self.name)


class Portuguese_Empire_Crumbles(Card):
    name = 'Portuguese_Empire_Crumbles'
    card_index = 52
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.USSR
    event_text = 'Add 2 USSR Influence in both SE African States and Angola.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.map.change_influence('Angola', Side.USSR, 2)
        game.map.change_influence('SE_African_States', Side.USSR, 2)


class South_African_Unrest(Card):
    name = 'South_African_Unrest'
    card_index = 53
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.USSR
    event_text = 'USSR either adds 2 Influence in South Africa or adds 1 Influence in South Africa and 2 Influence in any countries adjacent to South Africa.'

    def use_event(self, game, side: Side):
        def _sa():
            game.map.change_influence('South_Africa', Side.USSR, 2)

        def _sa_angola():
            game.map.change_influence('South_Africa', Side.USSR, 1)
            game.map.change_influence('Angola', Side.USSR, 2)

        def _sa_botswana():
            game.map.change_influence('South_Africa', Side.USSR, 1)
            game.map.change_influence('Botswana', Side.USSR, 2)

        def _sa_angola_botswana():
            game.map.change_influence('South_Africa', Side.USSR, 1)
            game.map.change_influence('Angola', Side.USSR, 1)
            game.map.change_influence('Botswana', Side.USSR, 1)

        self.event_occurred = True

        option_function_mapping = {
            'Add 2 Influence to South Africa.': _sa,
            'Add 1 Influence to South Africa and 2 Influence to Angola.': _sa_angola,
            'Add 1 Influence to South Africa and 2 Influence to Botswana.': _sa_botswana,
            'Add 1 Influence each to South Africa, Angola, and Botswana.': _sa_angola_botswana
        }

        game.input_state = Input(
            side, InputType.SELECT_MULTIPLE,
            partial(game.select_multiple_callback,
                    option_function_mapping),
            option_function_mapping.keys(),
            prompt='South African Unrest: Choose an option.'
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

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.map['Chile'].change_influence(2, 0)


class Willy_Brandt(Card, Effect):
    name = 'Willy_Brandt'
    card_index = 55
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.USSR
    event_text = 'USSR receives gains 1 VP. USSR receives 1 Influence in West Germany. Cancels NATO for West Germany. This event unplayable and/or cancelled by Tear Down This Wall.'
    event_unique = True

    def can_event(self, game, side):
        return 'Tear_Down_This_Wall' not in game.basket[Side.US]

    def use_event(self, game, side: Side):
        if self.can_event(game, Side.USSR):
            self.event_occurred = True
            game.change_defcon(1)
            game.map['West_Germany'].change_influence(1, 0)
            game.basket[Side.USSR].append('Willy_Brandt')


class Muslim_Revolution(Card):
    name = 'Muslim_Revolution'
    card_index = 56
    card_type = 'Event'
    stage = 'Mid War'
    ops = 4
    owner = Side.USSR
    event_text = 'Remove all US Influence in two of the following countries: Sudan, Iran, Iraq, Egypt, Libya, Saudi Arabia, Syria, Jordan.'

    def can_event(self, game, side):
        return False if 'AWACS_Sale_to_Saudis' in game.basket[Side.US] else True

    def use_event(self, game, side: Side):
        if self.can_event(game, Side.USSR):
            self.event_occurred = True
            mr = ['Sudan', 'Iran', 'Iraq', 'Egypt',
                  'Libya', 'Saudi_Arabia', 'Syria', 'Jordan']
            game.input_state = Input(
                Side.USSR, InputType.SELECT_COUNTRY,
                partial(game.event_influence_callback,
                        Country.remove_influence, Side.US),
                (n for n in mr if game.map[n].has_us_influence),
                prompt='Muslim Revolution: Select countries in which to remove all US influence.',
                reps=2,
                reps_unit='countries',
                max_per_option=1
            )


class ABM_Treaty(Card):
    name = 'ABM_Treaty'
    card_index = 57
    card_type = 'Event'
    stage = 'Mid War'
    ops = 4
    owner = Side.NEUTRAL
    event_text = 'Improve DEFCON one level. Then player may Conduct Operations as if they played a 4 Ops card.'

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.change_defcon(1)
        game.select_action(
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

    def use_event(self, game, side: Side):
        self.event_occurred = True
        if 'The_China_Card' in game.hand[Side.US]:
            game.cards['The_China_Card'].move(
                game, Side.US, made_playable=True)
        elif 'The_China_Card' in game.hand[Side.USSR]:
            game.change_vp(1)


class Flower_Power(Card, Effect):
    name = 'Flower_Power'
    card_index = 59
    card_type = 'Event'
    stage = 'Mid War'
    ops = 4
    owner = Side.USSR
    event_text = 'USSR gains 2 VP for every subsequently US played \'war card\' (played as an Event or Operations) unless played on the Space Race. War Cards: Arab-Israeli War, Korean War, Brush War, Indo-Pakistani War or Iran-Iraq War. This event cancelled by \'An Evil Empire\'.'
    event_unique = True

    def can_event(self, game, side):
        return 'An_Evil_Empire' not in game.basket[Side.US]

    def use_event(self, game, side: Side):
        if self.can_event(game, Side.USSR):
            self.event_occurred = True
            game.basket[Side.USSR].append('Flower_Power')


class U2_Incident(Card, Effect):
    name = 'U2_Incident'
    card_index = 60
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.USSR
    event_text = 'USSR gains 1 VP. If UN Intervention played later this turn as an Event, either by US or USSR, gain 1 additional VP.'
    event_unique = True

    def effect_end_turn(self, game, effect_side):
        game.basket[self.owner].remove(self.name)

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[self.owner].append(self.name)


class OPEC(Card):
    name = 'OPEC'
    card_index = 61
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.USSR
    event_text = 'USSR gains 1VP for each of the following countries he controls: Egypt, Iran, Libya, Saudi Arabia, Iraq, Gulf States, and Venezuela. Unplayable as an event if \'North Sea Oil\' is in effect.'

    def can_event(self, game, side):
        return 'North_Sea_Oil' not in game.basket[Side.US]

    def use_event(self, game, side: Side):
        if self.can_event(game, Side.USSR):
            self.event_occurred = True
            opec = ['Egypt', 'Iran', 'Libya', 'Saudi_Arabia',
                    'Iraq', 'Gulf_States', 'Venezuela']
            swing = sum(
                Side.USSR.vp_mult for country in opec if game.map[country].control == Side.USSR)
            game.change_vp(swing)


class Lone_Gunman(Card):
    name = 'Lone_Gunman'
    card_index = 62
    card_type = 'Event'
    stage = 'Mid War'
    ops = 1
    owner = Side.USSR
    event_text = 'US player reveals his hand. Then the USSR may Conduct Operations as if they played a 1 Op card.'
    event_unique = True

    def use_event(self, game, side: Side):
        game.players[Side.USSR].opp_hand.update(game.hand[Side.US])
        self.event_occurred = True
        game.select_action(
            Side.USSR, f'Blank_1_Op_Card', is_event_resolved=True)


class Colonial_Rear_Guards(Card):
    name = 'Colonial_Rear_Guards'
    card_index = 63
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'Add 1 US Influence in each of four different African and/or Southeast Asian countries.'

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.input_state = Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.increment_influence, Side.US),
            chain(CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA],
                  CountryInfo.REGION_ALL[MapRegion.AFRICA]),
            prompt='Place influence using Colonial Real Guards.',
            reps=4,
            reps_unit='influence',
            max_per_option=1
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

    def use_event(self, game, side: Side):
        self.event_occurred = True
        countries = ['Panama', 'Costa_Rica', 'Venezuela']
        for country in countries:
            game.map[country].change_influence(0, 1)


class Camp_David_Accords(Card, Effect):
    name = 'Camp_David_Accords'
    card_index = 65
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'US gains 1 VP. US receives 1 Influence in Israel, Jordan and Egypt. Arab-Israeli War event no longer playable.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.change_vp(-1)
        countries = ['Israel', 'Jordan', 'Egypt']
        for country in countries:
            game.map[country].change_influence(0, 1)
        game.basket[Side.US].append('Camp_David_Accords')


class Puppet_Governments(Card):
    name = 'Puppet_Governments'
    card_index = 66
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'US may add 1 Influence in three countries that currently contain no Influence from either power.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.input_state = Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.increment_influence, Side.US),
            (n for n in CountryInfo.ALL
                if not game.map[n].has_us_influence
                and not game.map[n].has_ussr_influence),
            prompt='Place influence using Puppet Governments.',
            reps=3,
            reps_unit='influence',
            max_per_option=1
        )


class Grain_Sales_to_Soviets(Card):
    name = 'Grain_Sales_to_Soviets'
    card_index = 67
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'Randomly choose one card from USSR hand. Play it or return it. If Soviet player has no cards, or returned, use this card to conduct Operations normally.'

    def use_un_intervention(self, game, card_name: str):
        # the only exception where UN intervention is used out of place without calling card_callback
        game.stage_list.append(
            partial(game.cards['UN_Intervention'].dispose,
                    game, Side.US))
        game.select_action(Side.US, card_name, un_intervention=True)
        if 'U2_Incident' in game.basket[Side.USSR]:
            game.change_vp(1)
            game.basket[Side.USSR].remove('U2_Incident')

    def action_stage(self, game, card_name: str):
        # if received card is Side.USSR, then offer to use UN intervention if holding
        option_function_mapping = {
            'Use card normally':
                partial(game.select_action, Side.US, card_name),
            'Return card to USSR':
                partial(game.select_action, Side.US,
                        'Blank_2_Op_Card', is_event_resolved=True)
        }

        if 'UN_Intervention' in game.hand[Side.US] and \
                game.cards[card_name].info.owner == Side.USSR:
            option_function_mapping['Use card with UN Intervention'] = partial(
                self.use_un_intervention, game, card_name)

        game.input_state = Input(
            Side.US, InputType.SELECT_MULTIPLE,
            partial(game.select_multiple_callback,
                    option_function_mapping),
            option_function_mapping.keys(),
            prompt='You may use the card selected by Grain Sales to Soviets.'
        )

    def random_card_callback(self, game, card_name: str):
        game.input_state.reps -= 1
        print(f'{card_name} was selected by Grain Sales to Soviets.')
        game.hand[Side.USSR].remove(card_name)
        game.hand[Side.US].append(card_name)
        game.stage_list.append(
            partial(self.action_stage, game, card_name))

    def use_event(self, game, side: Side):
        self.event_occurred = True
        restricted_ussr_hand = [n for n in game.hand[Side.USSR] if not (n == 'Grain_Sales_to_Soviets' or n == 'The_China_Card')]


        if not len(restricted_ussr_hand):
            game.stage_list.append(
                partial(game.select_action, Side.US, 'Blank_2_Op_Card', is_event_resolved=True))

        game.input_state = Input(
            Side.NEUTRAL, InputType.SELECT_CARD,
            partial(self.random_card_callback, game),
            restricted_ussr_hand,
            prompt='Grain Sales to Soviets: US player randomly selects a card from USSR player\'s hand.'
        )


class John_Paul_II_Elected_Pope(Card, Effect):
    name = 'John_Paul_II_Elected_Pope'
    card_index = 68
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'Remove 2 USSR Influence in Poland and then add 1 US Influence in Poland. Allows play of \'Solidarity\'.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.map['Poland'].change_influence(-2, 1)
        game.basket[Side.US].append('John_Paul_II_Elected_Pope')


class Latin_American_Death_Squads(Card, Effect):
    name = 'Latin_American_Death_Squads'
    card_index = 69
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'All of the player\'s Coup attempts in Central and South America are +1 for the remainder of the turn, while all opponent\'s Coup attempts are -1 for the remainder of the turn.'

    def effect_end_turn(self, game, effect_side):
        game.basket[effect_side].remove(self.name)

    def effect_coup_roll(self, game, effect_side, coup_side, country_name):
        if (country_name in CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA]
                or country_name in CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA]):
            if effect_side == coup_side:
                return 1
            else:
                return -1

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[side].append(self.name)


class OAS_Founded(Card):
    name = 'OAS_Founded'
    card_index = 70
    card_type = 'Event'
    stage = 'Mid War'
    ops = 1
    owner = Side.US
    event_text = 'Add 2 US Influence in Central America and/or South America.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.input_state = Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.increment_influence, Side.US),
            chain(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA],
                  CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA]),
            prompt='Place influence using OAS_Founded.',
            reps=2,
            reps_unit='influence',
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

    def use_event(self, game, side: Side):
        self.event_occurred = True
        if 'The_China_Card' in game.hand[Side.USSR]:
            game.cards['The_China_Card'].move(
                game, Side.USSR)
        elif 'The_China_Card' in game.hand[Side.US]:
            game.change_vp(-2)


class Sadat_Expels_Soviets(Card):
    name = 'Sadat_Expels_Soviets'
    card_index = 72
    card_type = 'Event'
    stage = 'Mid War'
    ops = 1
    owner = Side.US
    event_text = 'Remove all USSR Influence in Egypt and add one US Influence.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.map.set_influence(
            'Egypt', Side.USSR, 0)  # using alternate syntax
        game.map['Egypt'].change_influence(0, 1)


class Shuttle_Diplomacy(Card, Effect):
    name = 'Shuttle_Diplomacy'
    card_index = 73
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.US
    event_text = 'Play in front of US player. During the next scoring of the Middle East or Asia (whichever comes first), subtract one Battleground country from USSR total, then put this card in the discard pile. Does not count for Final Scoring at the end of Turn 10.'

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[Side.US].append('Shuttle_Diplomacy')

    def dispose(self, game, side):
        game.limbo.append(self.name)
        game.hand[side].remove(self.name)


class The_Voice_Of_America(Card):
    name = 'The_Voice_Of_America'
    card_index = 74
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.US
    event_text = 'Remove 4 USSR Influence from non-European countries. No more than 2 may be removed from any one country.'

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.input_state = Input(
            Side.US, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.decrement_influence, Side.USSR),
            (n for n in CountryInfo.ALL
                if n not in CountryInfo.REGION_ALL[MapRegion.EUROPE]
                and game.map[n].has_ussr_influence),
            prompt='Remove USSR influence using The Voice Of America.',
            reps=4,
            reps_unit='influence',
            max_per_option=2
        )


class Liberation_Theology(Card):
    name = 'Liberation_Theology'
    card_index = 75
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.USSR
    event_text = 'Add 3 USSR Influence in Central America, no more than 2 per country.'

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.input_state = Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA],
            prompt='Place influence using Liberation Theology.',
            reps=3,
            reps_unit='influence',
            max_per_option=2
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

    def use_event(self, game, side: Side):
        self.event_occurred = True
        if 'The_China_Card' in game.hand[Side.USSR]:
            game.cards['The_China_Card'].move(
                game, Side.USSR, made_playable=True)
        elif 'The_China_Card' in game.hand[Side.US]:
            game.input_state = Input(
                Side.US, InputType.SELECT_COUNTRY,
                partial(game.event_influence_callback,
                        Country.increment_influence, Side.US),
                CountryInfo.REGION_ALL[MapRegion.ASIA],
                prompt='Place influence using Ussuri River Skirmish.',
                reps=4,
                reps_unit='influence',
                max_per_option=2
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

    def callback(self, game, option_stop_early, card_name: str):
        game.input_state.reps -= 1
        if card_name != option_stop_early:
            game.hand[Side.US].remove(card_name)
            game.discard_pile.append(card_name)
        else:
            game.input_state.reps = 0
        return True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        option_stop_early = 'Do not discard.'
        reps_modifier = 1 if 'The_China_Card' in game.hand[Side.US] else 0
        reps = len(game.hand[Side.US]) - reps_modifier

        game.input_state = Input(
            Side.US, InputType.SELECT_CARD,
            partial(self.callback, game, option_stop_early),
            (n for n in game.hand[Side.US] if n != 'The_China_Card'),
            prompt='You may discard any number of cards.',
            reps=reps,
            max_per_option=1,
            option_stop_early=option_stop_early
        )


class Alliance_for_Progress(Card):
    name = 'Alliance_for_Progress'
    card_index = 78
    card_type = 'Event'
    stage = 'Mid War'
    ops = 3
    owner = Side.US
    event_text = 'US gains 1 VP for each US controlled Battleground country in Central America and South America.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        ca = list(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA])
        sa = list(CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA])
        ca.extend(sa)
        swing = sum(
            Side.US.vp_mult for n in ca if game.map[n].control == Side.US)
        game.change_vp(swing)


class Africa_Scoring(Card):
    name = 'Africa_Scoring'
    card_index = 79
    card_type = 'Scoring'
    stage = 'Mid War'
    scoring_region = MapRegion.AFRICA
    event_text = 'Both sides score: Presence: 1, Domination: 4, Control: 6. +1 per controlled Battleground Country in Region'
    may_be_held = False

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.score(MapRegion.AFRICA)


class One_Small_Step(Card):
    name = 'One_Small_Step'
    card_index = 80
    card_type = 'Event'
    stage = 'Mid War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'If you are behind on the Space Race Track, play this card to move your marker two boxes forward on the Space Rack Track, gaining the VP value of the second box only.'

    def can_event(self, game, side):
        return game.space_track[side] < game.space_track[side.opp]

    def use_event(self, game, side: Side):
        if self.can_event(game, side):
            self.event_occurred = True
            game.change_space(side, 2)


class South_America_Scoring(Card):
    name = 'South_America_Scoring'
    card_index = 81
    card_type = 'Scoring'
    stage = 'Mid War'
    scoring_region = MapRegion.SOUTH_AMERICA
    event_text = 'Both sides score: Presence: 2, Domination: 5, Control: 6. +1 per controlled Battleground Country in Region'
    may_be_held = False

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.score(MapRegion.SOUTH_AMERICA)


class Che(Card, Effect):
    name = 'Che'
    card_index = 107
    card_type = 'Event'
    stage = 'Mid War'
    optional = True
    ops = 3
    owner = Side.USSR
    event_text = 'USSR may immediately make a Coup attempt using this card\'s Operations value against a non-battleground country in Central America, South America, or Africa. If the Coup removes any US Influence, USSR may make a second Coup attempt against a different target under the same restrictions.'

    def __init__(self):
        super().__init__()
        self.coup_reps = 0

    def effect_coup_after(self, game, effect_side, coup_side, country_name, result):
        self.coup_reps -= 1
        if self.coup_reps and result > 0:
            self.second = True
            game.stage_list.append(partial(self.event_coup_stage, game))
        else:
            game.basket[effect_side].remove(self.name)

    def event_coup_callback(self, game, ops, country_name):
        if country_name == game.input_state.option_stop_early:
            return True
        return game.coup_country_callback(self.owner, ops, country_name)

    def event_coup_stage(self, game):
        eff_ops = game.get_global_effective_ops(self.owner, self.ops)

        options = {
            n for n in game.can_coup_all(self.owner, defcon=5)
            if not game.map[n].info.battleground
            and (
                n in CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA]
                or n in CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA]
                or n in CountryInfo.REGION_ALL[MapRegion.AFRICA]
            )
        }

        game.input_state = Input(
            self.owner, InputType.SELECT_COUNTRY,
            partial(self.event_coup_callback, game, eff_ops),
            options,
            prompt=f'Select a country to coup using {eff_ops} operations points.',
            option_stop_early='Do not coup.'
        )

    def use_event(self, game, side: Side):
        self.event_occurred = True
        self.coup_reps = 2
        game.basket[self.owner].append(self.name)
        self.event_coup_stage(game)


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

    def can_event(self, game, side):
        return any(game.map[n].control == Side.US for n in CountryInfo.REGION_ALL[MapRegion.MIDDLE_EAST])

    def stage_2(self, game):
        game.draw_pile.extend(game.hand[Side.NEUTRAL])
        game.players[Side.US].draw_pile.update(
            game.hand[Side.NEUTRAL])
        game.hand[Side.NEUTRAL] = []
        return True

    def callback(self, game, opt: str):
        game.input_state.reps -= 1
        game.cards[opt].dispose(game, Side.NEUTRAL)
        game.stage_list.append(partial(self.stage_2, game))
        return True

    def use_event(self, game, side: Side):
        if self.can_event(game, Side.US):
            self.event_occurred = True
            game.deal(first_side=Side.NEUTRAL)

            game.input_state = Input(
                Side.US, InputType.SELECT_CARD,
                partial(self.callback, game),
                (n for n in game.hand[Side.NEUTRAL]),
                prompt=f'Our Man In Tehran: Discard any of these cards.',
                reps=5
            )


# --
# -- LATE WAR
# --


class Iranian_Hostage_Crisis(Card, Effect):
    name = 'Iranian_Hostage_Crisis'
    card_index = 82
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.USSR
    event_text = 'Remove all US Influence in Iran. Add 2 USSR Influence in Iran. Doubles the effect of Terrorism card against US.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.map.set_influence('Iran', Side.US, 0)
        game.map.change_influence('Iran', Side.USSR, 2)
        game.basket[Side.US].append('Iranian_Hostage_Crisis')


class The_Iron_Lady(Card, Effect):
    name = 'The_Iron_Lady'
    card_index = 83
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.US
    event_text = 'US gains 1 VP. Add 1 USSR Influence in Argentina. Remove all USSR Influence from UK. Socialist Governments event no longer playable.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.map.change_influence('Argentina', Side.USSR, 1)
        game.map.set_influence('UK', Side.USSR, 0)
        game.change_vp(-1)
        game.basket[Side.US].append('The_Iron_Lady')


class Reagan_Bombs_Libya(Card):
    name = 'Reagan_Bombs_Libya'
    card_index = 84
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.US
    event_text = 'US gains 1 VP for every 2 USSR Influence in Libya.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        swing = math.floor(game.map['Libya'].influence[Side.USSR] / 2)
        game.change_vp(-swing)


class Star_Wars(Card):
    name = 'Star_Wars'
    card_index = 85
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.US
    event_text = 'If the US is ahead on the Space Race Track, play this card to search through the discard pile for a non-scoring card of your choice. Event occurs immediately.'
    event_unique = True

    def can_event(self, game, side):
        return game.space_track[Side.US] > game.space_track[Side.USSR]

    def callback(self, game, card_name: str):
        game.input_state.reps -= 1
        game.trigger_event(Side.US, card_name)
        return True

    def use_event(self, game, side: Side):
        if self.can_event(game, Side.US):
            self.event_occurred = True
            game.input_state = Input(
                side, InputType.SELECT_CARD,
                partial(self.callback, game, side),
                (n for n in game.discard_pile if game.cards[n].info.card_type != 'Scoring'),
                prompt=f'Pick a non-scoring card from the discard pile for Event use immediately.'
            )


class North_Sea_Oil(Card, Effect):
    name = 'North_Sea_Oil'
    card_index = 86
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.US
    event_text = 'OPEC event is no longer playable. US may play 8 cards this turn.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[Side.US].append('North_Sea_Oil')
        game.ars_by_turn[Side.US][game.turn_track] = 8


class The_Reformer(Card, Effect):
    name = 'The_Reformer'
    card_index = 87
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.USSR
    event_text = 'Add 4 Influence in Europe (no more than 2 per country). If USSR is ahead of US in VP, then 6 Influence may be added instead. USSR may no longer conduct Coup attempts in Europe. Improves effect of Glasnost event.'
    event_unique = True

    def use_event(self, game, side: Side):
        reps = 6 if game.vp_track * Side.USSR.vp_mult > 0 else 4
        game.input_state = Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.increment_influence, Side.USSR),
            CountryInfo.REGION_ALL[MapRegion.EUROPE],
            prompt=f'The Reformer: Add {reps} influence to Europe.',
            reps=reps,
            reps_unit='influence',
            max_per_option=2
        )
        game.basket[Side.USSR].append('The_Reformer')

    def effect_coup_country_restrict(self, game, side):
        if side == Side.USSR:
            return CountryInfo.REGION_ALL[MapRegion.EUROPE]


class Marine_Barracks_Bombing(Card):
    name = 'Marine_Barracks_Bombing'
    card_index = 88
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.USSR
    event_text = 'Remove all US Influence in Lebanon plus remove 2 additional US Influence from anywhere in the Middle East.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.map.set_influence('Lebanon', Side.US, 0)
        game.input_state = Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.decrement_influence, Side.US),
            (n for n in CountryInfo.REGION_ALL[MapRegion.MIDDLE_EAST]
                if game.map[n].has_us_influence),
            prompt='Remove US influence using Marine_Barracks_Bombing.',
            reps=2,
            reps_unit='influence',
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

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.change_defcon(-1)
        game.change_vp(-2)
        if game.map['South_Korea'].control == Side.US:
            game.select_action(
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

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.change_defcon(1)
        game.change_vp(2)
        if 'The_Reformer' in game.basket[Side.USSR]:
            game.select_action(
                Side.USSR, f'Blank_4_Op_Card', can_coup=False, is_event_resolved=True)


class Ortega_Elected_in_Nicaragua(Card, Effect):
    name = 'Ortega_Elected_in_Nicaragua'
    card_index = 91
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.USSR
    event_text = 'Remove all US Influence from Nicaragua. Then USSR may make one free Coup attempt (with this card\'s Operations value) in a country adjacent to Nicaragua.'
    event_unique = True

    def effect_coup_after(self, game, effect_side, coup_side, country_name, result):
        game.basket[effect_side].remove(self.name)
        return CoupEffects(no_milops=True)

    def event_coup_callback(self, game, ops, country_name):
        if country_name == game.input_state.option_stop_early:
            return True
        return game.coup_country_callback(self.owner, ops, country_name)

    def use_event(self, game, side: Side):

        self.event_occurred = True
        game.map['Nicaragua'].remove_influence(Side.US)
        game.basket[self.owner].append(self.name)
        eff_ops = game.get_global_effective_ops(self.owner, self.ops)

        game.input_state = Input(
            self.owner, InputType.SELECT_COUNTRY,
            partial(self.event_coup_callback, game, eff_ops),
            (n for n in game.can_coup_all(self.owner, defcon=5)
                if n in game.map['Nicaragua'].info.adjacent_countries),
            prompt=f'Select a country to coup using {eff_ops} operations points.',
            option_stop_early='Do not coup.'
        )


class Terrorism(Card):
    name = 'Terrorism'
    card_index = 92
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'Opponent must randomly discard one card. If played by USSR and Iranian Hostage Crisis is in effect, the US player must randomly discard two cards. (Events on discards do not occur.)'

    def callback(self, game, side, card_name: str):
        game.input_state.reps -= 1
        game.cards[card_name].dispose(game, side.opp)
        return True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        reps = 2 if 'Iranian_Hostage_Crisis' in game.basket[
            Side.USSR] and side == Side.USSR else 1
        reps = len(game.hand[side.opp]) if len(
            game.hand[side.opp]) <= reps else reps

        game.input_state = Input(
            Side.NEUTRAL, InputType.SELECT_CARD,
            self.callback,
            game.hand[side.opp],
            prompt='Randomly discard a card.',
            reps=reps,
            reps_unit='cards to discard',
            max_per_option=1
        )


class Iran_Contra_Scandal(Card, Effect):
    name = 'Iran_Contra_Scandal'
    card_index = 93
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.USSR
    event_text = 'All US Realignment rolls have a -1 die roll modifier for the remainder of the turn.'
    event_unique = True

    def effect_end_turn(self, game, effect_side):
        game.basket[self.owner].remove(self.name)

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[self.owner].append(self.name)

    def effect_realign_roll(self, game, effect_side, roll_side, country_name):
        if roll_side == Side.US:
            return -1


class Chernobyl(Card, Effect):
    name = 'Chernobyl'
    card_index = 94
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.US
    event_text = 'The US player may designate one Region. For the remainder of the turn the USSR may not add additional Influence to that Region by the play of Operations Points via placing Influence.'
    event_unique = True

    def __init(self):
        super().__init__()
        self.region = None

    def set_region(self, region):
        self.region = region

    def effect_opsinf_region_ops(self, game, effect_side, ops_side) -> Optional[Tuple[MapRegion, int]]:
        if ops_side == Side.USSR:
            return self.region, -999

    def use_event(self, game, side: Side):

        game.basket[self.owner].append(self.name)

        option_function_mapping = {
            r.name: partial(self.set_region, r) for r in MapRegion.main_regions()
        }

        game.input_state = Input(
            side.opp, InputType.SELECT_MULTIPLE,
            partial(game.select_multiple_callback,
                    option_function_mapping),
            option_function_mapping,
            prompt='Chernobyl: Designate a single Region where USSR cannot place influence using operations for the rest of the turn.'
        )

    def effect_end_turn(self, game, effect_side):
        game.basket[effect_side].remove(self.name)
        self.region = None


class Latin_American_Debt_Crisis(Card):
    name = 'Latin_American_Debt_Crisis'
    card_index = 95
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.USSR
    event_text = 'Unless the US Player immediately discards a \'3\' or greater Operations card, double USSR Influence in two countries in South America.'
    event_unique = True

    def use_event(self, game, side: Side):
        def double_inf_ussr_callback(country_name: str) -> bool:
            if game.map[country_name].get_ussr_influence == 0:
                return False
            game.map[country_name].influence[Side.USSR] *= 2
            return True

        def did_not_discard_fn():
            game.input_state = Input(
                Side.USSR, InputType.SELECT_COUNTRY,
                double_inf_ussr_callback,
                (n for n in CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA]
                    if game.map[n].has_ussr_influence),
                prompt='Select countries to double USSR influence.',
                reps=2,
                reps_unit='countries',
                max_per_option=1
            )

        self.event_occurred = True

        game.input_state = Input(
            Side.US, InputType.SELECT_CARD,
            partial(game.may_discard_callback, Side.US,
                    did_not_discard_fn=partial(game.stage_list.append, did_not_discard_fn)),
            (n for n in game.hand[Side.US]
                if n != 'The_China_Card'
                and game.get_global_effective_ops(side, game.cards[n].info.ops) >= 3),
            prompt='You may discard a card. If you choose not to discard, USSR chooses two countries in South America to double USSR influence.',
            option_stop_early='Do not discard.'
        )


class Tear_Down_This_Wall(Card, Effect):
    name = 'Tear_Down_This_Wall'
    card_index = 96
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.US
    event_text = 'Cancels/prevent Willy Brandt. Add 3 US Influence in East Germany. Then US may make a free Coup attempt or Realignment rolls in Europe using this card\'s Ops Value.'
    event_unique = True

    def __init__(self):
        super().__init__()
        self.event_realign_active = False  # IF the event is currently happening

    def effect_coup_after(self, game, effect_side, coup_side, country_name, result):
        game.basket[coup_side].remove(self.name)
        return CoupEffects(no_milops=True)

    def event_coup_stage(self, game):
        eff_ops = game.get_global_effective_ops(self.owner, self.ops)
        game.input_state = Input(
            self.owner, InputType.SELECT_COUNTRY,
            partial(game.coup_country_callback, self.owner, eff_ops),
            (n for n in game.can_coup_all(self.owner, defcon=5)
             if n in CountryInfo.REGION_ALL[MapRegion.EUROPE]),
            prompt=f'Select a country to coup using {eff_ops} operations points.'
        )

    def event_coup_callback(self, game):
        game.basket[self.owner].append(self.name)
        game.stage_list.append(partial(self.event_coup_stage, game))
        return True

    def effect_realign_after(self, game, effect_side):
        self.event_realign_active = False

    def effect_realign_country_restrict(self, game, side):
        if self.event_realign_active:
            return set(CountryInfo.ALL) - CountryInfo.REGION_ALL[MapRegion.EUROPE]

    def event_realign_callback(self, game):
        self.event_realign_active = True
        eff_ops = game.get_global_effective_ops(self.owner, self.ops)
        game.realign_state = RealignState(self.owner, reps=eff_ops, defcon=5)
        game.stage_list.append(game.realign_country_stage)

    def use_event(self, game, side: Side):
        self.event_occurred = True
        if Willy_Brandt.name in game.basket[Willy_Brandt.owner]:
            game.basket[Willy_Brandt.owner].remove(Willy_Brandt.name)
        game.map['East_Germany'].increment_influence(Side.US, amt=3)
        game.basket[self.owner].append(self.name)

        option_function_mapping = {
            'Free coup attempt': partial(self.event_coup_callback, game),
            'Free realignment rolls': partial(self.event_realign_callback, game)
        }

        game.input_state = Input(
            side.opp, InputType.SELECT_MULTIPLE,
            partial(game.select_multiple_callback,
                    option_function_mapping),
            option_function_mapping.keys(),
            prompt='Tear Down This Wall: US player may make free Coup attempts or realignment rolls in Europe.'
        )


class An_Evil_Empire(Card, Effect):
    name = 'An_Evil_Empire'
    card_index = 97
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.US
    event_text = 'Cancels/Prevents Flower Power. US gains 1 VP.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.change_vp(-1)
        if 'Flower_Power' in game.basket[Side.USSR]:
            game.basket[Side.USSR].remove('Flower_Power')
        game.basket[Side.US].append('An_Evil_Empire')


class Aldrich_Ames_Remix(Card):
    name = 'Aldrich_Ames_Remix'
    card_index = 98
    card_type = 'Event'
    stage = 'Late War'
    ops = 3
    owner = Side.USSR
    event_text = 'US player exposes his hand to USSR player for remainder of turn. USSR then chooses one card from US hand, this card is discarded.'
    event_unique = True

    def use_event(self, game, side: Side):
        game.players[Side.USSR].opp_hand.update(
            game.hand[Side.US])
        game.input_state = Input(
            Side.USSR, InputType.SELECT_CARD,
            partial(game.may_discard_callback, Side.US),
            (n for n in game.hand[Side.US]
                if n != 'The_China_Card'),
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

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.change_vp(1)
        game.input_state = Input(
            Side.USSR, InputType.SELECT_COUNTRY,
            partial(game.event_influence_callback,
                    Country.decrement_influence, Side.US),
            (n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]
                if game.map[n].has_us_influence),
            prompt='Pershing II Deployed: Remove 1 US influence from any 3 countries in Western Europe.',
            reps=3,
            reps_unit='influence',
            max_per_option=1
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

    def can_event(self, game, side):
        return game.defcon_track == 2

    def use_event(self, game, side: Side):
        if self.can_event(game, side):
            self.event_occurred = True
            game.change_vp(6*side.opp.vp_mult)
            game.terminate()


class Solidarity(Card):
    name = 'Solidarity'
    card_index = 101
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.US
    event_text = 'Playable as an event only if John Paul II Elected Pope is in effect. Add 3 US Influence in Poland.'
    event_unique = True

    def can_event(self, game, side):
        return 'John_Paul_II_Elected_Pope' in game.basket[Side.US]

    def use_event(self, game, side: Side):
        if self.can_event(game, Side.US):
            self.event_occurred = True
            game.map['Poland'].change_influence(0, 3)
            game.basket[Side.US].remove('John_Paul_II_Elected_Pope')


class Iran_Iraq_War(Card):
    name = 'Iran_Iraq_War'
    card_index = 102
    card_type = 'Event'
    stage = 'Late War'
    ops = 2
    owner = Side.NEUTRAL
    event_text = 'Iran or Iraq invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to target of invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track Effects of Victory: Player gains 2 VP and replaces opponent\'s Influence in target country with his own.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.input_state = Input(
            side, InputType.SELECT_COUNTRY,
            partial(game.war_country_callback, side),
            ['Iran', 'Iraq'],
            prompt='Iran/Iraq War: Choose target of war.'
        )


class Yuri_and_Samantha(Card, Effect):
    name = 'Yuri_and_Samantha'
    card_index = 109
    card_type = 'Event'
    stage = 'Late War'
    optional = True
    ops = 2
    owner = Side.USSR
    event_text = 'USSR receives 1 VP for each US coup attempt made for the remainder of the current turn.'
    event_unique = True

    def effect_end_turn(self, game, effect_side):
        game.basket[self.owner].remove(self.name)

    def effect_coup_after(self, game, effect_side, coup_side, country_name, result):
        if coup_side == Side.US:
            return CoupEffects(vp=Side.USSR.vp_mult)

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.basket[self.owner].append(self.name)


class AWACS_Sale_to_Saudis(Card, Effect):
    name = 'AWACS_Sale_to_Saudis'
    card_index = 110
    card_type = 'Event'
    stage = 'Late War'
    optional = True
    ops = 3
    owner = Side.US
    event_text = 'US receives 2 Influence in Saudi Arabia. Muslim Revolution may no longer be played as an event.'
    event_unique = True

    def use_event(self, game, side: Side):
        self.event_occurred = True
        game.map.change_influence('Saudi_Arabia', Side.US, 2)
        game.basket[Side.US].append('AWACS_Sale_to_Saudis')


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

    def can_event(self, game, side):
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

    def can_event(self, game, side):
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

    def can_event(self, game, side):
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

    def can_event(self, game, side):
        return False
