import os

from flask import Flask
from flask import render_template
from flask import request

import matplotlib

from turbo_catan.generate import CatanBoard
from turbo_catan.hexes import plot_hexes

matplotlib.use("Agg")
app = Flask(__name__)

FIG_DIR = os.path.join("static", "images")


@app.route("/")
def generate_board():
    players = request.args.get("players", "")
    full_filename = os.path.join(FIG_DIR, "new_plot.png")
    create_fig(float(players), full_filename)
    return render_template("index.html", user_image=full_filename, n=players)


def create_fig(n_players, save_dir):
    os.makedirs(FIG_DIR, exist_ok=True)
    board = CatanBoard(n_players=n_players, enable_bonus_rolls=True)
    board.gen_map()
    fig, ax = plot_hexes(board.tiles)
    fig.savefig(save_dir)
