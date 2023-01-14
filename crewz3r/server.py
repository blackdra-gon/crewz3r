import json
from dataclasses import dataclass
from enum import Enum, auto

from crew_types import Card, CardDistribution
from crew_utils import (
    DEFAULT_PARAMETERS,
    CrewGameParameters,
    get_deck,
    no_card_duplicates,
)
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit


class UserStatus(Enum):
    CONNECTED = auto()
    CARD_SELECTION = auto()
    CARD_SELECTION_FINISHED = auto()
    TASK_SELECTION = auto()
    TASK_SELECTION_FINISHED = auto()
    AWAITING_RESULT = auto()


@dataclass
class User:
    sid: str
    name: str
    status: UserStatus
    player_index: int | None = None


# define websocket server
app: Flask = Flask(__name__)
socketio: SocketIO = SocketIO(app, cors_allowed_origins="*")

COLOUR_NAMES = {-1: "Trumpf", 0: "Rot", 1: "Grün", 2: "Blau", 3: "Gelb"}

all_possible_cards: list[Card]
card_distribution: CardDistribution

users: dict[str, User] = {}


# ***********************************************************
#        helper functions
# ***********************************************************


def get_sid() -> str:
    return request.sid  # type: ignore


def get_user_list() -> dict[str, str]:
    return {user.sid: user.name for user in users.values()}


def send_user_list() -> None:
    emit("user list", json.dumps(get_user_list()), broadcast=True)


# ***********************************************************
#        start page
# ***********************************************************


@socketio.on("connect")
def connect() -> None:

    global users

    sid: str = get_sid()
    users[sid] = User(sid, "", UserStatus.CONNECTED)

    print(f"New connection: {sid}, user count: {len(users)}.")
    print("Users:", users, sep="\n")

    send_user_list()


@socketio.on("update name")
def update_name(name: str) -> None:

    sid: str = get_sid()

    print(f"User {sid!r} updated name from {users[sid].name!r} to {name!r}.")

    users[sid].name = name
    send_user_list()


@socketio.on("start card selection")
def start_card_selection() -> None:

    global all_possible_cards, card_distribution, users

    player_count = len(users)
    parameters: CrewGameParameters = DEFAULT_PARAMETERS
    try:
        parameters.number_of_players = player_count
    except ValueError as e:
        print(f"Invalid player count:\n{e!r}")
        emit("not enough players")
        return

    all_possible_cards = get_deck(parameters)
    card_distribution = [[] for _ in range(player_count)]

    for i, user in enumerate(users.values()):
        if user.status == UserStatus.CONNECTED:
            user.status = UserStatus.CARD_SELECTION
            user.player_index = i

    print("Starting card selection.")
    print("Parameters:", parameters, sep="\n")
    print("Users:", users, sep="\n")

    emit("card selection started", json.dumps(get_user_list()), broadcast=True)
    emit("cards updated", json.dumps(list(all_possible_cards)), broadcast=True)


# ***********************************************************
#        card selection
# ***********************************************************

# when one player adds a card to its deck remove it from possible cards
@socketio.on("card_or_task taken")
def card_or_task_taken(card_str: str) -> None:
    sid: str = get_sid()
    user = users[sid]
    card: Card = tuple(json.loads(card_str))

    if user.status == UserStatus.CARD_SELECTION:
        card_taken(card, user)
    elif user.status == UserStatus.TASK_SELECTION:
        task_taken(card, user)
    else:
        print(
            f"Warning: {user.name} ({user.sid}) "
            + f"tried to take a card in status {user.status}"
        )


def card_taken(card: Card, user: User) -> None:

    global all_possible_cards, card_distribution

    if card not in all_possible_cards:
        print(f"Unavailable card {card} was taken by {user.name} ({user.sid}).")
        return

    player = user.player_index

    all_possible_cards.remove(card)
    emit("cards updated", json.dumps(list(all_possible_cards)), broadcast=True)

    card_distribution[player].append(card)

    print(f"Card {card} was taken by {user.name} ({user.sid}).")
    print("Card distribution:", card_distribution, sep="\n")

    selected_cards = ", ".join(
        f"({COLOUR_NAMES[c]}, {v})" for c, v in card_distribution[player]
    )
    emit("selected cards updated", selected_cards)


@socketio.on("finish card selection")
def finish_card_selection() -> None:

    global all_possible_cards, card_distribution

    sid: str = get_sid()

    if users[sid].status == UserStatus.CARD_SELECTION:
        users[sid].status = UserStatus.CARD_SELECTION_FINISHED
        print(f"User {users[sid].name!r} ({sid!r}) finished card selection.")

    if all(u.status == UserStatus.CARD_SELECTION_FINISHED for u in users.values()):
        print("Card selection finished for all users.")
        if no_card_duplicates(card_distribution):
            for user in users.values():
                if user.status == UserStatus.CARD_SELECTION_FINISHED:
                    user.status = UserStatus.TASK_SELECTION

            print("Starting task selection.")
            print("Users:", users, sep="\n")

            emit("task selection started", broadcast=True)
            emit("cards updated", json.dumps(list(all_possible_cards)), broadcast=True)
        else:
            print("ERROR: duplicate cards.")
            emit("end game")


@socketio.on("task taken")
def task_taken() -> None:
    pass  # TODO: implement


@socketio.on("finish task selection")
def finish_task_selection() -> None:

    sid: str = get_sid()

    if users[sid].status == UserStatus.TASK_SELECTION:
        users[sid].status = UserStatus.TASK_SELECTION_FINISHED
        print(f"User {users[sid].name!r} ({sid!r}) finished task selection.")

    if all(u.status == UserStatus.TASK_SELECTION_FINISHED for u in users.values()):
        print("Task selection finished for all users.")
        if True:  # TODO: check for duplicates
            for user in users.values():
                if user.status == UserStatus.TASK_SELECTION_FINISHED:
                    user.status = UserStatus.AWAITING_RESULT

            # TODO: start solver

            print("Starting solver.")

            emit("solver started")
        else:
            print("ERROR: duplicate tasks.")
            emit("end game")


@socketio.on("end game")
def end_game() -> None:

    for u in users.values():
        u.status = UserStatus.CONNECTED
        u.player_index = None

    print("Ending the game.")

    emit("game ended", broadcast=True)


@socketio.on("disconnect")
def disconnect() -> None:

    global users

    sid: str = get_sid()
    users.pop(sid)
    send_user_list()

    print(f"User {users[sid].name!r} ({sid!r}) disconnected, user count: {len(users)}.")


@app.route("/")
def index() -> str:
    return render_template("index.html")


def main() -> None:
    socketio.run(app, host="0.0.0.0", allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
