from tests.helpers import make_game
from twilight_enums import Side


def test_missile_envy_exchange_callback_sets_game_input_and_returns_true():
    game = make_game()
    game.hand[Side.US] = ["NATO", "Fidel"]
    card = game.cards["Missile_Envy"]

    game.cards["Missile_Envy"].use_event(game, Side.USSR)
    assert game.input_state is not None

    accepted = game.input_state.recv("NATO")
    assert accepted is True
    assert game.input_state is not None
    assert game.input_state.prompt.startswith("Opponent has traded NATO")


def test_missile_envy_opponent_owned_exchange_does_not_offer_play_event():
    game = make_game()
    game.hand[Side.US] = ["NATO"]
    game.cards["Missile_Envy"].use_event(game, Side.USSR)

    assert game.input_state.recv("NATO") is True
    options = set(game.input_state.selection.keys())
    assert "PLAY_EVENT" not in options
    assert "RESOLVE_EVENT_FIRST" not in options


def test_qbt_forces_missile_envy_when_not_degraded():
    game = make_game()
    game.basket[Side.US].extend(["Quagmire", "Missile_Envy"])
    game.hand[Side.US] = ["Missile_Envy", "NATO"]

    game.qbt_discard(Side.US, "Quagmire")

    assert game.input_state is not None
    assert set(game.input_state.selection.keys()) == {"Missile_Envy"}


def test_qbt_excludes_missile_envy_when_degraded_by_red_scare():
    game = make_game()
    game.basket[Side.US].extend(["Quagmire", "Missile_Envy"])
    game.basket[Side.USSR].append("Red_Scare_Purge")
    game.hand[Side.US] = ["Missile_Envy", "NATO", "Fidel"]

    game.qbt_discard(Side.US, "Quagmire")

    assert game.input_state is not None
    options = set(game.input_state.selection.keys())
    assert "Missile_Envy" not in options
    assert options == {"NATO"}


def test_qbt_forced_scoring_uses_play_event_and_disposes_card():
    game = make_game()
    game.basket[Side.US].append("Quagmire")
    game.hand[Side.US] = ["Asia_Scoring"]
    game.ar_track = 6

    game.qbt_discard(Side.US, "Quagmire")
    assert game.input_state is not None
    assert set(game.input_state.selection.keys()) == {"Asia_Scoring"}

    assert game.input_state.recv("Asia_Scoring") is True
    # Run queued stages: resolve action -> trigger event -> dispose.
    game.stage_complete()
    game.stage_complete()
    game.stage_complete()

    assert "Asia_Scoring" not in game.hand[Side.US]
    assert "Asia_Scoring" in game.discard_pile
