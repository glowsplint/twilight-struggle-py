"""
Tests for the cards module: Card base class, GameCards, and specific card properties.

Covers card creation, ops values, owner/side, scoring identification,
can_event behaviour, and the GameCards container.
"""
from __future__ import annotations

import pytest

from enums import MapRegion, Side
from cards import Card, GameCards


# ---------------------------------------------------------------------------
# Card class-level registry
# ---------------------------------------------------------------------------

class TestCardRegistry:

    def test_card_all_populated(self):
        """Card.ALL should contain all registered card subclasses."""
        assert len(Card.ALL) > 0

    def test_card_index_populated(self):
        """Card.INDEX should map card_index -> Card subclass."""
        assert len(Card.INDEX) > 0

    def test_known_card_in_all(self):
        assert "Asia_Scoring" in Card.ALL
        assert "Duck_and_Cover" in Card.ALL
        assert "Fidel" in Card.ALL
        assert "The_China_Card" in Card.ALL

    def test_card_index_lookup(self):
        assert Card.INDEX[1].name == "Asia_Scoring"
        assert Card.INDEX[4].name == "Duck_and_Cover"
        assert Card.INDEX[6].name == "The_China_Card"


# ---------------------------------------------------------------------------
# Card properties
# ---------------------------------------------------------------------------

class TestCardProperties:

    def test_scoring_card_ops_zero(self):
        card = Card.ALL["Asia_Scoring"]
        assert card.ops == 0

    def test_event_card_ops(self):
        assert Card.ALL["Duck_and_Cover"].ops == 3
        assert Card.ALL["Fidel"].ops == 2
        assert Card.ALL["The_China_Card"].ops == 4

    def test_card_type_scoring(self):
        assert Card.ALL["Asia_Scoring"].card_type == "Scoring"
        assert Card.ALL["Europe_Scoring"].card_type == "Scoring"
        assert Card.ALL["Middle_East_Scoring"].card_type == "Scoring"

    def test_card_type_event(self):
        assert Card.ALL["Duck_and_Cover"].card_type == "Event"
        assert Card.ALL["Fidel"].card_type == "Event"

    def test_card_stage(self):
        assert Card.ALL["Asia_Scoring"].stage == "Early War"
        assert Card.ALL["Duck_and_Cover"].stage == "Early War"

    def test_card_owner_us(self):
        assert Card.ALL["Duck_and_Cover"].owner == Side.US
        assert Card.ALL["Five_Year_Plan"].owner == Side.US

    def test_card_owner_ussr(self):
        assert Card.ALL["Fidel"].owner == Side.USSR
        assert Card.ALL["Vietnam_Revolts"].owner == Side.USSR

    def test_card_owner_neutral(self):
        assert Card.ALL["The_China_Card"].owner == Side.NEUTRAL

    def test_scoring_card_may_not_be_held(self):
        assert Card.ALL["Asia_Scoring"].may_be_held is False
        assert Card.ALL["Europe_Scoring"].may_be_held is False

    def test_event_card_may_be_held(self):
        assert Card.ALL["Duck_and_Cover"].may_be_held is True

    def test_china_card_cannot_headline(self):
        assert Card.ALL["The_China_Card"].can_headline is False

    def test_most_cards_can_headline(self):
        assert Card.ALL["Duck_and_Cover"].can_headline is True
        assert Card.ALL["Fidel"].can_headline is True

    def test_event_unique_fidel(self):
        assert Card.ALL["Fidel"].event_unique is True

    def test_event_not_unique_duck_and_cover(self):
        assert Card.ALL["Duck_and_Cover"].event_unique is False

    def test_scoring_region(self):
        assert Card.ALL["Asia_Scoring"].scoring_region == MapRegion.ASIA
        assert Card.ALL["Europe_Scoring"].scoring_region == MapRegion.EUROPE
        assert Card.ALL["Middle_East_Scoring"].scoring_region == MapRegion.MIDDLE_EAST

    def test_event_text_present(self):
        assert len(Card.ALL["Duck_and_Cover"].event_text) > 0
        assert len(Card.ALL["Fidel"].event_text) > 0


# ---------------------------------------------------------------------------
# Card instance behaviour
# ---------------------------------------------------------------------------

class TestCardInstanceBehaviour:

    def test_card_info_returns_self(self, game_cards: GameCards):
        card = game_cards["Duck_and_Cover"]
        assert card.info is card

    def test_card_repr_event(self, game_cards: GameCards):
        card = game_cards["Duck_and_Cover"]
        r = repr(card)
        assert "Duck_and_Cover" in r
        assert "3" in r  # ops

    def test_card_repr_scoring(self, game_cards: GameCards):
        card = game_cards["Asia_Scoring"]
        r = repr(card)
        assert "Asia_Scoring" in r
        # Scoring cards should not show ops in repr
        assert " - " not in r

    def test_card_eq_by_name(self, game_cards: GameCards):
        card = game_cards["Duck_and_Cover"]
        assert card == "Duck_and_Cover"
        assert not (card == "Fidel")

    def test_card_is_playable_default(self, game_cards: GameCards):
        card = game_cards["Duck_and_Cover"]
        assert card.is_playable is True

    def test_card_event_occurred_default(self, game_cards: GameCards):
        card = game_cards["Duck_and_Cover"]
        assert card.event_occurred is False


# ---------------------------------------------------------------------------
# can_event checks
# ---------------------------------------------------------------------------

class TestCanEvent:

    def test_can_event_own_side(self, game: "Game"):
        """US-owned card can be evented by US."""
        assert game.cards["Duck_and_Cover"].can_event(game, Side.US) is True

    def test_can_event_neutral_card(self, game: "Game"):
        """Neutral cards cannot be evented by either side via can_event base implementation,
        but The_China_Card overrides this to always return False."""
        assert game.cards["The_China_Card"].can_event(game, Side.USSR) is False
        assert game.cards["The_China_Card"].can_event(game, Side.US) is False

    def test_cannot_event_opponents_card(self, game: "Game"):
        """USSR-owned card cannot be evented by US."""
        assert game.cards["Fidel"].can_event(game, Side.US) is False

    def test_can_event_ussr_card_by_ussr(self, game: "Game"):
        """USSR-owned card can be evented by USSR."""
        assert game.cards["Fidel"].can_event(game, Side.USSR) is True


# ---------------------------------------------------------------------------
# GameCards container
# ---------------------------------------------------------------------------

class TestGameCards:

    def test_gamecards_all_populated(self, game_cards: GameCards):
        assert len(game_cards.ALL) > 0

    def test_gamecards_getitem(self, game_cards: GameCards):
        card = game_cards["Duck_and_Cover"]
        assert card.name == "Duck_and_Cover"

    def test_gamecards_early_war_list(self, game_cards: GameCards):
        assert len(game_cards.early_war) > 0
        assert "Asia_Scoring" in game_cards.early_war
        assert "Duck_and_Cover" in game_cards.early_war

    def test_gamecards_in_play_starts_empty(self, game_cards: GameCards):
        assert len(game_cards.in_play) == 0

    def test_gamecards_instances_are_distinct(self, game_cards: GameCards):
        """Each GameCards instance should have its own card objects."""
        gc2 = GameCards()
        gc2["Duck_and_Cover"].event_occurred = True
        assert game_cards["Duck_and_Cover"].event_occurred is False


# ---------------------------------------------------------------------------
# Card dispose mechanics
# ---------------------------------------------------------------------------

class TestCardDispose:

    def test_dispose_non_unique_goes_to_discard(self, game: "Game"):
        """A non-unique card goes to the discard pile after disposal."""
        game.hand[Side.US].append("Duck_and_Cover")
        card = game.cards["Duck_and_Cover"]
        card.event_occurred = True
        card.dispose(game, Side.US)
        assert "Duck_and_Cover" in game.discard_pile
        assert "Duck_and_Cover" not in game.hand[Side.US]

    def test_dispose_unique_card_removed(self, game: "Game"):
        """A unique card whose event occurred goes to the removed pile."""
        game.hand[Side.USSR].append("Fidel")
        card = game.cards["Fidel"]
        card.event_occurred = True
        card.dispose(game, Side.USSR)
        assert "Fidel" in game.removed_pile
        assert "Fidel" not in game.discard_pile

    def test_dispose_unique_card_not_evented_goes_to_discard(self, game: "Game"):
        """A unique card whose event did NOT occur goes to discard."""
        game.hand[Side.USSR].append("Fidel")
        card = game.cards["Fidel"]
        card.event_occurred = False
        card.dispose(game, Side.USSR)
        assert "Fidel" in game.discard_pile
        assert "Fidel" not in game.removed_pile
