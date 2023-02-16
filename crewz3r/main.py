import time

from crew_example_games import example_game, random_game_mission_26
from crew_game import CrewGame
from crew_print import print_initial_game_state, print_solution


def run_game(game: CrewGame) -> None:
    print_initial_game_state(game.parameters, game.initial_state)

    print(game.get_assertions())

    start_time: float = time.time()

    game.solve()

    duration: float = time.time() - start_time
    print(f"\nSolving took {int(duration // 60)}m {duration % 60:.1f}s.")

    if game.has_solution():
        print_solution(game.get_solution())
    else:
        print("No solution exists.")
        print(game.get_unsat_core())
        print(game.solver.statistics())


def run_n_random_games(number: int) -> None:
    games_with_solution = 0
    for i in range(1, number + 1):
        game = random_game_mission_26()
        run_game(game)
        if game.has_solution():
            games_with_solution += 1
        print(f"Intermediate Result: {i}/{number} game solved.")
        print(f"{games_with_solution} of them had a solution")


def main() -> None:
    run_game(example_game(2))
    # run_game(example_game(2))
    # run_game(example_game(3))
    # run_game(example_game(4))
    # run_game(random_game())
    # run_game(example_game(7))
    # for game_state in all_task_distributions(
    #    game.player_hands, game.initial_state.tasks, game.parameters
    # ):
    #    run_game(CrewGame(game.parameters, game_state))
    # run_n_random_games(100)


if __name__ == "__main__":
    main()
