import os
import threading
import webbrowser
import argparse

from pathlib import Path
from flask import Flask, render_template, json, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from interfacing import Output
from twilight_ui import UI


class VueCompatibleFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='$$',
        block_end_string='$$',
        variable_start_string='$',
        variable_end_string='$',
        comment_start_string='$#',
        comment_end_string='#$',
    ))


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

    def run(self):

        self.output_state.notification.append('Initalising game.')
        self.client_response = threading.Event()

        while True:

            self.prepare_json()
            self.output_state.show()

            self.client_response.wait()
            self.client_response.clear()
            user_choice = self.user_choice.split(' ', 1)
            end_loop = self.parse_input(user_choice)
            if end_loop:
                break

        print('Thread temporarily suspended.')

    def prepare_json(self):
        self.server_move = self.output_state.json.copy()
        if hasattr(app, 'server_response'):
            app.server_response.set()


# Constant definitions
DIST = Path("./front-end/dist/")
FLASK_URL = "http://localhost:5000"
VUE_URL = "http://localhost:8080"

# Starts game engine, back-end and socket connection
app = VueCompatibleFlask(__name__,
                         static_folder=str(DIST/"static"),
                         template_folder=str(DIST))
socketio = SocketIO(app, json=json,
                    cors_allowed_origins=(VUE_URL, FLASK_URL))
gui = GUI(daemon=True)

# Provides -n command line argument
parser = argparse.ArgumentParser(
    description='Runs the Flask development server for twilight-struggle-py.')
parser.add_argument('-n', '--nobrowser', action='store_true',
                    help='Silences the automatic opening of a browser window.')
args = parser.parse_args()


@app.route('/')
def index():
    return render_template("index.html")


@socketio.on('connect')
def connect():
    print('Client connected.')


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected.')


@socketio.on('client_move')
def client_move(json):
    # Receive a move and wait on GUI to provide an output
    print('Received JSON: ' + json['move'])
    gui.user_choice = str(json['move'])
    gui.client_response.set()
    app.server_response = threading.Event()
    app.server_response.wait()

    # When gui.server_move is ready
    emit('server_move', gui.server_move)
    # print(f'Sending to client: {gui.server_move}')


@socketio.on('client_restart')
def client_restart():
    print('Received request to restart.')
    if not gui.is_alive():
        gui.run()
        print('GUI restarted from previous run.')
    else:
        print('GUI is running - no restart was conducted.')


if 'WERKZEUG_RUN_MAIN' not in os.environ and not args.nobrowser:
    threading.Timer(
        1.25, lambda: webbrowser.open(FLASK_URL)).start()
gui.start()
socketio.run(app, debug=True)
