from crew_example_games import example_game
from crew_game import CrewGame

def main():
    #game = example_game(1)
    game = CrewGame()

    game.add_card_task(1, (1,7))
    game.add_card_task(4, (2,4))
    game.add_task_constraint_relative_order((game.task_cards[1], game.task_cards[0]))

    # Add tasks.
    # for i in sorted(random.sample(range(1, game.NUMBER_OF_PLAYERS + 1), 4)):
    #     game.add_card_task(i)
    #
    # game.add_task_constraint_relative_order(random.sample(game.task_cards, 2))
    # game.add_task_constraint_absolute_order(random.sample(game.task_cards, 1))
    # game.add_task_constraint_absolute_order_last(random.choice(game.task_cards))
    # game.add_special_task_no_tricks_value(game.CARD_MAX_VALUE)

    game.check()
    game.print_solution()


if __name__ == '__main__':
    main()