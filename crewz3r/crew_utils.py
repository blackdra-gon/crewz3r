import random
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from itertools import permutations
from typing import Any

from crewz3r.crew_tasks import SpecialTask, Task
from crewz3r.crew_types import Card, CardDistribution, Colour, Hand, Player

# Internal constant representing the colour of trump cards.
TRUMP_COLOUR: Colour = -1


# https://docs.python.org/3/howto/descriptor.html#validator-class
class Validator(ABC):
    """Abstract descriptor class for validating field values."""

    def __set_name__(self, owner: type, name: str) -> None:
        self.private_name = "_" + name

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        return getattr(obj, self.private_name)

    def __set__(self, obj: Any, value: Any) -> None:
        self.validate(value)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validate(self, value: Any) -> None:
        raise NotImplementedError


@dataclass(kw_only=True)
class IntegerV(Validator):
    """Descriptor for integers with optional min and max value constraints."""

    min_value: int | None = None
    max_value: int | None = None

    def validate(self, value: int) -> None:
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"Expected {value} to be at least {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"Expected {value} to be no more than {self.max_value}")


@dataclass
class CrewGameParametersData:
    number_of_players: int | IntegerV
    number_of_colours: int | IntegerV
    max_card_value: int | IntegerV
    max_trump_value: int | IntegerV


class CrewGameParameters(CrewGameParametersData):
    """The base parameters needed to initialize a crew game.

    Setting max_trump_value to 0 disables trump cards."""

    number_of_players = IntegerV(min_value=3)
    number_of_colours = IntegerV(min_value=1)
    max_card_value = IntegerV(min_value=1)
    max_trump_value = IntegerV(min_value=0)


FOUR_PLAYER_PARAMETERS: CrewGameParameters = CrewGameParameters(4, 4, 9, 4)
THREE_PLAYER_PARAMETERS: CrewGameParameters = CrewGameParameters(3, 3, 9, 3)
FIVE_PLAYER_PARAMETERS: CrewGameParameters = CrewGameParameters(5, 4, 9, 4)
DEFAULT_PARAMETERS: CrewGameParameters = FOUR_PLAYER_PARAMETERS


@dataclass
class CrewGameState:
    """The card distribution, tasks and active player of a crew game.

    When active_player is set to None, the first starting player is
    determined by the highest trump card."""

    hands: CardDistribution | None = None
    active_player: Player | None = None
    tasks: list[Task] = field(default_factory=list)
    special_tasks: list[SpecialTask] = field(default_factory=list)


@dataclass
class CrewGameTrick:
    """A single trick within a game."""

    played_cards: list[Card]
    active_colour: Colour
    starting_player: Player
    winning_player: Player


@dataclass
class CrewGameSolution:
    """A sequence of tricks that fulfill all tasks and requirements of a game
    instance."""

    initial_state: CrewGameState
    tricks: list[CrewGameTrick]


def get_deck_without_trump(parameters: CrewGameParameters) -> list[Card]:
    return [
        (color, value)
        for color in range(parameters.number_of_colours)
        for value in range(1, parameters.max_card_value + 1)
    ]


def get_deck(parameters: CrewGameParameters) -> list[Card]:
    return get_deck_without_trump(parameters) + [
        (TRUMP_COLOUR, value)
        for value in range(1, parameters.max_trump_value + 1)
        if parameters.max_trump_value > 0
    ]


def deal_cards(parameters: CrewGameParameters) -> CardDistribution:
    number_of_cards: int = (
        parameters.number_of_colours * parameters.max_card_value
        + parameters.max_trump_value
    )
    number_of_tricks: int = number_of_cards // parameters.number_of_players
    if not number_of_tricks * parameters.number_of_players == number_of_cards:
        raise ValueError("Invalid parameters.")
    remaining_cards: list[Card] = get_deck(parameters)
    hands: list[Hand] = []
    for i in range(parameters.number_of_players):
        hand: list[Card] = sorted(random.sample(remaining_cards, number_of_tricks))
        for card in hand:
            remaining_cards.remove(card)
        hands.append(hand)
    return hands


def all_task_distributions(
    hands: CardDistribution, tasks: list[Task], parameter: CrewGameParameters
) -> Iterator[CrewGameState]:
    def task_distributions(
        number_of_players: int, number_of_tasks: int
    ) -> Iterator[tuple[int, ...]]:
        base_list = [(i % number_of_players) + 1 for i in range(number_of_tasks)]
        yield from dict.fromkeys(permutations(base_list))

    for k, d in enumerate(task_distributions(parameter.number_of_players, len(tasks))):
        for j, task in enumerate(tasks):
            task.player = d[j]
        yield CrewGameState(hands, None, tasks)


def print_random_card_distribution(number_of_players: int) -> None:
    if number_of_players == 3:
        hands = deal_cards(THREE_PLAYER_PARAMETERS)
    elif number_of_players == 4:
        hands = deal_cards(FOUR_PLAYER_PARAMETERS)
    elif number_of_players == 5:
        hands = deal_cards(FIVE_PLAYER_PARAMETERS)
    else:
        raise ValueError
    print(hands)


def no_card_duplicates(distribution: CardDistribution) -> bool:
    for j, hand in enumerate(distribution):
        for i, card in enumerate(hand):
            if any(
                [card in h for h in distribution[j + 1 :]]
                + [card == c for c in hand[i + 1 :]]
            ):
                return False
    return True


def no_task_duplicates(task_list: list[Task]) -> bool:
    card_list: list[Card] = []
    for task in task_list:
        if task.card in card_list:
            return False
        card_list.append(task.card)
    return True


# counted from 1
def get_captain_index(
    cards: CardDistribution, parameters: CrewGameParameters
) -> Player:
    for i, hand in enumerate(cards, start=1):
        if (-1, parameters.max_trump_value) in hand:
            return i


if __name__ == "__main__":
    print_random_card_distribution(4)
