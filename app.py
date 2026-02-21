from __future__ import annotations

import argparse
import os
import queue
import random
import threading
import time
import webbrowser
from pathlib import Path

from flask import Flask, json, render_template
from flask_socketio import SocketIO, emit

from enums import Side
from player import Player
from twilight_ui import UI


class VueCompatibleFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(
        dict(
            block_start_string="$$",
            block_end_string="$$",
            variable_start_string="$",
            variable_end_string="$",
            comment_start_string="$#",
            comment_end_string="#$",
        )
    )


class GUI(threading.Thread, UI):
    """
    GUI runs in its own thread concurrently with Flask when called by the start() method.

    Methods
    -------
    run :
        Contains the game loop.
        Waits on a socket event to update the self.user_choice variable.
        Called by the start() method inherited by threading.Thread.

    Attributes
    ----------
    move_queue :
        Queue for client->game messages (moves from Flask handlers).
    response_queue :
        Queue for game->client responses (server state sent back to Flask handlers).
    server_move :
        Contains the dictionary which serves as the JSON payload sent to the client.
    """

    def __init__(self, **kwargs: object) -> None:
        threading.Thread.__init__(self, **kwargs)
        UI.__init__(self)
        self.move_queue: queue.Queue[str] = queue.Queue()
        self.response_queue: queue.Queue[dict[str, object]] = queue.Queue()
        self.server_move: dict[str, object] = {}
        self.ai_mode: bool = False
        self.ai_side: Side | None = None
        self.ai_player: Player | None = None
        self.ai_difficulty: str = "medium"

    def run(self) -> None:
        """Outer loop that supports restart: runs the game loop, then waits for restart signal."""
        while True:
            self._run_game_loop()
            print("Thread waiting for restart signal.")
            # Block until a restart signal comes through
            msg = self.move_queue.get()
            if msg == "__restart__":
                print("GUI restarted.")
                # Reset game state for a fresh session
                UI.__init__(self)
                continue
            else:
                # Unexpected message after quit; ignore and keep waiting
                continue

    def _run_game_loop(self) -> None:
        self.output_state.notification.append("Initalising game.")
        self._waiting_for_response = False

        while True:

            self.prepare_json()
            self.output_state.show()

            # AI auto-play: if it's the AI's turn, generate a move
            if self.ai_mode and self.game_in_progress and self._is_ai_turn():
                self._handle_ai_turn()
                continue

            user_choice_str = self.move_queue.get()
            self._waiting_for_response = True
            user_choice = user_choice_str.split(" ", 1)
            end_loop = self.parse_input(user_choice)
            if end_loop:
                break

        print("Game loop ended.")

    def prepare_json(self) -> None:
        self.server_move = self.output_state.json.copy()

        # Include AI explanation if available
        if self.ai_mode and self.ai_player and hasattr(self.ai_player, 'last_explanation'):
            self.server_move['ai_explanation'] = self.ai_player.last_explanation

        # Only send response when a Flask handler is waiting
        if self._waiting_for_response:
            self._waiting_for_response = False
            self.response_queue.put(self.server_move)

    def _is_ai_turn(self) -> bool:
        """Check if the current input is for the AI player."""
        if not self.game.input_state:
            return False
        side = self.game.input_state.side
        # AI handles its own side and NEUTRAL (dice rolls)
        return side == self.ai_side or side == Side.NEUTRAL

    def _handle_ai_turn(self) -> None:
        """Let the AI make its move."""
        input_state = self.game.input_state
        if not input_state:
            return

        # Notify client that AI is thinking
        if input_state.side == self.ai_side:
            socketio.emit("ai_thinking", {})

        # Brief delay for readability
        if input_state.side == self.ai_side:
            time.sleep(1.0)

        # Get AI move
        move = self.ai_player.get_move(input_state, self.game)
        if move:
            self.move(move)
            self.game_state_changed()

    def setup_ai_game(self, human_side: str, difficulty: str = "medium") -> None:
        """Configure an AI game."""
        self.ai_mode = True
        self.ai_difficulty = difficulty

        if human_side == "ussr":
            self.ai_side = Side.US
        else:
            self.ai_side = Side.USSR

        # Difficulty settings (MCTS simulations)
        sim_settings = {
            "easy": {"num_worlds": 5, "num_simulations": 50},
            "medium": {"num_worlds": 10, "num_simulations": 200},
            "hard": {"num_worlds": 20, "num_simulations": 800},
        }
        settings = sim_settings.get(difficulty, sim_settings["medium"])

        # Try to import AI player; fall back to random
        try:
            from ai.ai_player import AIPlayer
            # Try to load a trained network
            network = None
            checkpoint_path = Path("checkpoints/best_model.pt")
            if checkpoint_path.exists():
                try:
                    from ai.network import TwilightNet
                    network = TwilightNet.load_checkpoint(str(checkpoint_path))
                    print(f"Loaded AI model from {checkpoint_path}")
                except Exception as e:
                    print(f"Could not load model: {e}")

            self.ai_player = AIPlayer(
                self.ai_side,
                network=network,
                **settings,
            )
            print(f"AI Player initialized: side={self.ai_side.toStr}, difficulty={difficulty}")
        except ImportError:
            from player import RandomPlayer
            self.ai_player = RandomPlayer(self.ai_side)
            print(f"AI module not available, using RandomPlayer for {self.ai_side.toStr}")


# Constant definitions
DIST = Path("./frontend/dist/")
FLASK_URL = os.environ.get("FLASK_URL", "http://localhost:5000")
VUE_URL = os.environ.get("VUE_URL", "http://localhost:8080")

# Starts game engine, back-end and socket connection
app = VueCompatibleFlask(
    __name__, static_folder=str(DIST / "static"), template_folder=str(DIST)
)
socketio = SocketIO(app, json=json, cors_allowed_origins=(VUE_URL, FLASK_URL))
gui = GUI(daemon=True)

# Provides -n command line argument
parser = argparse.ArgumentParser(
    description="Runs the Flask development server for twilight-struggle-py."
)
parser.add_argument(
    "-n",
    "--nobrowser",
    action="store_true",
    help="Silences the automatic opening of a browser window.",
)
args = parser.parse_args()


@app.route("/")
def index() -> str:
    return render_template("index.html")


@socketio.on("connect")
def connect() -> None:
    print("Client connected.")


@socketio.on("disconnect")
def disconnect() -> None:
    print("Client disconnected.")


@socketio.on("client_move")
def client_move(data: object) -> None:
    if not isinstance(data, dict):
        return
    move = data.get("move")
    if not isinstance(move, str):
        return

    # Send move to GUI thread, wait for response
    print("Received JSON: " + move)
    gui.move_queue.put(move)
    try:
        response = gui.response_queue.get(timeout=30)
    except queue.Empty:
        emit("server_move", {"error": "Server timed out waiting for game state."})
        return

    emit("server_move", response)


@socketio.on("client_new_ai_game")
def client_new_ai_game(config: object) -> None:
    """Start a new game against AI."""
    if not isinstance(config, dict):
        return
    human_side = config.get("side", "us")
    difficulty = config.get("difficulty", "medium")
    if not isinstance(human_side, str) or not isinstance(difficulty, str):
        return

    print(f"Starting AI game: {config}")
    gui.setup_ai_game(human_side, difficulty)

    # Signal the GUI thread to start a new game
    gui.move_queue.put("new")
    try:
        response = gui.response_queue.get(timeout=30)
    except queue.Empty:
        emit("server_move", {"error": "Server timed out waiting for game state."})
        return

    emit("server_move", response)


@socketio.on("client_restart")
def client_restart() -> None:
    print("Received request to restart.")
    # Signal the GUI thread to restart via the move queue
    gui.move_queue.put("quit")
    gui.move_queue.put("__restart__")
    print("GUI restart signalled.")


if "WERKZEUG_RUN_MAIN" not in os.environ and not args.nobrowser:
    threading.Timer(1.25, lambda: webbrowser.open(FLASK_URL)).start()
gui.start()
debug = os.environ.get("FLASK_DEBUG", "0") == "1"
socketio.run(app, debug=debug)
