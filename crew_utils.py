import random
from dataclasses import dataclass, field

from crew_tasks import SpecialTask, Task
from crew_types import Card, CardDistribution, Colour, Player, Hand


def deal_cards(number_of_players: int,
               number_of_colours: int,
               max_card_value: int,
               max_trump_value: int) -> CardDistribution:
    trump_colour = -1
    number_of_cards: int = number_of_colours * max_card_value + max_trump_value
    number_of_tricks: int = number_of_cards // number_of_players
    assert number_of_tricks * number_of_players == number_of_cards
    remaining_cards: list[Card] = \
        [(color, value)
         for color in range(number_of_colours)
         for value in range(1, max_card_value + 1)] + \
        [(trump_colour, value)
         for value in range(1, max_trump_value + 1)
         if max_trump_value > 0]
    hands: list[Hand] = []
    for i in range(number_of_players):
        hand = tuple(sorted(random.sample(remaining_cards, number_of_tricks)))
        for card in hand:
            remaining_cards.remove(card)
        hands.append(hand)
    return tuple(hands)


# If the first starting player shall be determined by the highest trump card,
# active_player should be set to None
@dataclass
class CrewGameState:
    hands: CardDistribution
    tasks: list[Task | SpecialTask]
    active_player: Player | None = None
    special_tasks: list[SpecialTask] = field(default_factory=list)


@dataclass
class CrewGameTrick:
    played_cards: list[Card]
    active_colour: Colour
    active_player: Player
    winning_player: Player


@dataclass
class CrewGameSolution:
    initial_state: CrewGameState
    tricks: list[CrewGameTrick]
