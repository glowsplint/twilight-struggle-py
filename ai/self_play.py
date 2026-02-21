"""
Self-Play Pipeline for generating training data.

Components:
- SelfPlayWorker: Plays games using current network + PIMC-MCTS
- TrainingPipeline: Orchestrates self-play -> train -> evaluate loop
"""

import time
from pathlib import Path

from ai.ai_player import AIPlayer
from ai.network import TwilightNet
from ai.trainer import ReplayBuffer, Trainer
from enums import Side
from game_runner import GameResult, GameRunner
from player import RandomPlayer


class SelfPlayWorker:
    """
    Plays games using the current network to generate training data.

    Parameters
    ----------
    network : TwilightNet or None
        Neural network for evaluation.
    num_worlds : int
        PIMC worlds per move.
    num_simulations : int
        MCTS simulations per world.
    temperature : float
        Action selection temperature.
    """

    def __init__(self, network=None, num_worlds: int = 10,
                 num_simulations: int = 100, temperature: float = 1.0):
        self.network = network
        self.num_worlds = num_worlds
        self.num_simulations = num_simulations
        self.temperature = temperature

    def play_game(self) -> tuple:
        """
        Play a single self-play game.

        Returns
        -------
        tuple
            (game_result, training_data) where training_data is a list
            of (state, policy, outcome) from both sides.
        """
        ussr_player = AIPlayer(
            Side.USSR, network=self.network,
            num_worlds=self.num_worlds,
            num_simulations=self.num_simulations,
            temperature=self.temperature,
            collect_data=True,
        )
        us_player = AIPlayer(
            Side.US, network=self.network,
            num_worlds=self.num_worlds,
            num_simulations=self.num_simulations,
            temperature=self.temperature,
            collect_data=True,
        )

        runner = GameRunner(ussr_player, us_player, silent=True)

        try:
            result = runner.run_game()
        except Exception as e:
            print(f"Game failed with error: {e}")
            return None, []

        # Fill in outcomes
        ussr_player.set_game_outcome(result.winner)
        us_player.set_game_outcome(result.winner)

        # Combine training data from both sides
        training_data = ussr_player.get_training_data() + us_player.get_training_data()

        return result, training_data

    def play_games(self, num_games: int) -> tuple:
        """
        Play multiple self-play games.

        Returns
        -------
        tuple
            (results_list, all_training_data)
        """
        results = []
        all_data = []

        for i in range(num_games):
            result, data = self.play_game()
            if result is not None:
                results.append(result)
                all_data.extend(data)
                if (i + 1) % 10 == 0:
                    print(f"  Completed {i + 1}/{num_games} games")

        return results, all_data


def evaluate_network(network, opponent_type: str = "random",
                     num_games: int = 100, num_worlds: int = 10,
                     num_simulations: int = 100) -> dict:
    """
    Evaluate a network against a baseline opponent.

    Parameters
    ----------
    network : TwilightNet or None
        Network to evaluate.
    opponent_type : str
        "random" or "network" (for old vs new).
    num_games : int
        Number of evaluation games.
    num_worlds : int
        PIMC worlds for AI player.
    num_simulations : int
        MCTS simulations per world.

    Returns
    -------
    dict
        Evaluation metrics.
    """
    wins = {Side.USSR: 0, Side.US: 0, Side.NEUTRAL: 0}
    ussr_wins_as_ai = 0
    us_wins_as_ai = 0
    total_played = 0

    for i in range(num_games):
        # Alternate sides
        if i % 2 == 0:
            ai_side = Side.USSR
            ai_player = AIPlayer(
                Side.USSR, network=network,
                num_worlds=num_worlds,
                num_simulations=num_simulations,
                temperature=0.1,  # Near-greedy for evaluation
            )
            if opponent_type == "random":
                opp_player = RandomPlayer(Side.US)
            else:
                opp_player = AIPlayer(Side.US, network=None, num_worlds=5, num_simulations=50)
            runner = GameRunner(ai_player, opp_player, silent=True)
        else:
            ai_side = Side.US
            ai_player = AIPlayer(
                Side.US, network=network,
                num_worlds=num_worlds,
                num_simulations=num_simulations,
                temperature=0.1,
            )
            if opponent_type == "random":
                opp_player = RandomPlayer(Side.USSR)
            else:
                opp_player = AIPlayer(Side.USSR, network=None, num_worlds=5, num_simulations=50)
            runner = GameRunner(opp_player, ai_player, silent=True)

        try:
            result = runner.run_game()
            wins[result.winner] += 1
            if result.winner == ai_side:
                if ai_side == Side.USSR:
                    ussr_wins_as_ai += 1
                else:
                    us_wins_as_ai += 1
            total_played += 1
        except Exception as e:
            print(f"Evaluation game {i} failed: {e}")

        if (i + 1) % 10 == 0:
            print(f"  Evaluated {i + 1}/{num_games} games")

    ai_wins = ussr_wins_as_ai + us_wins_as_ai
    win_rate = ai_wins / max(1, total_played)

    return {
        "total_games": total_played,
        "ai_wins": ai_wins,
        "win_rate": win_rate,
        "ussr_wins_as_ai": ussr_wins_as_ai,
        "us_wins_as_ai": us_wins_as_ai,
        "draws": wins[Side.NEUTRAL],
    }


class TrainingPipeline:
    """
    Full self-play training pipeline.

    Orchestrates:
    1. Self-play game generation
    2. Network training on replay buffer
    3. Evaluation against baseline
    4. Checkpoint management

    Parameters
    ----------
    hidden_size : int
        Network hidden layer size.
    num_residual_blocks : int
        Number of residual blocks.
    device : str
        Training device.
    checkpoint_dir : str
        Directory for saving checkpoints.
    """

    def __init__(self, hidden_size: int = 512, num_residual_blocks: int = 8,
                 device: str = "cpu", checkpoint_dir: str = "checkpoints"):
        self.device = device
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.network = TwilightNet(
            hidden_size=hidden_size,
            num_residual_blocks=num_residual_blocks,
        ).to(device)

        self.trainer = Trainer(self.network, device=device)
        self.replay_buffer = ReplayBuffer()
        self.best_win_rate = 0.0
        self.iteration = 0

    def run(self, num_iterations: int = 100, games_per_iter: int = 100,
            train_steps: int = 1000, eval_games: int = 50,
            num_worlds: int = 10, num_simulations: int = 100,
            win_rate_threshold: float = 0.55):
        """
        Run the full training pipeline.

        Parameters
        ----------
        num_iterations : int
            Number of training iterations.
        games_per_iter : int
            Self-play games per iteration.
        train_steps : int
            Training steps per iteration.
        eval_games : int
            Evaluation games per iteration.
        num_worlds : int
            PIMC worlds for self-play.
        num_simulations : int
            MCTS simulations for self-play.
        win_rate_threshold : float
            Minimum win rate to accept new network.
        """
        print(f"Starting training pipeline on {self.device}")
        print(f"  Iterations: {num_iterations}")
        print(f"  Games/iter: {games_per_iter}")
        print(f"  Train steps/iter: {train_steps}")
        print(f"  Network params: {sum(p.numel() for p in self.network.parameters()):,}")
        print()

        for iteration in range(num_iterations):
            self.iteration = iteration + 1
            iter_start = time.time()
            print(f"=== Iteration {self.iteration}/{num_iterations} ===")

            # Phase 1: Self-play
            print(f"Phase 1: Self-play ({games_per_iter} games)...")
            worker = SelfPlayWorker(
                network=self.network if iteration > 0 else None,
                num_worlds=num_worlds,
                num_simulations=num_simulations,
                temperature=1.0,
            )
            results, training_data = worker.play_games(games_per_iter)

            # Add to replay buffer
            self.replay_buffer.add_batch(training_data)

            # Print self-play stats
            if results:
                ussr_wins = sum(1 for r in results if r.winner == Side.USSR)
                us_wins = sum(1 for r in results if r.winner == Side.US)
                draws = sum(1 for r in results if r.winner == Side.NEUTRAL)
                avg_turns = sum(r.turn for r in results) / len(results)
                print(f"  Results: USSR {ussr_wins} / US {us_wins} / Draw {draws}")
                print(f"  Avg turns: {avg_turns:.1f}, Buffer size: {len(self.replay_buffer)}")
                print(f"  Training samples generated: {len(training_data)}")

            # Phase 2: Train
            if len(self.replay_buffer) >= 256:
                print(f"Phase 2: Training ({train_steps} steps)...")
                metrics = self.trainer.train_on_buffer(
                    self.replay_buffer, batch_size=256, num_steps=train_steps
                )
                print(f"  Policy loss: {metrics['policy_loss']:.4f}")
                print(f"  Value loss: {metrics['value_loss']:.4f}")
                print(f"  Total loss: {metrics['total_loss']:.4f}")

            # Phase 3: Evaluate
            print(f"Phase 3: Evaluation ({eval_games} games vs random)...")
            eval_metrics = evaluate_network(
                self.network, opponent_type="random",
                num_games=eval_games, num_worlds=num_worlds,
                num_simulations=num_simulations // 2,
            )
            win_rate = eval_metrics["win_rate"]
            print(f"  Win rate vs random: {win_rate:.1%}")
            print(f"  AI wins: {eval_metrics['ai_wins']}/{eval_metrics['total_games']}")

            # Save checkpoint
            if win_rate >= self.best_win_rate:
                self.best_win_rate = win_rate
                checkpoint_path = self.checkpoint_dir / f"best_model.pt"
                self.network.save_checkpoint(str(checkpoint_path))
                print(f"  New best model saved (win rate: {win_rate:.1%})")

            # Always save latest
            checkpoint_path = self.checkpoint_dir / f"model_iter_{self.iteration}.pt"
            self.network.save_checkpoint(str(checkpoint_path))

            # Save replay buffer periodically
            if self.iteration % 10 == 0:
                buf_path = self.checkpoint_dir / "replay_buffer.npz"
                self.replay_buffer.save(str(buf_path))

            elapsed = time.time() - iter_start
            print(f"  Iteration time: {elapsed:.1f}s")
            print()

        print("Training complete!")
        print(f"Best win rate: {self.best_win_rate:.1%}")
