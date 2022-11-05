from crew_game import CrewGame


def example_game(number: int):
    if number == 1:
        game = CrewGame(cards_distribution=[
        [(1,5),(2,3),(-1,3)],
        [(2,5),(2,4),(-1,2)],
        [(3,8),(2,7),(1,3)],
        [(1,6),(2,2),(1,7)]
        ])
        game.add_card_task(1, (1,7))
        game.add_card_task(4, (2,4))
        game.add_task_constraint_relative_order((game.task_cards[1], game.task_cards[0]))
    else:
        print(f"There is no example game number {number}. Returning random game instead")
        return CrewGame()
    return game
