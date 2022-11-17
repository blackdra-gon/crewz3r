import random
from dataclasses import dataclass
from typing import TypeAlias

# Type alias for cards: The first integer represents the color (or suit),
# the second determines the card value.
Card: TypeAlias = tuple[int, int]

Task: TypeAlias = None  # TODO: specify representation of a task


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


@dataclass
class CrewGameState(object):
    hands: list[list[Card]]
    tasks: list[Task]
    active_player: int


if __name__ == '__main__':
    print(deal_cards(4, 4, 9, 4))
