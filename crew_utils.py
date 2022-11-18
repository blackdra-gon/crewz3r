import random
from dataclasses import dataclass, field
from typing import TypeAlias

# Type alias for cards: The first integer represents the color (or suit),
# the second determines the card value.
Card: TypeAlias = tuple[int, int]


# Class representing a task assigned to a player
# If order_constraint == 0, there is no order constraint.
# If relative_constraint == False, we have an absolute order constraint.
# In this case -1 means: The task has to be fulfilled at last.
class Task:

    def __init__(self, card: Card, player: int, order_constraint=0, relative_constraint=False):
        if relative_constraint:
            assert order_constraint in (0, 1, 2, 3, 4)
        else:
            assert order_constraint in (-1, 0, 1, 2, 3, 4, 5)
        self.card = card
        self.player = player
        self.order_constraint: int = order_constraint
        self.relative_constraint: bool = relative_constraint


class SpecialTask:
    pass


class NoTricksWithValue(SpecialTask):

    def __init__(self, forbidden_value):
        self.forbidden_value = forbidden_value



def deal_cards(number_of_players: int,
               number_of_colours: int,
               max_card_value: int,
               max_trump_value: int) -> list[list[Card]]:
    trump_colour = -1
    number_of_cards = number_of_colours * max_card_value + max_trump_value
    number_of_tricks = number_of_cards // number_of_players
    assert number_of_tricks * number_of_players == number_of_cards
    remaining_cards = [(color, value)
                       for color in range(number_of_colours)
                       for value in range(1, max_card_value + 1)] + \
                      [(trump_colour, value)
                       for value in range(1, max_trump_value + 1)
                       if max_trump_value > 0]
    hands = []
    for i in range(number_of_players):
        hand = sorted(random.sample(remaining_cards, number_of_tricks))
        for card in hand:
            remaining_cards.remove(card)
        hands.append(hand)
    return hands

# If the first starting player shall be determined by the highest trump card, active_player should be set to None
@dataclass
class CrewGameState(object):
    hands: list[list[Card]]
    tasks: list[Task]
    active_player: int = 0
    special_tasks: list[SpecialTask] = field(default_factory=list)


if __name__ == '__main__':
    print(deal_cards(number_of_players=3, number_of_colours=3, max_card_value=9, max_trump_value=3))
