from pathlib import Path
from flask import Flask, render_template, request
# from twilight_ui import UI


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


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/game/', methods=['GET', 'POST'])
def game():
    clicked = None
    if request.method == "POST":
        clicked = request.json['data']
    return {'clicked': clicked}


app.run(debug=True)
