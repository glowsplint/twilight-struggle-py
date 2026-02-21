"""
Training CLI entry point for Twilight Struggle AI.

Usage:
    python train.py --iterations 100 --games-per-iter 100 --simulations 200
    python train.py --device cuda --hidden-size 512 --residual-blocks 8
"""

import argparse

import torch


def main():
    parser = argparse.ArgumentParser(description="Train Twilight Struggle AI")
    parser.add_argument("--iterations", type=int, default=100,
                        help="Number of training iterations")
    parser.add_argument("--games-per-iter", type=int, default=100,
                        help="Self-play games per iteration")
    parser.add_argument("--train-steps", type=int, default=1000,
                        help="Training steps per iteration")
    parser.add_argument("--eval-games", type=int, default=50,
                        help="Evaluation games per iteration")
    parser.add_argument("--simulations", type=int, default=200,
                        help="MCTS simulations per world")
    parser.add_argument("--worlds", type=int, default=10,
                        help="PIMC worlds per move")
    parser.add_argument("--hidden-size", type=int, default=512,
                        help="Network hidden layer size")
    parser.add_argument("--residual-blocks", type=int, default=8,
                        help="Number of residual blocks")
    parser.add_argument("--device", type=str, default="auto",
                        help="Device: cpu, cuda, or auto")
    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints",
                        help="Directory for checkpoints")
    parser.add_argument("--win-threshold", type=float, default=0.55,
                        help="Win rate threshold for accepting new model")
    args = parser.parse_args()

    # Auto-detect device
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device

    print(f"Device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    from ai.self_play import TrainingPipeline

    pipeline = TrainingPipeline(
        hidden_size=args.hidden_size,
        num_residual_blocks=args.residual_blocks,
        device=device,
        checkpoint_dir=args.checkpoint_dir,
    )

    pipeline.run(
        num_iterations=args.iterations,
        games_per_iter=args.games_per_iter,
        train_steps=args.train_steps,
        eval_games=args.eval_games,
        num_worlds=args.worlds,
        num_simulations=args.simulations,
        win_rate_threshold=args.win_threshold,
    )


if __name__ == "__main__":
    main()
