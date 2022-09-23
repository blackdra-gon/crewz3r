import random

from z3 import *

CARD_MAX_VALUE = 9
NUMBER_OF_COLOURS = 4
NUMBER_OF_PLAYERS = 4
NUMBER_OF_CARDS = NUMBER_OF_COLOURS * CARD_MAX_VALUE
assert NUMBER_OF_CARDS % NUMBER_OF_PLAYERS == 0
NUMBER_OF_TRICKS = NUMBER_OF_CARDS // NUMBER_OF_PLAYERS


def deal_cards(print_distribution: bool = True) -> list[list[tuple[int, int]]]:
    remaining_cards = [(color, value) for color in range(NUMBER_OF_COLOURS)
                       for value in range(1, CARD_MAX_VALUE + 1)]
    hands = []
    for i in range(NUMBER_OF_PLAYERS):
        hand = random.sample(remaining_cards, NUMBER_OF_TRICKS)
        for card in hand:
            remaining_cards.remove(card)
        hand.sort()
        hands.append(hand)

    if print_distribution:
        print('\nCard distribution:')
        for i, cs in enumerate(hands):
            print(f'{PLAYER_PREFIX}{i + 1}: ', end='')
            print(', '.join([f'({COLOUR_NAMES[c[0]]:{COLOUR_NAME_WIDTH}} ' +
                             f'{c[1]:>{CARD_VALUE_WIDTH}})' for c in cs]))
    return hands


COLUMN_SEPARATOR = ' | '
PLAYER_PREFIX = 'P'

COLUMN_HEADERS = ['Trick', '*', 'A'] + \
                 [f'{PLAYER_PREFIX}{i + 1}'
                  for i in range(NUMBER_OF_PLAYERS)] + \
                 ['Winner']

COLOUR_NAMES = ('R', 'G', 'B', 'Y')
assert NUMBER_OF_COLOURS <= len(COLOUR_NAMES)
COLOUR_NAME_WIDTH = max(map(len, COLOUR_NAMES[:NUMBER_OF_COLOURS]))
CARD_VALUE_WIDTH = len(str(CARD_MAX_VALUE))

CONTENT_WIDTHS = [len(str(NUMBER_OF_TRICKS)),
                  len(PLAYER_PREFIX + str(NUMBER_OF_PLAYERS)),
                  COLOUR_NAME_WIDTH] + \
                 [COLOUR_NAME_WIDTH + 1 + CARD_VALUE_WIDTH] * \
                 NUMBER_OF_PLAYERS + \
                 [len(PLAYER_PREFIX + str(NUMBER_OF_PLAYERS))]


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

    for j in range(NUMBER_OF_TRICKS):

        # Only valid player indices may be used.
        s.add(0 < trick_winners[j])
        s.add(trick_winners[j] <= NUMBER_OF_PLAYERS)
        s.add(0 < starting_players[j])
        s.add(starting_players[j] <= NUMBER_OF_PLAYERS)

        # Only valid colour indices may be used.
        s.add(0 <= active_colours[j])
        s.add(active_colours[j] < NUMBER_OF_COLOURS)

        for i in range(NUMBER_OF_PLAYERS):

            card = cards[j][i]
            player = i + 1

            # Only valid colour indices may be used.
            s.add(0 <= card[0])
            s.add(card[0] < NUMBER_OF_COLOURS)

            # Only valid card values may be used.
            s.add(0 < card[1])
            s.add(card[1] <= CARD_MAX_VALUE)

            # Players may only play cards that they hold.
            s.add(Or([And(card[0] == c[0], card[1] == c[1])
                      for c in player_hands[i]]))

            # If a player wins a trick, that player is the starting player in
            # the next trick.
            if j + 1 != NUMBER_OF_TRICKS:
                s.add(Implies(trick_winners[j] == player,
                              starting_players[j + 1] == player))

            # The colour played by the starting player is the active colour.
            s.add(Implies(starting_players[j] == player,
                          active_colours[j] == card[0]))

            # If a player's card is of the active colour and higher than all
            # other cards of the active colour in the trick, that player has
            # won the trick.
            s.add(Implies(And(card[0] == active_colours[j],
                              And([Or(cards[j][k][0] != active_colours[j],
                                      card[1] > cards[j][k][1])
                                   for k in range(NUMBER_OF_PLAYERS)
                                   if i != k])),
                          trick_winners[j] == player))

            # If a player holds a card of the active colour, that player may
            # only play a card of that colour.
            s.add(Implies(Or([cards[m][i][0] == active_colours[j]
                              for m in range(j + 1, NUMBER_OF_TRICKS)]),
                          card[0] == active_colours[j]))

    task_cards = []

    def add_card_task(tasked_player: int, card: tuple[int, int] = None,
                      print_task: bool = True) -> None:
        if card:
            assert 0 <= card[0] < NUMBER_OF_COLOURS
            assert 0 < card[1] <= CARD_MAX_VALUE
            assert card not in task_cards
        else:
            card = random.choice([c for hand in player_hands for c in hand
                                  if c not in task_cards])
        task_cards.append(card)

        # If a trick contains the task card, that trick must be won by the
        # tasked player.
        for i in range(NUMBER_OF_TRICKS):
            s.add(Implies(Or([And(card[0] == c[0], card[1] == c[1])
                              for c in cards[i]]),
                          trick_winners[i] == tasked_player))

        if print_task:
            print(f'Task for {PLAYER_PREFIX}{tasked_player}: ' +
                  f'{COLOUR_NAMES[card[0]]:{COLOUR_NAME_WIDTH}} ' +
                  f'{card[1]:>{CARD_VALUE_WIDTH}}')

    for i in range(1, NUMBER_OF_PLAYERS + 1):
        add_card_task(i)

    if s.check() == sat:

        m = s.model()

        table_lines = []
        for j in range(NUMBER_OF_TRICKS):
            s = f'{PLAYER_PREFIX}{m.evaluate(starting_players[j]).as_long()}'
            c = COLOUR_NAMES[m.evaluate(active_colours[j]).as_long()]
            table_line = [f'{j + 1}', s, c]
            for i in range(NUMBER_OF_PLAYERS):
                colour = COLOUR_NAMES[m.evaluate(cards[j][i][0]).as_long()]
                value = m.evaluate(cards[j][i][1]).as_long()
                r = f'{colour:{COLOUR_NAME_WIDTH}} {value:>{CARD_VALUE_WIDTH}}'
                table_line.append(r)
            w = f'{PLAYER_PREFIX}{m.evaluate(trick_winners[j]).as_long()}'
            table_line.append(w)
            table_lines.append(table_line)
        print_table(COLUMN_HEADERS, table_lines, CONTENT_WIDTHS, ' | ')

    else:
        print('unsat')


if __name__ == '__main__':
    main()
