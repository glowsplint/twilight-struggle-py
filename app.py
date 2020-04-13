from pathlib import Path
from flask import Flask, render_template
from flask_socketio import SocketIO, emit


class VueFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='$$',
        block_end_string='$$',
        variable_start_string='$',
        variable_end_string='$',
        comment_start_string='$#',
        comment_end_string='#$',
    ))


dist = Path("front-end/vue/dist/")
app = VueFlask(__name__,
               static_folder=str(dist/"static"),
               template_folder=str(dist))
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template("index.html")


@socketio.on('connect')
def test_connect():
    emit('Initial connection', {'data': 'Connected'})


@socketio.on('my event')
def handle_json(json):
    print('Received JSON: ' + str(json))


app.run(debug=True)
