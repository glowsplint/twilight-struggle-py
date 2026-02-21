import argparse
import os
import random
import threading
import time
import webbrowser
from pathlib import Path

from flask import Flask, json, render_template
from flask_socketio import SocketIO, emit

from enums import Side
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
    self.user_choice :
        Contains the string of actions sent by the client.
        Updated when the socket listener receives the socket event 'client_move'.

    self.server_move :
        Contains the dictionary which serves as the JSON payload sent to the client.
    """

    def __init__(self, **kwargs):
        threading.Thread.__init__(self, **kwargs)
        UI.__init__(self)
        self.user_choice = []
        self.server_move = {}
        self.ai_mode = False
        self.ai_side = None
        self.ai_player = None
        self.ai_difficulty = "medium"

    def run(self):

        self.output_state.notification.append("Initalising game.")
        self.client_response = threading.Event()

        while True:

            self.prepare_json()
            self.output_state.show()

            # AI auto-play: if it's the AI's turn, generate a move
            if self.ai_mode and self.game_in_progress and self._is_ai_turn():
                self._handle_ai_turn()
                continue

            self.client_response.wait()
            self.client_response.clear()
            user_choice = self.user_choice.split(" ", 1)
            end_loop = self.parse_input(user_choice)
            if end_loop:
                break

        print("Thread temporarily suspended.")

    def prepare_json(self):
        self.server_move = self.output_state.json.copy()

        # Include AI explanation if available
        if self.ai_mode and self.ai_player and hasattr(self.ai_player, 'last_explanation'):
            self.server_move['ai_explanation'] = self.ai_player.last_explanation

        if hasattr(app, "server_response"):
            app.server_response.set()

    def _is_ai_turn(self):
        """Check if the current input is for the AI player."""
        if not self.game.input_state:
            return False
        side = self.game.input_state.side
        # AI handles its own side and NEUTRAL (dice rolls)
        return side == self.ai_side or side == Side.NEUTRAL

    def _handle_ai_turn(self):
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

    def setup_ai_game(self, human_side: str, difficulty: str = "medium"):
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
FLASK_URL = "http://localhost:5000"
VUE_URL = "http://localhost:8080"

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
def index():
    return render_template("index.html")


@socketio.on("connect")
def connect():
    print("Client connected.")


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected.")


@socketio.on("client_move")
def client_move(json):
    # Receive a move and wait on GUI to provide an output
    print("Received JSON: " + json["move"])
    gui.user_choice = str(json["move"])
    gui.client_response.set()
    app.server_response = threading.Event()
    app.server_response.wait()

    # When gui.server_move is ready
    emit("server_move", gui.server_move)
    # print(f'Sending to client: {gui.server_move}')


@socketio.on("client_new_ai_game")
def client_new_ai_game(config):
    """Start a new game against AI."""
    print(f"Starting AI game: {config}")
    human_side = config.get("side", "us")
    difficulty = config.get("difficulty", "medium")

    gui.setup_ai_game(human_side, difficulty)

    # Start the game
    gui.user_choice = "new"
    gui.client_response.set()
    app.server_response = threading.Event()
    app.server_response.wait()

    emit("server_move", gui.server_move)


@socketio.on("client_restart")
def client_restart():
    print("Received request to restart.")
    if not gui.is_alive():
        gui.run()
        print("GUI restarted from previous run.")
    else:
        print("GUI is running - no restart was conducted.")


if "WERKZEUG_RUN_MAIN" not in os.environ and not args.nobrowser:
    threading.Timer(1.25, lambda: webbrowser.open(FLASK_URL)).start()
gui.start()
socketio.run(app, debug=True)
