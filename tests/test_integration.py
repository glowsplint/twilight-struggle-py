"""
Integration tests: run random games to detect engine crashes.

These tests exercise the full game loop with RandomPlayer instances.
Use ``pytest -m slow`` to include the long-running stability suite.
"""
from __future__ import annotations

import signal
import sys
import traceback
from collections import Counter

import pytest

from enums import Side
from game_runner import GameRunner
from player import RandomPlayer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_single_game(seed: int, timeout: int = 30) -> str | None:
    """
    Run one random game with the given seed.

    Returns None on success, or an error description string on failure.
    """
    import random
    random.seed(seed)

    ussr = RandomPlayer(Side.USSR)
    us = RandomPlayer(Side.US)
    runner = GameRunner(ussr, us, handicap=0, silent=True, max_turns=10)

    # Use signal-based timeout on Unix; on Windows fall back to no timeout.
    use_alarm = hasattr(signal, "SIGALRM")
    if use_alarm:

        def _timeout_handler(signum, frame):
            raise TimeoutError(f"Game with seed {seed} exceeded {timeout}s")

        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout)

    try:
        runner.run_game()
        return None
    except TimeoutError:
        return f"timeout (>{timeout}s)"
    except Exception:
        return traceback.format_exc().splitlines()[-1]
    finally:
        if use_alarm:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)


# ---------------------------------------------------------------------------
# Smoke tests  (quick, always run)
# ---------------------------------------------------------------------------

SMOKE_SEEDS = [0, 1, 2, 42, 100, 256, 512, 1024, 2048, 9999]


class TestRandomGameSmoke:
    """Parametrised smoke test: each seed must not raise an unhandled exception."""

    @pytest.mark.parametrize("seed", SMOKE_SEEDS, ids=[f"seed={s}" for s in SMOKE_SEEDS])
    def test_random_game_completes(self, seed: int):
        error = _run_single_game(seed, timeout=30)
        assert error is None, f"Game with seed {seed} crashed: {error}"


# ---------------------------------------------------------------------------
# Stability suite  (slow marker — skipped unless explicitly requested)
# ---------------------------------------------------------------------------

class TestRandomGameStability:
    """Run many random games and assert a minimum success rate."""

    @pytest.mark.slow
    def test_stability_50_games(self):
        n_games = 50
        errors: list[str] = []
        successes = 0

        for seed in range(n_games):
            err = _run_single_game(seed, timeout=30)
            if err is None:
                successes += 1
            else:
                errors.append(f"seed={seed}: {err}")

        rate = successes / n_games
        error_summary = Counter(errors)

        # Report regardless of outcome
        print(f"\n--- Stability report: {successes}/{n_games} ({rate:.0%}) succeeded ---")
        if error_summary:
            print("Error breakdown:")
            for err, count in error_summary.most_common():
                print(f"  [{count}x] {err}")

        assert rate >= 0.50, (
            f"Only {successes}/{n_games} ({rate:.0%}) games completed. "
            f"Minimum threshold is 50%. Errors:\n" + "\n".join(errors[:20])
        )
