from tests.helpers import make_game
from twilight_enums import Side


def test_blockade_no_eligible_discard_applies_forced_penalty_immediately():
    game = make_game()
    game.hand[Side.US] = ["Fidel"]  # 2 ops, cannot satisfy Blockade discard requirement.
    game.map["West_Germany"].set_influence(0, 4)

    game.cards["Blockade"].use_event(game, Side.USSR)

    assert game.map["West_Germany"].influence[Side.US] == 0
    assert game.input_state is None


def test_blockade_eligibility_uses_us_side_ops_modifiers():
    game = make_game()
    game.hand[Side.US] = ["NATO"]  # 4 ops raw
    game.basket[Side.USSR].append("Red_Scare_Purge")

    game.cards["Blockade"].use_event(game, Side.USSR)

    # Red Scare reduces US effective ops by 1, so NATO is still eligible at 3.
    assert game.input_state is not None
    assert set(game.input_state.selection.keys()) == {"NATO"}


def test_latin_debt_no_eligible_discard_goes_directly_to_ussr_choice():
    game = make_game()
    game.hand[Side.US] = ["Fidel"]
    game.map["Brazil"].set_influence(2, 0)

    game.cards["Latin_American_Debt_Crisis"].use_event(game, Side.USSR)

    assert game.input_state is not None
    assert game.input_state.side == Side.USSR
    assert game.input_state.prompt == "Select countries to double USSR influence."
    assert game.input_state.reps == 2


def test_latin_debt_eligibility_uses_us_side_ops_modifiers():
    game = make_game()
    game.hand[Side.US] = ["NATO"]
    game.basket[Side.USSR].append("Red_Scare_Purge")

    game.cards["Latin_American_Debt_Crisis"].use_event(game, Side.USSR)

    assert game.input_state is not None
    assert game.input_state.side == Side.US
    assert set(game.input_state.selection.keys()) == {"NATO"}


def test_event_influence_callback_accepts_stop_early_option():
    game = make_game()
    game.map["UK"].set_influence(0, 1)

    game.cards["Pershing_II_Deployed"].use_event(game, Side.USSR)
    assert game.input_state is not None
    assert game.input_state.option_stop_early == "Do not remove more influence."

    assert game.input_state.recv("Do not remove more influence.") is True
    assert game.input_state.complete is True
