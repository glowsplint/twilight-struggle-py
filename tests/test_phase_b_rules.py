from tests.helpers import make_game
from twilight_enums import MapRegion, Side
from twilight_playerview import PlayerView


def test_nato_only_protects_current_us_controlled_europe():
    game = make_game()
    game.basket[Side.US].append("NATO")
    game.map["France"].set_influence(3, 0)  # USSR control
    game.map["Italy"].set_influence(0, 3)   # US control

    protected = set(game.calculate_nato_countries())
    assert "Italy" in protected
    assert "France" not in protected


def test_summit_tie_has_no_defcon_choice_input():
    game = make_game()
    summit = game.cards["Summit"]
    game.input_state = type("InputStub", (), {"reps": 1})()

    # Equal totals -> tie, should not create follow-up chooser input.
    summit.dice_callback(game, 0, (4, 4))
    assert game.input_state.reps == 0


def test_cuban_missile_cancel_prompt_uses_acting_side():
    game = make_game()
    game.map["Cuba"].set_influence(2, 0)

    cmc = game.cards["Cuban_Missile_Crisis"]
    cmc.cuban_missile_remove(game, Side.USSR)

    assert game.input_state is not None
    assert game.input_state.side == Side.USSR


def test_cuban_missile_crisis_offers_cancellation_before_action_round():
    game = make_game()
    game.ar_track = 0
    game.ar_side = Side.USSR
    game.basket[Side.US].append("Cuban_Missile_Crisis")
    game.map["Cuba"].set_influence(2, 0)

    game.ar_complete()
    game.stage_complete()

    assert game.input_state.side == Side.USSR
    assert game.input_state.prompt.startswith("Cuban Missile Crisis:")
    assert game.input_state.recv("Cuba") is True
    assert "Cuban_Missile_Crisis" not in game.basket[Side.US]

    game.stage_complete()
    assert game.input_state.side == Side.USSR
    assert game.input_state.prompt == "Select a card in hand to play."


def test_che_second_coup_excludes_first_target():
    game = make_game()
    # Ensure first coup target has US influence to trigger second coup permission.
    game.map["Costa_Rica"].set_influence(0, 2)
    game.input_state = type("InputStub", (), {"reps": 1})()

    # Directly run dice callback path for Che.
    game.coup_dice_callback("Costa_Rica", Side.USSR, 3, False, "6", che=True)
    game.stage_complete()

    assert game.input_state is not None
    options = set(game.input_state.selection.keys())
    assert "Costa_Rica" not in options


def test_che_no_second_coup_after_thermonuclear_termination():
    game = make_game()
    # Cuban Missile Crisis in the opponent basket: the first coup drops DEFCON
    # to 1 and terminates the game (thermonuclear war) mid-callback.
    game.basket[Side.US].append("Cuban_Missile_Crisis")
    game.map["Costa_Rica"].set_influence(0, 2)
    game.input_state = type("InputStub", (), {"reps": 1})()

    result = game.coup_dice_callback("Costa_Rica", Side.USSR, 3, False, "6", che=True)

    assert result is True
    assert game.terminated
    assert game.termination_reason == "thermonuclear_war"
    # The Che follow-up coup must not revive the terminated game: no new input
    # and no stage pushed back onto the cleared stage list.
    assert game.input_state is None
    assert not game.stage_list


def test_cuban_missile_crisis_coup_loses_for_couping_side_not_phasing_side():
    game = make_game()
    game.ar_side = Side.USSR
    game.defcon_track = 2
    game.basket[Side.USSR].append("Cuban_Missile_Crisis")
    game.map["Costa_Rica"].set_influence(1, 0)

    game.map.coup(game, "Costa_Rica", Side.US, 1, 1)

    assert game.terminated
    assert game.defcon_track == 1
    assert game.termination_reason == "thermonuclear_war"
    assert game.termination_winner == Side.USSR
    assert game.termination_context == {
        "defcon": 1,
        "cause": "Cuban_Missile_Crisis",
        "loser": "US",
    }


def test_formosan_scoring_does_not_mutate_global_country_info():
    game = make_game()
    game.basket[Side.US].append("Formosan_Resolution")
    game.map["Taiwan"].set_influence(0, 2)

    game.score(MapRegion.ASIA)

    assert game.map["Taiwan"].info.battleground is False


def test_player_view_is_snapshot_not_live_alias():
    game = make_game()
    view = PlayerView(Side.US)
    view.update(game, Side.US)

    view.hand.append("Fake_Card")
    view.milops_track[Side.US] = 99

    assert "Fake_Card" not in game.hand[Side.US]
    assert game.milops_track[Side.US] != 99


def test_china_and_vietnam_reset_extra_point_taken_flag():
    china = make_game().cards["The_China_Card"]
    vietnam = make_game().cards["Vietnam_Revolts"]

    china.extra_point_taken = True
    vietnam.extra_point_taken = True
    china.reset()
    vietnam.reset()

    assert china.extra_point_taken is False
    assert vietnam.extra_point_taken is False


def test_wwby_awards_vp_on_us_non_event_action():
    # Any US action other than playing UN Intervention as an Event triggers
    # the +3 VP, including plain Operations.
    game = make_game()
    game.basket[Side.USSR].append("We_Will_Bury_You")

    game.resolve_card_action(Side.US, "Duck_and_Cover", "INFLUENCE")

    assert game.vp_track == 3
    assert "We_Will_Bury_You" not in game.basket[Side.USSR]


def test_wwby_no_vp_when_un_intervention_played_as_event():
    game = make_game()
    game.basket[Side.USSR].append("We_Will_Bury_You")

    game.resolve_card_action(Side.US, "UN_Intervention", "PLAY_EVENT")

    assert game.vp_track == 0
    assert "We_Will_Bury_You" not in game.basket[Side.USSR]


def test_wwby_not_consumed_on_ussr_action_round():
    # The pending penalty resolves on the US player's next action round;
    # the USSR's own action round must not consume the basket marker.
    game = make_game()
    game.basket[Side.USSR].append("We_Will_Bury_You")

    game.resolve_card_action(Side.USSR, "Nuclear_Test_Ban", "INFLUENCE")

    assert game.vp_track == 0
    assert "We_Will_Bury_You" in game.basket[Side.USSR]


def test_wwby_vp_autovictory_stops_action_resolution():
    game = make_game()
    game.vp_track = 17
    game.basket[Side.USSR].append("We_Will_Bury_You")

    game.resolve_card_action(Side.US, "Duck_and_Cover", "PLAY_EVENT")

    assert game.terminated
    assert game.termination_reason == "vp_autovictory"
    # No stage may be scheduled on the terminated game.
    assert not game.stage_list
    assert game.input_state is None


def test_flower_power_vp_autovictory_stops_action_resolution():
    game = make_game()
    game.vp_track = 18
    game.basket[Side.USSR].append("Flower_Power")

    game.resolve_card_action(Side.US, "Korean_War", "PLAY_EVENT")

    assert game.terminated
    assert game.termination_reason == "vp_autovictory"
    assert not game.stage_list
    assert game.input_state is None


def test_flower_power_only_rewards_us_played_war_cards():
    # Rule: "USSR gains 2 VP for every subsequently US played war card".
    # The USSR playing a war card itself (any of the 5 war cards, as event
    # or for ops) must NOT award the +2 VP.
    for action in ("PLAY_EVENT", "INFLUENCE", "REALIGNMENT", "COUP"):
        game = make_game()
        game.basket[Side.USSR].append("Flower_Power")

        game.resolve_card_action(Side.USSR, "Korean_War", action)

        assert game.vp_track == 0, f"USSR playing a war card via {action} must not trigger Flower Power"
        assert not game.terminated


def test_flower_power_awards_on_us_war_card_play():
    # US playing a war card as an Event awards USSR 2 VP.
    game = make_game()
    game.basket[Side.USSR].append("Flower_Power")

    game.resolve_card_action(Side.US, "Korean_War", "PLAY_EVENT")

    assert game.vp_track == 2


def test_flower_power_not_awarded_on_space_race():
    # "unless played on the Space Race": spacing a war card must not award VP.
    game = make_game()
    game.basket[Side.USSR].append("Flower_Power")
    game.space_track[Side.US] = 0
    game.spaced_turns = [0, 0]

    game.resolve_card_action(Side.US, "Korean_War", "SPACE")

    assert game.vp_track == 0


def test_flower_power_resolve_event_first_is_awarded_only_once():
    game = make_game()
    game.basket[Side.USSR].append("Flower_Power")

    game.resolve_card_action(
        Side.US, "Korean_War", "RESOLVE_EVENT_FIRST")
    assert game.vp_track == 2
    select_ops = game.stage_list[0]
    game.stage_list = []
    select_ops()
    assert game.input_state.recv("INFLUENCE") is True
    game.stage_complete()

    assert game.vp_track == 2


def test_headline_thermo_blames_resolving_side():
    # A headline event degrading DEFCON to 1: the side whose headline is
    # being resolved is the phasing player and loses, regardless of any
    # stale ar_side value.
    game = make_game()
    game.ar_track = 0
    game.ar_side = Side.US  # stale value must not decide attribution
    game.defcon_track = 2
    game.headline_bin[Side.USSR] = "We_Will_Bury_You"
    game.hand[Side.USSR].append("We_Will_Bury_You")

    game.resolve_headline(Side.USSR)
    game.stage_complete()  # trigger_event -> DEFCON 2 -> 1

    assert game.terminated
    assert game.termination_reason == "thermonuclear_war"
    assert game.termination_winner == Side.US  # USSR's headline -> USSR loses


def test_headline_granted_ops_thermo_blames_headline_owner():
    # DEFCON 2 after the US headline resolved; the USSR's CIA Created is
    # being resolved and the US uses the granted 1 Op to coup Cuba. The
    # USSR loses: attribution follows whose headline is being resolved,
    # not who conducts the operation.
    game = make_game()
    game.ar_track = 0
    game.ar_side = Side.US  # stale, must not matter
    game.defcon_track = 2
    game.headline_resolving_side = Side.USSR
    game.map["Cuba"].set_influence(3, 0)

    game.map.coup(game, "Cuba", Side.US, 1, 1)

    assert game.terminated
    assert game.termination_reason == "thermonuclear_war"
    assert game.termination_winner == Side.US


def test_ar_thermo_blames_phasing_player_for_granted_ops():
    # Rule 6.3: during action rounds the phasing player is responsible for
    # all DEFCON degradation, even when the opponent conducts granted Ops
    # (e.g. Lone Gunman played by the US, USSR coups with the free Op).
    game = make_game()
    game.ar_track = 3
    game.ar_side = Side.US
    game.defcon_track = 2
    game.map["Cuba"].set_influence(0, 3)

    game.map.coup(game, "Cuba", Side.USSR, 1, 1)

    assert game.terminated
    assert game.termination_winner == Side.USSR  # US (phasing) loses


def test_un_intervention_callback_rejects_when_game_terminated():
    game = make_game()
    game.terminated = True
    game.input_state = type("InputStub", (), {"reps": 1})()

    accepted = game.cards["UN_Intervention"].callback(game, Side.US, "NATO")

    assert accepted is False
    assert game.input_state.reps == 1
