from crew_example_games import example_game, random_game
from crew_game import CrewGame


def main():
    game = example_game(4)
    # game = random_game()

    game.solve()
    game.print_solution()


if __name__ == '__main__':
    main()
