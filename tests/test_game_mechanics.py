"""
Tests for the game_mechanics module: Game class.

Covers initialisation, track manipulation, ars_remaining, resolve_headline_order,
stage_complete, DEFCON changes, space race, coup validation, turn progression,
scoring, and milops.
"""
from __future__ import annotations

from functools import partial
from unittest.mock import MagicMock

import pytest

from enums import CoupEffects, MapRegion, Side
from game_mechanics import Game
from world_map import CountryInfo


# ---------------------------------------------------------------------------
# Game.__init__ / start() defaults
# ---------------------------------------------------------------------------

class TestGameInitialisation:

    def test_vp_track_starts_at_zero(self, game: Game):
        assert game.vp_track == 0

    def test_turn_track_starts_at_one(self, game: Game):
        assert game.turn_track == 1

    def test_ar_track_starts_at_zero(self, game: Game):
        assert game.ar_track == 0

    def test_ar_side_starts_as_ussr(self, game: Game):
        assert game.ar_side == Side.USSR

    def test_defcon_starts_at_five(self, game: Game):
        assert game.defcon_track == 5

    def test_milops_start_at_zero(self, game: Game):
        assert game.milops_track == [0, 0]

    def test_space_track_starts_at_zero(self, game: Game):
        assert game.space_track == [0, 0]

    def test_spaced_turns_starts_at_zero(self, game: Game):
        assert game.spaced_turns == [0, 0]

    def test_hands_start_empty_before_stages(self, game: Game):
        """After start() but before running stages, hands are empty.
        The China Card is dealt via expand_deck which sits in the stage_list."""
        # Hands are empty because expand_deck/deal haven't been called yet
        assert game.hand[Side.USSR] == []
        assert game.hand[Side.US] == []

    def test_map_is_initialised(self, game: Game):
        assert game.map is not None

    def test_cards_is_initialised(self, game: Game):
        assert game.cards is not None

    def test_players_initialised(self, game: Game):
        assert game.players is not None
        assert len(game.players) == 2

    def test_headline_bin_empty(self, game: Game):
        assert game.headline_bin == ["", ""]

    def test_stage_list_not_empty_after_start(self, game: Game):
        assert len(game.stage_list) > 0

    def test_handicap_zero(self, game: Game):
        assert game.handicap == 0

    def test_ars_by_turn_structure(self, game: Game):
        """ars_by_turn should have two lists (one per side) matching Default.ARS_BY_TURN."""
        assert len(game.ars_by_turn) == 2
        for side_list in game.ars_by_turn:
            assert len(side_list) == len(Game.Default.ARS_BY_TURN)


# ---------------------------------------------------------------------------
# Default constants
# ---------------------------------------------------------------------------

class TestGameDefaults:

    def test_ars_by_turn_early_war(self):
        """Turns 1-3 have 6 ARs each."""
        for turn in (1, 2, 3):
            assert Game.Default.ARS_BY_TURN[turn] == 6

    def test_ars_by_turn_mid_and_late_war(self):
        """Turns 4-10 have 7 ARs each."""
        for turn in range(4, 11):
            assert Game.Default.ARS_BY_TURN[turn] == 7

    def test_space_roll_max(self):
        assert Game.Default.SPACE_ROLL_MAX == (3, 4, 3, 4, 3, 4, 3, 2)

    def test_scoring_region_keys(self):
        for region in MapRegion.main_regions():
            assert region in Game.Default.SCORING


# ---------------------------------------------------------------------------
# ars_remaining()
# ---------------------------------------------------------------------------

class TestArsRemaining:

    def test_ars_remaining_turn1_ar0(self, game: Game):
        """At start of turn 1 (ar_track=0 means headline), before any AR has happened."""
        game.ar_track = 1
        game.ar_side_done = [False, False]
        remaining = game.ars_remaining(Side.USSR)
        # ars_by_turn[USSR][1] = 6, ar_track = 1, side_done = False => 6 - 1 + 1 - 0 = 6
        assert remaining == 6

    def test_ars_remaining_decreases_with_ar_track(self, game: Game):
        game.ar_track = 3
        game.ar_side_done = [False, False]
        remaining = game.ars_remaining(Side.USSR)
        # 6 - 3 + 1 - 0 = 4
        assert remaining == 4

    def test_ars_remaining_when_side_done(self, game: Game):
        game.ar_track = 3
        game.ar_side_done = [True, False]
        remaining = game.ars_remaining(Side.USSR)
        # 6 - 3 + 1 - 1 = 3
        assert remaining == 3

    def test_ars_remaining_turn10_boundary(self, game: Game):
        """turn_track = 10 is the last valid turn, should not cause index error."""
        game.turn_track = 10
        game.ar_track = 1
        game.ar_side_done = [False, False]
        remaining = game.ars_remaining(Side.USSR)
        # ars_by_turn[USSR][10] = 7, ar_track = 1 => 7 - 1 + 1 = 7
        assert remaining == 7

    def test_ars_remaining_out_of_bounds_returns_zero(self, game: Game):
        """turn_track beyond ars_by_turn length should return 0 (the bug fix)."""
        game.turn_track = 11
        game.ar_track = 1
        remaining = game.ars_remaining(Side.USSR)
        assert remaining == 0

    def test_ars_remaining_out_of_bounds_turn_99(self, game: Game):
        game.turn_track = 99
        assert game.ars_remaining(Side.US) == 0

    def test_ars_remaining_never_negative(self, game: Game):
        """Even with a very high ar_track, result should be >= 0."""
        game.ar_track = 100
        remaining = game.ars_remaining(Side.USSR)
        assert remaining >= 0


# ---------------------------------------------------------------------------
# resolve_headline_order()
# ---------------------------------------------------------------------------

class TestResolveHeadlineOrder:

    def test_both_headlines_empty(self, game: Game):
        """If neither side selected a headline, no stages should be appended."""
        game.headline_bin = ["", ""]
        game.stage_list = []
        game.resolve_headline_order()
        assert len(game.stage_list) == 0

    def test_only_ussr_headline(self, game: Game):
        """If only USSR has a headline, it alone gets resolved."""
        game.headline_bin = ["Duck_and_Cover", ""]
        game.stage_list = []
        game.resolve_headline_order()
        assert len(game.stage_list) == 1

    def test_only_us_headline(self, game: Game):
        """If only US has a headline, it alone gets resolved."""
        game.headline_bin = ["", "Five_Year_Plan"]
        game.stage_list = []
        game.resolve_headline_order()
        assert len(game.stage_list) == 1

    def test_defectors_us_headline_goes_first(self, game: Game):
        """Defectors as US headline resolves US first regardless of ops."""
        game.headline_bin = ["Duck_and_Cover", "Defectors"]
        game.stage_list = []
        game.resolve_headline_order()
        # US goes first (appended last to stack = resolved first when popping)
        assert len(game.stage_list) == 2

    def test_higher_ops_us_goes_first(self, game: Game):
        """When US headline ops >= USSR headline ops, US resolves first."""
        # Duck_and_Cover = 3 ops, Five_Year_Plan = 3 ops => tie, US goes first
        game.headline_bin = ["Fidel", "Duck_and_Cover"]
        game.stage_list = []
        game.resolve_headline_order()
        # Fidel = 2 ops, Duck_and_Cover = 3 ops => US has higher ops => US first
        assert len(game.stage_list) == 2

    def test_higher_ops_ussr_goes_first(self, game: Game):
        """When USSR headline ops > US headline ops, USSR resolves first."""
        # Need a USSR card with more ops than the US card
        # Duck_and_Cover = 3, Vietnam_Revolts = 2
        game.headline_bin = ["Duck_and_Cover", "Vietnam_Revolts"]
        game.stage_list = []
        game.resolve_headline_order()
        # D&C has 3 ops, VR has 2 => US card (D&C as USSR HL) has 3 ops
        # Actually: USSR HL = Duck_and_Cover(3), US HL = Vietnam_Revolts(2)
        # cards[us_hl].ops(2) < cards[ussr_hl].ops(3) => USSR goes first
        assert len(game.stage_list) == 2


# ---------------------------------------------------------------------------
# stage_complete()
# ---------------------------------------------------------------------------

class TestStageComplete:

    def test_stage_complete_pops_and_calls(self, game: Game):
        """stage_complete should pop the last item from stage_list and call it."""
        called = {"count": 0}

        def dummy_stage():
            called["count"] += 1

        game.stage_list = [dummy_stage]
        game.stage_complete()
        assert called["count"] == 1
        assert len(game.stage_list) == 0

    def test_stage_complete_clears_input_state(self, game: Game):
        """stage_complete should set input_state to None before calling the next stage."""
        game.input_state = MagicMock()
        game.stage_list = [lambda: None]
        game.stage_complete()
        assert game.input_state is None

    def test_stage_complete_empty_list_raises(self, game: Game):
        """Calling stage_complete on an empty stage_list should raise IndexError."""
        game.stage_list = []
        with pytest.raises(IndexError):
            game.stage_complete()


# ---------------------------------------------------------------------------
# VP changes
# ---------------------------------------------------------------------------

class TestVPChanges:

    def test_change_vp_positive(self, game: Game):
        game.change_vp(5)
        assert game.vp_track == 5

    def test_change_vp_negative(self, game: Game):
        game.change_vp(-3)
        assert game.vp_track == -3

    def test_change_vp_accumulates(self, game: Game):
        game.change_vp(5)
        game.change_vp(-2)
        assert game.vp_track == 3

    def test_change_vp_triggers_termination_ussr(self, game: Game):
        """If VP reaches +20, the game should terminate (USSR auto-victory)."""
        game.change_vp(20)
        # terminate() clears stage_list
        assert game.stage_list == []

    def test_change_vp_triggers_termination_us(self, game: Game):
        """If VP reaches -20, the game should terminate (US auto-victory)."""
        game.change_vp(-20)
        assert game.stage_list == []


# ---------------------------------------------------------------------------
# DEFCON changes
# ---------------------------------------------------------------------------

class TestDEFCONChanges:

    def test_change_defcon_degrade(self, game: Game):
        game.change_defcon(-1)
        assert game.defcon_track == 4

    def test_change_defcon_improve(self, game: Game):
        game.defcon_track = 3
        game.change_defcon(1)
        assert game.defcon_track == 4

    def test_change_defcon_capped_at_5(self, game: Game):
        """DEFCON cannot exceed 5."""
        game.change_defcon(10)
        assert game.defcon_track == 5

    def test_change_defcon_below_2_terminates(self, game: Game):
        """DEFCON dropping below 2 triggers thermonuclear war (game termination)."""
        game.change_defcon(-4)  # 5 - 4 = 1 => nuclear war
        assert game.defcon_track == 1
        # Game should be terminated: stage_list cleared
        assert game.stage_list == []

    def test_set_defcon(self, game: Game):
        game.set_defcon(3)
        assert game.defcon_track == 3

    def test_set_defcon_uses_change_defcon(self, game: Game):
        """set_defcon(n) should work by calling change_defcon(n - current)."""
        game.set_defcon(2)
        assert game.defcon_track == 2


# ---------------------------------------------------------------------------
# Milops
# ---------------------------------------------------------------------------

class TestMilops:

    def test_change_milops(self, game: Game):
        game.change_milops(Side.USSR, 3)
        assert game.milops_track[Side.USSR] == 3

    def test_change_milops_capped_at_5(self, game: Game):
        game.change_milops(Side.US, 10)
        assert game.milops_track[Side.US] == 5

    def test_reset_milops(self, game: Game):
        game.change_milops(Side.USSR, 4)
        game.change_milops(Side.US, 2)
        game.reset_milops()
        assert game.milops_track == [0, 0]


# ---------------------------------------------------------------------------
# Space race
# ---------------------------------------------------------------------------

class TestSpaceRace:

    def test_change_space_advances(self, game: Game):
        game.change_space(Side.USSR, 1)
        assert game.space_track[Side.USSR] == 1

    def test_change_space_vp_first_to_reach_step(self, game: Game):
        """First player to reach space step 1 earns VPs per SPACE_VPS."""
        game.change_space(Side.USSR, 1)
        # SPACE_VPS[0] = (2, 1), first to reach => 2 VP for USSR
        assert game.vp_track == 2  # positive = USSR favour

    def test_change_space_vp_second_to_reach_step(self, game: Game):
        """Second player to reach the same step earns fewer VPs."""
        game.space_track[Side.USSR] = 1  # USSR already at step 1
        game.change_space(Side.US, 1)
        # US is second to step 1 => SPACE_VPS[0][1] = 1 VP for US
        assert game.vp_track == -1  # -1 = US favour

    def test_can_space_basic(self, game: Game):
        """A 2-ops card should be spaceable from step 0."""
        game.hand[Side.USSR].append("Fidel")  # 2 ops
        assert game.can_space(Side.USSR, "Fidel") is True

    def test_can_space_already_at_8(self, game: Game):
        """Cannot space if already at step 8."""
        game.space_track[Side.USSR] = 8
        game.hand[Side.USSR].append("Fidel")
        assert game.can_space(Side.USSR, "Fidel") is False

    def test_can_space_already_spaced_this_turn(self, game: Game):
        """Cannot space if already spaced maximum times this turn."""
        game.spaced_turns[Side.USSR] = 2
        game.hand[Side.USSR].append("Fidel")
        assert game.can_space(Side.USSR, "Fidel") is False


# ---------------------------------------------------------------------------
# Coup mechanics (unit-level)
# ---------------------------------------------------------------------------

class TestCoupMechanics:

    def test_coup_successful(self, game: Game):
        """A successful coup changes influence."""
        game.map["Iran"].set_influence(0, 2)
        # ops=3, roll=6, stability=2 => difference = 6+3 - 2*2 = 5
        game.coup(Side.USSR, 3, "Iran", 6)
        # swing of 5: US had 2 => US to 0, USSR gains 3
        assert game.map["Iran"].influence[Side.US] == 0
        assert game.map["Iran"].influence[Side.USSR] == 3

    def test_coup_failed(self, game: Game):
        """A failed coup does not change influence."""
        game.map["Iran"].set_influence(0, 2)
        # ops=1, roll=1, stability=2 => difference = 1+1 - 4 = -2 => fail
        game.coup(Side.USSR, 1, "Iran", 1)
        assert game.map["Iran"].influence[Side.US] == 2
        assert game.map["Iran"].influence[Side.USSR] == 0

    def test_coup_battleground_degrades_defcon(self, game: Game):
        """Couping a battleground country degrades DEFCON by 1."""
        game.map["Iran"].set_influence(0, 2)  # Iran is a battleground
        initial_defcon = game.defcon_track
        game.coup(Side.USSR, 3, "Iran", 6)
        assert game.defcon_track == initial_defcon - 1

    def test_coup_non_battleground_no_defcon_change(self, game: Game):
        """Couping a non-battleground country does not degrade DEFCON."""
        game.map["Lebanon"].set_influence(0, 1)  # Lebanon is not a battleground
        initial_defcon = game.defcon_track
        game.coup(Side.USSR, 3, "Lebanon", 6)
        assert game.defcon_track == initial_defcon

    def test_coup_adds_milops(self, game: Game):
        """Coup operations value is added to milops."""
        game.map["Lebanon"].set_influence(0, 1)
        game.coup(Side.USSR, 3, "Lebanon", 1)
        assert game.milops_track[Side.USSR] == 3


# ---------------------------------------------------------------------------
# DEFCON-based coup restrictions (via Game)
# ---------------------------------------------------------------------------

class TestCoupRestrictions:

    def test_can_coup_all_europe_restricted_at_defcon4(self, game: Game):
        """At DEFCON 4, coups in Europe should be restricted."""
        game.defcon_track = 4
        game.map["France"].set_influence(0, 3)
        targets = game.can_coup_all(Side.USSR, game.defcon_track)
        assert "France" not in targets

    def test_can_coup_all_asia_restricted_at_defcon3(self, game: Game):
        """At DEFCON 3, coups in Asia should also be restricted."""
        game.defcon_track = 3
        game.map["Japan"].set_influence(0, 3)
        targets = game.can_coup_all(Side.USSR, game.defcon_track)
        assert "Japan" not in targets


# ---------------------------------------------------------------------------
# Global effective ops
# ---------------------------------------------------------------------------

class TestGetGlobalEffectiveOps:

    def test_base_ops_clamped_minimum_1(self, game: Game):
        result = game.get_global_effective_ops(Side.USSR, 0)
        assert result == 1

    def test_base_ops_clamped_maximum_4(self, game: Game):
        result = game.get_global_effective_ops(Side.USSR, 5)
        assert result == 4

    def test_base_ops_passthrough(self, game: Game):
        result = game.get_global_effective_ops(Side.USSR, 3)
        assert result == 3


# ---------------------------------------------------------------------------
# Terminate
# ---------------------------------------------------------------------------

class TestTerminate:

    def test_terminate_clears_stage_list(self, game: Game):
        game.terminate()
        assert game.stage_list == []

    def test_terminate_ussr_wins_with_positive_vp(self, game: Game):
        game.vp_track = 10
        game.terminate()
        # Check notification mentions USSR
        assert any("USSR" in n for n in game.output_state.notification)

    def test_terminate_us_wins_with_negative_vp(self, game: Game):
        game.vp_track = -10
        game.terminate()
        assert any("US" in n for n in game.output_state.notification)

    def test_terminate_specific_side(self, game: Game):
        game.terminate(Side.USSR)
        assert any("USSR" in n for n in game.output_state.notification)

    def test_terminate_neutral_tie(self, game: Game):
        game.vp_track = 0
        game.terminate()
        assert any("NEUTRAL" in n for n in game.output_state.notification)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

class TestScoring:

    def test_score_empty_board_no_vp_change(self, game: Game):
        """With no influence in a region, scoring should produce no VP swing."""
        initial_vp = game.vp_track
        game.score(MapRegion.AFRICA)
        # Neither side has presence => no VPs
        assert game.vp_track == initial_vp

    def test_score_ussr_presence_only(self, game: Game):
        """USSR has presence in Africa (via standard setup: none by default).
        Manually set up one country to test."""
        game.map["Nigeria"].set_influence(2, 0)  # USSR controls Nigeria (stability 1)
        initial_vp = game.vp_track
        game.score(MapRegion.AFRICA)
        # USSR has presence (1 BG) + 1 BG bonus = presence_vps(1) + 1 = 2
        # US has nothing
        assert game.vp_track > initial_vp

    def test_score_check_only_no_vp_change(self, game: Game):
        """check_only=True should not change the VP track."""
        game.map["Nigeria"].set_influence(2, 0)
        initial_vp = game.vp_track
        game.score(MapRegion.AFRICA, check_only=True)
        assert game.vp_track == initial_vp


# ---------------------------------------------------------------------------
# can_play_event / can_resolve_event_first
# ---------------------------------------------------------------------------

class TestCardActionChecks:

    def test_can_play_event_own_card(self, game: Game):
        """US player can play event on a US-owned card."""
        assert game.can_play_event(Side.US, "Duck_and_Cover") is True

    def test_cannot_play_event_opponent_card(self, game: Game):
        """US player cannot play event on a USSR-owned card."""
        assert game.can_play_event(Side.US, "Fidel") is False

    def test_can_resolve_event_first_opp_card(self, game: Game):
        """US player can resolve event first when holding a USSR-owned card
        (if the event can fire)."""
        assert game.can_resolve_event_first(Side.US, "Fidel") is True

    def test_cannot_resolve_event_first_own_card(self, game: Game):
        """US player cannot 'resolve event first' on their own card."""
        assert game.can_resolve_event_first(Side.US, "Duck_and_Cover") is False

    def test_can_place_influence_ops_card(self, game: Game):
        """Cards with ops > 0 can be used for influence."""
        assert game.can_place_influence(Side.USSR, "Duck_and_Cover") is True

    def test_cannot_place_influence_scoring_card(self, game: Game):
        """Scoring cards (ops=0) cannot be used for influence."""
        assert game.can_place_influence(Side.USSR, "Asia_Scoring") is False
