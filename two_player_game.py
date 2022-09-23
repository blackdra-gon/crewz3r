import random

from z3 import *

CARD_MAX_VALUE = 8
NUMBER_OF_COLOURS = 4
NUMBER_OF_PLAYERS = 4
NUMBER_OF_CARDS = NUMBER_OF_COLOURS * CARD_MAX_VALUE
assert NUMBER_OF_CARDS % NUMBER_OF_PLAYERS == 0
NUMBER_OF_TRICKS = NUMBER_OF_CARDS // NUMBER_OF_PLAYERS


def deal_cards() -> list:
    remaining_cards = [(color, value) for color in range(NUMBER_OF_COLOURS)
                       for value in range(1, CARD_MAX_VALUE + 1)]
    hands = []
    for i in range(NUMBER_OF_PLAYERS):
        hand = random.sample(remaining_cards, NUMBER_OF_TRICKS)
        for card in hand:
            remaining_cards.remove(card)
        hand.sort()
        hands.append(hand)
    return hands


COLUMN_SEPARATOR = ' | '
TRICK_HEADER = 'Trick'
STARTING_HEADER = '*'
ACTIVE_HEADER = 'A'
PLAYER_PREFIX = 'P'
WINNER_HEADER = 'Winner'
COLOUR_NAMES = ('R', 'G', 'B', 'Y', '')  # Empty string is used for headers.
assert NUMBER_OF_COLOURS < len(COLOUR_NAMES)
COLOUR_NAME_WIDTH = max(map(len, COLOUR_NAMES[:NUMBER_OF_COLOURS]))
CARD_VALUE_WIDTH = len(str(CARD_MAX_VALUE))
COLUMN_WIDTH = max(COLOUR_NAME_WIDTH + 1 + CARD_VALUE_WIDTH,
                   len(PLAYER_PREFIX + str(NUMBER_OF_PLAYERS)))
TRICK_COLUMN_WIDTH = max(len(str(NUMBER_OF_TRICKS)), len(TRICK_HEADER))
STARTING_COLUMN_WIDTH = max(len(str(NUMBER_OF_PLAYERS) + PLAYER_PREFIX),
                            len(STARTING_HEADER))
ACTIVE_COLUMN_WIDTH = max(len(ACTIVE_HEADER), COLOUR_NAME_WIDTH)
WINNER_COLUMN_WIDTH = max(len(str(NUMBER_OF_PLAYERS) + PLAYER_PREFIX),
                          len(WINNER_HEADER))
TOTAL_WIDTH = TRICK_COLUMN_WIDTH + STARTING_COLUMN_WIDTH + ACTIVE_COLUMN_WIDTH \
              + NUMBER_OF_PLAYERS * (COLUMN_WIDTH + len(COLUMN_SEPARATOR)) \
              + WINNER_COLUMN_WIDTH + (3 * len(COLUMN_SEPARATOR))


def print_table_row(index: int, starting_player: int, active_colour: int,
                    cards_played: list, trick_winner: int) -> None:
    def card_repr(cards):
        cr = []
        for card in cards:
            r = f'{COLOUR_NAMES[card[0]]:{COLOUR_NAME_WIDTH}} ' + \
                f'{card[1]:>{CARD_VALUE_WIDTH}}'
            cr.append(f'{r:^{COLUMN_WIDTH}}')
        return cr

    def print_row(i, s, a, cr, w):
        ir = [f'{i:^{TRICK_COLUMN_WIDTH}}']
        sr = [f'{s:^{STARTING_COLUMN_WIDTH}}']
        ar = [f'{a:^{ACTIVE_COLUMN_WIDTH}}']
        wr = [f'{w:^{WINNER_COLUMN_WIDTH}}']
        print(COLUMN_SEPARATOR.join(ir + sr + ar + cr + wr))

    # Print table header before first row.
    if index == 1:
        player_headers = [f'{f"{PLAYER_PREFIX}{i + 1}":{COLUMN_WIDTH}}'
                          for i in range(NUMBER_OF_PLAYERS)]
        print()
        print_row(TRICK_HEADER, STARTING_HEADER, ACTIVE_HEADER,
                  player_headers, WINNER_HEADER)
        print('-' * TOTAL_WIDTH)

    # Print regular rows.
    print_row(index, f'{PLAYER_PREFIX}{starting_player}',
              COLOUR_NAMES[active_colour], card_repr(cards_played),
              f'{PLAYER_PREFIX}{trick_winner}')


def print_card_distribution(hands):
    print('\nCard distribution:')
    for i, cs in enumerate(hands):
        print(f'{PLAYER_PREFIX}{i + 1}: ', end='')
        print(', '.join([f'({COLOUR_NAMES[c[0]]:{COLOUR_NAME_WIDTH}} ' +
                         f'{c[1]:>{CARD_VALUE_WIDTH}})' for c in cs]))


def main():
    player_hands = deal_cards()
    print_card_distribution(player_hands)

    # A card is represented by two integers.
    # The first represents the colour, the second the card value.
    cards = [[IntVector('c_%s_%s' % (i, j), 2)
              for i in range(NUMBER_OF_PLAYERS)]
             for j in range(NUMBER_OF_TRICKS)]

    # Lists of integers store the starting player, active colour and winner
    # for each trick.
    starting_players = [Int('s_%s' % i) for i in range(NUMBER_OF_TRICKS)]
    active_colours = [Int('a_%s' % i) for i in range(NUMBER_OF_TRICKS)]
    trick_winners = [Int('w_%s' % i) for i in range(NUMBER_OF_TRICKS)]

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

            # The colour played by the starting player is the active colour
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

            # If the player holds a card of the active colour, the player may
            # only play a card of that colour.
            s.add(Implies(Or([cards[m][i][0] == active_colours[j]
                              for m in range(j + 1, NUMBER_OF_TRICKS)]),
                          card[0] == active_colours[j]))

    if s.check() == sat:

        m = s.model()

        for j in range(NUMBER_OF_TRICKS):
            starting = m.evaluate(starting_players[j]).as_long()
            active = m.evaluate(active_colours[j]).as_long()
            played = [(m.evaluate(cards[j][i][0]).as_long(),
                       m.evaluate(cards[j][i][1]).as_long())
                      for i in range(NUMBER_OF_PLAYERS)]
            winner = m.evaluate(trick_winners[j]).as_long()
            print_table_row(j + 1, starting, active, played, winner)
    else:
        print('unsat')


if __name__ == '__main__':
    main()
