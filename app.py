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

    Variables
    ---------
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

        self.output_state.notification += 'Initalising game.'
        self.client_response = threading.Event()

        while True:

            self.prepare_json()
            self.output_state.show()  # different -- this line is not printing anything!!

            self.client_response.wait()
            self.client_response.clear()
            user_choice = self.user_choice.split(' ', 1)  # different
            end_loop = self.parse_input(user_choice)
            if end_loop:
                break

    def prepare_json(self):
        self.server_move = self.output_state.json.copy()
        if hasattr(app, 'server_response'):
            app.server_response.set()


# Starts game engine, back-end and socket connection
dist = Path("./front-end/dist/")
app = VueCompatibleFlask(__name__,
                         static_folder=str(dist/"static"),
                         template_folder=str(dist))
socketio = SocketIO(app, json=json,
                    cors_allowed_origins=['http://localhost:8080'])
gui = GUI(daemon=True)

# Provides -n command line argument
parser = argparse.ArgumentParser(
    description='Runs the Flask development server for twilight-struggle-py.')
parser.add_argument('-n', '--no_browser', action='store_true',
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
    print(f'server is sending: {gui.server_move}')


url = "http://localhost:5000"
if 'WERKZEUG_RUN_MAIN' not in os.environ and not args.no_browser:
    threading.Timer(
        1.25, lambda: webbrowser.open(url)).start()
gui.start()
app.run(debug=True)
