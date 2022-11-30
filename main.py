import time

from crew_example_games import hands, tasks
from crew_game import CrewGame
from crew_print import print_initial_game_state, print_solution
from crew_utils import THREE_PLAYER_PARAMETERS, all_task_distributions


def run_game(game: CrewGame) -> None:
    print_initial_game_state(game.parameters, game.initial_state)

    start_time: float = time.time()

    game.solve()

    duration: float = time.time() - start_time
    print(f"\nSolving took {int(duration // 60)}m {duration % 60:.1f}s.")

    if game.has_solution():
        print_solution(game.get_solution())
    else:
        print("No solution exists.")


def main() -> None:
    # run_game(example_game(1))
    # run_game(example_game(2))
    # run_game(example_game(3))
    # run_game(example_game(4))
    # run_game(random_game())
    for game_state in all_task_distributions(hands, tasks, THREE_PLAYER_PARAMETERS):
        run_game(CrewGame(THREE_PLAYER_PARAMETERS, game_state))


if __name__ == "__main__":
    main()
