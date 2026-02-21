"""
Evaluation CLI entry point for Twilight Struggle AI.

Usage:
    python evaluate.py --checkpoint checkpoints/best_model.pt --opponent random --games 100
    python evaluate.py --checkpoint checkpoints/model_iter_50.pt --opponent random --games 200
"""

import argparse

import torch


def main():
    parser = argparse.ArgumentParser(description="Evaluate Twilight Struggle AI")
    parser.add_argument("--checkpoint", type=str, required=True,
                        help="Path to model checkpoint")
    parser.add_argument("--opponent", type=str, default="random",
                        choices=["random", "mcts"],
                        help="Opponent type: random or mcts (no network)")
    parser.add_argument("--games", type=int, default=100,
                        help="Number of evaluation games")
    parser.add_argument("--simulations", type=int, default=200,
                        help="MCTS simulations per world")
    parser.add_argument("--worlds", type=int, default=10,
                        help="PIMC worlds per move")
    parser.add_argument("--device", type=str, default="auto",
                        help="Device: cpu, cuda, or auto")
    args = parser.parse_args()

    # Auto-detect device
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device

    print(f"Device: {device}")
    print(f"Loading checkpoint: {args.checkpoint}")

    from ai.network import TwilightNet
    from ai.self_play import evaluate_network

    network = TwilightNet.load_checkpoint(args.checkpoint, device=device)
    print(f"Model loaded ({sum(p.numel() for p in network.parameters()):,} parameters)")

    print(f"\nEvaluating vs {args.opponent} ({args.games} games)...")
    metrics = evaluate_network(
        network,
        opponent_type=args.opponent,
        num_games=args.games,
        num_worlds=args.worlds,
        num_simulations=args.simulations,
    )

    print(f"\n=== Results ===")
    print(f"Total games:       {metrics['total_games']}")
    print(f"AI wins:           {metrics['ai_wins']}")
    print(f"Win rate:          {metrics['win_rate']:.1%}")
    print(f"  As USSR:         {metrics['ussr_wins_as_ai']}")
    print(f"  As US:           {metrics['us_wins_as_ai']}")
    print(f"Draws:             {metrics['draws']}")


if __name__ == "__main__":
    main()
