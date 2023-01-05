import json

from crew_types import Card, CardDistribution
from crew_utils import DEFAULT_PARAMETERS, get_deck, no_card_duplicates
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
player_ids: dict[str, int] = {}
players_finished: dict[str, bool] = {}
colour_names = {-1: "Trumpf", 0: "Rot", 1: "Grün", 2: "Blau", 3: "Gelb"}

card_distribution: CardDistribution


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
    global players, player_ids, card_distribution, players_finished
    players = users.copy()
    player_ids = {sid: i for (i, sid) in enumerate(players.keys())}
    players_finished = {sid: False for sid in players.keys()}
    print(player_ids)
    card_distribution = [[]] * len(players)
    emit("game started", json.dumps(players), broadcast=True)
    emit("cards updated", json.dumps(list(all_possible_cards)), broadcast=True)


@socketio.on("end game")
def end_game() -> None:
    players.clear()
    emit("game ended", broadcast=True)


@socketio.on("finish card selection")
def finish_card_selection() -> None:
    players_finished[request.sid] = True  # type: ignore
    if all(players_finished.values()):
        if no_card_duplicates(card_distribution):
            emit("task selection")
        else:
            print("Duplicate Cards")
            emit("end game")


# when one player adds a card to its deck remove it from possible cards
@socketio.on("card taken")
def card_taken(card_str: str) -> None:
    global card_distribution
    card: Card = tuple(json.loads(card_str))
    player = player_ids[request.sid]  # type: ignore

    if card in all_possible_cards:
        all_possible_cards.remove(card)
        card_distribution[player].append(card)
        print("Card " + card_str + f" was taken from player {player}")
        emit("cards updated", json.dumps(list(all_possible_cards)), broadcast=True)
        selected_cards = ""
        for colour, value in card_distribution[player]:
            selected_cards += f"({colour_names[colour]}, {value}), "
        emit("selected card updated", selected_cards)


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
