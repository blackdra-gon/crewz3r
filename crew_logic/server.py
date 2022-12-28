import json

from crew_types import Card
from crew_utils import DEFAULT_PARAMETERS, get_deck
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app: Flask = Flask(__name__)

# start websocket server
socketio: SocketIO = SocketIO(app, cors_allowed_origins="*")

all_possible_cards: list[Card] = get_deck(DEFAULT_PARAMETERS)

# all users that have the site open
users: dict[str, str] = {}
# users that started a game (empty when no game started)
players: dict[str, str] = {}


@socketio.on("connect")
def connect() -> None:
    users.update({request.sid: ""})  # type: ignore
    emit("user list", json.dumps(users), broadcast=True)
    print(f"new connection: {request.sid}, user count: {len(users)}")  # type: ignore
    if len(players) > 0:
        emit("game started", json.dumps(players), broadcast=True)
        emit(
            "cards updated",
            json.dumps(list(all_possible_cards)),
            broadcast=True,
        )


@socketio.on("update name")
def update_name(name: str) -> None:
    users.update({request.sid: name})  # type: ignore
    emit("user list", json.dumps(users), broadcast=True)


@socketio.on("start game")
def start_game() -> None:
    global players
    players = users
    emit("game started", json.dumps(players), broadcast=True)
    emit("cards updated", json.dumps(list(all_possible_cards)), broadcast=True)


@socketio.on("end game")
def end_game() -> None:
    players.clear()
    emit("game ended", broadcast=True)


# when one player adds a card to its deck remove it from possible cards
@socketio.on("card taken")
def card_taken(card: Card) -> None:
    print(card)
    all_possible_cards.remove(card)
    emit("cards updated", json.dumps(list(all_possible_cards)), broadcast=True)


@socketio.on("disconnect")
def disconnect() -> None:
    users.pop(request.sid)  # type: ignore
    emit("user list", json.dumps(users), broadcast=True)
    print(f"disconnected: {request.sid}, user count: {len(users)}")  # type: ignore


@app.route("/")
def index() -> str:
    return render_template("index.html")


# If you are running it using python <filename> then below command will be used
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", allow_unsafe_werkzeug=True)
