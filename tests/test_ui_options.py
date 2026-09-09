from twilight_enums import InputType, Side
from twilight_input_output import Input
from twilight_ui import UI


def test_generate_options_uses_legal_options_including_stop_early_for_country():
    ui = UI()
    ui.game.input_state = Input(
        Side.US,
        InputType.SELECT_COUNTRY,
        lambda _: True,
        ["France"],
        option_stop_early="Stop",
    )

    ui.generate_options()

    values = set(ui.options.values())
    assert "France" in values
    assert "Stop" in values
    assert len(values) == 2


def test_parse_move_reports_ambiguous_prefix(capsys):
    ui = UI()
    ui.game_in_progress = True
    ui.options = {1: "France", 2: "Finland"}
    ui.game.input_state = Input(
        Side.US,
        InputType.SELECT_COUNTRY,
        lambda _: True,
        ["France", "Finland"],
    )

    ui.parse_move("f")

    assert "multiple matching options" in capsys.readouterr().out
    assert all(count == 0 for count in ui.input_state.selection.values())


def test_parse_move_accepts_abbreviated_commit(monkeypatch):
    ui = UI()
    ui.game_in_progress = True
    ui.game_lookahead = object()
    called = []
    monkeypatch.setattr(ui, "commit", lambda: called.append("commit"))

    ui.parse_move("y")

    assert called == ["commit"]
