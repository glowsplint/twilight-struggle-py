"""
AI Decision Explainer: Generates human-readable explanations of AI moves.

Provides template-based strategic reasoning from action type and game context.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from enums import CardAction, InputType, Side
from cards import Card
from world_map import CountryInfo

if TYPE_CHECKING:
    from game_mechanics import Game
    from interfacing import Input


def explain_move(explanation: dict[str, object], input_state: Input, game: Game) -> dict[str, object]:
    """
    Generate a human-readable explanation of an AI decision.

    Parameters
    ----------
    explanation : dict
        Raw explanation from PIMCSearch (chosen_action, confidence, alternatives).
    input_state : Input
        The input state when the decision was made.
    game : Game
        The game state when the decision was made.

    Returns
    -------
    dict
        Enhanced explanation with human-readable reasoning.
    """
    if not explanation:
        return {"text": "No explanation available.", "details": {}}

    chosen = explanation.get("chosen_action", "")
    confidence = explanation.get("confidence", 0.0)
    alternatives = explanation.get("alternatives", [])
    input_type = input_state.state

    reasoning = _generate_reasoning(chosen, input_type, game, input_state.side)

    # Format alternatives for display
    formatted_alts = []
    for alt in alternatives[:5]:
        action = alt.get("action", "?")
        conf = alt.get("confidence", 0.0)
        value = alt.get("avg_value", 0.0)
        formatted_alts.append({
            "action": _format_action_name(action, input_type),
            "confidence": f"{conf:.0%}",
            "win_rate": f"{(value + 1) / 2:.0%}",
            "raw_confidence": conf,
            "raw_value": value,
        })

    return {
        "chosen_action": _format_action_name(chosen, input_type),
        "confidence": f"{confidence:.0%}",
        "reasoning": reasoning,
        "alternatives": formatted_alts,
        "total_simulations": explanation.get("total_simulations", 0),
        "num_worlds": explanation.get("num_worlds", 0),
    }


def _format_action_name(action: str, input_type: InputType) -> str:
    """Format an action name for human display."""
    if input_type == InputType.SELECT_CARD:
        return action.replace("_", " ")
    elif input_type == InputType.SELECT_CARD_ACTION:
        action_names = {
            "PLAY_EVENT": "Play Event",
            "RESOLVE_EVENT_FIRST": "Resolve Event First",
            "INFLUENCE": "Place Influence",
            "REALIGNMENT": "Realignment Roll",
            "COUP": "Coup",
            "SPACE": "Space Race",
            "SKIP_OPTIONAL_AR": "Skip",
        }
        return action_names.get(action, action)
    elif input_type == InputType.SELECT_COUNTRY:
        return action.replace("_", " ")
    return action


def _generate_reasoning(action: str, input_type: InputType,
                        game: Game, side: Side) -> str:
    """Generate template-based strategic reasoning."""
    if input_type == InputType.SELECT_CARD:
        return _reason_card_selection(action, game, side)
    elif input_type == InputType.SELECT_CARD_ACTION:
        return _reason_action_selection(action, game, side)
    elif input_type == InputType.SELECT_COUNTRY:
        return _reason_country_selection(action, game, side)
    return "Evaluating position..."


def _reason_card_selection(card_name: str, game: Game, side: Side) -> str:
    """Reasoning for card selection."""
    if card_name not in Card.ALL:
        return f"Playing {card_name}."

    card = Card.ALL[card_name]

    if card.card_type == "Scoring":
        region = card.scoring_region
        return f"Playing {card_name.replace('_', ' ')} - scoring must be resolved this turn."

    if card.owner == side:
        return f"Playing own event ({card.ops} ops) for maximum value."
    elif card.owner == side.opp:
        return f"Must play opponent's card ({card.ops} ops) - minimizing its impact."
    else:
        return f"Playing neutral card ({card.ops} ops)."


def _reason_action_selection(action: str, game: Game, side: Side) -> str:
    """Reasoning for action type selection."""
    reasons = {
        "PLAY_EVENT": "Event effect is valuable in current position.",
        "RESOLVE_EVENT_FIRST": "Resolving opponent's event first to mitigate damage before using ops.",
        "INFLUENCE": "Strengthening position through influence placement.",
        "REALIGNMENT": "Attempting to destabilize opponent's position.",
        "COUP": "Aggressive action to shift control and gain military ops.",
        "SPACE": "Using space race to safely dispose of this card.",
        "SKIP_OPTIONAL_AR": "Choosing to pass this optional action round.",
    }

    base = reasons.get(action, "Evaluating best use of this card.")

    # Add context
    if action == "COUP" and game.defcon_track <= 3:
        base += " DEFCON is low - limited targets available."
    elif action == "INFLUENCE" and game.ar_track <= 2:
        base += " Early in the turn - building position."
    elif action == "SPACE" and game.space_track[side] < game.space_track[side.opp]:
        base += " Behind in space race."

    return base


def _reason_country_selection(country_name: str, game: Game, side: Side) -> str:
    """Reasoning for country selection."""
    if country_name not in CountryInfo.ALL:
        return f"Targeting {country_name}."

    info = CountryInfo.ALL[country_name]
    country = game.map[country_name]

    parts = []

    if info.battleground:
        parts.append("battleground country")

    control = country.control
    if control == side:
        parts.append("reinforcing own control")
    elif control == side.opp:
        parts.append("contesting opponent control")
    else:
        parts.append("competing for uncontrolled territory")

    region_str = ", ".join(r.name.replace("_", " ").title() for r in info.regions)
    if region_str:
        parts.append(f"in {region_str}")

    return f"Targeting {country_name.replace('_', ' ')} - {', '.join(parts)}."
