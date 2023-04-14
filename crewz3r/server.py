import json
import uuid
from dataclasses import dataclass
from enum import Enum, auto

from crew_game import CrewGame
from crew_tasks import Task
from crew_types import Card, CardDistribution
from crew_utils import (
    DEFAULT_PARAMETERS,
    FIVE_PLAYER_PARAMETERS,
    THREE_PLAYER_PARAMETERS,
    CrewGameParameters,
    CrewGameState,
    get_deck,
    get_deck_without_trump,
    no_card_duplicates,
    no_task_duplicates,
    valid_order_constraints,
)
from flask import Flask, request
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
status_in_game: bool = False

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


def string_to_int_if_possible(element: str):
    try:
        element = int(element)
    finally:
        return element


def order_constraint_from_str(string):
    order_constraint = 0
    relative_constraint = False
    match string:
        case 1 | 2 | 3 | 4 | 5 | -1:
            order_constraint = string
        case "❯" | "❯❯" | "❯❯❯" | "❯❯❯❯":
            order_constraint = len(string)
            relative_constraint = True
        case "Ω":
            order_constraint = -1
    return order_constraint, relative_constraint


def valid_cards_and_tasks() -> bool:
    return (
        no_card_duplicates(card_distribution)
        and no_task_duplicates(chosen_tasks)
        and valid_order_constraints(chosen_tasks)
    )


def start_solver():
    print("Starting solver.")
    game_state = CrewGameState(card_distribution, tasks=chosen_tasks)
    game = CrewGame(game_parameters, game_state)
    game.solve()
    print_initial_game_state(game_parameters, game_state)
    if game.has_solution():
        print_solution(game.get_solution())
    else:
        print("No solution exists.")


# ***********************************************************
#        start page
# ***********************************************************


@socketio.on("connect")
def connect() -> None:

    global users

    uid: str = request.cookies.get("crewz3r_id")
    if not uid:
        cookie_value = str(uuid.uuid4())
        emit("cookie value", cookie_value)
        uid = cookie_value
    if uid not in users:
        users[uid] = User(uid, "", UserStatus.CONNECTED)
        print(f"New connection: {uid}, user count: {len(users)}.")
    else:
        print(f"User {users[uid].name} ({uid}) reconnected")
    print("Users:", users, sep="\n")
    match users[uid].status:
        case UserStatus.CARD_SELECTION:
            emit("open card selection view")
            emit("card list", json.dumps(list(all_possible_cards)))
            emit("task list", json.dumps(list(all_possible_tasks)))
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
    global game_parameters, all_unselected_cards, status_in_game

    status_in_game = True
    player_count = len(users)
    game_parameters = DEFAULT_PARAMETERS
    if player_count == 3:
        game_parameters = THREE_PLAYER_PARAMETERS
    if player_count == 5:
        game_parameters = FIVE_PLAYER_PARAMETERS
    # try:
    #    game_parameters.number_of_players = player_count
    # except ValueError:  # as e:
    # print(f"Invalid player count:\n{e!r}")
    # emit("not enough players")
    # return
    # for development it should be possible to start a game with one player:
    #    pass

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

    emit("card list", json.dumps(list(all_possible_cards)), broadcast=True)
    emit("task list", json.dumps(list(all_possible_tasks)), broadcast=True)
    emit("open card selection view", broadcast=True)


# ***********************************************************
#        card selection
# ***********************************************************


@socketio.on("cards selected")
def cards_selected(card_list_str: str):

    global card_distribution

    uid: str = request.cookies.get("crewz3r_id")
    user = users[uid]
    player = user.player_index
    card_list = [tuple(card) for card in json.loads(card_list_str)]
    card_distribution[player] = card_list

    print("Card distribution:", card_distribution, sep="\n")


@socketio.on("tasks selected")
def tasks_selected(task_list_str: str):

    global card_distribution

    uid: str = request.cookies.get("crewz3r_id")
    user = users[uid]
    player = user.player_index
    if users[uid].status == UserStatus.CARD_SELECTION:
        users[uid].status = UserStatus.TASK_SELECTION_FINISHED
        print(f"User {users[uid].name!r} ({uid!r}) finished task selection.")

    for task in json.loads(task_list_str):
        task_list = task.split(",")
        task_list = [string_to_int_if_possible(element) for element in task_list]
        card = tuple(task_list[:2])
        order_constraint, relative_constraint = order_constraint_from_str(task_list[2])
        chosen_tasks.append(
            Task(card, player + 1, order_constraint, relative_constraint)
        )
    print(chosen_tasks)

    if all(u.status == UserStatus.TASK_SELECTION_FINISHED for u in users.values()):
        print("Task selection finished for all users.")
        if valid_cards_and_tasks():
            for user in users.values():
                if user.status == UserStatus.TASK_SELECTION_FINISHED:
                    user.status = UserStatus.AWAITING_RESULT
            start_solver()
        else:
            print(
                "Invalid card or task selection. "
                "Players should check their selection"
            )
            for user in users.values():
                user.status = UserStatus.CARD_SELECTION
            emit("invalid card or task selection", broadcast=True)


@socketio.on("end game")
def end_game() -> None:

    global card_distribution, chosen_tasks, all_possible_tasks, all_possible_cards
    global all_unselected_cards, status_in_game

    status_in_game = False

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


# @socketio.on("disconnect")
# def disconnect() -> None:
#
#     global users, status_in_game
#
#     uid: str = request.cookies.get("crewz3r_id")
#
#     print(
#         f"User {users[uid].name!r} ({uid!r}) disconnected, "
#         + f"user count: {len(users) - 1}."
#     )
#     if not status_in_game:
#         users.pop(uid)
#     send_user_list()


@socketio.on("new cookie required")
def new_cookie_required():
    cookie_value = str(uuid.uuid4())
    emit("cookie value", cookie_value)


def main() -> None:
    socketio.run(app, host="0.0.0.0", allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
