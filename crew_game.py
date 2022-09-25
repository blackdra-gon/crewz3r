import random
import time

from z3 import *

# Type alias for cards: The first integer represents the color (or suit),
# the second determines the card value.
Card = tuple[int, int]

# Cards of each colour will be created ranging from 1 to this value, inclusive.
CARD_MAX_VALUE = 9

# The number of different colours. Trump cards are not counted.
NUMBER_OF_COLOURS = 4

# The number of players for which to solve the game.
NUMBER_OF_PLAYERS = 4

# Trump cards can entirely be toggled on and off.
USE_TRUMP_CARDS = True

# The player with the highest trump card starts the first trick.
# Disable to allow for more solving options with different start players.
HIGHEST_TRUMP_STARTS_FIRST_TRICK = True

# Constant representing the trump cards' colour.
# Changing this requires to adapt the implementation accordingly.
TRUMP_COLOUR = -1

NUMBER_OF_CARDS = NUMBER_OF_COLOURS * CARD_MAX_VALUE
if USE_TRUMP_CARDS:
    NUMBER_OF_CARDS += NUMBER_OF_PLAYERS
assert NUMBER_OF_CARDS % NUMBER_OF_PLAYERS == 0
NUMBER_OF_TRICKS = NUMBER_OF_CARDS // NUMBER_OF_PLAYERS

# Table formatting parameters.
COLUMN_SEPARATOR = ' | '
PLAYER_PREFIX = 'Player '
START_MARKER = '>'
TASK_MARKER = '*'

# In-column start and task markers can be toggled.
MARK_START = True
MARK_TASK = True

# Table column headers.
COLUMN_HEADERS = ['Trick', 'Starting', 'A'] + \
                 [f'{PLAYER_PREFIX}{i + 1}'
                  for i in range(NUMBER_OF_PLAYERS)] + \
                 ['Winner', 'T']

# Text representation of colours.
COLOUR_NAMES = ('R', 'G', 'B', 'Y', 'X')  # Last name reserved for trump cards.

assert NUMBER_OF_COLOURS < len(COLOUR_NAMES)
COLOUR_NAME_WIDTH = max(map(len, COLOUR_NAMES[:NUMBER_OF_COLOURS]))
CARD_VALUE_WIDTH = len(str(CARD_MAX_VALUE))
START_MARKER_WIDTH = len(START_MARKER) if MARK_START else 0
TASK_MARKER_WIDTH = len(TASK_MARKER) if MARK_TASK else 0

CONTENT_WIDTHS = [len(str(NUMBER_OF_TRICKS))] + \
                 [len(PLAYER_PREFIX + str(NUMBER_OF_PLAYERS))] + \
                 [COLOUR_NAME_WIDTH] + \
                 [(START_MARKER_WIDTH + 1 if MARK_START else 0) +
                  COLOUR_NAME_WIDTH + 1 + CARD_VALUE_WIDTH +
                  (1 + TASK_MARKER_WIDTH if MARK_TASK else 0)] \
                 * NUMBER_OF_PLAYERS + \
                 [len(PLAYER_PREFIX + str(NUMBER_OF_PLAYERS))] + \
                 [len(TASK_MARKER)]


def deal_cards(print_distribution: bool = True) -> list[list[Card]]:
    remaining_cards = [(color, value) for color in range(NUMBER_OF_COLOURS)
                       for value in range(1, CARD_MAX_VALUE + 1)] + \
                      [(TRUMP_COLOUR, value)
                       for value in range(1, NUMBER_OF_PLAYERS + 1)
                       if USE_TRUMP_CARDS]
    hands = []
    for i in range(NUMBER_OF_PLAYERS):
        hand = sorted(random.sample(remaining_cards, NUMBER_OF_TRICKS))
        for card in hand:
            remaining_cards.remove(card)
        hands.append(hand)

    if print_distribution:
        print('\nCard distribution:')
        for i, cs in enumerate(hands):
            print(f'{PLAYER_PREFIX}{i + 1}: ', end='')
            print(', '.join([f'({COLOUR_NAMES[c[0]]:{COLOUR_NAME_WIDTH}} '
                             f'{c[1]:>{CARD_VALUE_WIDTH}})' for c in cs]))
    return hands


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


def main():
    player_hands = deal_cards()

    # A card is represented by two integers.
    # The first represents the colour, the second the card value.
    cards = [[IntVector('card_%s_%s' % (j, i), 2)
              for i in range(1, NUMBER_OF_PLAYERS + 1)]
             for j in range(1, NUMBER_OF_TRICKS + 1)]

    # Lists of integers store the starting player, active colour and winner
    # for each trick.
    starting_players = [Int('s_%s' % i) for i in range(1, NUMBER_OF_TRICKS + 1)]
    active_colours = [Int('a_%s' % i) for i in range(1, NUMBER_OF_TRICKS + 1)]
    trick_winners = [Int('w_%s' % i) for i in range(1, NUMBER_OF_TRICKS + 1)]

    s = Solver()

    # Each card may occur only once.
    s.add(Distinct(*[card[0] * CARD_MAX_VALUE + card[1]
                     for trick in cards for card in trick]))

    # The player with the highest trump card starts the first trick.
    if USE_TRUMP_CARDS and HIGHEST_TRUMP_STARTS_FIRST_TRICK:
        for i in range(NUMBER_OF_PLAYERS):
            s.add(Implies((TRUMP_COLOUR, NUMBER_OF_PLAYERS) in player_hands[i],
                          starting_players[0] == i + 1))

    for j in range(NUMBER_OF_TRICKS):

        starting_player = starting_players[j]
        active_colour = active_colours[j]
        trick_winner = trick_winners[j]

        # Only valid player indices may be used.
        s.add(0 < trick_winner)
        s.add(trick_winner <= NUMBER_OF_PLAYERS)
        s.add(0 < starting_player)
        s.add(starting_player <= NUMBER_OF_PLAYERS)

        # Only valid colour indices may be used.
        s.add(0 <= active_colour)
        s.add(active_colour < NUMBER_OF_COLOURS)

        for i in range(NUMBER_OF_PLAYERS):

            colour, value = cards[j][i][0], cards[j][i][1]
            player = i + 1

            # Only valid colour indices may be used.
            s.add(-1 <= colour)
            s.add(colour < NUMBER_OF_COLOURS)

            # Only valid card values may be used.
            s.add(0 < value)
            s.add(value <= CARD_MAX_VALUE)

            # Trump cards are limited in number to one per player.
            s.add(Implies(colour == TRUMP_COLOUR,
                          value <= NUMBER_OF_PLAYERS))

            # Players may only play cards that they hold.
            s.add(Or([And(colour == c[0], value == c[1])
                      for c in player_hands[i]]))

            # If a player wins a trick, that player is the starting player in
            # the next trick.
            if j + 1 != NUMBER_OF_TRICKS:
                s.add(Implies(trick_winner == player,
                              starting_players[j + 1] == player))

            # The colour played by the starting player is the active colour.
            s.add(Implies(starting_player == player,
                          active_colour == colour))

            # Case 1: The player has played a trump card.
            # If the player's card is the highest trump card in the trick,
            # that player has won the trick.
            if USE_TRUMP_CARDS:
                s.add(Implies(And(colour == TRUMP_COLOUR,
                                  And([Or(cards[j][k][0] != TRUMP_COLOUR,
                                          value > cards[j][k][1])
                                       for k in range(NUMBER_OF_PLAYERS)
                                       if i != k])),
                              trick_winner == player))

            # Case 2: The player has not played a trump card and no trump
            # card is present in the trick.
            # If the player's card is of the active colour and higher than all
            # other cards of the active colour in the trick, that player has
            # won the trick.
            s.add(Implies(And(colour == active_colour,
                              And([And(cards[j][k][0] != TRUMP_COLOUR,
                                       Or(cards[j][k][0] != active_colour,
                                          value > cards[j][k][1]))
                                   for k in range(NUMBER_OF_PLAYERS)
                                   if i != k])),
                          trick_winner == player))

            # If a player holds a card of the active colour, that player may
            # only play a card of that colour.
            s.add(Implies(Or([cards[m][i][0] == active_colour
                              for m in range(j + 1, NUMBER_OF_TRICKS)]),
                          colour == active_colour))

    task_cards: list[Card] = []
    tasks: list[IntVector] = []

    def valid_card(card: Card) -> bool:
        return 0 <= card[0] < NUMBER_OF_COLOURS and \
               0 < card[1] <= CARD_MAX_VALUE

    def add_card_task(tasked_player: int, card: Card = None,
                      print_task: bool = True) -> None:
        if card:
            assert valid_card(card)
            assert card not in tasks
        else:
            card = random.choice([c for hand in player_hands for c in hand
                                  if c not in task_cards
                                  and c[0] != TRUMP_COLOUR])
        task_cards.append(card)

        # A task is represented by four integers:
        # - The first two represent the card color and value,
        # - the third represents the tasked player,
        # - the fourth stores the trick in which the task was completed
        new_task = IntVector('task_%s' % str(len(tasks) + 1), 4)
        tasks.append(new_task)
        s.add(new_task[0] == card[0])
        s.add(new_task[1] == card[1])
        s.add(new_task[2] == tasked_player)
        s.add(0 < new_task[3])
        s.add(new_task[3] <= NUMBER_OF_TRICKS)

        # If a trick contains the task card, that trick must be won by the
        # tasked player. The task is then completed.
        for j in range(NUMBER_OF_TRICKS):
            s.add(Implies(Or([And(card[0] == c[0], card[1] == c[1])
                              for c in cards[j]]),
                          And(trick_winners[j] == tasked_player,
                              new_task[3] == j)))
        if print_task:
            print(f'Task for {PLAYER_PREFIX}{tasked_player}: ('
                  f'{COLOUR_NAMES[card[0]]:{COLOUR_NAME_WIDTH}} '
                  f'{card[1]:>{CARD_VALUE_WIDTH}})')

    def add_task_constraint_relative_order(ordered_tasks: tuple[Card, ...],
                                           print_task: bool = True) -> None:
        assert 1 < len(ordered_tasks) <= len(tasks)
        assert all([valid_card(card) for card in ordered_tasks])

        # If a trick contains one of the order-constrained task cards, the
        # subsequent order-constrained task card must be played in a later
        # trick.
        for i, o_task in enumerate(ordered_tasks[:-1]):
            next_task = ordered_tasks[i + 1]
            for j in range(NUMBER_OF_TRICKS):
                s.add(Implies(Or([And(o_task[0] == c[0], o_task[1] == c[1])
                                  for c in cards[j]]),
                              Or([And(next_task[0] == c[0],
                                      next_task[1] == c[1])
                                  for k in range(j + 1,
                                                 NUMBER_OF_TRICKS + i -
                                                 len(ordered_tasks))
                                  for c in cards[k]])))
            if print_task:
                print('Task order constraint (relative): ('
                      f'{COLOUR_NAMES[o_task[0]]:{COLOUR_NAME_WIDTH}} '
                      f'{o_task[1]:>{CARD_VALUE_WIDTH}}) '
                      'must be completed before ('
                      f'{COLOUR_NAMES[next_task[0]]:{COLOUR_NAME_WIDTH}} '
                      f'{next_task[1]:>{CARD_VALUE_WIDTH}}).')

    def add_task_constraint_absolute_order(ordered_tasks: tuple[Card, ...],
                                           print_task: bool = True) -> None:
        assert 1 <= len(ordered_tasks) <= len(tasks)
        assert all([valid_card(card) for card in ordered_tasks])

        # Absolute order is specified as a set of relative order constraints.
        if len(ordered_tasks) > 1:
            add_task_constraint_relative_order(ordered_tasks, False)
        for i, o_task in enumerate(ordered_tasks):
            for u_task in [u_t for u_t in task_cards
                           if u_t not in ordered_tasks]:
                add_task_constraint_relative_order((o_task, u_task), False)
            if print_task:
                print('Task order constraint (absolute): ('
                      f'{COLOUR_NAMES[o_task[0]]:{COLOUR_NAME_WIDTH}} '
                      f'{o_task[1]:>{CARD_VALUE_WIDTH}}) '
                      f'must be number {i + 1} in the order of all '
                      f'{len(tasks)} completed tasks.')

    def add_special_task_no_tricks_value(
            forbidden_value: int, print_task: bool = True) -> None:
        assert 0 < forbidden_value <= CARD_MAX_VALUE

        # No trick may be won with a card of the given value.
        for j in range(NUMBER_OF_TRICKS):
            for i in range(NUMBER_OF_PLAYERS):
                s.add(Implies(cards[j][i][1] == forbidden_value,
                              cards[j][i][0] != active_colours[j]))
        if print_task:
            print('Special task: No tricks may be won '
                  f'with cards of value {forbidden_value}.')

    # Add tasks.
    for i in sorted(random.sample(range(1, NUMBER_OF_PLAYERS + 1), 3)):
        add_card_task(i)
    add_task_constraint_relative_order(random.sample(task_cards, 2))
    add_task_constraint_absolute_order(random.sample(task_cards, 1))
    add_special_task_no_tricks_value(CARD_MAX_VALUE)

    def timing_info(start_time):
        duration = time.time() - start_time
        print(f'\nSolving took {int(duration // 60)}m {duration % 60:.1f}s.')

    start_check = time.time()

    if s.check() == sat:

        timing_info(start_check)

        m = s.model()

        table_lines = []
        for j in range(NUMBER_OF_TRICKS):
            sp = m.evaluate(starting_players[j]).as_long()
            ac = m.evaluate(active_colours[j]).as_long()
            table_line = [f'{j + 1}', f'{PLAYER_PREFIX}{sp}', COLOUR_NAMES[ac]]
            for i in range(NUMBER_OF_PLAYERS):
                colour = m.evaluate(cards[j][i][0]).as_long()
                value = m.evaluate(cards[j][i][1]).as_long()
                start_mark = START_MARKER if MARK_START and i + 1 == s else ''
                task_mark = TASK_MARKER if (colour, value) in task_cards else ''
                card_repr = (f'{start_mark:{START_MARKER_WIDTH}} '
                             f'{COLOUR_NAMES[colour]:{COLOUR_NAME_WIDTH}} '
                             f'{value:>{CARD_VALUE_WIDTH}} '
                             f'{task_mark:{TASK_MARKER_WIDTH}}')
                table_line.append(card_repr)
            w = f'{PLAYER_PREFIX}{m.evaluate(trick_winners[j]).as_long()}'
            table_line.append(w)
            t = TASK_MARKER \
                if j in [m.evaluate(x[3]).as_long() for x in tasks] \
                else ' ' * len(TASK_MARKER)
            table_line.append(t)
            table_lines.append(table_line)
        print_table(COLUMN_HEADERS, table_lines, CONTENT_WIDTHS, ' | ')

    else:
        timing_info(start_check)
        print('No solution exists.')


if __name__ == '__main__':
    main()
