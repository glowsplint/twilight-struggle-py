import pytest

from tests.helpers import make_game
from ts_save import build_save_text, position_snapshot, split_save_text
from twilight_enums import Side


BASE = "SETUP: USSR will play as USSR.\nUS will play as USA.\n"


def test_no_extensions_is_byte_for_byte_espionnage():
    game = make_game()
    assert build_save_text(BASE, game) == BASE


def test_seed_extension_round_trips_without_private_hands():
    game = make_game()
    game.select_card(Side.USSR)

    saved = build_save_text(
        BASE, game, include_seed=True, seed=123, player_actions=["Poland"])
    base, extension = split_save_text(saved)

    assert base == BASE
    assert extension["replay"] == {"seed": 123, "actions": ["Poland"]}
    assert extension["capabilities"] == {
        "deterministic_replay": True,
        "private_hands": False,
        "private_state_derivable_from_seed": True,
        "engine_resume": False,
    }
    assert "hands" not in extension["position"]
    assert "headline" not in extension["position"]
    assert extension["position"]["input"]["options_redacted"] is True
    assert "options" not in extension["position"]["input"]


def test_hands_extension_preserves_both_sides_without_seed():
    game = make_game()
    game.hand[Side.USSR] = ["Fidel"]
    game.hand[Side.US] = ["NATO"]
    game.headline_bin = ["COMECON", "Duck_and_Cover"]

    saved = build_save_text(BASE, game, include_hands=True)
    base, extension = split_save_text(saved)

    assert base == BASE
    assert "replay" not in extension
    assert extension["position"]["hands"] == {
        "USSR": ["Fidel"], "US": ["NATO"],
    }
    assert extension["position"]["ars_by_turn"]["USSR"][1] == 6
    assert extension["position"]["card_state"]["The_China_Card"] == {
        "is_playable": True,
    }
    assert extension["position"]["headline"] == ["COMECON", "Duck_and_Cover"]
    assert extension["capabilities"]["private_hands"] is True
    assert extension["capabilities"]["private_state_derivable_from_seed"] is False


def test_position_snapshot_preserves_scored_region_history():
    game = make_game()
    game.cards["Europe_Scoring"].event_occurred = True
    game.cards["Africa_Scoring"].event_occurred = True

    position = position_snapshot(game, include_hands=True)

    assert position["scored_regions"] == [
        "Africa_Scoring", "Europe_Scoring"]


def test_extension_is_human_editable_commented_json():
    saved = build_save_text(BASE, make_game(), include_hands=True)
    assert "# TSX-DATA\n# {\n" in saved
    assert '\n#   "position": {' in saved


def test_parser_accepts_legacy_one_line_v1_block():
    payload = {
        "format": "ts-espionnage-save",
        "version": 1,
        "position": {},
    }
    saved = (BASE + "\n# TSX-BEGIN v1\n# TSX-DATA " +
             __import__("json").dumps(payload) + "\n# TSX-END\n")
    base, extension = split_save_text(saved)
    assert base == BASE
    assert extension == payload


def test_legacy_espionnage_parser_ignores_extension(tmp_path):
    parse_espionnage = pytest.importorskip("rl.replay_parser").parse_espionnage

    base = (
        "SETUP: USSR will play as USSR.\n"
        "US will play as USA.\n\n"
        "Turn 1, USSR AR1: COMECON*: Place Influence (3 Ops):\n"
        "USSR +1 in Poland [0][4]\n"
    )
    plain_path = tmp_path / "plain.tsg"
    extended_path = tmp_path / "extended.tsg"
    plain_path.write_text(base, encoding="utf-8")
    extended_path.write_text(
        build_save_text(base, make_game(), include_hands=True),
        encoding="utf-8",
    )

    assert parse_espionnage(str(extended_path)) == \
        parse_espionnage(str(plain_path))


def test_seed_and_player_actions_reconstruct_exact_engine_position():
    TwilightSelfPlayEnv = pytest.importorskip("rl.env").TwilightSelfPlayEnv

    seed = 20260827
    original = TwilightSelfPlayEnv(seed=seed, suppress_output=True)
    original.reset()
    actions = []
    for _ in range(12):
        action = original.legal_actions()[0]
        actions.append(action)
        original.step(action)

    text = build_save_text(
        BASE, original.game, include_seed=True, seed=seed,
        player_actions=actions, include_hands=True)
    _, extension = split_save_text(text)

    restored = TwilightSelfPlayEnv(
        seed=extension["replay"]["seed"], suppress_output=True)
    restored.reset()
    for action in extension["replay"]["actions"]:
        restored.step(action)

    assert position_snapshot(restored.game, include_hands=True) == \
        position_snapshot(original.game, include_hands=True)


def test_position_snapshot_contains_public_piles_and_tracks():
    game = make_game()
    game.discard_pile = ["Fidel"]
    game.removed_pile = ["NATO"]
    game.basket[Side.US].append("Chernobyl_Asia")

    position = position_snapshot(game)

    assert position["discard"] == ["Fidel"]
    assert position["removed"] == ["NATO"]
    assert position["basket"]["US"] == ["Chernobyl_Asia"]
    assert position["map"]["North_Korea"] == [3, 0]
    assert position["vp"] == 0
    assert position["defcon"] == 5


def test_seed_must_be_concrete_when_requested():
    with pytest.raises(ValueError, match="integer seed"):
        build_save_text(BASE, make_game(), include_seed=True)


def test_malformed_extension_is_rejected():
    malformed = BASE + "\n# TSX-BEGIN v1\n# TSX-DATA {}\n"
    with pytest.raises(ValueError, match="malformed"):
        split_save_text(malformed)