import threading

from pathlib import Path
from copy import deepcopy
from flask import Flask, render_template, json
from flask_socketio import SocketIO, emit
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

    def __init__(self, **kwargs):
        threading.Thread.__init__(self, **kwargs)
        UI.__init__(self)
        self.user_choice = []

    def run(self):

        print('Initalising game.')
        while True:

            self.response_handler = threading.Event()
            self.response_handler.wait()
            self.response_handler.clear()

            user_choice = self.user_choice.split(' ', 1)
            # below lines are identical to those in game loop in twilight_ui
            end_loop = self.parse_input(user_choice)
            if end_loop:
                break


dist = Path("front-end/vue/dist/")
app = VueCompatibleFlask(__name__,
                         static_folder=str(dist/"static"),
                         template_folder=str(dist))
socketio = SocketIO(app, json=json,
                    cors_allowed_origins=['http://localhost:8080'])
gui = GUI(daemon=True)


@app.route('/')
def index():
    return render_template("index.html")


@socketio.on('connect')
def connect():
    emit('Initial connection', {'data': 'Connected'})
    print('Client connected.')


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected.')


@socketio.on('client-new-game')
def new_game():
    print('New game requested.')


@socketio.on('client-move')
def move(json):
    # Receive a move and immediately send back a response
    # emit('server-move', server_to_client_data())
    print('Received JSON: ' + json['move'])
    gui.user_choice = json['move']
    gui.response_handler.set()


def server_to_client_data():
    # to add printouts here
    return {'data': 41}


gui.start()
app.run(debug=True)
