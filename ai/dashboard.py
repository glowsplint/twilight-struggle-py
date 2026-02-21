"""
Training Dashboard: TensorBoard-based metrics logging.

Logs training loss curves, ELO progression, win rates, and game lengths.
"""

from pathlib import Path

try:
    from torch.utils.tensorboard import SummaryWriter
    HAS_TENSORBOARD = True
except ImportError:
    HAS_TENSORBOARD = False


class TrainingDashboard:
    """
    TensorBoard-based training metrics dashboard.

    Usage:
        dashboard = TrainingDashboard("runs/experiment_1")
        dashboard.log_training(iteration=1, policy_loss=0.5, value_loss=0.3)
        dashboard.log_evaluation(iteration=1, win_rate=0.65, elo=1200)
        dashboard.close()

    View with: tensorboard --logdir runs/
    """

    def __init__(self, log_dir: str = "runs/twilight_ai"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        if HAS_TENSORBOARD:
            self.writer = SummaryWriter(str(self.log_dir))
        else:
            self.writer = None
            print("TensorBoard not available. Metrics will be printed to console only.")

    def log_training(self, iteration: int, policy_loss: float,
                     value_loss: float, total_loss: float,
                     buffer_size: int = 0):
        """Log training metrics."""
        if self.writer:
            self.writer.add_scalar("Loss/policy", policy_loss, iteration)
            self.writer.add_scalar("Loss/value", value_loss, iteration)
            self.writer.add_scalar("Loss/total", total_loss, iteration)
            self.writer.add_scalar("Buffer/size", buffer_size, iteration)

    def log_evaluation(self, iteration: int, win_rate: float,
                       ai_wins: int = 0, total_games: int = 0,
                       elo: float = 0):
        """Log evaluation metrics."""
        if self.writer:
            self.writer.add_scalar("Eval/win_rate", win_rate, iteration)
            self.writer.add_scalar("Eval/ai_wins", ai_wins, iteration)
            self.writer.add_scalar("Eval/total_games", total_games, iteration)
            if elo:
                self.writer.add_scalar("Eval/elo", elo, iteration)

    def log_self_play(self, iteration: int, ussr_wins: int,
                      us_wins: int, draws: int, avg_turns: float,
                      samples_generated: int):
        """Log self-play statistics."""
        total = ussr_wins + us_wins + draws
        if self.writer and total > 0:
            self.writer.add_scalar("SelfPlay/ussr_win_rate", ussr_wins / total, iteration)
            self.writer.add_scalar("SelfPlay/us_win_rate", us_wins / total, iteration)
            self.writer.add_scalar("SelfPlay/draw_rate", draws / total, iteration)
            self.writer.add_scalar("SelfPlay/avg_turns", avg_turns, iteration)
            self.writer.add_scalar("SelfPlay/samples", samples_generated, iteration)

    def close(self):
        """Close the TensorBoard writer."""
        if self.writer:
            self.writer.close()
