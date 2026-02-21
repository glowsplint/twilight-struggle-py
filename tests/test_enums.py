"""
Tests for the enums module: Side, MapRegion, InputType, CardAction,
TrackEffects, CoupEffects, RealignState, OpsInfState.
"""
from __future__ import annotations

import pytest

from enums import (
    Side,
    MapRegion,
    InputType,
    CardAction,
    TrackEffects,
    CoupEffects,
    RealignState,
    OpsInfState,
)


# ---------------------------------------------------------------------------
# Side enum
# ---------------------------------------------------------------------------

class TestSideEnum:

    def test_side_values(self):
        assert Side.USSR == 0
        assert Side.US == 1
        assert Side.NEUTRAL == 2

    def test_side_opp_ussr(self):
        assert Side.USSR.opp == Side.US

    def test_side_opp_us(self):
        assert Side.US.opp == Side.USSR

    def test_side_opp_neutral(self):
        assert Side.NEUTRAL.opp == Side.NEUTRAL

    def test_side_vp_mult_ussr(self):
        assert Side.USSR.vp_mult == 1

    def test_side_vp_mult_us(self):
        assert Side.US.vp_mult == -1

    def test_side_vp_mult_neutral(self):
        assert Side.NEUTRAL.vp_mult == 0

    @pytest.mark.parametrize("input_str,expected", [
        ("us", Side.US),
        ("US", Side.US),
        ("ussr", Side.USSR),
        ("USSR", Side.USSR),
        ("neutral", Side.NEUTRAL),
        ("Neutral", Side.NEUTRAL),
    ])
    def test_side_fromStr(self, input_str: str, expected: Side):
        assert Side.fromStr(input_str) == expected

    def test_side_fromStr_invalid(self):
        with pytest.raises(NameError):
            Side.fromStr("invalid")

    @pytest.mark.parametrize("side,expected", [
        (Side.US, "US"),
        (Side.USSR, "USSR"),
        (Side.NEUTRAL, "NEUTRAL"),
    ])
    def test_side_toStr(self, side: Side, expected: str):
        assert side.toStr == expected

    def test_side_players(self):
        players = Side.PLAYERS()
        assert players == (Side.USSR, Side.US)
        assert Side.NEUTRAL not in players


# ---------------------------------------------------------------------------
# MapRegion enum
# ---------------------------------------------------------------------------

class TestMapRegionEnum:

    def test_main_region_values(self):
        assert MapRegion.EUROPE == 0
        assert MapRegion.ASIA == 1
        assert MapRegion.MIDDLE_EAST == 2
        assert MapRegion.AFRICA == 3
        assert MapRegion.CENTRAL_AMERICA == 4
        assert MapRegion.SOUTH_AMERICA == 5

    def test_sub_region_values(self):
        assert MapRegion.WESTERN_EUROPE == 6
        assert MapRegion.EASTERN_EUROPE == 7
        assert MapRegion.SOUTHEAST_ASIA == 8

    @pytest.mark.parametrize("input_str,expected", [
        ("europe", MapRegion.EUROPE),
        ("eu", MapRegion.EUROPE),
        ("asia", MapRegion.ASIA),
        ("as", MapRegion.ASIA),
        ("middle east", MapRegion.MIDDLE_EAST),
        ("me", MapRegion.MIDDLE_EAST),
        ("africa", MapRegion.AFRICA),
        ("af", MapRegion.AFRICA),
        ("central america", MapRegion.CENTRAL_AMERICA),
        ("ca", MapRegion.CENTRAL_AMERICA),
        ("south america", MapRegion.SOUTH_AMERICA),
        ("sa", MapRegion.SOUTH_AMERICA),
        ("western europe", MapRegion.WESTERN_EUROPE),
        ("we", MapRegion.WESTERN_EUROPE),
        ("eastern europe", MapRegion.EASTERN_EUROPE),
        ("ee", MapRegion.EASTERN_EUROPE),
        ("southeast asia", MapRegion.SOUTHEAST_ASIA),
        ("se", MapRegion.SOUTHEAST_ASIA),
    ])
    def test_mapregion_fromStr(self, input_str: str, expected: MapRegion):
        assert MapRegion.fromStr(input_str) == expected

    def test_mapregion_fromStr_invalid_returns_none(self):
        assert MapRegion.fromStr("atlantis") is None

    def test_main_regions_list(self):
        main = MapRegion.main_regions()
        assert len(main) == 6
        assert MapRegion.WESTERN_EUROPE not in main
        assert MapRegion.EASTERN_EUROPE not in main
        assert MapRegion.SOUTHEAST_ASIA not in main


# ---------------------------------------------------------------------------
# InputType enum
# ---------------------------------------------------------------------------

class TestInputTypeEnum:

    def test_input_type_values(self):
        assert InputType.COMMIT == 0
        assert InputType.ROLL_DICE == 1
        assert InputType.SELECT_CARD_ACTION == 3
        assert InputType.SELECT_CARD == 4
        assert InputType.SELECT_COUNTRY == 5
        assert InputType.SELECT_MULTIPLE == 6


# ---------------------------------------------------------------------------
# CardAction enum
# ---------------------------------------------------------------------------

class TestCardActionEnum:

    def test_card_action_values(self):
        assert CardAction.PLAY_EVENT == 0
        assert CardAction.RESOLVE_EVENT_FIRST == 1
        assert CardAction.INFLUENCE == 2
        assert CardAction.REALIGNMENT == 3
        assert CardAction.COUP == 4
        assert CardAction.SPACE == 5
        assert CardAction.SKIP_OPTIONAL_AR == 6


# ---------------------------------------------------------------------------
# TrackEffects dataclass-like
# ---------------------------------------------------------------------------

class TestTrackEffects:

    def test_default_values(self):
        t = TrackEffects()
        assert t.defcon == 0
        assert t.vp == 0
        assert t.milops == 0

    def test_custom_values(self):
        t = TrackEffects(defcon=-1, vp=3, milops=2)
        assert t.defcon == -1
        assert t.vp == 3
        assert t.milops == 2

    def test_iadd(self):
        a = TrackEffects(defcon=1, vp=2, milops=3)
        b = TrackEffects(defcon=-1, vp=1, milops=0)
        a += b
        assert a.defcon == 0
        assert a.vp == 3
        assert a.milops == 3

    def test_repr_empty(self):
        t = TrackEffects()
        assert repr(t) == ""

    def test_repr_with_values(self):
        t = TrackEffects(defcon=-1, vp=2)
        r = repr(t)
        assert "DEFCON" in r
        assert "VP" in r


# ---------------------------------------------------------------------------
# CoupEffects
# ---------------------------------------------------------------------------

class TestCoupEffects:

    def test_default_flags(self):
        c = CoupEffects()
        assert c.no_milops is False
        assert c.no_defcon_bg is False

    def test_flags_set(self):
        c = CoupEffects(no_milops=True, no_defcon_bg=True)
        assert c.no_milops is True
        assert c.no_defcon_bg is True

    def test_iadd_flags(self):
        a = CoupEffects(no_milops=False, no_defcon_bg=False)
        b = CoupEffects(no_milops=True)
        a += b
        assert a.no_milops is True
        assert a.no_defcon_bg is False

    def test_repr_with_flags(self):
        c = CoupEffects(no_milops=True, no_defcon_bg=True, defcon=-1)
        r = repr(c)
        assert "No mil. ops." in r
        assert "No DEFCON reduction" in r


# ---------------------------------------------------------------------------
# RealignState
# ---------------------------------------------------------------------------

class TestRealignState:

    def test_defaults(self):
        r = RealignState()
        assert r.side is None
        assert r.reps == 0
        assert r.countries == []
        assert r.defcon is None

    def test_iadd(self):
        a = RealignState(reps=3, countries=["France"])
        b = RealignState(reps=-1, countries=["Italy"])
        a += b
        assert a.reps == 2
        assert a.countries == ["France", "Italy"]


# ---------------------------------------------------------------------------
# OpsInfState
# ---------------------------------------------------------------------------

class TestOpsInfState:

    def test_defaults(self):
        o = OpsInfState(ops=3)
        assert o.ops == 3
        assert o.countries == []

    def test_iadd(self):
        a = OpsInfState(ops=3, countries=["France"])
        b = OpsInfState(ops=-1, countries=["Italy"])
        a += b
        assert a.ops == 2
        assert a.countries == ["France", "Italy"]
