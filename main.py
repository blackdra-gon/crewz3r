import time

from crew_example_games import example_game, random_game
from crew_game import CrewGame
from crew_print import print_solution, print_initial_game_state


def run_game(game: CrewGame):
    print_initial_game_state(game.initial_state)

    start_time = time.time()

    game.solve()

    duration = time.time() - start_time
    print(f'\nSolving took {int(duration // 60)}m {duration % 60:.1f}s.')

    if game.has_solution():
        print_solution(game.get_solution())
    else:
        print('No solution exists.')


def main():
    # run_game(example_game(1))
    # run_game(example_game(2))
    run_game(example_game(3))
    # run_game(example_game(4))
    # run_game(random_game())


if __name__ == '__main__':
    main()
