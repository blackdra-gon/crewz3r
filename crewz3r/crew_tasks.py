from .crew_types import Card, Player


class Task:
    """A task for a specific card assigned to a player.

    If order_constraint == 0, there is no order constraint.
    If relative_constraint == False, we have an absolute order constraint.
    In this case -1 means: The task has to be completed last."""

    def __init__(
        self,
        card: Card,
        player: Player | None = None,
        order_constraint: int = 0,
        relative_constraint: bool = False,
    ) -> None:
        if relative_constraint:
            assert order_constraint in (0, 1, 2, 3, 4)
        else:
            assert order_constraint in (-1, 0, 1, 2, 3, 4, 5)
        self.card: Card = card
        self.player: Player | None = player
        self.order_constraint: int = order_constraint
        self.relative_constraint: bool = relative_constraint

    def __str__(self):
        ret = f"Task: {self.card} to player {self.player}"
        if self.order_constraint != 0:
            constraint_type = "relative" if self.relative_constraint else "absolute"
            ret += f", {constraint_type} order: {self.order_constraint}"
        return ret

    def __repr__(self):
        return self.__str__()


class SpecialTask:
    """Base class for all non-standard tasks."""

    def __init__(self, description: str) -> None:
        self.description = description


class NoTricksWithValueTask(SpecialTask):
    def __init__(self, forbidden_value: int) -> None:
        super().__init__(f"No tricks may be won with cards of value {forbidden_value}.")
        self.forbidden_value: int = forbidden_value


class AssignTrickToPlayer(SpecialTask):
    def __init__(self, player: Player, trick_number: int):
        super().__init__(f"Trick number {trick_number} must be won by player {player}")
        self.player = player
        self.trick_number = trick_number
        # Idea: Adjust the print such that it marks the tricks


class NullGame(SpecialTask):
    def __init__(self, player: Player):
        super().__init__(f"Player {player} must not win any tricks")
        self.player = player


class WinTricksWithSpecificValues(SpecialTask):
    def __init__(self, value: int, number: int = 1):
        super().__init__(
            f"At least {number} tricks have to be won with a (non-trump) card of "
            + f"value {value}."
        )
        self.value = value
        self.number = number
