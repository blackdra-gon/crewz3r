from crew_types import Card, Player


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
        self.player: Player = player
        self.order_constraint: int = order_constraint
        self.relative_constraint: bool = relative_constraint


class SpecialTask:
    """Base class for all non-standard tasks."""

    def __init__(self, description: str) -> None:
        self.description = description


class NoTricksWithValueTask(SpecialTask):
    def __init__(self, forbidden_value: int) -> None:
        super().__init__(f"No tricks may be won with cards of value {forbidden_value}.")
        self.forbidden_value: int = forbidden_value
