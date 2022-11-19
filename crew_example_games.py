import random

from crew_game import CrewGame
from crew_utils import Task, CrewGameState


def example_game(number: int):
    if number == 1:
        game = CrewGame(cards_distribution=[
            [(1, 5), (2, 3), (-1, 3)],
            [(2, 5), (2, 4), (-1, 2)],
            [(3, 8), (2, 7), (1, 3)],
            [(1, 6), (2, 2), (1, 7)]
        ], first_starting_player=4)
        game.add_card_task(1, (1, 7))
        game.add_card_task(4, (2, 4))
        game.add_task_constraint_relative_order(
            (game.task_cards[0], game.task_cards[1]))
    if number == 2:
        # Should not be solvable: (1, 7) is alone on Player 1's hand,
        # and Player 2 has to win his own (1, 5) before.
        # Takes around 3 min to solve on Benni's Laptop
        game = CrewGame(cards_distribution=[
            [(-1, 3), (0, 2), (0, 4), (0, 6), (0, 7), (1, 7), (2, 5), (3, 3),
             (3, 6), (3, 9)],
            [(-1, 2), (-1, 4), (1, 1), (1, 3), (1, 4), (1, 5), (2, 7), (2, 8),
             (2, 9), (3, 1)],
            [(-1, 1), (0, 1), (0, 5), (0, 8), (0, 9), (1, 6), (2, 1), (2, 2),
             (3, 4), (3, 8)],
            [(0, 3), (1, 2), (1, 8), (1, 9), (2, 3), (2, 4), (2, 6), (3, 2),
             (3, 5), (3, 7)]])
        game.add_card_task(1, (1, 7))
        game.add_card_task(2, (1, 5))
        game.add_task_constraint_relative_order(
            (game.task_cards[1], game.task_cards[0]))
    if number == 3:
        # this game is solvable, took 30s on Benni's Laptop
        hands = [
            [(0, 1), (0, 7), (1, 2), (1, 3), (1, 5), (1, 6), (1, 8), (2, 3)],
            [(-1, 2), (-1, 4), (0, 3), (1, 1), (1, 7), (2, 7), (2, 9), (3, 7)],
            [(0, 4), (0, 5), (0, 9), (2, 1), (2, 4), (2, 6), (3, 1), (3, 2)],
            [(-1, 1), (0, 2), (1, 9), (2, 5), (3, 4), (3, 5), (3, 8), (3, 9)],
            [(-1, 3), (0, 6), (0, 8), (1, 4), (2, 2), (2, 8), (3, 3), (3, 6)]]
        tasks = [Task(card=(0, 1), player=1, order_constraint=-1),
                 Task(card=(1, 9), player=4, order_constraint=1),
                 Task(card=(1, 8), player=2, order_constraint=2)]
        game_state = CrewGameState(hands, tasks, active_player=0)
        game = CrewGame(game_state)
    if number == 4:
        # this game is solvable, took 2s on Benni's Laptop
        hands = [
            [(0, 4), (0, 5), (0, 6), (1, 1), (1, 2), (1, 3), (1, 6), (1, 7),
             (1, 8), (1, 9)],
            [(-1, 2), (-1, 3), (0, 2), (0, 7), (0, 9), (1, 4), (2, 1), (2, 3),
             (2, 6), (2, 9)],
            [(-1, 1), (0, 1), (0, 3), (0, 8), (1, 5), (2, 2), (2, 4), (2, 5),
             (2, 7), (2, 8)]]
        tasks = [Task(card=(2, 2), player=1, order_constraint=3,
                      relative_constraint=True),
                 Task(card=(1, 9), player=1, order_constraint=1,
                      relative_constraint=True),
                 Task(card=(1, 8), player=2, order_constraint=2,
                      relative_constraint=True)]
        game_state = CrewGameState(hands, tasks, active_player=0)
        game = CrewGame(game_state)
    else:
        print(f"There is no example game number {number}."
              f"Returning random game instead")
        return CrewGame()
    return game


def random_game():
    game = CrewGame()
    # Add tasks.
    for i in sorted(random.sample(range(1, game.NUMBER_OF_PLAYERS + 1), 4)):
        game.add_card_task(i)

    game.add_task_constraint_relative_order(random.sample(game.task_cards, 2))
    game.add_task_constraint_absolute_order(random.sample(game.task_cards, 1))
    game.add_task_constraint_absolute_order_last(random.choice(game.task_cards))
    # game.add_special_task_no_tricks_value(game.CARD_MAX_VALUE)

    return game
