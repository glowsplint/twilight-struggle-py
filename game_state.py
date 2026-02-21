from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enums import RealignState, Side


@dataclass
class GameState:
    """Pure data container for all game state."""

    # Scalar tracks
    vp_track: int = 0
    turn_track: int = 0
    ar_track: int = 0
    ar_side: Side | None = None
    defcon_track: int = 0
    handicap: int = -2
    started: bool = False

    # Per-side lists [USSR, US]
    milops_track: list[int] = field(default_factory=lambda: [0, 0])
    space_track: list[int] = field(default_factory=lambda: [0, 0])
    spaced_turns: list[int] = field(default_factory=lambda: [0, 0])
    ars_by_turn: list[list[int | None]] = field(default_factory=lambda: [[], []])
    ar_side_done: list[bool] = field(default_factory=lambda: [False, False])

    # Card piles (3 = [USSR, US, NEUTRAL])
    hand: list[list[str]] = field(default_factory=lambda: [[], [], []])
    removed_pile: list[str] = field(default_factory=list)
    discard_pile: list[str] = field(default_factory=list)
    draw_pile: list[str] = field(default_factory=list)
    limbo: list[str] = field(default_factory=list)
    basket: list[list[str]] = field(default_factory=lambda: [[], [], []])
    headline_bin: list[str] = field(default_factory=lambda: ["", ""])

    # End-turn hooks
    end_turn_stage_list: list[Callable[[], None]] = field(default_factory=list)

    # Transient state
    realign_state: RealignState | None = None
    opsinf_state: dict[str, int] | None = None
