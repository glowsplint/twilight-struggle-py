"""
State Encoder: Converts game state into a fixed-size numpy feature vector.

The encoding is normalized from the acting player's perspective:
- my_influence / opp_influence (rather than fixed USSR/US)
- VP sign flipped if acting as US

Feature layout (~756 features):
  Map state:        87 countries x 4 = 348
  Track state:      44
  Card state:       330 (110 cards x 3 flags)
  Active effects:   30
  Meta:             4
  Total:            ~756
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from cards import Card
from enums import MapRegion, Side
from world_map import CountryInfo

if TYPE_CHECKING:
    from game_mechanics import Game


# Build deterministic ordered lists at import time
COUNTRY_NAMES = sorted(CountryInfo.ALL.keys(), key=lambda n: CountryInfo.ALL[n].country_index)
CARD_NAMES = sorted(Card.ALL.keys(), key=lambda n: Card.ALL[n].card_index)

NUM_COUNTRIES = len(COUNTRY_NAMES)
NUM_CARDS = len(CARD_NAMES)

# Map indices for fast lookup
COUNTRY_TO_IDX = {name: i for i, name in enumerate(COUNTRY_NAMES)}
CARD_TO_IDX = {name: i for i, name in enumerate(CARD_NAMES)}

# Feature dimensions
MAP_FEATURES = NUM_COUNTRIES * 4      # ussr_inf, us_inf, stability, battleground per country
DEFCON_FEATURES = 5                   # one-hot DEFCON 1-5
TURN_FEATURES = 10                    # one-hot turn 1-10
AR_FEATURES = 8                       # one-hot AR 0-7
VP_FEATURES = 1                       # normalized VP
MILOPS_FEATURES = 2                   # my_milops, opp_milops
SPACE_FEATURES = 18                   # my_space one-hot(9) + opp_space one-hot(9)
TRACK_FEATURES = DEFCON_FEATURES + TURN_FEATURES + AR_FEATURES + VP_FEATURES + MILOPS_FEATURES + SPACE_FEATURES
CARD_FEATURES = NUM_CARDS * 3         # in_hand, in_discard, removed per card
EFFECT_FEATURES = 30                  # binary flags for active effects in basket
META_FEATURES = 4                     # side, china_card_playable, china_card_holder, opp_hand_size_normalized

TOTAL_FEATURES = MAP_FEATURES + TRACK_FEATURES + CARD_FEATURES + EFFECT_FEATURES + META_FEATURES

# Known effect card names for basket encoding
EFFECT_CARDS = [
    "NATO", "Marshall_Plan", "Warsaw_Pact_Formed", "De_Gaulle_Leads_France",
    "Containment", "Red_Scare_Purge", "US_Japan_Mutual_Defense_Pact",
    "Formosan_Resolution", "NORAD", "The_China_Card", "Vietnam_Revolts",
    "Flower_Power", "U2_Incident", "Cuban_Missile_Crisis", "Nuclear_Subs",
    "Quagmire", "Bear_Trap", "Salt_Negotiations", "Brezhnev_Doctrine",
    "Willy_Brandt", "Camp_David_Accords", "John_Paul_II_Elected_Pope",
    "Latin_American_Death_Squads", "Missile_Envy", "We_Will_Bury_You",
    "North_Sea_Oil", "The_Reformer", "The_Iron_Lady", "Yuri_and_Samantha",
    "AWACS_Sale_to_Saudis",
]
EFFECT_TO_IDX = {name: i for i, name in enumerate(EFFECT_CARDS)}


def encode_state(game: Game, perspective_side: Side) -> np.ndarray:
    """
    Encode the full game state into a fixed-size numpy array from perspective_side's POV.

    Parameters
    ----------
    game : Game
        The game instance to encode.
    perspective_side : Side
        The side from whose perspective we encode (my vs opponent).

    Returns
    -------
    np.ndarray
        Feature vector of shape (TOTAL_FEATURES,), dtype float32.
    """
    features = np.zeros(TOTAL_FEATURES, dtype=np.float32)
    offset = 0

    my_side = perspective_side
    opp_side = my_side.opp

    # --- Map features (87 countries x 4) ---
    for i, name in enumerate(COUNTRY_NAMES):
        country = game.map[name]
        base = offset + i * 4
        features[base + 0] = country.influence[my_side] / 10.0     # normalize
        features[base + 1] = country.influence[opp_side] / 10.0
        features[base + 2] = country.info.stability / 5.0
        features[base + 3] = float(country.info.battleground)
    offset += MAP_FEATURES

    # --- DEFCON one-hot (5) ---
    defcon = max(1, min(5, game.defcon_track))
    features[offset + defcon - 1] = 1.0
    offset += DEFCON_FEATURES

    # --- Turn one-hot (10) ---
    turn = max(1, min(10, game.turn_track))
    features[offset + turn - 1] = 1.0
    offset += TURN_FEATURES

    # --- AR one-hot (8) ---
    ar = max(0, min(7, game.ar_track))
    features[offset + ar] = 1.0
    offset += AR_FEATURES

    # --- VP (1), normalized and flipped for perspective ---
    vp = game.vp_track * my_side.vp_mult  # positive = good for perspective_side
    features[offset] = vp / 20.0
    offset += VP_FEATURES

    # --- Milops (2) ---
    features[offset + 0] = game.milops_track[my_side] / 5.0
    features[offset + 1] = game.milops_track[opp_side] / 5.0
    offset += MILOPS_FEATURES

    # --- Space race one-hot (9 + 9 = 18) ---
    my_space = max(0, min(8, game.space_track[my_side]))
    opp_space = max(0, min(8, game.space_track[opp_side]))
    features[offset + my_space] = 1.0
    features[offset + 9 + opp_space] = 1.0
    offset += SPACE_FEATURES

    # --- Card state (NUM_CARDS x 3) ---
    my_hand = set(game.hand[my_side])
    discard = set(game.discard_pile)
    removed = set(game.removed_pile)
    for i, name in enumerate(CARD_NAMES):
        base = offset + i * 3
        features[base + 0] = float(name in my_hand)
        features[base + 1] = float(name in discard)
        features[base + 2] = float(name in removed)
    offset += CARD_FEATURES

    # --- Active effects (30 binary flags) ---
    for side_idx in (my_side, opp_side):
        for eff_name in game.basket[side_idx]:
            if eff_name in EFFECT_TO_IDX:
                features[offset + EFFECT_TO_IDX[eff_name]] = (
                    1.0 if side_idx == my_side else -1.0
                )
    offset += EFFECT_FEATURES

    # --- Meta features (4) ---
    features[offset + 0] = 1.0 if my_side == Side.USSR else 0.0
    china_holder = _china_card_holder(game)
    features[offset + 1] = float(china_holder == my_side)
    features[offset + 2] = float(
        "The_China_Card" in game.hand[my_side]
        and game.cards["The_China_Card"].is_playable
    )
    features[offset + 3] = len(game.hand[opp_side]) / 10.0
    offset += META_FEATURES

    assert offset == TOTAL_FEATURES
    return features


def _china_card_holder(game: Game) -> Side:
    """Determine which side holds the China Card."""
    if "The_China_Card" in game.hand[Side.USSR]:
        return Side.USSR
    elif "The_China_Card" in game.hand[Side.US]:
        return Side.US
    return Side.NEUTRAL
