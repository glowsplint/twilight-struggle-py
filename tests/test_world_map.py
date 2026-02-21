"""
Tests for the world_map module: CountryInfo, Country, GameMap.

Covers initialisation, influence operations, control checks, adjacency,
region membership, battleground status, stability values, and the standard
map builder.
"""
from __future__ import annotations

import pytest

from enums import MapRegion, Side
from world_map import CountryInfo, Country, GameMap


# ---------------------------------------------------------------------------
# CountryInfo (class-level registry)
# ---------------------------------------------------------------------------

class TestCountryInfo:

    def test_all_countries_populated(self):
        """CountryInfo.ALL should contain all 86 countries (+ superpowers)."""
        # 84 non-superpower countries + 2 superpowers = 86
        # Chinese_Civil_War is commented out in the module, so 85 total
        assert len(CountryInfo.ALL) >= 85

    def test_known_country_exists(self):
        assert "France" in CountryInfo.ALL
        assert "USSR" in CountryInfo.ALL
        assert "US" in CountryInfo.ALL

    def test_superpower_flag(self):
        assert CountryInfo.ALL["USSR"].superpower is True
        assert CountryInfo.ALL["US"].superpower is True
        assert CountryInfo.ALL["France"].superpower is False

    def test_battleground_flag(self):
        assert CountryInfo.ALL["France"].battleground is True
        assert CountryInfo.ALL["Canada"].battleground is False

    def test_stability(self):
        assert CountryInfo.ALL["France"].stability == 3
        assert CountryInfo.ALL["Lebanon"].stability == 1
        assert CountryInfo.ALL["UK"].stability == 5

    def test_region_assignment_western_europe(self):
        info = CountryInfo.ALL["France"]
        assert MapRegion.EUROPE in info.regions
        assert MapRegion.WESTERN_EUROPE in info.regions

    def test_region_assignment_eastern_europe(self):
        info = CountryInfo.ALL["Poland"]
        assert MapRegion.EUROPE in info.regions
        assert MapRegion.EASTERN_EUROPE in info.regions

    def test_region_assignment_europe_both(self):
        """Finland has region 'Europe' which gives EUROPE + EASTERN_EUROPE + WESTERN_EUROPE."""
        info = CountryInfo.ALL["Finland"]
        assert MapRegion.EUROPE in info.regions
        assert MapRegion.EASTERN_EUROPE in info.regions
        assert MapRegion.WESTERN_EUROPE in info.regions

    def test_region_assignment_southeast_asia(self):
        info = CountryInfo.ALL["Vietnam"]
        assert MapRegion.ASIA in info.regions
        assert MapRegion.SOUTHEAST_ASIA in info.regions

    def test_region_assignment_middle_east(self):
        info = CountryInfo.ALL["Egypt"]
        assert MapRegion.MIDDLE_EAST in info.regions

    def test_region_assignment_africa(self):
        info = CountryInfo.ALL["Nigeria"]
        assert MapRegion.AFRICA in info.regions

    def test_region_assignment_central_america(self):
        info = CountryInfo.ALL["Cuba"]
        assert MapRegion.CENTRAL_AMERICA in info.regions

    def test_region_assignment_south_america(self):
        info = CountryInfo.ALL["Brazil"]
        assert MapRegion.SOUTH_AMERICA in info.regions

    def test_region_assignment_asia(self):
        info = CountryInfo.ALL["Japan"]
        assert MapRegion.ASIA in info.regions

    def test_region_all_sets_populated(self):
        """REGION_ALL sets should have countries for every main region."""
        for region in MapRegion.main_regions():
            assert len(CountryInfo.REGION_ALL[region]) > 0, f"No countries in {region.name}"

    def test_adjacent_countries_france(self):
        adj = CountryInfo.ALL["France"].adjacent_countries
        assert "UK" in adj
        assert "West_Germany" in adj
        assert "Spain_Portugal" in adj
        assert "Italy" in adj
        assert "Algeria" in adj

    def test_superpower_adjacent(self):
        ussr_adj = CountryInfo.ALL["USSR"].adjacent_countries
        assert "Finland" in ussr_adj
        assert "Poland" in ussr_adj
        us_adj = CountryInfo.ALL["US"].adjacent_countries
        assert "Japan" in us_adj
        assert "Mexico" in us_adj
        assert "Cuba" in us_adj
        assert "Canada" in us_adj


# ---------------------------------------------------------------------------
# Country class
# ---------------------------------------------------------------------------

class TestCountry:

    def test_initial_influence_zero(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        assert france.influence[Side.USSR] == 0
        assert france.influence[Side.US] == 0

    def test_set_influence(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(2, 3)
        assert france.influence[Side.USSR] == 2
        assert france.influence[Side.US] == 3

    def test_change_influence_positive(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.change_influence(1, 2)
        assert france.influence[Side.USSR] == 1
        assert france.influence[Side.US] == 2

    def test_change_influence_clamped_to_zero(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.change_influence(-5, -10)
        assert france.influence[Side.USSR] == 0
        assert france.influence[Side.US] == 0

    def test_increment_influence(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.increment_influence(Side.USSR, 3)
        assert france.influence[Side.USSR] == 3
        france.increment_influence(Side.US)
        assert france.influence[Side.US] == 1

    def test_decrement_influence(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(3, 2)
        france.decrement_influence(Side.USSR, 2)
        assert france.influence[Side.USSR] == 1

    def test_decrement_influence_clamped(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(1, 0)
        france.decrement_influence(Side.USSR, 5)
        assert france.influence[Side.USSR] == 0

    def test_decrement_influence_returns_false_when_zero(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        result = france.decrement_influence(Side.USSR)
        assert result is False

    def test_remove_influence(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(3, 0)
        result = france.remove_influence(Side.USSR)
        assert result is True
        assert france.influence[Side.USSR] == 0

    def test_remove_influence_returns_false_when_zero(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        result = france.remove_influence(Side.US)
        assert result is False

    def test_reset_influence(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(5, 3)
        france.reset_influence()
        assert france.influence[Side.USSR] == 0
        assert france.influence[Side.US] == 0

    def test_match_influence(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(0, 5)
        france.match_influence(Side.USSR)
        assert france.influence[Side.USSR] == 5

    # -- Control checks --

    def test_control_us(self, bare_game_map: GameMap):
        """France (stability 3): US controls if US_inf - USSR_inf >= 3."""
        france = bare_game_map["France"]
        france.set_influence(0, 3)
        assert france.control == Side.US

    def test_control_ussr(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(4, 1)
        assert france.control == Side.USSR

    def test_control_neutral(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(1, 2)
        assert france.control == Side.NEUTRAL

    def test_control_exact_threshold(self, bare_game_map: GameMap):
        """Lebanon (stability 1): even 1 influence difference gives control."""
        leb = bare_game_map["Lebanon"]
        leb.set_influence(0, 1)
        assert leb.control == Side.US

    # -- has_influence helpers --

    def test_has_influence(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(2, 0)
        assert france.has_influence(Side.USSR)
        assert not france.has_influence(Side.US)

    def test_has_us_influence_property(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(0, 1)
        assert france.has_us_influence is True
        assert france.has_ussr_influence is False

    def test_us_influence_only(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(0, 3)
        assert france.us_influence_only is True
        france.set_influence(1, 3)
        assert france.us_influence_only is False

    def test_ussr_influence_only(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(3, 0)
        assert france.ussr_influence_only is True

    # -- coup_influence --

    def test_coup_influence_removes_opponent_first(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(0, 4)
        france.coup_influence(Side.USSR, 3)
        # swing = 3, US had 4 => US goes to 1, USSR stays 0
        assert france.influence[Side.US] == 1
        assert france.influence[Side.USSR] == 0

    def test_coup_influence_overflow_adds_to_couper(self, bare_game_map: GameMap):
        france = bare_game_map["France"]
        france.set_influence(0, 2)
        france.coup_influence(Side.USSR, 5)
        # swing = 5, US had 2 => US goes to 0, USSR gains 3 overflow
        assert france.influence[Side.US] == 0
        assert france.influence[Side.USSR] == 3


# ---------------------------------------------------------------------------
# GameMap class
# ---------------------------------------------------------------------------

class TestGameMap:

    def test_gamemap_all_countries_count(self, bare_game_map: GameMap):
        assert len(bare_game_map.ALL) >= 85

    def test_gamemap_getitem(self, bare_game_map: GameMap):
        country = bare_game_map["France"]
        assert isinstance(country, Country)
        assert country.info.name == "France"

    def test_build_standard_ussr_influence(self, game_map: GameMap):
        assert game_map["USSR"].influence[Side.USSR] == 999
        assert game_map["North_Korea"].influence[Side.USSR] == 3
        assert game_map["East_Germany"].influence[Side.USSR] == 3
        assert game_map["Finland"].influence[Side.USSR] == 1
        assert game_map["Syria"].influence[Side.USSR] == 1
        assert game_map["Iraq"].influence[Side.USSR] == 1

    def test_build_standard_us_influence(self, game_map: GameMap):
        assert game_map["US"].influence[Side.US] == 999
        assert game_map["Australia"].influence[Side.US] == 4
        assert game_map["UK"].influence[Side.US] == 5
        assert game_map["Israel"].influence[Side.US] == 1
        assert game_map["Iran"].influence[Side.US] == 1
        assert game_map["Japan"].influence[Side.US] == 1
        assert game_map["Philippines"].influence[Side.US] == 1
        assert game_map["South_Korea"].influence[Side.US] == 1
        assert game_map["South_Africa"].influence[Side.US] == 1
        assert game_map["Panama"].influence[Side.US] == 1
        assert game_map["Canada"].influence[Side.US] == 2

    def test_has_us_influence_property(self, game_map: GameMap):
        us_inf = game_map.has_us_influence
        assert "UK" in us_inf
        assert "USSR" not in us_inf  # superpowers excluded

    def test_has_ussr_influence_property(self, game_map: GameMap):
        ussr_inf = game_map.has_ussr_influence
        assert "North_Korea" in ussr_inf
        assert "US" not in ussr_inf  # superpowers excluded

    def test_has_influence_generator(self, game_map: GameMap):
        """has_influence(side) returns generator of country names with influence, minus superpowers."""
        ussr_names = list(game_map.has_influence(Side.USSR))
        assert "North_Korea" in ussr_names
        assert "USSR" not in ussr_names

    def test_change_influence_via_map(self, bare_game_map: GameMap):
        bare_game_map.change_influence("France", Side.USSR, 3)
        assert bare_game_map["France"].influence[Side.USSR] == 3
        bare_game_map.change_influence("France", Side.US, 2)
        assert bare_game_map["France"].influence[Side.US] == 2

    def test_set_influence_via_map(self, bare_game_map: GameMap):
        bare_game_map.set_influence("France", Side.USSR, 5)
        assert bare_game_map["France"].influence[Side.USSR] == 5

    # -- DEFCON-restricted coup/realign --

    def test_can_coup_all_defcon5(self, game_map: GameMap):
        """At DEFCON 5 all regions are open."""
        targets = list(game_map.can_coup_all(Side.USSR, defcon=5))
        # USSR can coup countries with US influence
        assert "UK" in targets

    def test_can_coup_all_defcon4_europe_restricted(self, game_map: GameMap):
        """At DEFCON 4, Europe is restricted."""
        targets = list(game_map.can_coup_all(Side.USSR, defcon=4))
        # UK is in Western Europe => restricted
        assert "UK" not in targets
        # Iran is in Middle East => still open
        assert "Iran" in targets

    def test_can_coup_all_defcon3_asia_restricted(self, game_map: GameMap):
        """At DEFCON 3, Europe and Asia are restricted."""
        targets = list(game_map.can_coup_all(Side.USSR, defcon=3))
        assert "Japan" not in targets
        assert "South_Korea" not in targets
        # Middle East still open
        assert "Iran" in targets

    def test_can_coup_all_defcon2_middle_east_restricted(self, game_map: GameMap):
        """At DEFCON 2, Europe, Asia, and Middle East are restricted."""
        targets = list(game_map.can_coup_all(Side.USSR, defcon=2))
        assert "Iran" not in targets
        assert "Israel" not in targets
        # South Africa (Africa) still open
        assert "South_Africa" in targets

    def test_can_realign_matches_coup_defcon_restrictions(self, game_map: GameMap):
        """Realignment follows the same DEFCON-based region restrictions as coup."""
        realign_d5 = set(game_map.can_realign_all(Side.USSR, defcon=5))
        realign_d4 = set(game_map.can_realign_all(Side.USSR, defcon=4))
        assert "UK" in realign_d5
        assert "UK" not in realign_d4

    def test_has_influence_around(self, game_map: GameMap):
        """France is adjacent to UK which has US influence."""
        assert game_map.has_influence_around(Side.US, "France") is True

    def test_has_influence_around_false(self, bare_game_map: GameMap):
        """With no influence on the map, nobody has influence around any country."""
        assert bare_game_map.has_influence_around(Side.US, "France") is False
