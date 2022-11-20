import time

from crew_example_games import example_game
from crew_print import print_solution, print_initial_game_state


def main():
    game = example_game(4)
    # game = random_game()

    print_initial_game_state(game.initial_state)

    start_time = time.time()

    game.solve()

    duration = time.time() - start_time
    print(f'\nSolving took {int(duration // 60)}m {duration % 60:.1f}s.')

    if game.has_solution():
        print_solution(game.get_solution())
    else:
        print('No solution exists.')


if __name__ == '__main__':
    main()
