import json
import uuid
from dataclasses import dataclass
from enum import Enum, auto

from crew_game import CrewGame
from crew_tasks import Task
from crew_types import Card, CardDistribution
from crew_utils import (
    DEFAULT_PARAMETERS,
    CrewGameParameters,
    CrewGameState,
    get_deck,
    get_deck_without_trump,
    no_card_duplicates,
    no_task_duplicates,
)
from flask import Flask, make_response, render_template, request
from flask_socketio import SocketIO, emit

from crewz3r.crew_print import print_initial_game_state, print_solution


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
    # player_index is counted from 0
    player_index: int | None = None


# define websocket server
app: Flask = Flask(__name__)
socketio: SocketIO = SocketIO(app, cors_allowed_origins="*")

COLOUR_NAMES = {-1: "Trumpf", 0: "Rot", 1: "Grün", 2: "Blau", 3: "Gelb"}

game_parameters: CrewGameParameters
all_possible_cards: list[Card]
all_unselected_cards: list[Card]
all_possible_tasks: list[Card]
card_distribution: CardDistribution
chosen_tasks: list[Task] = []

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


def card_string(card: Card) -> str:
    return f"({COLOUR_NAMES[card[0]]}, {card[1]})"


# ***********************************************************
#        start page
# ***********************************************************


@socketio.on("connect")
def connect() -> None:

    global users

    uid: str = request.cookies.get("crewz3r_id")
    if uid not in users:
        users[uid] = User(uid, "", UserStatus.CONNECTED)
        print(f"New connection: {uid}, user count: {len(users)}.")
    else:
        print(f"User {users[uid].name} ({uid}) reconnected")
    print("Users:", users, sep="\n")
    match users[uid].status:
        case UserStatus.CARD_SELECTION:
            emit("open card selection view")
            emit("cards updated", json.dumps(list(all_possible_cards)))
            emit(
                "set card selection checkboxes",
                json.dumps(card_distribution[users[uid].player_index]),
            )
        case UserStatus.TASK_SELECTION:
            emit("open task selection view")
            emit("cards updated", json.dumps(list(all_possible_tasks)))
        case UserStatus.TASK_SELECTION_FINISHED:
            emit("open task selection view")
            emit("cards updated", json.dumps(list(all_possible_tasks)))
        case UserStatus.AWAITING_RESULT:
            emit("open result view")
        case _:
            pass

    send_user_list()


@socketio.on("update name")
def update_name(name: str) -> None:

    uid: str = request.cookies.get("crewz3r_id")

    print(f"User {uid!r} updated name from {users[uid].name!r} to {name!r}.")

    users[uid].name = name
    send_user_list()


@socketio.on("start card selection")
def start_card_selection() -> None:

    global all_possible_cards, card_distribution, users, all_possible_tasks
    global game_parameters, all_unselected_cards

    player_count = len(users)
    game_parameters = DEFAULT_PARAMETERS
    try:
        game_parameters.number_of_players = player_count
    except ValueError:  # as e:
        # print(f"Invalid player count:\n{e!r}")
        # emit("not enough players")
        # return
        # for development it should be possible to start a game with one player:
        pass

    all_possible_cards = get_deck(game_parameters)
    all_unselected_cards = all_possible_cards
    all_possible_tasks = get_deck_without_trump(game_parameters)
    card_distribution = [[] for _ in range(player_count)]

    for i, user in enumerate(users.values()):
        if user.status == UserStatus.CONNECTED:
            user.status = UserStatus.CARD_SELECTION
            user.player_index = i

    print("Starting card selection.")
    print("Parameters:", game_parameters, sep="\n")
    print("Users:", users, sep="\n")

    emit("open card selection view", json.dumps(get_user_list()), broadcast=True)
    emit("cards updated", json.dumps(list(all_possible_cards)), broadcast=True)


# ***********************************************************
#        card selection
# ***********************************************************

# when one player adds a card to its deck remove it from possible cards
@socketio.on("card_or_task taken")
def card_or_task_taken(card_str: str) -> None:
    uid: str = request.cookies.get("crewz3r_id")
    user = users[uid]
    card: Card = tuple(json.loads(card_str))

    if user.status == UserStatus.CARD_SELECTION:
        card_taken(card, user)
    elif user.status == UserStatus.TASK_SELECTION:
        task_taken(card, user)
    else:
        print(
            f"Warning: {user.name} ({user.uid}) "
            + f"tried to take a card in status {user.status}"
        )


def card_taken(card: Card, user: User) -> None:

    global all_possible_cards, card_distribution, all_unselected_cards

    if card not in all_unselected_cards:
        print(f"Unavailable card {card} was taken by {user.name} ({user.sid}).")
        return

    player = user.player_index

    all_unselected_cards.remove(card)
    # TODO check if we still need this
    # emit("cards updated", json.dumps(list(all_possible_cards)), broadcast=True)

    card_distribution[player].append(card)

    print(f"Card {card} was taken by {user.name} ({user.sid}).")
    print("Card distribution:", card_distribution, sep="\n")

    emit("selected cards updated", json.dumps(card_distribution[player]))


@socketio.on("finish card selection")
def finish_card_selection() -> None:

    global all_possible_cards, card_distribution

    uid: str = request.cookies.get("crewz3r_id")

    if users[uid].status == UserStatus.CARD_SELECTION:
        users[uid].status = UserStatus.TASK_SELECTION
        print(f"User {users[uid].name!r} ({uid!r}) finished card selection.")

        print(f"User {users[uid].name!r} ({uid!r}) starts task selection.")
        # print("Users:", users, sep="\n")

        emit("open task selection view")
        emit("cards updated", json.dumps(list(all_possible_tasks)))
        # TODO send selected cards
        # else:
        #    print("ERROR: duplicate cards.")
        #    emit("end game")


@socketio.on("task taken")
def task_taken(card: Card, user: User) -> None:
    global all_possible_tasks, chosen_tasks

    if card not in all_possible_tasks:
        print(f"Unavailable task {card} was taken by {user.name} ({user.sid}).")
        return

    player = user.player_index

    all_possible_tasks.remove(card)
    # TODO check if we still need this
    # emit("cards updated", json.dumps(list(all_possible_tasks)), broadcast=True)

    chosen_tasks.append(Task(card, player + 1))

    print(f"Task {card} was taken by {user.name} ({user.sid}).")
    print("Chosen tasks:", chosen_tasks, sep="\n")

    emit("selected tasks updated", json.dumps(chosen_tasks[player]))


@socketio.on("back to card selection")
def back_to_card_selection() -> None:
    uid: str = request.cookies.get("crewz3r_id")
    if users[uid].status == UserStatus.TASK_SELECTION:
        users[uid].status = UserStatus.CARD_SELECTION
    print(f"User {users[uid].name!r} ({uid!r}) goes back to card selection.")
    emit("open card selection view")
    emit("cards updated", json.dumps(list(all_possible_cards)))


@socketio.on("finish task selection")
def finish_task_selection() -> None:

    global card_distribution, game_parameters

    uid: str = request.cookies.get("crewz3r_id")

    if users[uid].status == UserStatus.TASK_SELECTION:
        users[uid].status = UserStatus.TASK_SELECTION_FINISHED
        print(f"User {users[uid].name!r} ({uid!r}) finished task selection.")

    if all(u.status == UserStatus.TASK_SELECTION_FINISHED for u in users.values()):
        print("Task selection finished for all users.")
        if no_card_duplicates(card_distribution) and no_task_duplicates(chosen_tasks):
            for user in users.values():
                if user.status == UserStatus.TASK_SELECTION_FINISHED:
                    user.status = UserStatus.AWAITING_RESULT

            emit("open result view", broadcast=True)
            print("Starting solver.")
            game_state = CrewGameState(card_distribution, tasks=chosen_tasks)
            game = CrewGame(game_parameters, game_state)
            game.solve()
            print_initial_game_state(game_parameters, game_state)
            if game.has_solution():
                print_solution(game.get_solution())
            else:
                print("No solution exists.")

        else:
            print("ERROR: duplicate tasks.")
            emit("end game")


@socketio.on("end game")
def end_game() -> None:

    global card_distribution, chosen_tasks, all_possible_tasks, all_possible_cards
    global all_unselected_cards

    for u in users.values():
        u.status = UserStatus.CONNECTED
        u.player_index = None

    card_distribution = None
    chosen_tasks = None
    all_possible_tasks = None
    all_possible_cards = None
    all_unselected_cards = None

    print("Ending the game.")

    emit("game ended", broadcast=True)


@socketio.on("disconnect")
def disconnect() -> None:

    global users

    uid: str = request.cookies.get("crewz3r_id")

    print(
        f"User {users[uid].name!r} ({uid!r}) disconnected, "
        + f"user count: {len(users) - 1}."
    )
    users.pop(uid)
    send_user_list()


@app.route("/")
def index() -> str:
    resp = make_response(render_template("index.html"))

    if request.cookies.get("crewz3r_id") is None:
        resp.set_cookie("crewz3r_id", str(uuid.uuid4()), httponly=True)

    return resp


def main() -> None:
    socketio.run(app, host="0.0.0.0", allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
