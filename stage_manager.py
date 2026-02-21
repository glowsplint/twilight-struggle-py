from __future__ import annotations

from collections.abc import Callable


class StageManager:
    """Manages the game's stage execution pipeline."""

    def __init__(self) -> None:
        self.stage_list: list[Callable[[], None]] = []

    def complete(self, clear_input_fn: Callable[[], None]) -> None:
        """Pop and execute the top stage, clearing input state first."""
        clear_input_fn()
        self.stage_list.pop()()

    def clear(self) -> None:
        """Clear all stages."""
        self.stage_list.clear()
