"""Versioned save extension layered on an unchanged TS Espionnage record.

The standard text is always the prefix of an extended save. Consumers that
understand only TS Espionnage can ignore the final ``# TSX`` block. When both
optional features are disabled, :func:`build_save_text` returns the input text
byte-for-byte unchanged.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Optional, Tuple

from game_mechanics import Game
from twilight_enums import InputType, Side


FORMAT_NAME = "ts-espionnage-save"
FORMAT_VERSION = 1
BEGIN_MARKER = "# TSX-BEGIN v1"
DATA_MARKER = "# TSX-DATA"
DATA_PREFIX = "# TSX-DATA "
END_MARKER = "# TSX-END"


def _side_name(value: object) -> str:
    return value.name if hasattr(value, "name") else str(value)


def _current_input(game: Game, include_hands: bool) -> Optional[dict]:
    input_state = game.input_state
    if input_state is None:
        return None
    input_type = _side_name(input_state.state)
    payload = {
        "side": _side_name(input_state.side),
        "type": input_type,
        "prompt": input_state.prompt or "",
        "reps": input_state.reps,
        "reps_unit": input_state.reps_unit or "",
        "max_per_option": input_state.max_per_option,
    }
    if input_type != InputType.SELECT_CARD.name or include_hands:
        payload["options"] = [str(option) for option in input_state.legal_options]
    else:
        payload["options_redacted"] = True
    return payload


def position_snapshot(game: Game, *, include_hands: bool = False) -> dict:
    """Serialize the current inspectable position without Python callables.

    This is a scenario/debug snapshot, not a pickle of the stage stack. Exact
    engine reconstruction is provided separately by ``replay`` when a seed is
    included.
    """
    winner = getattr(game, "termination_winner", Side.NEUTRAL)
    position = {
        "turn": game.turn_track,
        "ar": game.ar_track,
        "ar_side": _side_name(game.ar_side),
        "vp": game.vp_track,
        "defcon": game.defcon_track,
        "milops": list(game.milops_track),
        "space": list(game.space_track),
        "spaced_turns": list(game.spaced_turns),
        "ars_by_turn": {
            "USSR": list(game.ars_by_turn[Side.USSR]),
            "US": list(game.ars_by_turn[Side.US]),
        },
        "map": {
            name: [country.influence[Side.USSR], country.influence[Side.US]]
            for name, country in game.map.ALL.items()
            if not country.info.superpower
            and (country.influence[Side.USSR] or country.influence[Side.US])
        },
        "discard": list(game.discard_pile),
        "removed": list(game.removed_pile),
        "basket": {
            "USSR": list(game.basket[Side.USSR]),
            "US": list(game.basket[Side.US]),
        },
        "draw_count": len(game.draw_pile),
        "limbo": list(game.limbo),
        "scored_regions": sorted(
            name for name, card in game.cards.ALL.items()
            if card.info.card_type == "Scoring" and card.event_occurred
        ),
        "input": _current_input(game, include_hands),
        "terminated": bool(game.terminated),
        "termination_reason": getattr(game, "termination_reason", "") or "",
        "termination_winner": _side_name(winner),
    }
    if include_hands:
        position["hands"] = {
            "USSR": list(game.hand[Side.USSR]),
            "US": list(game.hand[Side.US]),
        }
        position["headline"] = list(game.headline_bin)
        position["card_state"] = {
            "The_China_Card": {
                "is_playable": bool(
                    game.cards["The_China_Card"].is_playable),
            },
            "Missile_Envy": {
                "exchange": bool(game.cards["Missile_Envy"].exchange),
            },
        }
    return position


def build_save_text(
        espionnage_text: str,
        game: Game,
        *,
        include_seed: bool = False,
        seed: Optional[int] = None,
        player_actions: Iterable[object] = (),
        include_hands: bool = False) -> str:
    """Return standard text or append one machine-readable TSX v1 block."""
    if not include_seed and not include_hands:
        return espionnage_text
    if include_seed and not isinstance(seed, int):
        raise ValueError("include_seed requires an integer seed")

    extension: Dict[str, Any] = {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "capabilities": {
            "deterministic_replay": bool(include_seed),
            "private_hands": bool(include_hands),
            "private_state_derivable_from_seed": bool(include_seed),
            "engine_resume": False,
        },
        "position": position_snapshot(game, include_hands=include_hands),
    }
    if include_seed:
        extension["replay"] = {
            "seed": seed,
            "actions": [str(action) for action in player_actions],
        }

    encoded = json.dumps(extension, ensure_ascii=False, indent=2, sort_keys=True)
    commented = "\n".join(f"# {line}" for line in encoded.splitlines())
    return (f"{espionnage_text}\n{BEGIN_MARKER}\n{DATA_MARKER}\n"
            f"{commented}\n{END_MARKER}\n")


def split_save_text(text: str) -> Tuple[str, Optional[dict]]:
    """Split an optional TSX block and validate its versioned envelope."""
    separator = "\n" + BEGIN_MARKER + "\n"
    if separator not in text:
        return text, None
    base, block = text.rsplit(separator, 1)
    lines = block.splitlines()
    if len(lines) < 2 or lines[-1] != END_MARKER:
        raise ValueError("malformed TSX save block")
    if lines[0].startswith(DATA_PREFIX):
        if len(lines) != 2:
            raise ValueError("malformed TSX save block")
        payload = lines[0][len(DATA_PREFIX):]
    elif lines[0] == DATA_MARKER:
        json_lines = lines[1:-1]
        if not json_lines or any(not line.startswith("# ") for line in json_lines):
            raise ValueError("malformed TSX save block")
        payload = "\n".join(line[2:] for line in json_lines)
    else:
        raise ValueError("malformed TSX save block")
    try:
        extension = json.loads(payload)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid TSX save JSON") from exc
    if not isinstance(extension, dict) \
            or extension.get("format") != FORMAT_NAME \
            or extension.get("version") != FORMAT_VERSION:
        raise ValueError("unsupported TSX save format or version")
    return base, extension