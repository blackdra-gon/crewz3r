import random

from crew_game import CrewGame
from crew_tasks import (
    AssignTrickToPlayer,
    NullGame,
    SpecialTask,
    WinTricksWithSpecificValues,
)
from crew_types import CardDistribution, Player
from crew_utils import (
    DEFAULT_PARAMETERS,
    FIVE_PLAYER_PARAMETERS,
    THREE_PLAYER_PARAMETERS,
    CrewGameParameters,
    CrewGameState,
    Task,
    deal_cards,
)


def example_game(number: int | None) -> CrewGame:
    description: str = ""
    hands: CardDistribution
    active_player: Player | None = None
    tasks: list[Task] = []
    special_tasks: list[SpecialTask] = []
    parameters: CrewGameParameters = DEFAULT_PARAMETERS

    match number:
        case 1:
            hands = (
                ((1, 5), (2, 3), (-1, 3)),
                ((2, 5), (2, 4), (-1, 2)),
                ((3, 8), (2, 7), (1, 3)),
                ((1, 6), (2, 2), (1, 7)),
            )
            active_player = 4
            tasks = [
                Task((1, 7), 1, order_constraint=1, relative_constraint=True),
                Task((2, 4), 4, order_constraint=2, relative_constraint=True),
            ]
        case 2:
            description = (
                "Should not be solvable: (1, 7) is alone on Player 1's hand, "
                "and Player 2 has to win his own (1, 5) before. "
                "Takes around 3 min to solve on Benni's Laptop."
            )
            hands = (
                (
                    (-1, 3),
                    (0, 2),
                    (0, 4),
                    (0, 6),
                    (0, 7),
                    (1, 7),
                    (2, 5),
                    (3, 3),
                    (3, 6),
                    (3, 9),
                ),
                (
                    (-1, 2),
                    (-1, 4),
                    (1, 1),
                    (1, 3),
                    (1, 4),
                    (1, 5),
                    (2, 7),
                    (2, 8),
                    (2, 9),
                    (3, 1),
                ),
                (
                    (-1, 1),
                    (0, 1),
                    (0, 5),
                    (0, 8),
                    (0, 9),
                    (1, 6),
                    (2, 1),
                    (2, 2),
                    (3, 4),
                    (3, 8),
                ),
                (
                    (0, 3),
                    (1, 2),
                    (1, 8),
                    (1, 9),
                    (2, 3),
                    (2, 4),
                    (2, 6),
                    (3, 2),
                    (3, 5),
                    (3, 7),
                ),
            )
            tasks = [
                Task((1, 5), 2, order_constraint=1, relative_constraint=True),
                Task((1, 7), 1, order_constraint=2, relative_constraint=True),
            ]
        case 3:
            description = "This game is solvable, took 30s on Benni's Laptop."
            hands = (
                ((0, 1), (0, 7), (1, 2), (1, 3), (1, 5), (1, 6), (1, 8), (2, 3)),
                ((-1, 2), (-1, 4), (0, 3), (1, 1), (1, 7), (2, 7), (2, 9), (3, 7)),
                ((0, 4), (0, 5), (0, 9), (2, 1), (2, 4), (2, 6), (3, 1), (3, 2)),
                ((-1, 1), (0, 2), (1, 9), (2, 5), (3, 4), (3, 5), (3, 8), (3, 9)),
                ((-1, 3), (0, 6), (0, 8), (1, 4), (2, 2), (2, 8), (3, 3), (3, 6)),
            )
            tasks = [
                Task((0, 1), 1, order_constraint=-1),
                Task((1, 9), 4, order_constraint=1),
                Task((1, 8), 2, order_constraint=2),
            ]
            parameters.number_of_players = 5
        case 4:
            description = "This game is solvable, took 2s on Benni's Laptop."
            hands = (
                (
                    (0, 4),
                    (0, 5),
                    (0, 6),
                    (1, 1),
                    (1, 2),
                    (1, 3),
                    (1, 6),
                    (1, 7),
                    (1, 8),
                    (1, 9),
                ),
                (
                    (-1, 2),
                    (-1, 3),
                    (0, 2),
                    (0, 7),
                    (0, 9),
                    (1, 4),
                    (2, 1),
                    (2, 3),
                    (2, 6),
                    (2, 9),
                ),
                (
                    (-1, 1),
                    (0, 1),
                    (0, 3),
                    (0, 8),
                    (1, 5),
                    (2, 2),
                    (2, 4),
                    (2, 5),
                    (2, 7),
                    (2, 8),
                ),
            )
            tasks = [
                Task((2, 2), 1, order_constraint=3, relative_constraint=True),
                Task((1, 9), 1, order_constraint=1, relative_constraint=True),
                Task((1, 8), 2, order_constraint=2, relative_constraint=True),
            ]
            parameters = THREE_PLAYER_PARAMETERS
        case 42:
            hands = (
                (
                    (0, 2),
                    (0, 4),
                    (0, 5),
                    (-1, 2),
                    (1, 2),
                    (2, 1),
                    (2, 2),
                    (2, 3),
                    (2, 7),
                    (2, 8),
                ),
                (
                    (0, 9),
                    (0, 6),
                    (0, 1),
                    (-1, 1),
                    (1, 3),
                    (1, 6),
                    (1, 7),
                    (1, 8),
                    (1, 9),
                    (2, 9),
                ),
                (
                    (0, 3),
                    (0, 7),
                    (0, 8),
                    (-1, 3),
                    (1, 1),
                    (1, 4),
                    (1, 5),
                    (2, 4),
                    (2, 5),
                    (2, 6),
                ),
            )
            tasks = [
                Task((1, 1)),
                Task((0, 9)),
                Task((2, 3), order_constraint=1),
                Task((1, 5), order_constraint=2),
                Task((1, 6), order_constraint=3),
                Task((1, 2)),
            ]
            parameters = THREE_PLAYER_PARAMETERS
        case 5:
            description = "Test assigning tricks to players"
            hands = (
                (
                    (0, 3),
                    (0, 4),
                    (0, 6),
                    (0, 9),
                    (1, 2),
                    (1, 4),
                    (2, 6),
                    (3, 1),
                    (3, 4),
                    (3, 6),
                ),
                (
                    (0, 5),
                    (1, 1),
                    (1, 3),
                    (1, 5),
                    (2, 1),
                    (2, 3),
                    (2, 5),
                    (2, 7),
                    (3, 3),
                    (3, 8),
                ),
                (
                    (-1, 1),
                    (-1, 2),
                    (0, 1),
                    (0, 2),
                    (1, 6),
                    (1, 7),
                    (1, 8),
                    (2, 2),
                    (2, 8),
                    (3, 5),
                ),
                (
                    (-1, 3),
                    (-1, 4),
                    (0, 7),
                    (0, 8),
                    (1, 9),
                    (2, 4),
                    (2, 9),
                    (3, 2),
                    (3, 7),
                    (3, 9),
                ),
            )
            special_tasks = [AssignTrickToPlayer(1, 2), AssignTrickToPlayer(2, 3)]
        case 6:
            description = "Test Nullgame"
            hands = (
                (
                    (-1, 1),
                    (0, 2),
                    (0, 7),
                    (1, 5),
                    (1, 9),
                    (2, 3),
                    (2, 5),
                    (3, 1),
                    (3, 3),
                    (3, 4),
                ),
                (
                    (0, 1),
                    (0, 3),
                    (0, 4),
                    (0, 8),
                    (1, 2),
                    (1, 3),
                    (1, 8),
                    (2, 1),
                    (2, 2),
                    (2, 7),
                ),
                (
                    (-1, 3),
                    (0, 6),
                    (0, 9),
                    (1, 1),
                    (2, 8),
                    (3, 2),
                    (3, 6),
                    (3, 7),
                    (3, 8),
                    (3, 9),
                ),
                (
                    (-1, 2),
                    (-1, 4),
                    (0, 5),
                    (1, 4),
                    (1, 6),
                    (1, 7),
                    (2, 4),
                    (2, 6),
                    (2, 9),
                    (3, 5),
                ),
            )
            special_tasks.append(NullGame(1))
        case 7:
            description = "Test one trick won with a 1"
            hands = (
                (
                    (-1, 1),
                    (0, 2),
                    (0, 7),
                    (1, 5),
                    (1, 9),
                    (2, 3),
                    (2, 5),
                    (3, 1),
                    (3, 3),
                    (3, 4),
                ),
                (
                    (0, 1),
                    (0, 3),
                    (0, 4),
                    (0, 8),
                    (1, 2),
                    (1, 3),
                    (1, 8),
                    (2, 1),
                    (2, 2),
                    (2, 7),
                ),
                (
                    (-1, 3),
                    (0, 6),
                    (0, 9),
                    (1, 1),
                    (2, 8),
                    (3, 2),
                    (3, 6),
                    (3, 7),
                    (3, 8),
                    (3, 9),
                ),
                (
                    (-1, 2),
                    (-1, 4),
                    (0, 5),
                    (1, 4),
                    (1, 6),
                    (1, 7),
                    (2, 4),
                    (2, 6),
                    (2, 9),
                    (3, 5),
                ),
            )
            special_tasks.append(WinTricksWithSpecificValues(1, 4))
            # for 1 to 3 ones, there exists a solution, for 4 not
        case _:
            if number:
                description = f"There is no example game number {number}."
            description += "Creating random game."

            hands = deal_cards(parameters)
            task_cards = random.sample([c for h in hands for c in h], 3)
            tasks = [
                Task(c, i + 1, order_constraint=i + 1, relative_constraint=True)
                for i, c in enumerate(task_cards)
            ]

    if number:
        print(f"Example game #{number}:")
    if description:
        print(description)

    return CrewGame(
        parameters, CrewGameState(hands, active_player, tasks, special_tasks)
    )


def random_game() -> CrewGame:
    return example_game(None)


def random_game_mission_26(parameters: CrewGameParameters = FIVE_PLAYER_PARAMETERS):
    special_tasks = [WinTricksWithSpecificValues(1, 2)]
    return CrewGame(parameters, CrewGameState(special_tasks=special_tasks))
