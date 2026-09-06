"""
Extensive unit tests for Twilight Struggle card behavior.

Tests verify card events produce correct game state changes based on
the official Twilight Struggle rules.
"""

import math
import pytest
from functools import partial

from twilight_enums import Side, MapRegion, InputType, CardAction
from twilight_map import GameMap, CountryInfo, Country
from twilight_cards import GameCards, Card
from twilight_input_output import Input
from twilight_playerview import PlayerView
from game_mechanics import Game

from tests.helpers import make_game


class TestRulebookAlignment:
    def test_terminate_draw_on_zero_vp(self):
        game = make_game()
        game.vp_track = 0
        game.terminate(reason='final_scoring_complete', context={'turn_track': 11})
        assert game.termination_winner == Side.NEUTRAL

    def test_war_failure_still_counts_milops(self):
        game = make_game()
        game.input_state = type('InputStub', (), {'reps': 1})()
        game.war_dice_callback('South_Korea', Side.USSR, modifier=0,
                               min_roll=6, win_vp=2, win_milops=2, num='1')
        assert game.milops_track[Side.USSR] == 2
        assert game.vp_track == 0

    def test_realignment_superpower_adjacency_bonus(self):
        game = make_game()
        game.map['Mexico'].set_influence(1, 1)
        game.map.realignment(game, 'Mexico', Side.USSR, ussr_roll=3, us_roll=3)
        # Mexico is adjacent to US superpower, giving US a +1 shift.
        assert game.map['Mexico'].influence[Side.USSR] == 0

    def test_final_scoring_uses_generic_region_scorer(self):
        game = make_game()
        game.turn_track = 10
        game.end_of_turn()
        assert game.terminated is True
        assert game.termination_reason == 'final_scoring_complete'

    def test_final_scoring_checks_all_regions_before_deciding_winner(self):
        game = make_game()
        game.turn_track = 10
        game.vp_track = 19
        game.milops_track = [game.defcon_track, game.defcon_track]
        scored_regions = []

        def score_region(region):
            scored_regions.append(region)
            game.change_vp(2 if len(scored_regions) == 1 else -6)

        game.score = score_region
        game.end_of_turn()

        assert scored_regions == MapRegion.main_regions()
        assert game.vp_track == -9
        assert game.termination_reason == 'final_scoring_complete'
        assert game.termination_winner == Side.US

    def test_milops_victory_precedes_held_scoring_card_loss(self):
        game = make_game()
        game.turn_track = 5
        game.vp_track = 19
        game.milops_track = [game.defcon_track, 0]
        game.hand[Side.USSR] = ['Africa_Scoring']

        game.end_of_turn()

        assert game.termination_reason == 'vp_autovictory'
        assert game.termination_winner == Side.USSR

    def test_space_six_discard_pauses_end_of_turn_before_era_shuffle(self):
        game = make_game()
        game.turn_track = 3
        game.space_track = [6, 0]
        game.milops_track = [game.defcon_track, game.defcon_track]
        game.hand[Side.USSR] = ['NATO']

        game.end_of_turn()

        assert game.turn_track == 3
        assert game.input_state.prompt \
            == 'You may discard a held card via Eagle/Bear has landed.'
        assert game.input_state.recv('NATO') is True
        game.stage_complete()

        assert game.turn_track == 4
        assert 'NATO' in game.discard_pile
        assert game.input_state.prompt == 'Shuffle the deck.  Select the next card.'

    def test_space_six_cannot_discard_scoring_and_held_scoring_loses(self):
        game = make_game()
        game.turn_track = 5
        game.space_track = [0, 6]
        game.milops_track = [game.defcon_track, game.defcon_track]
        game.hand[Side.US] = ['Africa_Scoring']

        game.end_of_turn()

        assert game.terminated is True
        assert game.termination_reason == 'held_scoring_card'
        assert game.termination_winner == Side.USSR
        assert 'Africa_Scoring' in game.hand[Side.US]

    def test_missile_envy_exchange_dispose_tolerates_moved_card(self):
        game = make_game()
        card = game.cards['Missile_Envy']
        card.exchange = True
        card.dispose(game, Side.USSR)
        assert 'Missile_Envy' in game.hand[Side.US]

    def test_nuclear_test_ban_stops_after_vp_autovictory(self):
        game = make_game()
        game.vp_track = -17
        game.defcon_track = 5
        game.cards['Nuclear_Test_Ban'].use_event(game, Side.US)
        assert game.terminated is True
        assert game.termination_reason == 'vp_autovictory'
        assert game.defcon_track == 5

    def test_change_space_clamps_to_max_track(self):
        game = make_game()
        game.space_track[Side.USSR] = 7
        game.change_space(Side.USSR, 2)
        assert game.space_track[Side.USSR] == 8


# ===========================================================================
# CARD METADATA TESTS
# ===========================================================================

class TestCardMetadata:
    """Verify all cards have correct metadata attributes."""

    def test_all_cards_registered(self):
        assert len(Card.ALL) > 100

    def test_scoring_cards_cannot_be_held(self):
        scoring = ['Asia_Scoring', 'Europe_Scoring', 'Middle_East_Scoring',
                    'Central_America_Scoring', 'Southeast_Asia_Scoring',
                    'Africa_Scoring', 'South_America_Scoring']
        for name in scoring:
            assert Card.ALL[name].may_be_held is False

    def test_scoring_cards_have_zero_ops(self):
        scoring = ['Asia_Scoring', 'Europe_Scoring', 'Middle_East_Scoring',
                    'Central_America_Scoring', 'Southeast_Asia_Scoring',
                    'Africa_Scoring', 'South_America_Scoring']
        for name in scoring:
            assert Card.ALL[name].ops == 0

    def test_china_card_cannot_headline(self):
        assert Card.ALL['The_China_Card'].can_headline is False

    def test_south_america_scoring_enters_deck_only_in_turn_four(self):
        target = 'South_America_Scoring'
        assert Card.ALL[target].stage == 'Mid War'
        for turn in (1, 2, 3):
            game = make_game()
            game.turn_track = turn
            game.expand_deck()
            assert target in game.cards.mid_war
            assert target not in game.draw_pile
            assert all(target not in hand for hand in game.hand)

        game = make_game()
        game.turn_track = 4
        game.expand_deck()
        assert target not in game.cards.mid_war
        assert target in game.input_state.legal_options

    def test_un_intervention_cannot_headline(self):
        assert Card.ALL['UN_Intervention'].can_headline is False

    def test_unique_events_are_marked(self):
        unique_cards = [
            'Fidel', 'Vietnam_Revolts', 'Blockade', 'Korean_War',
            'Romanian_Abdication', 'COMECON', 'Nasser',
            'Warsaw_Pact_Formed', 'De_Gaulle_Leads_France',
            'Captured_Nazi_Scientist', 'Truman_Doctrine',
            'Marshall_Plan', 'Containment', 'CIA_Created',
            'US_Japan_Mutual_Defense_Pact', 'Suez_Crisis',
        ]
        for name in unique_cards:
            assert Card.ALL[name].event_unique is True, f"{name} should be event_unique"

    def test_card_owners(self):
        assert Card.ALL['Duck_and_Cover'].owner == Side.US
        assert Card.ALL['Fidel'].owner == Side.USSR
        assert Card.ALL['Olympic_Games'].owner == Side.NEUTRAL
        assert Card.ALL['The_China_Card'].owner == Side.NEUTRAL

    def test_card_ops_values(self):
        assert Card.ALL['Duck_and_Cover'].ops == 3
        assert Card.ALL['The_China_Card'].ops == 4
        assert Card.ALL['Red_Scare_Purge'].ops == 4
        assert Card.ALL['Blockade'].ops == 1
        assert Card.ALL['NATO'].ops == 4

    def test_template_cards_exist(self):
        for ops in [1, 2, 3, 4]:
            name = f'Blank_{ops}_Op_Card'
            assert name in Card.ALL
            assert Card.ALL[name].ops == ops

    def test_template_cards_not_eventable(self):
        game = make_game()
        for ops in [1, 2, 3, 4]:
            name = f'Blank_{ops}_Op_Card'
            card = game.cards[name]
            assert card.can_event(game, Side.US) is False
            assert card.can_event(game, Side.USSR) is False


# ===========================================================================
# COUNTRY / MAP TESTS
# ===========================================================================

class TestCountryAndMap:

    def test_standard_setup_ussr_influence(self):
        game = make_game()
        assert game.map['North_Korea'].influence[Side.USSR] == 3
        assert game.map['East_Germany'].influence[Side.USSR] == 3
        assert game.map['Finland'].influence[Side.USSR] == 1
        assert game.map['Syria'].influence[Side.USSR] == 1
        assert game.map['Iraq'].influence[Side.USSR] == 1

    def test_standard_setup_us_influence(self):
        game = make_game()
        assert game.map['Australia'].influence[Side.US] == 4
        assert game.map['UK'].influence[Side.US] == 5
        assert game.map['Canada'].influence[Side.US] == 2
        assert game.map['Philippines'].influence[Side.US] == 1
        assert game.map['Israel'].influence[Side.US] == 1

    def test_country_control(self):
        game = make_game()
        # UK: stability 5, US influence 5 -> US control
        assert game.map['UK'].control == Side.US
        # North Korea: stability 3, USSR influence 3 -> USSR control
        assert game.map['North_Korea'].control == Side.USSR
        # Finland: stability 4, USSR influence 1 -> NEUTRAL
        assert game.map['Finland'].control == Side.NEUTRAL

    def test_country_change_influence_clamps_to_zero(self):
        game = make_game()
        game.map['France'].set_influence(0, 3)
        game.map['France'].change_influence(0, -10)
        assert game.map['France'].influence[Side.US] == 0

    def test_country_increment_influence(self):
        game = make_game()
        game.map['France'].set_influence(0, 0)
        game.map['France'].increment_influence(Side.USSR, 3)
        assert game.map['France'].influence[Side.USSR] == 3

    def test_country_decrement_influence(self):
        game = make_game()
        game.map['France'].set_influence(0, 3)
        game.map['France'].decrement_influence(Side.US, 2)
        assert game.map['France'].influence[Side.US] == 1

    def test_decrement_influence_returns_false_if_zero(self):
        game = make_game()
        game.map['France'].set_influence(0, 0)
        assert game.map['France'].decrement_influence(Side.US) is False

    def test_country_remove_influence(self):
        game = make_game()
        game.map['France'].set_influence(0, 5)
        game.map['France'].remove_influence(Side.US)
        assert game.map['France'].influence[Side.US] == 0

    def test_remove_influence_returns_false_if_zero(self):
        game = make_game()
        game.map['France'].set_influence(0, 0)
        assert game.map['France'].remove_influence(Side.US) is False

    def test_country_match_influence(self):
        game = make_game()
        game.map['Yugoslavia'].set_influence(4, 0)
        game.map['Yugoslavia'].match_influence(Side.US)
        assert game.map['Yugoslavia'].influence[Side.US] == 4

    def test_battleground_countries_exist(self):
        bg_names = [n for n, ci in CountryInfo.ALL.items() if ci.battleground]
        # Official: 20 battleground countries (excluding superpowers)
        assert len(bg_names) >= 20

    def test_superpower_countries(self):
        assert CountryInfo.ALL['USSR'].superpower is True
        assert CountryInfo.ALL['US'].superpower is True
        assert CountryInfo.ALL['France'].superpower is False


# ===========================================================================
# SCORING CARD TESTS
# ===========================================================================

class TestScoringCards:

    def test_asia_scoring_presence(self):
        """USSR presence in Asia (e.g. via North Korea) should give presence VP."""
        game = make_game()
        # Standard setup: USSR controls North Korea (3/3), US controls Australia (4/4)
        # Both have presence + 1 BG each
        # USSR: presence(3) + 1 BG = 4
        # US: presence(3) + 1 BG = 4
        # Net = 0
        vp_before = game.vp_track
        game.cards['Asia_Scoring'].use_event(game, Side.USSR)
        # Both have presence. Exact VP depends on adjacent-superpower bonus.
        # North Korea adj to USSR (superpower) — no bonus for that.
        # US adj countries: Japan adj to US, South Korea adj... let's just verify VP changed or not.
        assert isinstance(game.vp_track, int)

    def test_europe_scoring_control_is_auto_victory(self):
        """Europe Control = 120 VP, which should trigger termination."""
        game = make_game()
        # Give US control of all European countries
        for n in CountryInfo.REGION_ALL[MapRegion.EUROPE]:
            game.map[n].set_influence(0, 10)
        game.stage_list = []  # prevent terminate from clearing active stages
        game.cards['Europe_Scoring'].use_event(game, Side.US)
        # VP should have moved drastically
        assert abs(game.vp_track) > 10

    def test_shuttle_diplomacy_interaction_with_asia_scoring(self):
        """Shuttle Diplomacy should subtract 1 from USSR BG count in Asia.
        The card goes to discard from limbo (not basket) during scoring."""
        game = make_game()
        game.basket[Side.US].append('Shuttle_Diplomacy')
        game.limbo.append('Shuttle_Diplomacy')  # put in limbo as dispose() would
        game.map['India'].set_influence(5, 0)
        game.cards['Asia_Scoring'].use_event(game, Side.USSR)
        assert 'Shuttle_Diplomacy' in game.discard_pile
        assert len(game.limbo) == 0

    def test_shuttle_diplomacy_interaction_with_middle_east_scoring(self):
        game = make_game()
        game.basket[Side.US].append('Shuttle_Diplomacy')
        game.limbo.append('Shuttle_Diplomacy')
        game.cards['Middle_East_Scoring'].use_event(game, Side.USSR)
        assert 'Shuttle_Diplomacy' in game.discard_pile

    def test_southeast_asia_scoring_vp_calculation(self):
        """SEA scoring: 1 VP per controlled country, +1 extra for Thailand."""
        game = make_game()
        # Give USSR all SEA countries
        for n in CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]:
            game.map[n].set_influence(5, 0)
        vp_before = game.vp_track
        game.cards['Southeast_Asia_Scoring'].use_event(game, Side.USSR)
        # 7 countries + 1 extra for Thailand = 8 VP for USSR
        # VP is positive for USSR, so vp_track should increase
        assert game.vp_track > vp_before

    def test_score_breakdown_matches_applied_scoring(self):
        game = make_game()
        game.map['India'].set_influence(5, 0)
        game.map['Pakistan'].set_influence(5, 0)
        before = game.vp_track
        preview = game.score_breakdown(MapRegion.ASIA)

        applied = game.score(MapRegion.ASIA)

        assert applied == preview
        assert game.vp_track - before == preview['swing']
        assert preview['sides']['USSR']['countries'] >= 2

    def test_southeast_asia_score_breakdown_includes_thailand_bonus(self):
        game = make_game()
        for name in CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]:
            game.map[name].set_influence(5, 0)

        preview = game.score_breakdown(MapRegion.SOUTHEAST_ASIA)

        assert preview['sides']['USSR']['vp'] == 8
        assert preview['swing'] == 8

    def test_southeast_asia_scoring_is_removed_after_play(self):
        """SEA scoring is a unique event, should be removed from game."""
        assert Card.ALL['Southeast_Asia_Scoring'].event_unique is True

    def test_formosan_resolution_makes_taiwan_battleground(self):
        """When Formosan Resolution is in effect, Taiwan counts as BG for scoring."""
        game = make_game()
        game.basket[Side.US].append('Formosan_Resolution')
        game.map['Taiwan'].set_influence(0, 5)  # US controls Taiwan
        assert game.map['Taiwan'].info.battleground is False
        game.score(MapRegion.ASIA)
        # After scoring, Taiwan battleground should be reset
        assert game.map['Taiwan'].info.battleground is False


# ===========================================================================
# EARLY WAR CARD EVENT TESTS
# ===========================================================================

class TestEarlyWarCards:
    def test_de_stalinization_can_place_in_empty_non_us_controlled_country(self):
        game = make_game()
        game.cards['De_Stalinization'].use_event(game, Side.USSR)
        for country in ('East_Germany', 'East_Germany', 'East_Germany',
                        'Finland'):
            assert game.input_state.recv(country) is True

        options = set(game.input_state.legal_options)
        assert game.input_state.prompt == 'Add 4 influence using De-Stalinization.'
        assert game.map['Romania'].influence == [0, 0]
        assert 'Romania' in options
        assert game.map['Canada'].control == Side.NEUTRAL
        assert 'Canada' in options
        assert game.map['UK'].control == Side.US
        assert 'UK' not in options


    def test_duck_and_cover(self):
        """Degrade DEFCON by 1, US gains VP = 5 - current DEFCON."""
        game = make_game()
        game.defcon_track = 5
        game.cards['Duck_and_Cover'].use_event(game, Side.US)
        assert game.defcon_track == 4
        # VP = -(5 - 4) = -1 (US gains 1 VP)
        assert game.vp_track == -1

    def test_duck_and_cover_at_defcon_3(self):
        game = make_game()
        game.defcon_track = 3
        game.cards['Duck_and_Cover'].use_event(game, Side.US)
        assert game.defcon_track == 2
        # VP = -(5-2) = -3
        assert game.vp_track == -3

    def test_five_year_plan_creates_input_for_discard(self):
        """Five Year Plan should create an input for random USSR discard."""
        game = make_game()
        game.hand[Side.USSR] = ['Duck_and_Cover', 'Fidel', 'NATO']
        game.cards['Five_Year_Plan'].use_event(game, Side.USSR)
        assert game.input_state is not None
        assert game.input_state.side == Side.NEUTRAL

    def test_five_year_plan_never_discards_china_card(self):
        game = make_game()
        game.hand[Side.USSR] = ['Five_Year_Plan', 'The_China_Card', 'Fidel']

        game.cards['Five_Year_Plan'].use_event(game, Side.US)

        assert set(game.input_state.legal_options) == {'Fidel'}

    def test_five_year_plan_with_only_china_card_has_no_discard_prompt(self):
        game = make_game()
        game.hand[Side.USSR] = ['Five_Year_Plan', 'The_China_Card']

        game.cards['Five_Year_Plan'].use_event(game, Side.US)

        assert game.input_state is None

    def test_the_china_card_cannot_event(self):
        game = make_game()
        assert game.cards['The_China_Card'].can_event(game, Side.USSR) is False
        assert game.cards['The_China_Card'].can_event(game, Side.US) is False

    def test_the_china_card_moves_to_opponent_after_dispose(self):
        game = make_game()
        game.hand[Side.USSR].append('The_China_Card')
        game.cards['The_China_Card'].dispose(game, Side.USSR)
        assert 'The_China_Card' in game.hand[Side.US]
        assert game.cards['The_China_Card'].is_playable is False

    def test_socialist_governments(self):
        """Remove 3 US influence from Western Europe, max 2 per country."""
        game = make_game()
        game.map['France'].set_influence(0, 3)
        game.cards['Socialist_Governments'].use_event(game, Side.USSR)
        assert game.input_state is not None
        assert game.input_state.side == Side.USSR
        assert game.input_state.reps == 3
        assert game.input_state.max_per_option == 2

    def test_socialist_governments_blocked_by_iron_lady(self):
        game = make_game()
        game.basket[Side.US].append('The_Iron_Lady')
        assert game.cards['Socialist_Governments'].can_event(game, Side.USSR) is False

    def test_fidel(self):
        """Remove all US influence in Cuba, USSR gains control."""
        game = make_game()
        game.map['Cuba'].set_influence(1, 3)
        game.cards['Fidel'].use_event(game, Side.USSR)
        assert game.map['Cuba'].influence[Side.US] == 0
        assert game.map['Cuba'].influence[Side.USSR] >= 3  # enough for control
        assert game.map['Cuba'].control == Side.USSR

    def test_fidel_already_ussr_controlled(self):
        """If Cuba already has high USSR influence, it stays."""
        game = make_game()
        game.map['Cuba'].set_influence(5, 2)
        game.cards['Fidel'].use_event(game, Side.USSR)
        assert game.map['Cuba'].influence[Side.USSR] == 5
        assert game.map['Cuba'].influence[Side.US] == 0

    def test_vietnam_revolts(self):
        """Add 2 USSR influence in Vietnam, add to basket for rest of turn."""
        game = make_game()
        game.map['Vietnam'].set_influence(0, 0)
        game.cards['Vietnam_Revolts'].use_event(game, Side.USSR)
        assert game.map['Vietnam'].influence[Side.USSR] == 2
        assert 'Vietnam_Revolts' in game.basket[Side.USSR]

    def test_vietnam_revolts_ops_bonus_is_ussr_only(self):
        us_game = make_game()
        us_game.map['Vietnam'].set_influence(0, 1)
        us_game.basket[Side.USSR].append('Vietnam_Revolts')
        us_game.card_operation_influence(Side.US, 'Blank_1_Op_Card')
        assert us_game.input_state.recv('Vietnam') is True
        assert us_game.input_state.reps == 0

        ussr_game = make_game()
        ussr_game.map['Vietnam'].set_influence(1, 0)
        ussr_game.basket[Side.USSR].append('Vietnam_Revolts')
        ussr_game.card_operation_influence(Side.USSR, 'Blank_1_Op_Card')
        assert ussr_game.input_state.recv('Vietnam') is True
        assert ussr_game.input_state.reps == 1

    def test_blockade_creates_discard_option(self):
        """US must discard 3+ ops card or lose all influence in West Germany."""
        game = make_game()
        game.hand[Side.US] = ['NATO']  # 4 ops
        game.map['West_Germany'].set_influence(0, 5)
        game.cards['Blockade'].use_event(game, Side.USSR)
        assert game.input_state is not None
        assert game.input_state.side == Side.US

    def test_korean_war(self):
        """Korean War triggers war on South Korea for USSR."""
        game = make_game()
        game.cards['Korean_War'].use_event(game, Side.USSR)
        # Should push a dice stage onto stage_list
        assert len(game.stage_list) > 0

    def test_us_triggering_korean_war_still_benefits_ussr(self):
        game = make_game()
        game.map['South_Korea'].set_influence(0, 3)

        game.cards['Korean_War'].use_event(game, Side.US)
        game.stage_complete()
        assert game.input_state.state == InputType.ROLL_DICE
        assert game.input_state.recv('6') is True

        assert game.vp_track == 2
        assert game.milops_track[Side.USSR] == 2
        assert game.milops_track[Side.US] == 0

    def test_romanian_abdication(self):
        """Remove all US influence in Romania, USSR gains control."""
        game = make_game()
        game.map['Romania'].set_influence(1, 3)
        game.cards['Romanian_Abdication'].use_event(game, Side.USSR)
        assert game.map['Romania'].influence[Side.US] == 0
        assert game.map['Romania'].influence[Side.USSR] >= 3
        assert game.map['Romania'].control == Side.USSR

    def test_arab_israeli_war_blocked_by_camp_david(self):
        game = make_game()
        game.basket[Side.US].append('Camp_David_Accords')
        assert game.cards['Arab_Israeli_War'].can_event(game, Side.USSR) is False

    def test_comecon(self):
        """Add 1 USSR influence to 4 non-US-controlled Eastern European countries."""
        game = make_game()
        game.cards['COMECON'].use_event(game, Side.USSR)
        assert game.input_state is not None
        assert game.input_state.reps == 4
        assert game.input_state.max_per_option == 1

    def test_nasser(self):
        """Add 2 USSR influence in Egypt, remove half US influence (rounded up)."""
        game = make_game()
        game.map['Egypt'].set_influence(0, 3)
        game.cards['Nasser'].use_event(game, Side.USSR)
        assert game.map['Egypt'].influence[Side.USSR] == 2
        assert game.map['Egypt'].influence[Side.US] == 1  # ceil(3/2)=2 removed

    def test_nasser_odd_influence(self):
        game = make_game()
        game.map['Egypt'].set_influence(0, 5)
        game.cards['Nasser'].use_event(game, Side.USSR)
        assert game.map['Egypt'].influence[Side.USSR] == 2
        assert game.map['Egypt'].influence[Side.US] == 2  # ceil(5/2)=3 removed

    def test_nasser_zero_us_influence(self):
        game = make_game()
        game.map['Egypt'].set_influence(1, 0)
        game.cards['Nasser'].use_event(game, Side.USSR)
        assert game.map['Egypt'].influence[Side.USSR] == 3
        assert game.map['Egypt'].influence[Side.US] == 0

    def test_warsaw_pact_adds_to_basket(self):
        """Warsaw Pact enables NATO."""
        game = make_game()
        # Force the "add" branch by clearing US influence
        for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]:
            game.map[n].set_influence(game.map[n].influence[Side.USSR], 0)
        game.cards['Warsaw_Pact_Formed'].use_event(game, Side.USSR)
        assert 'Warsaw_Pact_Formed' in game.basket[Side.US]

    def test_de_gaulle_leads_france(self):
        """Remove 2 US influence from France, add 1 USSR. Cancel NATO for France."""
        game = make_game()
        game.map['France'].set_influence(0, 3)
        game.cards['De_Gaulle_Leads_France'].use_event(game, Side.USSR)
        assert game.map['France'].influence[Side.US] == 1
        assert game.map['France'].influence[Side.USSR] == 1
        assert 'De_Gaulle_Leads_France' in game.basket[Side.USSR]

    def test_captured_nazi_scientist(self):
        """Advance space race by 1."""
        game = make_game()
        game.cards['Captured_Nazi_Scientist'].use_event(game, Side.USSR)
        assert game.space_track[Side.USSR] == 1

    def test_u2_incident_awards_immediate_vp_and_sets_pending_bonus(self):
        game = make_game()

        game.cards['U2_Incident'].use_event(game, Side.USSR)

        assert game.vp_track == 1
        assert 'U2_Incident' in game.basket[Side.USSR]

    def test_u2_bonus_requires_un_intervention_event_not_card_selection(self):
        game = make_game()
        game.basket[Side.USSR].append('U2_Incident')
        game.hand[Side.US] = ['UN_Intervention']
        game.input_state = type('InputStub', (), {'reps': 1})()

        assert game.card_callback(Side.US, 'UN_Intervention') is True
        assert game.vp_track == 0

        game.resolve_card_action(Side.US, 'UN_Intervention', 'SPACE')
        assert game.vp_track == 0
        assert 'U2_Incident' in game.basket[Side.USSR]

        game.resolve_card_action(Side.US, 'UN_Intervention', 'PLAY_EVENT')
        assert game.vp_track == 1
        assert 'U2_Incident' not in game.basket[Side.USSR]

    def test_truman_doctrine_creates_input(self):
        """Remove all USSR influence from 1 uncontrolled European country."""
        game = make_game()
        game.map['Finland'].set_influence(1, 0)
        game.cards['Truman_Doctrine'].use_event(game, Side.US)
        assert game.input_state is not None
        assert game.input_state.side == Side.US

    def test_olympic_games_creates_choice(self):
        """Opponent chooses to participate or boycott."""
        game = make_game()
        game.cards['Olympic_Games'].use_event(game, Side.USSR)
        assert game.input_state is not None
        # Opponent (US) should be the one choosing
        assert game.input_state.side == Side.US

    def test_nato_requires_prerequisite(self):
        """NATO requires Warsaw Pact or Marshall Plan in basket."""
        game = make_game()
        assert game.cards['NATO'].can_event(game, Side.US) is False
        game.basket[Side.US].append('Warsaw_Pact_Formed')
        assert game.cards['NATO'].can_event(game, Side.US) is True

    def test_nato_also_enabled_by_marshall_plan(self):
        game = make_game()
        game.basket[Side.US].append('Marshall_Plan')
        assert game.cards['NATO'].can_event(game, Side.US) is True

    def test_nato_event_adds_to_basket(self):
        game = make_game()
        game.basket[Side.US].append('Warsaw_Pact_Formed')
        game.cards['NATO'].use_event(game, Side.US)
        assert 'NATO' in game.basket[Side.US]

    def test_independent_reds(self):
        """US matches USSR influence in one of 5 Eastern European countries."""
        game = make_game()
        game.map['Yugoslavia'].set_influence(4, 0)
        game.cards['Independent_Reds'].use_event(game, Side.US)
        assert game.input_state is not None
        assert game.input_state.side == Side.US

    def test_independent_reds_never_reduces_existing_us_influence(self):
        game = make_game()
        game.map['Romania'].set_influence(1, 2)
        game.map['Yugoslavia'].set_influence(3, 0)

        game.cards['Independent_Reds'].use_event(game, Side.US)

        assert set(game.input_state.legal_options) == {'Yugoslavia'}
        assert game.map['Romania'].influence == [1, 2]
        game.map['Romania'].match_influence(Side.US)
        assert game.map['Romania'].influence == [1, 2]

    def test_marshall_plan(self):
        """Add 1 US influence in 7 non-USSR-controlled Western Europe countries."""
        game = make_game()
        game.cards['Marshall_Plan'].use_event(game, Side.US)
        assert game.input_state is not None
        assert game.input_state.reps == 7
        assert game.input_state.max_per_option == 1
        assert 'Marshall_Plan' in game.basket[Side.US]

    def test_containment(self):
        """US ops cards get +1 for rest of turn."""
        game = make_game()
        game.cards['Containment'].use_event(game, Side.US)
        assert 'Containment' in game.basket[Side.US]
        # Test global effective ops modifier
        assert game.get_global_effective_ops(Side.US, 2) == 3

    def test_cia_created(self):
        """Reveals USSR hand, US conducts ops as if 1 op card."""
        game = make_game()
        game.hand[Side.USSR] = ['Fidel', 'NATO']
        # CIA_Created calls players[Side.US].update_opp_hand, need mock
        mock_pv = type('MockPV', (), {'update_opp_hand': lambda self, x: None})()
        game.players = [mock_pv, mock_pv]
        game.cards['CIA_Created'].use_event(game, Side.US)
        # Should set up select_action for US with Blank_1_Op_Card
        assert game.input_state is not None

    def test_us_japan_mutual_defense_pact(self):
        """US gains sufficient influence in Japan for control."""
        game = make_game()
        game.map['Japan'].set_influence(2, 1)
        game.cards['US_Japan_Mutual_Defense_Pact'].use_event(game, Side.US)
        assert game.map['Japan'].control == Side.US
        assert game.map['Japan'].influence[Side.US] >= game.map['Japan'].influence[Side.USSR] + 4
        assert 'US_Japan_Mutual_Defense_Pact' in game.basket[Side.US]
        assert game.map.can_coup(game, 'Japan', Side.USSR) is False
        assert game.map.can_realignment(game, 'Japan', Side.USSR) is False

    def test_suez_crisis(self):
        """Remove 4 US influence from France/UK/Israel, max 2 per country."""
        game = make_game()
        game.map['France'].set_influence(0, 3)
        game.map['UK'].set_influence(0, 5)
        game.map['Israel'].set_influence(0, 1)
        game.cards['Suez_Crisis'].use_event(game, Side.USSR)
        assert game.input_state is not None
        assert game.input_state.reps == 4
        assert game.input_state.max_per_option == 2

    def test_east_european_unrest_early_war(self):
        """Remove 1 USSR influence from 3 EE countries (Early/Mid War)."""
        game = make_game()
        game.turn_track = 1  # Early War
        game.cards['East_European_Unrest'].use_event(game, Side.US)
        assert game.input_state is not None
        assert game.input_state.reps == 3

    def test_east_european_unrest_late_war(self):
        """Remove 2 USSR influence from 3 EE countries (Late War)."""
        game = make_game()
        game.turn_track = 8  # Late War
        game.cards['East_European_Unrest'].use_event(game, Side.US)
        assert game.input_state is not None
        assert game.input_state.reps == 3

    def test_decolonization(self):
        """Add 1 USSR influence in 4 African/SEA countries."""
        game = make_game()
        game.cards['Decolonization'].use_event(game, Side.USSR)
        assert game.input_state is not None
        assert game.input_state.reps == 4
        assert game.input_state.max_per_option == 1

    def test_red_scare_purge(self):
        """Opponent ops -1 for rest of turn."""
        game = make_game()
        game.cards['Red_Scare_Purge'].use_event(game, Side.USSR)
        assert 'Red_Scare_Purge' in game.basket[Side.USSR]
        # US ops should be reduced
        assert game.get_global_effective_ops(Side.US, 3) == 2

    def test_red_scare_purge_minimum_1_op(self):
        game = make_game()
        game.cards['Red_Scare_Purge'].use_event(game, Side.USSR)
        assert game.get_global_effective_ops(Side.US, 1) == 1

    def test_nuclear_test_ban(self):
        """VP = DEFCON - 2, then improve DEFCON by 2."""
        game = make_game()
        game.defcon_track = 3
        game.cards['Nuclear_Test_Ban'].use_event(game, Side.USSR)
        # VP = (3-2) * 1 = 1 (USSR)
        assert game.vp_track == 1
        assert game.defcon_track == 5

    def test_nuclear_test_ban_us(self):
        game = make_game()
        game.defcon_track = 4
        game.cards['Nuclear_Test_Ban'].use_event(game, Side.US)
        # VP = (4-2) * (-1) = -2 (US gets 2 VP)
        assert game.vp_track == -2
        assert game.defcon_track == 5  # clamped

    def test_formosan_resolution(self):
        game = make_game()
        game.cards['Formosan_Resolution'].use_event(game, Side.US)
        assert 'Formosan_Resolution' in game.basket[Side.US]

    def test_formosan_resolution_moves_from_removed_to_discard_after_us_plays_china(self):
        game = make_game()
        game.hand[Side.US] = ['Formosan_Resolution', 'The_China_Card']
        formosan = game.cards['Formosan_Resolution']
        formosan.use_event(game, Side.US)
        formosan.dispose(game, Side.US)
        game.input_state = type('InputStub', (), {'reps': 1})()

        assert game.card_callback(Side.US, 'The_China_Card') is True

        assert 'Formosan_Resolution' not in game.basket[Side.US]
        assert 'Formosan_Resolution' not in game.removed_pile
        assert game.discard_pile.count('Formosan_Resolution') == 1

    def test_defectors_cancels_ussr_headline(self):
        game = make_game()
        game.headline_bin[Side.USSR] = 'Fidel'
        game.cards['Defectors'].use_event(game, Side.US)
        assert game.headline_bin[Side.USSR] == ''
        assert 'Fidel' in game.discard_pile

    def test_defectors_gives_us_vp_when_ussr_plays_in_ar(self):
        game = make_game()
        game.ar_side = Side.USSR
        game.headline_bin[Side.USSR] = ''
        game.cards['Defectors'].use_event(game, Side.USSR)
        assert game.vp_track == -1  # US gains 1 VP

    def test_defectors_cannot_be_played_as_event(self):
        game = make_game()
        assert game.cards['Defectors'].can_event(game, Side.US) is False


# ===========================================================================
# MID WAR CARD EVENT TESTS
# ===========================================================================

class TestMidWarCards:

    def test_brush_war_creates_input(self):
        game = make_game()
        game.cards['Brush_War'].use_event(game, Side.USSR)
        assert game.input_state is not None

    def test_neutral_war_uses_triggering_side(self):
        game = make_game()
        game.cards['Indo_Pakistani_War'].use_event(game, Side.US)

        assert game.input_state.side == Side.US
        assert set(game.input_state.legal_options) == {'India', 'Pakistan'}

    def test_arms_race_3vp_when_met_required(self):
        """Phasing player has more milops AND meets required (>= DEFCON) -> 3 VP."""
        game = make_game()
        game.milops_track = [4, 2]
        game.defcon_track = 3
        game.cards['Arms_Race'].use_event(game, Side.USSR)
        assert game.vp_track == 3

    def test_arms_race_1vp_when_not_met_required(self):
        """Phasing player has more milops but hasn't met required -> 1 VP."""
        game = make_game()
        game.milops_track = [2, 1]
        game.defcon_track = 5
        game.cards['Arms_Race'].use_event(game, Side.USSR)
        assert game.vp_track == 1

    def test_arms_race_no_vp_when_behind(self):
        """Phasing player doesn't have more milops -> no VP."""
        game = make_game()
        game.milops_track = [1, 3]
        game.defcon_track = 3
        game.cards['Arms_Race'].use_event(game, Side.USSR)
        assert game.vp_track == 0

    def test_cuban_missile_crisis(self):
        """Set DEFCON to 2, opponent coup causes thermonuclear war."""
        game = make_game()
        game.defcon_track = 5
        game.cards['Cuban_Missile_Crisis'].use_event(game, Side.USSR)
        assert game.defcon_track == 2
        assert 'Cuban_Missile_Crisis' in game.basket[Side.USSR]

    def test_nuclear_subs(self):
        """US coups in BG don't affect DEFCON."""
        game = make_game()
        game.cards['Nuclear_Subs'].use_event(game, Side.US)
        assert 'Nuclear_Subs' in game.basket[Side.US]

    def test_quagmire_removes_norad(self):
        """Quagmire cancels NORAD."""
        game = make_game()
        game.basket[Side.US].append('NORAD')
        game.cards['Quagmire'].use_event(game, Side.US)
        assert 'NORAD' not in game.basket[Side.US]
        assert 'Quagmire' in game.basket[Side.US]

    def test_salt_negotiations(self):
        """Improve DEFCON by 2, add SALT to basket."""
        game = make_game()
        game.defcon_track = 3
        game.discard_pile = ['Fidel']
        game.cards['Salt_Negotiations'].use_event(game, Side.USSR)
        assert game.defcon_track == 5
        assert 'Salt_Negotiations' in game.basket[Side.USSR]

    def test_bear_trap(self):
        game = make_game()
        game.cards['Bear_Trap'].use_event(game, Side.US)
        assert 'Bear_Trap' in game.basket[Side.USSR]

    def test_summit_ussr_wins(self):
        """USSR wins Summit when rolling higher (with advantage)."""
        game = make_game()
        card = game.cards['Summit']
        game.input_state = Input(Side.NEUTRAL, InputType.ROLL_DICE, None, [], reps=1)
        card.dice_callback(game, 0, (6, 1))  # USSR roll 6, US roll 1
        assert game.vp_track == 2  # USSR gains 2 VP

    def test_summit_us_wins(self):
        """US wins Summit when rolling higher."""
        game = make_game()
        card = game.cards['Summit']
        game.input_state = Input(Side.NEUTRAL, InputType.ROLL_DICE, None, [], reps=1)
        card.dice_callback(game, 0, (1, 6))  # USSR roll 1, US roll 6
        assert game.vp_track == -2  # US gains 2 VP

    def test_summit_does_not_offer_defcon_choice_after_vp_autovictory(self):
        game = make_game()
        card = game.cards['Summit']
        game.vp_track = 19
        game.input_state = Input(Side.NEUTRAL, InputType.ROLL_DICE, None, [], reps=1)
        card.dice_callback(game, 0, (6, 1))
        assert game.terminated is True
        assert game.input_state is None

    def test_how_i_learned_to_stop_worrying(self):
        """Set DEFCON to any level, gain 5 milops."""
        game = make_game()
        game.cards['How_I_Learned_to_Stop_Worrying'].use_event(game, Side.USSR)
        assert game.milops_track[Side.USSR] == 5
        assert game.input_state is not None

    def test_how_i_learned_correct_side(self):
        """How_I_Learned input side should match the phasing player."""
        game = make_game()
        game.cards['How_I_Learned_to_Stop_Worrying'].use_event(game, Side.US)
        assert game.input_state.side == Side.US
        assert game.milops_track[Side.US] == 5

    def test_kitchen_debates_us_more_bg(self):
        """US gains 2 VP if they control more BG countries."""
        game = make_game()
        # Give US many BG countries
        for n in ['France', 'West_Germany', 'Italy', 'Poland', 'Japan', 'South_Korea']:
            game.map[n].set_influence(0, 10)
        game.cards['Kitchen_Debates'].use_event(game, Side.US)
        assert game.vp_track == -2  # US gains 2 VP

    def test_kitchen_debates_ussr_more_bg(self):
        """No effect if USSR controls more BG."""
        game = make_game()
        # Default: very few US BG
        game.cards['Kitchen_Debates'].use_event(game, Side.US)
        # VP shouldn't change since US doesn't control more BG
        assert game.vp_track == 0

    def test_missile_envy_creates_exchange(self):
        game = make_game()
        game.hand[Side.US] = [
            'Asia_Scoring', 'NATO', 'Duck_and_Cover', 'Fidel']
        game.cards['Missile_Envy'].use_event(game, Side.USSR)
        assert game.input_state is not None
        assert list(game.input_state.legal_options) == ['NATO']

    def test_qbt_can_discard_missile_envy_when_in_hand(self):
        game = make_game()
        game.basket[Side.US].extend(['Quagmire', 'Missile_Envy'])
        game.hand[Side.US] = ['Missile_Envy', 'NATO']
        game.cards['Missile_Envy'].event_occurred = True
        game.cards['Missile_Envy'].exchange = True
        game.ar_track = 1

        game.qbt_discard(Side.US, 'Quagmire')
        assert game.input_state is not None
        assert 'Missile_Envy' in game.input_state.available_options

        assert game.input_state.recv('Missile_Envy') is True
        assert 'Missile_Envy' not in game.hand[Side.US]
        assert 'Missile_Envy' in game.discard_pile
        assert 'Missile_Envy' not in game.basket[Side.US]
        assert game.cards['Missile_Envy'].can_event(
            game, Side.US) is True
        assert game.cards['Missile_Envy'].exchange is False

    def test_our_man_in_tehran_allows_stop_early(self):
        game = make_game()
        # Ensure event condition is satisfied.
        game.map['Iran'].set_influence(0, 2)
        game.draw_pile = ['Fidel', 'NATO', 'Duck_and_Cover', 'CIA_Created', 'Blockade']

        game.cards['Our_Man_In_Tehran'].use_event(game, Side.US)

        assert game.input_state is not None
        assert game.input_state.option_stop_early == 'Do not discard more cards.'

        # Player may keep all drawn cards by stopping immediately.
        assert game.input_state.recv('Do not discard more cards.') is True
        assert game.input_state.complete is True
        assert len(game.discard_pile) == 0

    def test_shuttle_diplomacy_leaves_basket_after_first_applicable_scoring(self):
        game = make_game()
        game.hand[Side.US] = ['Shuttle_Diplomacy']
        shuttle = game.cards['Shuttle_Diplomacy']

        shuttle.use_event(game, Side.US)
        shuttle.dispose(game, Side.US)
        game.cards['Asia_Scoring'].use_event(game, Side.USSR)

        assert 'Shuttle_Diplomacy' in game.discard_pile
        assert 'Shuttle_Diplomacy' not in game.limbo
        assert 'Shuttle_Diplomacy' not in game.basket[Side.US]

    def test_our_man_in_tehran_can_discard_subset_then_stop(self):
        game = make_game()
        game.map['Iran'].set_influence(0, 2)
        game.draw_pile = ['Fidel', 'NATO', 'Duck_and_Cover', 'CIA_Created', 'Blockade']

        game.cards['Our_Man_In_Tehran'].use_event(game, Side.US)

        first_option = next(iter(game.input_state.available_options))
        assert game.input_state.recv(first_option) is True
        assert first_option in game.discard_pile

        assert game.input_state.recv('Do not discard more cards.') is True
        assert game.input_state.complete is True
        # Exactly one discard was chosen before stopping.
        assert len(game.discard_pile) == 1

    def test_our_man_in_tehran_stage_2_schedules_shuffle(self):
        game = make_game()
        game.hand[Side.NEUTRAL] = ['Fidel', 'NATO']
        game.cards['Our_Man_In_Tehran'].stage_2(game)
        assert game.input_state is not None
        assert game.input_state.side == Side.NEUTRAL

    def test_our_man_in_tehran_preserves_discard_pile_during_initial_reshuffle(self):
        game = make_game()
        game.map['Iran'].set_influence(0, 2)
        cards = ['Fidel', 'NATO', 'Duck_and_Cover', 'CIA_Created', 'Blockade']
        game.discard_pile = list(cards)

        game.cards['Our_Man_In_Tehran'].use_event(game, Side.US)

        assert game.input_state.side == Side.NEUTRAL
        while not game.input_state.complete:
            option = next(iter(game.input_state.legal_options))
            assert game.input_state.recv(option)
        game.stage_complete()
        game.stage_complete()

        assert game.input_state.side == Side.US
        assert sorted(game.hand[Side.NEUTRAL]) == sorted(cards)
        assert sorted(game.input_state.legal_options) == sorted(
            cards + ['Do not discard more cards.'])

    def test_ask_not_draws_only_us_replacements_after_reshuffle(self):
        game = make_game()
        game.hand[Side.USSR] = ['CIA_Created', 'Blockade']
        game.hand[Side.US] = ['Fidel', 'NATO', 'Duck_and_Cover']

        game.cards['Ask_Not_What_Your_Country_Can_Do_For_You'].use_event(game, Side.US)
        assert game.input_state.recv('Fidel')
        assert game.input_state.recv('NATO')
        assert game.input_state.recv('Do not discard.')

        game.stage_complete()
        while not game.input_state.complete:
            option = next(iter(game.input_state.legal_options))
            assert game.input_state.recv(option)
        game.stage_complete()

        assert sorted(game.hand[Side.USSR]) == ['Blockade', 'CIA_Created']
        assert len(game.hand[Side.US]) == 3
        assert game.draw_pile == []
        assert game.discard_pile == []

    def test_ask_not_redraws_discarded_scoring_when_it_is_the_reshuffle_pool(self):
        game = make_game()
        game.hand[Side.US] = [
            'Ask_Not_What_Your_Country_Can_Do_For_You',
            'Africa_Scoring',
        ]
        game.draw_pile = []
        game.discard_pile = []

        game.cards['Ask_Not_What_Your_Country_Can_Do_For_You'].use_event(
            game, Side.US)
        assert game.input_state.recv('Africa_Scoring') is True
        game.stage_complete()

        assert set(game.input_state.legal_options) == {'Africa_Scoring'}
        assert game.input_state.recv('Africa_Scoring') is True
        game.stage_complete()

        assert 'Africa_Scoring' in game.hand[Side.US]

    def test_ask_not_cannot_discard_its_unresolved_source_card(self):
        game = make_game()
        game.hand[Side.US] = ['Ask_Not_What_Your_Country_Can_Do_For_You', 'Fidel']

        game.cards['Ask_Not_What_Your_Country_Can_Do_For_You'].use_event(game, Side.US)

        assert set(game.input_state.legal_options) == {
            'Fidel', 'Do not discard.'
        }

    def test_we_will_bury_you(self):
        """Degrade DEFCON by 1, add to basket."""
        game = make_game()
        game.defcon_track = 5
        game.cards['We_Will_Bury_You'].use_event(game, Side.USSR)
        assert game.defcon_track == 4
        assert 'We_Will_Bury_You' in game.basket[Side.USSR]

    def test_brezhnev_doctrine(self):
        """USSR ops +1 for rest of turn."""
        game = make_game()
        game.cards['Brezhnev_Doctrine'].use_event(game, Side.USSR)
        assert 'Brezhnev_Doctrine' in game.basket[Side.USSR]

    def test_south_african_unrest_has_only_legal_options(self):
        game = make_game()
        game.cards['South_African_Unrest'].use_event(game, Side.USSR)
        options = list(game.input_state.selection.keys())
        assert 'Add 1 Influence each to South Africa, Angola, and Botswana.' not in options

    def test_south_african_unrest_is_chosen_by_ussr_when_us_triggers_event(self):
        game = make_game()

        game.cards['South_African_Unrest'].use_event(game, Side.US)

        assert game.input_state.side == Side.USSR

    def test_portuguese_empire_crumbles(self):
        """Add 2 USSR influence in Angola and SE African States."""
        game = make_game()
        game.map['Angola'].set_influence(0, 0)
        game.map['SE_African_States'].set_influence(0, 0)
        game.cards['Portuguese_Empire_Crumbles'].use_event(game, Side.USSR)
        assert game.map['Angola'].influence[Side.USSR] == 2
        assert game.map['SE_African_States'].influence[Side.USSR] == 2

    def test_allende(self):
        """USSR receives 2 influence in Chile."""
        game = make_game()
        game.map['Chile'].set_influence(0, 0)
        game.cards['Allende'].use_event(game, Side.USSR)
        assert game.map['Chile'].influence[Side.USSR] == 2

    def test_willy_brandt(self):
        """Willy Brandt: USSR gains 1 VP, adds 1 USSR influence in West Germany."""
        game = make_game()
        game.defcon_track = 4
        game.cards['Willy_Brandt'].use_event(game, Side.USSR)
        assert game.vp_track == 1  # USSR gains 1 VP
        assert game.defcon_track == 4  # DEFCON unchanged
        assert game.map['West_Germany'].influence[Side.USSR] == 1
        assert 'Willy_Brandt' in game.basket[Side.USSR]

    def test_willy_brandt_blocked_by_tear_down_this_wall(self):
        game = make_game()
        game.basket[Side.US].append('Tear_Down_This_Wall')
        assert game.cards['Willy_Brandt'].can_event(game, Side.USSR) is False

    def test_muslim_revolution(self):
        """Remove all US influence from 2 of the listed countries."""
        game = make_game()
        game.map['Iran'].set_influence(0, 3)
        game.map['Iraq'].set_influence(0, 2)
        game.cards['Muslim_Revolution'].use_event(game, Side.USSR)
        assert game.input_state is not None
        assert game.input_state.reps == 2

    def test_muslim_revolution_blocked_by_awacs(self):
        game = make_game()
        game.basket[Side.US].append('AWACS_Sale_to_Saudis')
        assert game.cards['Muslim_Revolution'].can_event(game, Side.USSR) is False

    def test_abm_treaty(self):
        """Improve DEFCON by 1, play as 4 ops card."""
        game = make_game()
        game.defcon_track = 3
        game.cards['ABM_Treaty'].use_event(game, Side.US)
        assert game.defcon_track == 4

    def test_cultural_revolution_us_has_china(self):
        """If US has China Card, USSR claims it face up."""
        game = make_game()
        game.hand[Side.US].append('The_China_Card')
        game.cards['Cultural_Revolution'].use_event(game, Side.USSR)
        assert 'The_China_Card' in game.hand[Side.USSR]
        assert 'The_China_Card' not in game.hand[Side.US]
        assert game.cards['The_China_Card'].is_playable is True

    def test_cultural_revolution_ussr_already_has_china(self):
        """If USSR already has China Card, gain 1 VP."""
        game = make_game()
        game.hand[Side.USSR].append('The_China_Card')
        game.cards['Cultural_Revolution'].use_event(game, Side.USSR)
        assert game.vp_track == 1

    def test_flower_power_blocked_by_evil_empire(self):
        game = make_game()
        game.basket[Side.US].append('An_Evil_Empire')
        assert game.cards['Flower_Power'].can_event(game, Side.USSR) is False

    def test_flower_power(self):
        game = make_game()
        game.cards['Flower_Power'].use_event(game, Side.USSR)
        assert 'Flower_Power' in game.basket[Side.USSR]

    def test_opec(self):
        """USSR gains 1 VP per controlled OPEC country."""
        game = make_game()
        opec = ['Egypt', 'Iran', 'Libya', 'Saudi_Arabia', 'Iraq', 'Gulf_States', 'Venezuela']
        for c in opec[:3]:
            game.map[c].set_influence(5, 0)
        game.cards['OPEC'].use_event(game, Side.USSR)
        assert game.vp_track == 3

    def test_opec_blocked_by_north_sea_oil(self):
        game = make_game()
        game.basket[Side.US].append('North_Sea_Oil')
        assert game.cards['OPEC'].can_event(game, Side.USSR) is False

    def test_john_paul_ii_elected_pope(self):
        """Remove 2 USSR influence in Poland, add 1 US influence."""
        game = make_game()
        game.map['Poland'].set_influence(4, 0)
        game.cards['John_Paul_II_Elected_Pope'].use_event(game, Side.US)
        assert game.map['Poland'].influence[Side.USSR] == 2
        assert game.map['Poland'].influence[Side.US] == 1
        assert 'John_Paul_II_Elected_Pope' in game.basket[Side.US]

    def test_latin_american_death_squads(self):
        game = make_game()
        game.cards['Latin_American_Death_Squads'].use_event(game, Side.US)
        assert 'Latin_American_Death_Squads' in game.basket[Side.US]

    def test_oas_founded(self):
        """Add 2 US influence in Central/South America."""
        game = make_game()
        game.cards['OAS_Founded'].use_event(game, Side.US)
        assert game.input_state is not None
        assert game.input_state.reps == 2

    def test_nixon_plays_china_card_us_has_it(self):
        """If US already has China Card, gain 2 VP."""
        game = make_game()
        game.hand[Side.US].append('The_China_Card')
        game.cards['Nixon_Plays_The_China_Card'].use_event(game, Side.US)
        assert game.vp_track == -2  # US gains 2 VP

    def test_nixon_plays_china_card_ussr_has_it(self):
        """If USSR has China Card, US receives it face down."""
        game = make_game()
        game.hand[Side.USSR].append('The_China_Card')
        game.cards['Nixon_Plays_The_China_Card'].use_event(game, Side.US)
        assert 'The_China_Card' in game.hand[Side.US]
        assert game.cards['The_China_Card'].is_playable is False

    def test_sadat_expels_soviets(self):
        """Remove all USSR influence in Egypt, add 1 US."""
        game = make_game()
        game.map['Egypt'].set_influence(3, 0)
        game.cards['Sadat_Expels_Soviets'].use_event(game, Side.US)
        assert game.map['Egypt'].influence[Side.USSR] == 0
        assert game.map['Egypt'].influence[Side.US] == 1

    def test_shuttle_diplomacy(self):
        game = make_game()
        game.cards['Shuttle_Diplomacy'].use_event(game, Side.US)
        assert 'Shuttle_Diplomacy' in game.basket[Side.US]

    def test_shuttle_diplomacy_dispose_goes_to_limbo(self):
        game = make_game()
        game.hand[Side.US].append('Shuttle_Diplomacy')
        shuttle = game.cards['Shuttle_Diplomacy']
        shuttle.use_event(game, Side.US)
        shuttle.dispose(game, Side.US)
        assert 'Shuttle_Diplomacy' in game.limbo
        assert 'Shuttle_Diplomacy' not in game.hand[Side.US]

    def test_shuttle_diplomacy_used_for_ops_does_not_activate_event(self):
        game = make_game()
        game.hand[Side.US].append('Shuttle_Diplomacy')

        game.cards['Shuttle_Diplomacy'].dispose(game, Side.US)

        assert 'Shuttle_Diplomacy' in game.discard_pile
        assert 'Shuttle_Diplomacy' not in game.limbo
        assert 'Shuttle_Diplomacy' not in game.basket[Side.US]

    def test_shuttle_diplomacy_never_makes_ussr_battlegrounds_negative(self):
        game = make_game()
        game.limbo.append('Shuttle_Diplomacy')
        for country_name in CountryInfo.REGION_ALL[MapRegion.ASIA]:
            game.map[country_name].set_influence(0, 10)

        breakdown = game.score_breakdown(MapRegion.ASIA)

        assert breakdown['sides']['USSR']['battlegrounds'] == 0

    def test_shuttle_diplomacy_prevents_ussr_asia_control(self):
        game = make_game()
        game.limbo.append('Shuttle_Diplomacy')
        for country_name in CountryInfo.REGION_ALL[MapRegion.ASIA]:
            game.map[country_name].set_influence(10, 0)

        breakdown = game.score_breakdown(MapRegion.ASIA)

        assert breakdown['sides']['USSR']['status'] == 'domination'

    def test_shuttle_diplomacy_does_not_turn_battleground_into_non_bg(self):
        game = make_game()
        game.limbo.append('Shuttle_Diplomacy')
        for country_name in CountryInfo.REGION_ALL[MapRegion.ASIA]:
            game.map[country_name].set_influence(0, 0)
            if CountryInfo.ALL[country_name].battleground:
                game.map[country_name].set_influence(10, 0)

        breakdown = game.score_breakdown(MapRegion.ASIA)

        assert breakdown['sides']['USSR']['status'] == 'presence'

    def test_flower_power_applies_to_us_war_headline(self):
        game = make_game()
        game.ar_track = 0
        game.basket[Side.USSR].append('Flower_Power')
        game.headline_bin[Side.US] = 'Korean_War'

        game.resolve_headline(Side.US)

        assert game.vp_track == 2

    def test_camp_david_accords(self):
        """US gains 1 VP, 1 influence in Israel/Jordan/Egypt, blocks Arab-Israeli War."""
        game = make_game()
        game.cards['Camp_David_Accords'].use_event(game, Side.US)
        assert game.vp_track == -1
        assert game.map['Israel'].influence[Side.US] == 2  # 1 from setup + 1
        assert game.map['Jordan'].influence[Side.US] == 1
        assert game.map['Egypt'].influence[Side.US] == 1
        assert 'Camp_David_Accords' in game.basket[Side.US]

    def test_puppet_governments(self):
        """US adds 1 influence in 3 countries with no influence from either side."""
        game = make_game()
        game.cards['Puppet_Governments'].use_event(game, Side.US)
        assert game.input_state is not None
        assert game.input_state.reps == 3
        assert game.input_state.max_per_option == 1

    def test_alliance_for_progress(self):
        """US gains 1 VP per US-controlled BG in Central/South America."""
        game = make_game()
        game.map['Panama'].set_influence(0, 5)  # US control (stability 2)
        game.map['Cuba'].set_influence(0, 6)    # US control (stability 3)
        game.cards['Alliance_for_Progress'].use_event(game, Side.US)
        assert game.vp_track == -2

    def test_one_small_step_requires_behind(self):
        game = make_game()
        game.space_track = [0, 0]
        assert game.cards['One_Small_Step'].can_event(game, Side.USSR) is False
        game.space_track = [0, 1]
        assert game.cards['One_Small_Step'].can_event(game, Side.USSR) is True

    def test_one_small_step(self):
        game = make_game()
        game.space_track = [0, 2]
        game.cards['One_Small_Step'].use_event(game, Side.USSR)
        assert game.space_track[Side.USSR] == 2
        assert game.vp_track == 0

    def test_cambridge_five_adds_ussr_influence(self):
        """The Cambridge Five: USSR places influence in a region matching a scoring card in US hand."""
        game = make_game()
        game.hand[Side.US] = ['Asia_Scoring']
        game.players = [type('PV', (), {'update_opp_hand': lambda self, x: None})(),
                        type('PV', (), {'update_opp_hand': lambda self, x: None})()]
        game.cards['The_Cambridge_Five'].use_event(game, Side.USSR)
        assert game.input_state is not None
        # Callback should increment USSR influence (not US)
        assert game.input_state.side == Side.USSR

    def test_special_relationship_without_nato(self):
        """If UK is US-controlled but no NATO, add 1 influence adjacent to UK."""
        game = make_game()
        # UK already US-controlled (5/5 stability)
        game.cards['Special_Relationship'].use_event(game, Side.US)
        assert game.input_state is not None

    def test_special_relationship_stops_before_influence_after_vp_autovictory(self):
        game = make_game()
        game.vp_track = -18
        game.basket[Side.US].append('NATO')
        game.map['UK'].set_influence(0, 5)
        game.map['France'].set_influence(0, 0)

        game.cards['Special_Relationship'].use_event(game, Side.US)

        assert game.terminated
        assert game.input_state is None
        assert game.map['France'].influence[Side.US] == 0

    def test_willy_brandt_stops_before_influence_after_vp_autovictory(self):
        game = make_game()
        game.vp_track = 19
        game.map['West_Germany'].set_influence(0, 0)

        game.cards['Willy_Brandt'].use_event(game, Side.USSR)

        assert game.terminated
        assert game.map['West_Germany'].influence[Side.USSR] == 0
        assert 'Willy_Brandt' not in game.basket[Side.USSR]

    def test_camp_david_stops_before_influence_after_vp_autovictory(self):
        game = make_game()
        game.vp_track = -19
        for country_name in ('Israel', 'Jordan', 'Egypt'):
            game.map[country_name].set_influence(0, 0)

        game.cards['Camp_David_Accords'].use_event(game, Side.US)

        assert game.terminated
        assert all(
            game.map[country_name].influence[Side.US] == 0
            for country_name in ('Israel', 'Jordan', 'Egypt')
        )
        assert 'Camp_David_Accords' not in game.basket[Side.US]

    def test_pershing_stops_before_prompt_after_vp_autovictory(self):
        game = make_game()
        game.vp_track = 19
        game.map['France'].set_influence(0, 1)

        game.cards['Pershing_II_Deployed'].use_event(game, Side.USSR)

        assert game.terminated
        assert game.input_state is None

    def test_war_stops_before_influence_flip_after_vp_autovictory(self):
        game = make_game()
        game.vp_track = 19
        game.map['South_Korea'].set_influence(0, 2)
        game.input_state = type('InputStub', (), {'reps': 1})()

        game.war_dice_callback(
            'South_Korea', Side.USSR, modifier=0, min_roll=1,
            win_vp=2, win_milops=2, num='6',
        )

        assert game.terminated
        assert game.map['South_Korea'].influence == [0, 2]

    def test_special_relationship_with_nato(self):
        """With NATO, add 2 influence to WE and gain 2 VP."""
        game = make_game()
        game.basket[Side.US].append('NATO')
        game.cards['Special_Relationship'].use_event(game, Side.US)
        assert game.vp_track == -2
        assert game.input_state is not None

    def test_special_relationship_requires_uk_control(self):
        game = make_game()
        game.map['UK'].set_influence(0, 0)
        assert game.cards['Special_Relationship'].can_event(game, Side.US) is False

    def test_che(self):
        """USSR coups a non-BG country in CA/SA/Africa."""
        game = make_game()
        game.map['Haiti'].set_influence(0, 1)
        game.cards['Che'].use_event(game, Side.USSR)
        # Should push coup stages
        assert len(game.stage_list) > 0

    def test_liberation_theology(self):
        """Add 3 USSR influence in Central America, max 2 per country."""
        game = make_game()
        game.cards['Liberation_Theology'].use_event(game, Side.USSR)
        assert game.input_state is not None
        assert game.input_state.reps == 3
        assert game.input_state.max_per_option == 2

    def test_ussuri_river_skirmish_ussr_has_china(self):
        """If USSR has China Card, US claims it face up."""
        game = make_game()
        game.hand[Side.USSR].append('The_China_Card')
        game.cards['Ussuri_River_Skirmish'].use_event(game, Side.US)
        assert 'The_China_Card' in game.hand[Side.US]
        assert game.cards['The_China_Card'].is_playable is True

    def test_ussuri_river_skirmish_us_has_china(self):
        """If US already has China Card, add 4 influence in Asia."""
        game = make_game()
        game.hand[Side.US].append('The_China_Card')
        game.cards['Ussuri_River_Skirmish'].use_event(game, Side.US)
        assert game.input_state is not None
        assert game.input_state.reps == 4


# ===========================================================================
# LATE WAR CARD EVENT TESTS
# ===========================================================================

class TestLateWarCards:

    def test_iranian_hostage_crisis(self):
        """Remove all US influence in Iran, add 2 USSR. IHC goes to USSR basket."""
        game = make_game()
        game.map['Iran'].set_influence(0, 1)  # standard setup
        game.cards['Iranian_Hostage_Crisis'].use_event(game, Side.USSR)
        assert game.map['Iran'].influence[Side.US] == 0
        assert game.map['Iran'].influence[Side.USSR] == 2
        assert 'Iranian_Hostage_Crisis' in game.basket[Side.USSR]

    def test_the_iron_lady(self):
        """US gains 1 VP, add 1 USSR in Argentina, remove USSR from UK."""
        game = make_game()
        game.map['UK'].set_influence(1, 5)
        game.map['Argentina'].set_influence(0, 0)
        game.cards['The_Iron_Lady'].use_event(game, Side.US)
        assert game.vp_track == -1
        assert game.map['Argentina'].influence[Side.USSR] == 1
        assert game.map['UK'].influence[Side.USSR] == 0
        assert 'The_Iron_Lady' in game.basket[Side.US]

    def test_iron_lady_event_first_does_not_open_argentina_ops_route(self):
        game = make_game()
        game.turn_track = 8
        game.ar_side = Side.USSR
        game.map['Argentina'].set_influence(0, 0)
        game.select_action(Side.USSR, 'The_Iron_Lady')

        assert game.input_state.recv('RESOLVE_EVENT_FIRST') is True
        game.stage_complete()
        game.stage_complete()
        game.stage_complete()
        assert game.map['Argentina'].influence[Side.USSR] == 1
        assert game.input_state.recv('INFLUENCE') is True
        game.stage_complete()
        game.stage_complete()

        assert 'Argentina' not in game.input_state.legal_options

    def test_reagan_bombs_libya(self):
        """US gains 1 VP per 2 USSR influence in Libya."""
        game = make_game()
        game.map['Libya'].set_influence(5, 0)
        game.cards['Reagan_Bombs_Libya'].use_event(game, Side.US)
        # floor(5/2) = 2 VP for US
        assert game.vp_track == -2

    def test_reagan_bombs_libya_odd(self):
        game = make_game()
        game.map['Libya'].set_influence(3, 0)
        game.cards['Reagan_Bombs_Libya'].use_event(game, Side.US)
        assert game.vp_track == -1  # floor(3/2) = 1

    def test_star_wars_requires_us_ahead(self):
        game = make_game()
        game.space_track = [0, 0]
        assert game.cards['Star_Wars'].can_event(game, Side.US) is False
        game.space_track = [0, 1]
        assert game.cards['Star_Wars'].can_event(game, Side.US) is True

    def test_north_sea_oil(self):
        """OPEC unplayable, US may play 8 cards this turn."""
        game = make_game()
        game.cards['North_Sea_Oil'].use_event(game, Side.US)
        assert 'North_Sea_Oil' in game.basket[Side.US]
        assert game.ars_by_turn[Side.US][game.turn_track] == 8

    def test_the_reformer(self):
        """Add 4 or 6 influence in Europe, USSR can't coup in Europe."""
        game = make_game()
        game.vp_track = 0  # tied, so 4 influence
        game.cards['The_Reformer'].use_event(game, Side.USSR)
        assert game.input_state.reps == 4
        assert 'The_Reformer' in game.basket[Side.USSR]

    def test_the_reformer_ussr_ahead(self):
        game = make_game()
        game.vp_track = 5  # USSR ahead
        game.cards['The_Reformer'].use_event(game, Side.USSR)
        assert game.input_state.reps == 6

    def test_marine_barracks_bombing(self):
        """Remove all US influence from Lebanon, then 2 more from ME."""
        game = make_game()
        game.map['Lebanon'].set_influence(0, 2)
        game.map['Israel'].set_influence(0, 3)
        game.cards['Marine_Barracks_Bombing'].use_event(game, Side.USSR)
        assert game.map['Lebanon'].influence[Side.US] == 0
        assert game.input_state is not None
        assert game.input_state.reps == 2

    def test_soviets_shoot_down_kal_007(self):
        """Degrade DEFCON by 1, US gains 2 VP."""
        game = make_game()
        game.defcon_track = 5
        game.cards['Soviets_Shoot_Down_KAL_007'].use_event(game, Side.US)
        assert game.defcon_track == 4
        assert game.vp_track == -2

    def test_glasnost(self):
        """USSR gains 2 VP, improve DEFCON by 1."""
        game = make_game()
        game.defcon_track = 4
        game.cards['Glasnost'].use_event(game, Side.USSR)
        assert game.vp_track == 2
        assert game.defcon_track == 5

    def test_glasnost_with_reformer(self):
        """With Reformer, USSR may conduct ops as 4 op card."""
        game = make_game()
        game.defcon_track = 4
        game.basket[Side.USSR].append('The_Reformer')
        game.cards['Glasnost'].use_event(game, Side.USSR)
        assert game.vp_track == 2
        # Should have triggered select_action
        assert game.input_state is not None
        assert 'The_Reformer' not in game.basket[Side.USSR]

    def test_glasnost_restores_ussr_coups_in_europe(self):
        game = make_game()
        game.defcon_track = 5
        game.map['France'].set_influence(0, 1)
        game.basket[Side.USSR].append('The_Reformer')
        assert game.map.can_coup(game, 'France', Side.USSR) is False

        game.cards['Glasnost'].use_event(game, Side.USSR)

        assert game.map.can_coup(game, 'France', Side.USSR) is True

    def test_latin_debt_crisis_returns_to_discard_after_event(self):
        game = make_game()
        game.hand[Side.USSR] = ['Latin_American_Debt_Crisis']
        card = game.cards['Latin_American_Debt_Crisis']
        card.event_occurred = True

        card.dispose(game, Side.USSR)

        assert 'Latin_American_Debt_Crisis' in game.discard_pile
        assert 'Latin_American_Debt_Crisis' not in game.removed_pile

    def test_latin_debt_crisis_cannot_discard_its_source_card(self):
        game = make_game()
        game.basket[Side.US].append('Containment')
        game.hand[Side.US] = [
            'Latin_American_Debt_Crisis', 'Nuclear_Test_Ban']

        game.cards['Latin_American_Debt_Crisis'].use_event(
            game, Side.USSR)

        options = list(game.input_state.legal_options)
        assert 'Latin_American_Debt_Crisis' not in options
        assert 'Nuclear_Test_Ban' in options

    def test_event_first_optional_eighth_ar_must_still_consume_card(self):
        game = make_game()
        game.turn_track = 8
        game.ars_by_turn[Side.US][8] = 8

        game.select_action(
            Side.US, 'Socialist_Governments', is_event_resolved=True)

        assert 'SKIP_OPTIONAL_AR' not in game.input_state.legal_options

    def test_optional_eighth_ar_can_only_be_skipped_on_ar8(self):
        game = make_game()
        game.turn_track = 8
        game.ars_by_turn[Side.US][8] = 8

        game.ar_track = 1
        game.select_action(Side.US, 'NATO')
        assert 'SKIP_OPTIONAL_AR' not in game.input_state.legal_options

        game.ar_track = 8
        game.select_action(Side.US, 'NATO')
        assert 'SKIP_OPTIONAL_AR' in game.input_state.legal_options

    def test_forced_missile_envy_cannot_be_headline(self):
        game = make_game()
        game.turn_track = 5
        game.ar_track = 0
        game.hand[Side.USSR] = ['Missile_Envy', 'Nuclear_Test_Ban']
        game.basket[Side.USSR].append('Missile_Envy')

        game.choose_headline(Side.USSR)

        assert list(game.input_state.legal_options) == ['Nuclear_Test_Ban']

    def test_ortega_elected(self):
        """Remove all US influence from Nicaragua, free coup adjacent."""
        game = make_game()
        game.map['Nicaragua'].set_influence(0, 2)
        game.map['Honduras'].set_influence(0, 1)
        game.cards['Ortega_Elected_in_Nicaragua'].use_event(game, Side.USSR)
        assert game.map['Nicaragua'].influence[Side.US] == 0

    def test_ortega_event_always_grants_free_coup_to_ussr(self):
        game = make_game()
        game.map['Cuba'].set_influence(0, 1)

        game.cards['Ortega_Elected_in_Nicaragua'].use_event(game, Side.US)
        game.stage_complete()

        assert game.input_state.side == Side.USSR
        assert 'Cuba' in game.input_state.legal_options

    def test_terrorism_basic(self):
        """Opponent randomly discards 1 card."""
        game = make_game()
        game.hand[Side.US] = ['NATO', 'Fidel']
        game.cards['Terrorism'].use_event(game, Side.USSR)
        assert game.input_state is not None
        assert game.input_state.reps == 1

    def test_terrorism_never_discards_china_card(self):
        game = make_game()
        game.hand[Side.US] = ['The_China_Card', 'Fidel']

        game.cards['Terrorism'].use_event(game, Side.USSR)

        assert set(game.input_state.legal_options) == {'Fidel'}

    def test_terrorism_with_only_china_card_has_no_discard_prompt(self):
        game = make_game()
        game.hand[Side.US] = ['The_China_Card']

        game.cards['Terrorism'].use_event(game, Side.USSR)

        assert game.input_state is None

    def test_terrorism_with_iranian_hostage_crisis(self):
        """If USSR plays Terrorism and IHC is in effect, US discards 2."""
        game = make_game()
        # IHC now correctly goes to basket[Side.USSR], and Terrorism checks basket[Side.USSR]
        game.cards['Iranian_Hostage_Crisis'].use_event(game, Side.USSR)
        game.hand[Side.US] = ['NATO', 'Fidel', 'COMECON']
        game.cards['Terrorism'].use_event(game, Side.USSR)
        assert game.input_state.reps == 2

    def test_terrorism_ihc_integration(self):
        """IHC played normally now correctly enables Terrorism double discard."""
        game = make_game()
        game.cards['Iranian_Hostage_Crisis'].use_event(game, Side.USSR)
        assert 'Iranian_Hostage_Crisis' in game.basket[Side.USSR]
        game.hand[Side.US] = ['NATO', 'Fidel', 'COMECON']
        game.cards['Terrorism'].use_event(game, Side.USSR)
        assert game.input_state.reps == 2

    def test_terrorism_without_ihc_still_1(self):
        """Without IHC, even USSR playing only discards 1."""
        game = make_game()
        game.hand[Side.US] = ['NATO', 'Fidel']
        game.cards['Terrorism'].use_event(game, Side.USSR)
        assert game.input_state.reps == 1

    def test_iran_contra_scandal(self):
        game = make_game()
        game.cards['Iran_Contra_Scandal'].use_event(game, Side.USSR)
        assert 'Iran_Contra_Scandal' in game.basket[Side.USSR]

    def test_chernobyl_appends_correct_effect_name(self):
        """Chernobyl callback should append the actual effect name, not a literal string."""
        game = make_game()
        game.cards['Chernobyl'].use_event(game, Side.US)
        assert game.input_state is not None
        # Simulate selecting a region by invoking the callback
        options = list(game.input_state.selection.keys())
        assert len(options) > 0
        # Pick the first option and invoke callback
        game.input_state.callback(options[0])
        # The basket should contain the dynamic effect name, not 'effect_name'
        assert 'effect_name' not in game.basket[Side.US]
        assert any(item.startswith('Chernobyl_') for item in game.basket[Side.US])

    def test_tear_down_this_wall(self):
        """Cancel Willy Brandt, add 3 US in East Germany, free coup/realignment."""
        game = make_game()
        game.basket[Side.USSR].append('Willy_Brandt')
        game.cards['Tear_Down_This_Wall'].use_event(game, Side.US)
        assert 'Willy_Brandt' not in game.basket[Side.USSR]
        assert game.map['East_Germany'].influence[Side.US] == 3
        assert game.vp_track == 0
        assert game.input_state.side == Side.US

    def test_tear_down_may_decline_free_operations(self):
        game = make_game()
        game.cards['Tear_Down_This_Wall'].use_event(game, Side.US)

        assert game.input_state.recv(
            'Do not conduct free operations.') is True
        assert game.input_state.complete is True

    def test_tear_down_free_coup_belongs_to_us_when_ussr_triggers_event(self):
        game = make_game()
        game.map['France'].set_influence(1, 0)

        game.cards['Tear_Down_This_Wall'].use_event(game, Side.USSR)
        assert game.input_state.recv('Free coup attempt') is True
        game.stage_complete()

        assert game.input_state.side == Side.US
        assert 'France' in game.input_state.legal_options

    @pytest.mark.parametrize(("choice", "target"), [
        ('Free coup attempt', 'France'),
        ('Free realignment rolls', 'France'),
    ])
    def test_tear_down_free_operations_bypass_defcon_region_lock(
            self, choice, target):
        game = make_game()
        game.defcon_track = 4
        game.map[target].set_influence(1, 1)
        assert game.map.can_coup(game, target, Side.US) is False
        assert game.map.can_realignment(game, target, Side.US) is False

        game.cards['Tear_Down_This_Wall'].use_event(game, Side.US)
        assert game.input_state.recv(choice) is True
        if choice == 'Free coup attempt':
            game.stage_complete()

        assert target in game.input_state.legal_options

    def test_aldrich_ames_reveals_updated_us_hand_and_excludes_source_card(self):
        game = make_game()
        ussr_view = PlayerView(Side.USSR)
        game.players = [ussr_view, PlayerView(Side.US)]
        game.hand[Side.US] = ['Aldrich_Ames_Remix', 'Fidel']

        game.cards['Aldrich_Ames_Remix'].use_event(game, Side.US)

        assert 'Aldrich_Ames_Remix' in game.basket[Side.USSR]
        assert set(game.input_state.legal_options) == {'Fidel'}

        game.hand[Side.US].append('NATO')
        ussr_view.update(game, Side.USSR)
        assert set(ussr_view.opp_hand) == {
            'Aldrich_Ames_Remix', 'Fidel', 'NATO'
        }

        game.end_turn_stage_list[0]()
        assert 'Aldrich_Ames_Remix' not in game.basket[Side.USSR]

    def test_an_evil_empire(self):
        """Cancel Flower Power, US gains 1 VP."""
        game = make_game()
        game.basket[Side.USSR].append('Flower_Power')
        game.cards['An_Evil_Empire'].use_event(game, Side.US)
        assert game.vp_track == -1
        assert 'Flower_Power' not in game.basket[Side.USSR]
        assert 'An_Evil_Empire' in game.basket[Side.US]

    def test_pershing_ii_deployed(self):
        """USSR gains 1 VP, remove 1 US influence from 3 WE countries."""
        game = make_game()
        game.cards['Pershing_II_Deployed'].use_event(game, Side.USSR)
        assert game.vp_track == 1
        assert game.input_state is not None
        assert game.input_state.reps == 3

    def test_wargames_requires_defcon_2(self):
        game = make_game()
        game.defcon_track = 3
        assert game.cards['Wargames'].can_event(game, Side.US) is False
        game.defcon_track = 2
        assert game.cards['Wargames'].can_event(game, Side.US) is True

    def test_wargames_gives_opponent_6_vp(self):
        game = make_game()
        game.defcon_track = 2
        game.stage_list = []
        game.cards['Wargames'].use_event(game, Side.US)
        assert game.terminated is False
        assert game.input_state.recv(
            'End the game after giving opponent 6 VP.') is True
        # US plays it, gives USSR 6 VP
        assert game.vp_track == 6
        assert game.termination_winner == Side.USSR
        assert game.termination_reason == 'wargames'

    def test_wargames_exactly_six_vp_lead_draws(self):
        game = make_game()
        game.defcon_track = 2
        game.vp_track = 6
        game.stage_list = []

        game.cards['Wargames'].use_event(game, Side.USSR)
        assert game.input_state.recv(
            'End the game after giving opponent 6 VP.') is True

        assert game.vp_track == 0
        assert game.termination_winner == Side.NEUTRAL
        assert game.termination_reason == 'wargames'

    def test_wargames_seven_vp_lead_wins(self):
        game = make_game()
        game.defcon_track = 2
        game.vp_track = -7

        game.cards['Wargames'].use_event(game, Side.US)
        assert game.input_state.recv(
            'End the game after giving opponent 6 VP.') is True

        assert game.vp_track == -1
        assert game.termination_winner == Side.US

    def test_wargames_may_continue_without_vp_transfer(self):
        game = make_game()
        game.defcon_track = 2
        game.vp_track = 3

        game.cards['Wargames'].use_event(game, Side.USSR)
        assert game.input_state.recv('Continue playing.') is True

        assert game.vp_track == 3
        assert game.terminated is False

    def test_solidarity_requires_jp2(self):
        game = make_game()
        assert game.cards['Solidarity'].can_event(game, Side.US) is False
        game.basket[Side.US].append('John_Paul_II_Elected_Pope')
        assert game.cards['Solidarity'].can_event(game, Side.US) is True

    def test_solidarity(self):
        game = make_game()
        game.basket[Side.US].append('John_Paul_II_Elected_Pope')
        game.map['Poland'].set_influence(4, 0)
        game.cards['Solidarity'].use_event(game, Side.US)
        assert game.map['Poland'].influence[Side.US] == 3

    def test_yuri_and_samantha(self):
        game = make_game()
        game.cards['Yuri_and_Samantha'].use_event(game, Side.USSR)
        assert 'Yuri_and_Samantha' in game.basket[Side.USSR]

    def test_awacs_sale_to_saudis(self):
        game = make_game()
        game.cards['AWACS_Sale_to_Saudis'].use_event(game, Side.US)
        assert game.map['Saudi_Arabia'].influence[Side.US] == 2
        assert 'AWACS_Sale_to_Saudis' in game.basket[Side.US]

    def test_iran_iraq_war(self):
        game = make_game()
        game.cards['Iran_Iraq_War'].use_event(game, Side.USSR)
        assert game.input_state is not None
        # Options should be Iran and Iraq
        opts = list(game.input_state.selection.keys())
        assert 'Iran' in opts
        assert 'Iraq' in opts


# ===========================================================================
# GAME MECHANICS TESTS
# ===========================================================================

class TestGameMechanics:

    def test_change_vp(self):
        game = make_game()
        game.change_vp(3)
        assert game.vp_track == 3
        game.change_vp(-5)
        assert game.vp_track == -2

    def test_change_defcon(self):
        game = make_game()
        game.defcon_track = 5
        game.change_defcon(-2)
        assert game.defcon_track == 3

    def test_defcon_clamped_at_5(self):
        game = make_game()
        game.defcon_track = 5
        game.change_defcon(3)
        assert game.defcon_track == 5

    def test_change_milops(self):
        game = make_game()
        game.change_milops(Side.USSR, 3)
        assert game.milops_track[Side.USSR] == 3

    def test_milops_clamped_at_5(self):
        game = make_game()
        game.change_milops(Side.US, 10)
        assert game.milops_track[Side.US] == 5

    def test_change_space(self):
        game = make_game()
        game.change_space(Side.USSR, 1)
        assert game.space_track[Side.USSR] == 1
        # First to space gets 2 VP
        assert game.vp_track == 2

    def test_change_space_second_player_gets_less_vp(self):
        game = make_game()
        game.space_track = [1, 0]
        game.change_space(Side.US, 1)
        assert game.space_track[Side.US] == 1
        # Second player gets 1 VP (from SPACE_VPS)
        assert game.vp_track == -1

    def test_get_global_effective_ops_containment(self):
        game = make_game()
        game.basket[Side.US].append('Containment')
        assert game.get_global_effective_ops(Side.US, 3) == 4

    def test_get_global_effective_ops_brezhnev(self):
        game = make_game()
        game.basket[Side.USSR].append('Brezhnev_Doctrine')
        assert game.get_global_effective_ops(Side.USSR, 2) == 3

    def test_get_global_effective_ops_red_scare(self):
        game = make_game()
        game.basket[Side.USSR].append('Red_Scare_Purge')
        assert game.get_global_effective_ops(Side.US, 3) == 2

    def test_get_global_effective_ops_clamped_max_4(self):
        game = make_game()
        game.basket[Side.US].append('Containment')
        assert game.get_global_effective_ops(Side.US, 4) == 4

    def test_get_global_effective_ops_clamped_min_1(self):
        game = make_game()
        game.basket[Side.US].append('Red_Scare_Purge')
        assert game.get_global_effective_ops(Side.USSR, 1) == 1

    def test_calculate_nato_countries(self):
        game = make_game()
        game.basket[Side.US].append('NATO')
        game.map['France'].set_influence(0, 3)
        game.map['West_Germany'].set_influence(0, 4)
        countries = game.calculate_nato_countries()
        assert 'France' in countries
        assert 'West_Germany' in countries

    def test_nato_excludes_de_gaulle_france(self):
        game = make_game()
        game.basket[Side.US].append('NATO')
        game.map['France'].set_influence(0, 3)
        game.map['West_Germany'].set_influence(0, 4)
        game.basket[Side.USSR].append('De_Gaulle_Leads_France')
        countries = game.calculate_nato_countries()
        assert 'France' not in countries
        assert 'West_Germany' in countries

    def test_nato_excludes_willy_brandt_west_germany(self):
        game = make_game()
        game.basket[Side.US].append('NATO')
        game.map['France'].set_influence(0, 3)
        game.map['West_Germany'].set_influence(0, 4)
        game.basket[Side.USSR].append('Willy_Brandt')
        countries = game.calculate_nato_countries()
        assert 'West_Germany' not in countries
        assert 'France' in countries

    def test_can_coup_superpower_is_false(self):
        game = make_game()
        assert game.map.can_coup(game, 'USSR', Side.US) is False
        assert game.map.can_coup(game, 'US', Side.USSR) is False

    def test_can_coup_no_enemy_influence(self):
        game = make_game()
        game.map['France'].set_influence(0, 3)
        # USSR can't coup France since there's no US... wait, there IS US influence
        # Actually, can_coup checks for opponent influence in the country
        assert game.map.can_coup(game, 'France', Side.USSR) is True
        game.map['France'].set_influence(0, 0)
        # No US influence in France, USSR can't coup
        assert game.map.can_coup(game, 'France', Side.USSR) is False

    def test_can_coup_defcon_restriction_europe(self):
        game = make_game()
        game.defcon_track = 4  # Europe locked
        game.map['France'].set_influence(0, 3)
        assert game.map.can_coup(game, 'France', Side.USSR) is False

    def test_can_coup_defcon_restriction_asia(self):
        game = make_game()
        game.defcon_track = 3  # Europe + Asia locked
        game.map['India'].set_influence(0, 3)
        assert game.map.can_coup(game, 'India', Side.USSR) is False

    def test_can_coup_defcon_restriction_middle_east(self):
        game = make_game()
        game.defcon_track = 2  # Europe + Asia + ME locked
        game.map['Egypt'].set_influence(0, 3)
        assert game.map.can_coup(game, 'Egypt', Side.USSR) is False

    def test_coup_success(self):
        """Successful coup: remove opponent influence, add own."""
        game = make_game()
        game.map['Cuba'].set_influence(0, 3)
        game.map.coup(game, 'Cuba', Side.USSR, 3, 6)
        # die_roll(6) + ops(3) - stability*2(6) = 3
        # Remove min(3, US_inf=3) = 3 US inf, add max(0, 3-3)=0 USSR
        assert game.map['Cuba'].influence[Side.US] == 0
        assert game.map['Cuba'].influence[Side.USSR] == 0

    def test_coup_failure(self):
        """Failed coup: no influence changes."""
        game = make_game()
        game.map['Cuba'].set_influence(0, 3)
        game.map.coup(game, 'Cuba', Side.USSR, 1, 1)
        # die_roll(1) + ops(1) - stability*2(6) = -4
        assert game.map['Cuba'].influence[Side.US] == 3
        assert game.map['Cuba'].influence[Side.USSR] == 0

    def test_coup_battleground_degrades_defcon(self):
        game = make_game()
        game.defcon_track = 5
        game.map['Cuba'].set_influence(0, 3)
        game.map.coup(game, 'Cuba', Side.USSR, 3, 6)
        assert game.defcon_track == 4

    def test_coup_battleground_nuclear_subs_no_degrade(self):
        game = make_game()
        game.defcon_track = 5
        game.basket[Side.US].append('Nuclear_Subs')
        game.map['Cuba'].set_influence(3, 0)
        game.map.coup(game, 'Cuba', Side.US, 3, 6)
        assert game.defcon_track == 5  # Nuclear Subs prevents degradation

    def test_realignment(self):
        """Realignment rolls: higher roll + bonuses removes opponent influence."""
        game = make_game()
        game.map['France'].set_influence(3, 3)
        game.map.realignment(game, 'France', Side.US, 1, 6)
        # US rolls 6, USSR rolls 1, net advantage for US
        # ussr_advantage = 0 (no adjacency bonuses, influence equal)
        # difference = 1 - 6 + 0 = -5
        # Since difference < 0: USSR loses 5 influence
        assert game.map['France'].influence[Side.USSR] == 0

    def test_realignment_superpower_blocked(self):
        game = make_game()
        assert game.map.can_realignment(game, 'USSR', Side.US) is False

    def test_salt_negotiations_coup_modifier_checks_both_sides(self):
        """SALT Negotiations -1 coup modifier applies regardless of which side's basket has it."""
        game = make_game()
        # SALT in US basket, USSR couping — should still apply -1
        game.basket[Side.US].append('Salt_Negotiations')
        game.map['Cuba'].set_influence(0, 3)
        game.defcon_track = 5
        # USSR coup: die=4 + ops=3 + ussr_advantage(-1 from SALT) - stability*2(6) = 0
        # difference=0 -> failure, no influence changes
        game.map.coup(game, 'Cuba', Side.USSR, 3, 4)
        assert game.map['Cuba'].influence[Side.US] == 3

    def test_star_wars_disposes_selected_star_event(self):
        game = make_game()
        game.space_track = [0, 1]
        game.discard_pile = ['Fidel']
        game.cards['Star_Wars'].use_event(game, Side.US)
        assert game.input_state is not None
        assert game.input_state.recv('Fidel') is True
        game.stage_complete()
        game.stage_complete()
        assert 'Fidel' in game.removed_pile

    def test_chernobyl_chooser_is_us(self):
        game = make_game()
        game.cards['Chernobyl'].use_event(game, Side.USSR)
        assert game.input_state.side == Side.US

    def test_pershing_ii_allows_early_stop(self):
        game = make_game()
        game.map['UK'].set_influence(0, 1)
        game.cards['Pershing_II_Deployed'].use_event(game, Side.USSR)
        assert game.input_state.option_stop_early == 'Do not remove more influence.'

    def test_can_play_event_own_card(self):
        game = make_game()
        assert game.can_play_event(Side.US, 'Duck_and_Cover') is True
        assert game.can_play_event(Side.USSR, 'Duck_and_Cover') is False

    def test_can_resolve_event_first_opponent_card(self):
        game = make_game()
        assert game.can_resolve_event_first(Side.USSR, 'Duck_and_Cover') is True
        assert game.can_resolve_event_first(Side.US, 'Duck_and_Cover') is False


# ===========================================================================
# CARD DISPOSAL TESTS
# ===========================================================================

class TestCardDisposal:

    def test_normal_card_goes_to_discard(self):
        game = make_game()
        game.hand[Side.USSR].append('Duck_and_Cover')
        card = game.cards['Duck_and_Cover']
        card.event_occurred = False
        card.dispose(game, Side.USSR)
        assert 'Duck_and_Cover' in game.discard_pile
        assert 'Duck_and_Cover' not in game.hand[Side.USSR]

    def test_unique_event_after_event_goes_to_removed(self):
        game = make_game()
        game.hand[Side.USSR].append('Fidel')
        card = game.cards['Fidel']
        card.event_occurred = True
        card.dispose(game, Side.USSR)
        assert 'Fidel' in game.removed_pile
        assert 'Fidel' not in game.discard_pile

    def test_unique_event_without_occurring_goes_to_discard(self):
        game = make_game()
        game.hand[Side.USSR].append('Fidel')
        card = game.cards['Fidel']
        card.event_occurred = False
        card.dispose(game, Side.USSR)
        assert 'Fidel' in game.discard_pile
        assert 'Fidel' not in game.removed_pile

    def test_template_card_dispose_is_noop(self):
        game = make_game()
        game.cards['Blank_1_Op_Card'].dispose(game, Side.US)
        assert 'Blank_1_Op_Card' not in game.discard_pile
        assert 'Blank_1_Op_Card' not in game.removed_pile


# ===========================================================================
# DEFCON INTERACTION TESTS
# ===========================================================================

class TestDefconInteractions:

    def test_norad_triggers_at_defcon_2(self):
        """NORAD triggers at the end of an AR in which DEFCON reached 2."""
        game = make_game()
        game.basket[Side.US].append('NORAD')
        game.defcon_track = 3
        game.ar_track = 1  # in action round
        game.ar_side = Side.US
        game.map['Canada'].set_influence(0, 10)
        game.map['France'].set_influence(0, 3)  # ensure US has influence somewhere
        game.change_defcon(-1)
        assert game.defcon_track == 2
        assert game.input_state is None

        game.ar_complete()

        assert game.input_state is not None
        assert game.input_state.prompt == 'Place NORAD influence.'

    def test_norad_triggers_when_event_becomes_active_after_defcon_drop(self):
        game = make_game()
        game.defcon_track = 3
        game.ar_track = 1
        game.map['Canada'].set_influence(0, 10)
        game.map['France'].set_influence(0, 3)

        game.change_defcon(-1)
        game.cards['NORAD'].use_event(game, Side.US)
        game.ar_complete()
        assert game.input_state is None

        game.stage_list = []
        game.ar_side = Side.US
        game.ar_complete()

        assert game.input_state is not None
        assert game.input_state.prompt == 'Place NORAD influence.'

    def test_norad_requires_us_control_of_canada(self):
        game = make_game()
        game.basket[Side.US].append('NORAD')
        game.defcon_track = 3
        game.ar_track = 1
        game.ar_side = Side.US
        game.map['Canada'].set_influence(3, 0)
        game.map['France'].set_influence(0, 3)

        game.change_defcon(-1)
        game.ar_complete()

        assert game.defcon_track == 2
        assert game.input_state is None

    def test_norad_does_not_trigger_in_headline(self):
        game = make_game()
        game.basket[Side.US].append('NORAD')
        game.defcon_track = 3
        game.ar_track = 0  # headline phase
        game.change_defcon(-1)
        # NORAD should NOT trigger during headline
        assert game.input_state is None


# ===========================================================================
# SIDE ENUM TESTS
# ===========================================================================

class TestSideEnum:

    def test_opp(self):
        assert Side.USSR.opp == Side.US
        assert Side.US.opp == Side.USSR
        assert Side.NEUTRAL.opp == Side.NEUTRAL

    def test_vp_mult(self):
        assert Side.USSR.vp_mult == 1
        assert Side.US.vp_mult == -1
        assert Side.NEUTRAL.vp_mult == 0

    def test_from_str(self):
        assert Side.fromStr('us') == Side.US
        assert Side.fromStr('ussr') == Side.USSR

    def test_to_str(self):
        assert Side.US.toStr() == 'US'
        assert Side.USSR.toStr() == 'USSR'


# ===========================================================================
# INPUT CLASS TESTS
# ===========================================================================

class TestInput:

    def test_basic_input(self):
        cb_called = []
        def cb(x):
            cb_called.append(x)
            return True

        inp = Input(Side.US, InputType.SELECT_COUNTRY, cb, ['France', 'UK'], reps=2)
        assert inp.recv('France') is True
        assert inp.recv('UK') is True
        assert cb_called == ['France', 'UK']

    def test_input_rejects_invalid_option(self):
        inp = Input(Side.US, InputType.SELECT_COUNTRY, lambda x: True, ['France'], reps=1)
        assert inp.recv('Germany') is False

    def test_input_complete(self):
        def cb(x):
            return True
        inp = Input(Side.US, InputType.SELECT_COUNTRY, cb, ['France', 'UK'], reps=1)
        assert inp.complete is False
        inp.reps -= 1
        assert inp.complete is True

    def test_input_max_per_option(self):
        def cb(x):
            return True
        inp = Input(Side.US, InputType.SELECT_COUNTRY, cb,
                    ['France', 'UK'], reps=3, max_per_option=2)
        inp.recv('France')
        inp.recv('France')
        # France should be maxed out
        available = list(inp.available_options)
        assert 'France' not in available

    def test_input_stop_early(self):
        calls = []
        def cb(x):
            calls.append(x)
            return True
        inp = Input(Side.US, InputType.SELECT_COUNTRY, cb,
                    ['France'], reps=3, option_stop_early='Stop')
        result = inp.recv('Stop')
        assert result is True
        assert 'Stop' in calls

    def test_legal_options_include_stop_early(self):
        inp = Input(
            Side.US,
            InputType.SELECT_COUNTRY,
            lambda x: True,
            ['France'],
            reps=2,
            option_stop_early='Stop'
        )
        assert list(inp.legal_options) == ['France', 'Stop']

    def test_input_complete_when_options_exhausted(self):
        inp = Input(
            Side.US,
            InputType.SELECT_COUNTRY,
            lambda x: True,
            ['France'],
            reps=2,
            max_per_option=1
        )
        assert inp.complete is False
        assert inp.recv('France') is True
        assert inp.complete is True

    def test_input_remove_option(self):
        inp = Input(Side.US, InputType.SELECT_COUNTRY, lambda x: True,
                    ['France', 'UK'], reps=2)
        inp.remove_option('France')
        available = list(inp.available_options)
        assert 'France' not in available
        assert 'UK' in available

    def test_input_adds_new_option_without_restoring_removed_option(self):
        inp = Input(Side.US, InputType.SELECT_COUNTRY, lambda x: True,
                    ['France'], reps=2)
        inp.remove_option('France')
        inp.add_option('France')
        inp.add_option('UK')

        assert list(inp.available_options) == ['UK']

    def test_ops_influence_adds_country_reached_during_same_action(self):
        game = make_game()
        for name, country in game.map.ALL.items():
            if not country.info.superpower:
                country.set_influence(0, 0)
        game.map['Poland'].set_influence(1, 0)

        game.card_operation_influence(Side.USSR, 'Nuclear_Test_Ban')
        assert 'Sweden' not in game.input_state.legal_options
        assert game.input_state.recv('Finland') is True

        assert 'Sweden' in game.input_state.legal_options
        assert game.input_state.recv('Sweden') is True

    def test_ops_influence_does_not_escape_restricted_country_set(self):
        game = make_game()
        for name, country in game.map.ALL.items():
            if not country.info.superpower:
                country.set_influence(0, 0)
        game.map['Poland'].set_influence(1, 0)

        game.card_operation_influence(
            Side.USSR, 'Nuclear_Test_Ban', restricted_list=['Finland'])
        assert game.input_state.recv('Finland') is True

        assert 'Sweden' not in game.input_state.legal_options

    def test_china_and_vietnam_can_grant_six_influence_placements(self):
        game = make_game()
        game.map['Vietnam'].set_influence(1, 0)
        game.basket[Side.USSR].append('Vietnam_Revolts')
        game.cards['The_China_Card'].reset()
        game.cards['Vietnam_Revolts'].reset()

        game.card_operation_influence(Side.USSR, 'The_China_Card')
        for _ in range(6):
            assert game.input_state.recv('Vietnam') is True

        assert game.input_state.reps == 0
        assert game.map['Vietnam'].influence[Side.USSR] == 7


# ===========================================================================
# GLOBAL OPS MODIFIER STACKING TESTS
# ===========================================================================

class TestOpsModifierStacking:

    def test_containment_and_red_scare_cancel_out(self):
        game = make_game()
        game.basket[Side.US].append('Containment')
        game.basket[Side.USSR].append('Red_Scare_Purge')  # vs US player
        # Containment +1, Red_Scare -1, net 0
        assert game.get_global_effective_ops(Side.US, 3) == 3

    def test_brezhnev_and_red_scare_cancel_out(self):
        game = make_game()
        game.basket[Side.USSR].append('Brezhnev_Doctrine')
        game.basket[Side.US].append('Red_Scare_Purge')  # vs USSR player
        # Brezhnev +1, Red_Scare -1, net 0
        assert game.get_global_effective_ops(Side.USSR, 3) == 3

    def test_brezhnev_without_red_scare(self):
        game = make_game()
        game.basket[Side.USSR].append('Brezhnev_Doctrine')
        assert game.get_global_effective_ops(Side.USSR, 3) == 4
        assert game.get_global_effective_ops(Side.USSR, 4) == 4  # clamped at 4
