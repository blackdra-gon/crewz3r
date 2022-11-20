import random

from z3 import And, Distinct, Implies, Int, IntVector, Or, sat, Solver, \
    CheckSatResult

from crew_types import Card, CardDistribution
from crew_utils import deal_cards, CrewGameState, CrewGameSolution, \
    CrewGameTrick, CrewGameParameters


class CrewGameBase(object):

    def __init__(self, parameters: CrewGameParameters,
                 initial_state: CrewGameState) -> None:

        assert parameters.number_of_players >= 2
        assert parameters.number_of_colours >= 1
        assert parameters.max_card_value >= 1
        assert parameters.max_trump_value >= 0

        self.parameters = parameters
        self.initial_state = initial_state

        # Internal constant representing the colour of trump cards.
        self.TRUMP_COLOUR = -1

        # Rules for the game and the game setup.
        self.rules: dict[str, bool] = {
            'use_trump_cards': parameters.max_trump_value != 0,
            'highest_trump_starts_first_trick': True,
        }

        # When the first starting player is given
        if initial_state.active_player:
            self.rules['highest_trump_starts_first_trick'] = False

        # If the solver has been run.
        self.is_solved: bool = False

        # The solver result.
        self.check_result: CheckSatResult | None = None

        self.player_hands: CardDistribution = initial_state.hands
        if not self.player_hands:
            self.player_hands = deal_cards(parameters)

        # The number of hands must match the number of players.
        assert len(self.player_hands) == parameters.number_of_players

        self.NUMBER_OF_TRICKS = len(self.player_hands[0])

        # All hands must contain the same number of cards.
        for hand in self.player_hands:
            assert len(hand) == self.NUMBER_OF_TRICKS
        # Each card may only occur once in the given distribution.
        for i, card in enumerate(self.player_hands):
            assert card not in self.player_hands[:i]

        self._init_solver_setup()
        self._init_tasks_setup()

    def _init_solver_setup(self):
        # A card is represented by two integers.
        # The first represents the colour, the second the card value.
        self.cards = [[IntVector('card_%s_%s' % (j, i), 2)
                       for i in range(1, self.parameters.number_of_players + 1)]
                      for j in range(1, self.NUMBER_OF_TRICKS + 1)]

        # Lists of integers store the starting player, active colour and winner
        # for each trick.
        self.starting_players = \
            [Int('s_%s' % i) for i in range(1, self.NUMBER_OF_TRICKS + 1)]
        self.active_colours = \
            [Int('a_%s' % i) for i in range(1, self.NUMBER_OF_TRICKS + 1)]
        self.trick_winners = \
            [Int('w_%s' % i) for i in range(1, self.NUMBER_OF_TRICKS + 1)]

        self.solver = Solver()

        # Each card may occur only once.
        self.solver.add(
            Distinct(*[card[0] * self.parameters.max_card_value + card[1]
                       for trick in self.cards for card in trick]))

        # The player with the highest trump card starts the first trick.
        if self.rules['use_trump_cards'] and \
                self.rules['highest_trump_starts_first_trick']:
            for i in range(self.parameters.number_of_players):
                self.solver.add(Implies(
                    (self.TRUMP_COLOUR, self.parameters.max_trump_value)
                    in self.player_hands[i],
                    self.starting_players[0] == i + 1))
        elif self.initial_state.active_player:
            self.solver.add(
                self.starting_players[0] == self.initial_state.active_player)

        for j in range(self.NUMBER_OF_TRICKS):

            starting_player = self.starting_players[j]
            active_colour = self.active_colours[j]
            trick_winner = self.trick_winners[j]
            s = self.solver

            # Only valid player indices may be used.
            s.add(0 < trick_winner)
            s.add(trick_winner <= self.parameters.number_of_players)
            s.add(0 < starting_player)
            s.add(starting_player <= self.parameters.number_of_players)

            # Only valid colour indices may be used.
            s.add(0 <= active_colour)
            s.add(active_colour < self.parameters.number_of_colours)

            for i in range(self.parameters.number_of_players):

                colour, value = self.cards[j][i][0], self.cards[j][i][1]
                player = i + 1

                # Only valid colour indices may be used.
                s.add(-1 <= colour)
                s.add(colour < self.parameters.number_of_colours)

                # Only valid card values may be used.
                s.add(0 < value)
                s.add(value <= self.parameters.max_card_value)

                # Only valid trump card values may be used.
                s.add(Implies(colour == self.TRUMP_COLOUR,
                              value <= self.parameters.max_trump_value))

                # Players may only play cards that they hold.
                s.add(Or([And(colour == c[0], value == c[1])
                          for c in self.player_hands[i]]))

                # If a player wins a trick, that player is the starting player
                # in the next trick.
                if j + 1 != self.NUMBER_OF_TRICKS:
                    s.add(Implies(trick_winner == player,
                                  self.starting_players[j + 1] == player))

                # The colour played by the starting player is the active colour.
                s.add(Implies(starting_player == player,
                              active_colour == colour))

                # Case 1: The player has played a trump card.
                # If the player's card is the highest trump card in the trick,
                # that player has won the trick.
                if self.rules['use_trump_cards']:
                    s.add(Implies(And(colour == self.TRUMP_COLOUR,
                                      And([Or(self.cards[j][k][0] !=
                                              self.TRUMP_COLOUR,
                                              value > self.cards[j][k][1])
                                           for k in range(
                                              self.parameters.number_of_players)
                                           if i != k])),
                                  trick_winner == player))

                # Case 2: The player has not played a trump card and no trump
                # card is present in the trick.
                # If the player's card is of the active colour and higher
                # than all other cards of the active colour in the trick,
                # that player has won the trick.
                s.add(Implies(
                    And(colour == active_colour,
                        And([And(self.cards[j][k][0] != self.TRUMP_COLOUR,
                                 Or(self.cards[j][k][0] != active_colour,
                                    value > self.cards[j][k][1]))
                             for k in range(self.parameters.number_of_players)
                             if i != k])),
                    trick_winner == player))

                # If a player holds a card of the active colour, that player may
                # only play a card of that colour.
                s.add(Implies(Or([self.cards[m][i][0] == active_colour
                                  for m in range(j + 1,
                                                 self.NUMBER_OF_TRICKS)]),
                              colour == active_colour))

    def _init_tasks_setup(self):
        self.task_cards: list[Card] = []
        self.tasks: list[IntVector] = []

    def _valid_card(self, card: Card) -> bool:
        return 0 <= card[0] < self.parameters.number_of_colours and \
               0 < card[1] <= self.parameters.max_card_value

    def solve(self) -> None:
        self.check_result = self.solver.check()
        self.is_solved = True

    def has_solution(self) -> bool | None:
        return self.check_result == sat if self.is_solved else None

    def get_solution(self) -> CrewGameSolution | None:

        if not self.is_solved:
            return None

        if not self.has_solution():
            raise ValueError

        tricks: list[CrewGameTrick] = []

        m = self.solver.model()
        for j in range(self.NUMBER_OF_TRICKS):
            ac = m.evaluate(self.active_colours[j]).as_long()
            sp = m.evaluate(self.starting_players[j]).as_long()
            wp = m.evaluate(self.trick_winners[j]).as_long()
            cards = []
            for i in range(self.parameters.number_of_players):
                colour = m.evaluate(self.cards[j][i][0]).as_long()
                value = m.evaluate(self.cards[j][i][1]).as_long()
                cards.append((colour, value))
            tricks.append(CrewGameTrick(cards, ac, sp, wp))

        return CrewGameSolution(self.initial_state, tricks)


class CrewGame(CrewGameBase):

    def __init__(self, initial_state: CrewGameState,
                 cards_distribution: CardDistribution = None,
                 first_starting_player: int = None) -> None:

        number_of_players: int = len(initial_state.hands)
        assert number_of_players in (3, 4, 5)
        number_of_colours: int = 4
        trump_card_max_value: int = 4
        if number_of_players == 3:
            number_of_colours = 3
            trump_card_max_value = 3
        card_max_value: int = 9
        use_trump_cards: bool = True

        super().__init__(
            CrewGameParameters(number_of_players, number_of_colours,
                               card_max_value, trump_card_max_value),
            initial_state
        )

        # This function assumes that a standard crew card deck with 4*9+4 cards
        # is used for 4 and 5 players and 3*9+3 cards are used for 3 players.
        # Additionally, we assume that we do not mix relative and absolute task
        # order constraints.

        ordered_tasks = []
        last_task = None
        for task in initial_state.tasks:
            self.add_card_task(task.player, task.card)
            if task.order_constraint > 0:
                ordered_tasks.append(task)
            elif task.order_constraint == -1:
                last_task = task
        if len(ordered_tasks) > 0:
            ordered_tasks.sort(key=lambda o_task: o_task.order_constraint)
            if ordered_tasks[0].relative_constraint:
                self.add_task_constraint_relative_order(
                    [task.card for task in ordered_tasks])
            else:
                self.add_task_constraint_absolute_order(
                    [task.card for task in ordered_tasks])
        if last_task:
            self.add_task_constraint_absolute_order_last(last_task.card)

    def add_card_task(self, tasked_player: int, card: Card = None) -> None:
        if card:
            assert self._valid_card(card)
            assert card not in self.tasks
        else:
            card = random.choice([c for hand in self.player_hands for c in hand
                                  if c not in self.task_cards
                                  and c[0] != self.TRUMP_COLOUR])
        self.task_cards.append(card)

        # A task is represented by four integers:
        # - The first two represent the card color and value,
        # - the third represents the tasked player,
        # - the fourth stores the trick in which the task was completed
        new_task = IntVector('task_%s' % str(len(self.tasks) + 1), 4)
        self.tasks.append(new_task)
        self.solver.add(new_task[0] == card[0])
        self.solver.add(new_task[1] == card[1])
        self.solver.add(new_task[2] == tasked_player)
        self.solver.add(0 < new_task[3])
        self.solver.add(new_task[3] <= self.NUMBER_OF_TRICKS)

        # If a trick contains the task card, that trick must be won by the
        # tasked player. The task is then completed.
        for j in range(self.NUMBER_OF_TRICKS):
            self.solver.add(Implies(Or([And(card[0] == c[0], card[1] == c[1])
                                        for c in self.cards[j]]),
                                    And(self.trick_winners[j] == tasked_player,
                                        new_task[3] == j)))

    # parameter ordered_task: a tuple of task cards in the order, in which 
    # they have to be fulfilled has no influence on the other task cards. 
    def add_task_constraint_relative_order(self,
                                           ordered_tasks: list[Card]) -> None:
        assert 1 < len(ordered_tasks) <= len(self.tasks)
        assert all([self._valid_card(card) for card in ordered_tasks])

        for i, o_task in enumerate(ordered_tasks[:-1]):
            task_index = self.task_cards.index(o_task)
            next_task = ordered_tasks[i + 1]
            next_task_index = self.task_cards.index(next_task)
            # using the fourth field of a task, which stores the trick in
            # which it is fulfilled
            self.solver.add(
                self.tasks[task_index][3] <= self.tasks[next_task_index][3])

    # parameter ordered_task: a tuple of task cards in the order, in which 
    # they have to be fulfilled all other tasks have to be fulfilled after 
    # all tasks with an absolute order are finished 
    def add_task_constraint_absolute_order(self,
                                           ordered_tasks: list[Card]) -> None:
        assert 1 <= len(ordered_tasks) <= len(self.tasks)
        assert all([self._valid_card(card) for card in ordered_tasks])

        # Absolute order is specified as a set of relative order constraints.
        if len(ordered_tasks) > 1:
            self.add_task_constraint_relative_order(ordered_tasks)
        for i, o_task in enumerate(ordered_tasks):
            for u_task in [u_t for u_t in self.task_cards
                           if u_t not in ordered_tasks]:
                self.add_task_constraint_relative_order([o_task, u_task])

    def add_task_constraint_absolute_order_last(self, task: Card) -> None:
        assert self._valid_card(task)

        # Absolute order is specified as a set of relative order constraints.
        for u_task in [u_t for u_t in self.task_cards if u_t != task]:
            self.add_task_constraint_relative_order([u_task, task])

    def add_special_task_no_tricks_value(self, forbidden_value: int) -> None:
        assert 0 < forbidden_value <= self.parameters.max_card_value

        # No trick may be won with a card of the given value.
        for j in range(self.NUMBER_OF_TRICKS):
            for i in range(self.parameters.number_of_players):
                self.solver.add(
                    Implies(self.cards[j][i][1] == forbidden_value,
                            self.cards[j][i][0] != self.active_colours[j]))
