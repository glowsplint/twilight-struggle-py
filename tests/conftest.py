"""
Shared pytest fixtures for the Twilight Struggle test suite.

Provides reusable Game, GameMap, and helper fixtures for common test scenarios.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on sys.path so bare imports work.
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest

from enums import Side, MapRegion
from world_map import CountryInfo, GameMap, Country
from game_mechanics import Game
from cards import Card, GameCards


# ---------------------------------------------------------------------------
# Core fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def game() -> Game:
    """Return a freshly initialised and started Game instance (turn 1, standard setup)."""
    g = Game()
    g.start(handicap=0)  # no handicap so put_start_extra is a no-op
    return g


@pytest.fixture
def game_map() -> GameMap:
    """Return a fresh GameMap with standard starting influence."""
    gm = GameMap()
    gm.build_standard()
    return gm


@pytest.fixture
def bare_game_map() -> GameMap:
    """Return a GameMap with zero influence everywhere (useful for isolated tests)."""
    gm = GameMap()
    return gm


# ---------------------------------------------------------------------------
# Scenario fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mid_war_game() -> Game:
    """Return a Game instance set to turn 5 (mid-war) for testing turn-boundary logic."""
    g = Game()
    g.start(handicap=0)
    g.turn_track = 5
    g.defcon_track = 3
    return g


@pytest.fixture
def late_war_game() -> Game:
    """Return a Game instance set to turn 9 (late war)."""
    g = Game()
    g.start(handicap=0)
    g.turn_track = 9
    g.defcon_track = 2
    return g


@pytest.fixture
def game_cards() -> GameCards:
    """Return a fresh GameCards instance."""
    return GameCards()
