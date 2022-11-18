import random
import time
from typing import TypeAlias, Optional

from z3 import And, Distinct, Implies, Int, IntVector, Or, sat, Solver, \
    CheckSatResult

from crew_utils import Card, deal_cards, CrewGameState


class CrewGameBase(object):

    def __init__(self, number_of_players: int, number_of_colours: int,
                 card_max_value: int, use_trump_cards: bool,
                 trump_card_max_value: int,
                 cards_distribution: list[list[Card]] = None,
                 first_starting_player=None) -> None:

        assert number_of_players >= 2
        assert number_of_colours >= 1
        assert card_max_value >= 1

        # The number of players for which to solve the game.
        self.NUMBER_OF_PLAYERS: int = number_of_players

        # The number of different colours. Trump cards (if active) are not
        # counted.
        self.NUMBER_OF_COLOURS: int = number_of_colours

        # Cards of each colour will be created ranging from 1 to this value,
        # inclusive.
        self.CARD_MAX_VALUE: int = card_max_value

        # Trump cards will be created ranging from 1 to this value, inclusive.
        self.TRUMP_CARD_MAX_VALUE: int = trump_card_max_value

        # Internal constant representing the colour of trump cards.
        self.TRUMP_COLOUR = -1

        # Rules for the game and the game setup.
        self.rules: dict[str, bool] = {
            'use_trump_cards': use_trump_cards,
            'highest_trump_starts_first_trick': True,
        }
        # When the first starting player is given
        if first_starting_player:
            self.rules['highest_trump_starts_first_trick'] = False
            self.first_starting_player = first_starting_player

        # If the solver has been run.
        self.is_solved: bool = False

        # The solver result.
        self.check_result: Optional[CheckSatResult] = None

        # Text representation of colours.
        # Last name reserved for trump cards.
        self.COLOUR_NAMES = ('R', 'G', 'B', 'Y', 'P', 'N', 'X')
        assert self.NUMBER_OF_COLOURS < len(self.COLOUR_NAMES)

        # The total number of cards in the game.
        if not cards_distribution:
            # For a random game:
            self.NUMBER_OF_CARDS = self.NUMBER_OF_COLOURS * self.CARD_MAX_VALUE
            self.NUMBER_OF_CARDS +=\
                trump_card_max_value if use_trump_cards else 0
            # The number of cards must be a multiple of the number of players
            # so that the cards can be distributed evenly.
            assert self.NUMBER_OF_CARDS % number_of_players == 0, \
                (f'The number of {self.NUMBER_OF_CARDS} cards can\'t be '
                 f'evenly distributed between {number_of_players} players.')

            # The number of tricks that will be played in the game.
            self.NUMBER_OF_TRICKS =\
                self.NUMBER_OF_CARDS // self.NUMBER_OF_PLAYERS

            # Stores the distribution of cards between the players.
            self.player_hands: list[list[Card]] = deal_cards(
                self.NUMBER_OF_PLAYERS, self.NUMBER_OF_COLOURS,
                self.CARD_MAX_VALUE, self.TRUMP_CARD_MAX_VALUE)
        else:
            # For a given card distribution:
            # The number of hands must match the number of players.
            assert len(cards_distribution) == self.NUMBER_OF_PLAYERS
            # All hands must contain the same number of cards.
            for player_hand in cards_distribution:
                assert len(player_hand) == len(cards_distribution[0])
            # Each card may only occur once in the given distribution.
            for i, card in enumerate(cards_distribution):
                assert card not in cards_distribution[:i]
            self.NUMBER_OF_TRICKS = len(cards_distribution[0])
            self.player_hands: list[list[Card]] = cards_distribution

        self._init_table_setup()

        self._print_card_distribution()

        self._init_solver_setup()
        self._init_tasks_setup()

    def _init_table_setup(self):
        # Parameters determining the formatting of table output.
        self.table_elements: dict[str, str] = {
            'column_separator': ' | ',
            'player_prefix': 'Player ',
            'trick_start_marker': '>',
            'task_completion_marker': '*',
        }

        # Rules for the formatting of table output.
        self.table_formatting_rules: dict[str, bool] = {
            'mark_trick_start': True,
            'mark_task_completion': True,
        }

        # Table column headers.
        self.table_column_headers: dict[str, str] = {
            'trick_number': 'Trick',
            'starting_player': 'Starting',
            'active_colour': 'A',
            'winning_player': 'Winner',
            'task_completion': 'T',
        }

        # Widths of table elements.
        self.table_element_widths: dict[str, int] = {
            'colour_name': max(map(len,
                                   self.COLOUR_NAMES[:self.NUMBER_OF_PLAYERS] +
                                   (self.COLOUR_NAMES[1],)
                                   if self.rules['use_trump_cards'] else ())),
            'card_value': len(str(self.CARD_MAX_VALUE)),
            'trick_start_marker':
                len(self.table_elements['trick_start_marker'])
                if self.table_formatting_rules['mark_trick_start'] else 0,
            'task_completion_marker':
                len(self.table_elements['task_completion_marker'])
                if self.table_formatting_rules['mark_task_completion'] else 0,
        }

        # Width of the contents of the different table columns.
        self.table_content_widths: dict[str, int] = {
            'trick_number': len(str(self.NUMBER_OF_TRICKS)),
            'starting_player': len(self.table_elements['player_prefix'] +
                                   str(self.NUMBER_OF_PLAYERS)),
            'active_colour': self.table_element_widths['colour_name'],
            'content':
                ((self.table_element_widths['trick_start_marker'] + 1)
                 if self.table_formatting_rules['mark_trick_start'] else 0) +
                1 + self.table_element_widths['colour_name'] + 1 +
                self.table_element_widths['card_value'] + 1 +
                ((1 + self.table_element_widths['task_completion_marker'])
                 if self.table_formatting_rules['mark_task_completion'] else 0),
            'winning_player': len(self.table_elements['player_prefix'] +
                                  str(self.NUMBER_OF_PLAYERS)),
            'task_completion':
                len(self.table_elements['task_completion_marker']),
        }

    def _print_card_distribution(self):
        print('\nCard distribution:')
        for i, cs in enumerate(self.player_hands):
            print(f'{self.table_elements["player_prefix"]}'
                  f'{i + 1}:', end=' ')
            print(', '.join([self._card_string(c) for c in cs]))

    def _init_solver_setup(self):
        # A card is represented by two integers.
        # The first represents the colour, the second the card value.
        self.cards = [[IntVector('card_%s_%s' % (j, i), 2)
                       for i in range(1, self.NUMBER_OF_PLAYERS + 1)]
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
        self.solver.add(Distinct(*[card[0] * self.CARD_MAX_VALUE + card[1]
                                   for trick in self.cards for card in trick]))

        # The player with the highest trump card starts the first trick.
        if self.rules['use_trump_cards'] and \
                self.rules['highest_trump_starts_first_trick']:
            for i in range(self.NUMBER_OF_PLAYERS):
                self.solver.add(Implies(
                    (self.TRUMP_COLOUR, self.TRUMP_CARD_MAX_VALUE)
                    in self.player_hands[i],
                    self.starting_players[0] == i + 1))
        elif self.first_starting_player:
            self.solver.add(
                self.starting_players[0] == self.first_starting_player)

        for j in range(self.NUMBER_OF_TRICKS):

            starting_player = self.starting_players[j]
            active_colour = self.active_colours[j]
            trick_winner = self.trick_winners[j]
            s = self.solver

            # Only valid player indices may be used.
            s.add(0 < trick_winner)
            s.add(trick_winner <= self.NUMBER_OF_PLAYERS)
            s.add(0 < starting_player)
            s.add(starting_player <= self.NUMBER_OF_PLAYERS)

            # Only valid colour indices may be used.
            s.add(0 <= active_colour)
            s.add(active_colour < self.NUMBER_OF_COLOURS)

            for i in range(self.NUMBER_OF_PLAYERS):

                colour, value = self.cards[j][i][0], self.cards[j][i][1]
                player = i + 1

                # Only valid colour indices may be used.
                s.add(-1 <= colour)
                s.add(colour < self.NUMBER_OF_COLOURS)

                # Only valid card values may be used.
                s.add(0 < value)
                s.add(value <= self.CARD_MAX_VALUE)

                # Only valid trump card values may be used.
                s.add(Implies(colour == self.TRUMP_COLOUR,
                              value <= self.TRUMP_CARD_MAX_VALUE))

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
                                              self.NUMBER_OF_PLAYERS)
                                           if i != k])),
                                  trick_winner == player))

                # Case 2: The player has not played a trump card and no trump
                # card is present in the trick.
                # If the player's card is of the active colour and higher
                # than all other cards of the active colour in the trick,
                # that player has won the trick.
                s.add(Implies(And(colour == active_colour,
                                  And([And(self.cards[j][k][0] !=
                                           self.TRUMP_COLOUR,
                                           Or(self.cards[j][k][0] !=
                                              active_colour,
                                              value > self.cards[j][k][1]))
                                       for k in range(self.NUMBER_OF_PLAYERS)
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
        return 0 <= card[0] < self.NUMBER_OF_COLOURS and \
               0 < card[1] <= self.CARD_MAX_VALUE

    def _card_string(self, card: Card):
        width = self.table_element_widths["colour_name"]
        return (f'({self.COLOUR_NAMES[card[0]]:{width}} '
                f'{card[1]:>{self.table_element_widths["card_value"]}})')

    def check(self, print_time: bool = True) -> None:
        start_time = time.time()
        self.check_result = self.solver.check()
        duration = time.time() - start_time
        if print_time:
            print(f'\nSolving took {int(duration // 60)}m '
                  f'{duration % 60:.1f}s.')
        self.is_solved = True


class CrewGame(CrewGameBase):

    def __init__(self, number_of_players: int = 4, number_of_colours: int = 4,
                 card_max_value: int = 9, use_trump_cards: bool = True,
                 trump_card_max_value: int = 4,
                 cards_distribution: list[list[Card]] = None,
                 first_starting_player: int = None) -> None:

        super().__init__(number_of_players, number_of_colours,
                         card_max_value, use_trump_cards, trump_card_max_value,
                         cards_distribution, first_starting_player)

    # This function assumes that a standard crew card deck with 4*9+4 cards is used for 4 and 5 players and 3*9+3 cards
    # are used for 3 players
    # Additionally we assume that we do not mix relative and absolute task order constraints
    @classmethod
    def crew_game_from_game_state(cls, game_state: CrewGameState):
        number_of_players = len(game_state.hands)
        if number_of_players in [4, 5]:
            game = cls(number_of_players=number_of_players, cards_distribution=game_state.hands,
                       first_starting_player=game_state.active_player)
        elif number_of_players == 3:
            game = cls(number_of_players=number_of_players, number_of_colours=3, trump_card_max_value=3,
                       cards_distribution=game_state.hands, first_starting_player=game_state.active_player)
        else:
            assert False
        # Transform the CrewGameState tasks and task constraints
        ordered_tasks = []
        last_task = None
        for task in game_state.tasks:
            game.add_card_task(task.player, task.card)
            if task.order_constraint > 0:
                ordered_tasks.append(task)
            elif task.order_constraint == -1:
                last_task = task
        if len(ordered_tasks) > 0:
            ordered_tasks.sort(key=lambda task: task.order_constraint)
            if ordered_tasks[0].relative_constraint:
                game.add_task_constraint_relative_order(tuple([task.card for task in ordered_tasks]))
            else:
                game.add_task_constraint_absolute_order(tuple([task.card for task in ordered_tasks]))
        if last_task:
            game.add_task_constraint_absolute_order_last(last_task.card)
        return game

    def add_card_task(self, tasked_player: int, card: Card = None,
                      print_task: bool = True) -> None:
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
        if print_task:
            print(f'Task for {self.table_elements["player_prefix"]}'
                  f'{tasked_player}: {self._card_string(card)}')

    # parameter ordered_task: a tuple of task cards in the order, in which they have to be fulfilled
    # has no influence on the other task cards.
    def add_task_constraint_relative_order(
            self, ordered_tasks: tuple[Card, ...],
            print_task: bool = True) -> None:
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
            if print_task:
                print('Task order constraint (relative): '
                      f'{self._card_string(o_task)} must be completed before '
                      f'{self._card_string(next_task)}.')

    # parameter ordered_task: a tuple of task cards in the order, in which they have to be fulfilled
    # all other tasks have to be fulfilled after all tasks with an absolute order are finished
    def add_task_constraint_absolute_order(
            self, ordered_tasks: tuple[Card, ...],
            print_task: bool = True) -> None:
        assert 1 <= len(ordered_tasks) <= len(self.tasks)
        assert all([self._valid_card(card) for card in ordered_tasks])

        # Absolute order is specified as a set of relative order constraints.
        if len(ordered_tasks) > 1:
            self.add_task_constraint_relative_order(ordered_tasks, False)
        for i, o_task in enumerate(ordered_tasks):
            for u_task in [u_t for u_t in self.task_cards
                           if u_t not in ordered_tasks]:
                self.add_task_constraint_relative_order((o_task, u_task), False)
            if print_task:
                print('Task order constraint (absolute): '
                      f'{self._card_string(o_task)} must be number {i + 1} '
                      f'in the order of all {len(self.tasks)} completed tasks.')

    def add_task_constraint_absolute_order_last(
            self, task: Card, print_task: bool = True) -> None:
        assert self._valid_card(task)

        # Absolute order is specified as a set of relative order constraints.
        for u_task in [u_t for u_t in self.task_cards if u_t != task]:
            self.add_task_constraint_relative_order((u_task, task), False)
        if print_task:
            print('Task order constraint (absolute): '
                  f'{self._card_string(task)} '
                  f'must be the last task to be completed.')

    def add_special_task_no_tricks_value(
            self, forbidden_value: int, print_task: bool = True) -> None:
        assert 0 < forbidden_value <= self.CARD_MAX_VALUE

        # No trick may be won with a card of the given value.
        for j in range(self.NUMBER_OF_TRICKS):
            for i in range(self.NUMBER_OF_PLAYERS):
                self.solver.add(
                    Implies(self.cards[j][i][1] == forbidden_value,
                            self.cards[j][i][0] != self.active_colours[j]))
        if print_task:
            print('Special task: No tricks may be won '
                  f'with cards of value {forbidden_value}.')

    def print_solution(self) -> None:

        if not self.check_result:
            print('The game has not been solved yet.')
            return

        if self.check_result != sat:
            print('No solution exists.')
            return

        m = self.solver.model()
        table_lines = []

        for j in range(self.NUMBER_OF_TRICKS):
            sp = m.evaluate(self.starting_players[j]).as_long()
            ac = m.evaluate(self.active_colours[j]).as_long()
            table_line = [
                f'{j + 1}',
                f'{self.table_elements["player_prefix"]}{sp}',
                self.COLOUR_NAMES[ac]]
            for i in range(self.NUMBER_OF_PLAYERS):
                colour = m.evaluate(self.cards[j][i][0]).as_long()
                value = m.evaluate(self.cards[j][i][1]).as_long()
                start_mark = self.table_elements['trick_start_marker'] \
                    if (self.table_formatting_rules['mark_trick_start']
                        and i + 1 == sp) else ''
                task_mark = self.table_elements['task_completion_marker'] \
                    if (colour, value) in self.task_cards else ''
                tm_width = self.table_element_widths["trick_start_marker"]
                cm_width = self.table_element_widths["task_completion_marker"]
                card_repr = \
                    (f'{start_mark:{tm_width}} '
                     f'{self._card_string((colour, value))} '
                     f'{task_mark:{cm_width}}')
                table_line.append(card_repr)
            w = (f'{self.table_elements["player_prefix"]}'
                 f'{m.evaluate(self.trick_winners[j]).as_long()}')
            table_line.append(w)
            t = self.table_elements['task_completion_marker'] \
                if j in [m.evaluate(x[3]).as_long() for x in self.tasks] \
                else ' ' * self.table_element_widths['task_completion_marker']
            table_line.append(t)
            table_lines.append(table_line)

        headers = \
            [self.table_column_headers['trick_number']] + \
            [self.table_column_headers['starting_player']] + \
            [self.table_column_headers['active_colour']] + \
            [f'{self.table_elements["player_prefix"]}{i}'
             for i in range(1, self.NUMBER_OF_PLAYERS + 1)] + \
            [self.table_column_headers['winning_player']] + \
            [self.table_column_headers['task_completion']]
        widths = \
            [self.table_content_widths['trick_number']] + \
            [self.table_content_widths['starting_player']] + \
            [self.table_content_widths['active_colour']] + \
            [self.table_content_widths['content']] * self.NUMBER_OF_PLAYERS + \
            [self.table_content_widths['winning_player']] + \
            [self.table_content_widths['task_completion']]

        print_table(headers, table_lines, widths, ' | ')


def print_table(headers: list[str], lines: list[list[str]],
                content_widths: list[int], column_separator: str) -> None:
    assert len(headers) == len(content_widths)
    assert all([len(line) == len(headers) for line in lines])

    column_widths = list(map(max, zip(map(len, headers), content_widths)))
    total_width = sum(column_widths, (len(headers) - 1) * len(column_separator))

    print()
    print(column_separator.join([f'{header:^{column_widths[i]}}'
                                 for i, header in enumerate(headers)]))
    print('-' * total_width)
    for line in lines:
        print(column_separator.join([f'{element:^{column_widths[i]}}'
                                     for i, element in enumerate(line)]))
