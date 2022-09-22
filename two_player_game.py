import random

from z3 import *

CARD_MAX_VALUE = 16
NUMBER_OF_COLOURS = 1  # Values other than 1 are not supported yet.
NUMBER_OF_CARDS = NUMBER_OF_COLOURS * CARD_MAX_VALUE
NUMBER_OF_PLAYERS = 4
assert NUMBER_OF_CARDS % NUMBER_OF_PLAYERS == 0
NUMBER_OF_TRICKS = NUMBER_OF_CARDS // NUMBER_OF_PLAYERS


def deal_cards() -> list:
    remaining_cards = list(range(1, CARD_MAX_VALUE + 1))
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
PLAYER_PREFIX = 'P'
WINNER_HEADER = 'Winner'
COLUMN_WIDTH = max(len(str(CARD_MAX_VALUE)), len(PLAYER_PREFIX +
                                                 str(NUMBER_OF_PLAYERS)))
TRICK_COLUMN_WIDTH = max(len(str(NUMBER_OF_TRICKS)), len(TRICK_HEADER))
WINNER_COLUMN_WIDTH = max(len(str(NUMBER_OF_PLAYERS) + PLAYER_PREFIX),
                          len(WINNER_HEADER))
TOTAL_WIDTH = TRICK_COLUMN_WIDTH + WINNER_COLUMN_WIDTH + len(COLUMN_SEPARATOR) \
              + NUMBER_OF_PLAYERS * (COLUMN_WIDTH + len(COLUMN_SEPARATOR))


def print_table_row(index: int, cards_played: list, trick_winner: int) -> None:
    def print_row(i, cs, w):
        print(COLUMN_SEPARATOR.join([f'{i!s:^{TRICK_COLUMN_WIDTH}}'] +
                                    [f'{c!s:>{COLUMN_WIDTH}}' for c in cs] +
                                    [f'{w!s:^{WINNER_COLUMN_WIDTH}}']))

    if index == 1:
        print_row(TRICK_HEADER, [f'{PLAYER_PREFIX}{i + 1}' for i in range(
            NUMBER_OF_PLAYERS)], WINNER_HEADER)
        print('-' * TOTAL_WIDTH)
    print_row(index, cards_played, f'{PLAYER_PREFIX}{trick_winner}')


def main():
    player_hands = deal_cards()
    print(f'Card distribution: {player_hands}')

    cards = [[Int('c_%s_%s' % (i, j)) for i in range(NUMBER_OF_PLAYERS)] for
             j in range(NUMBER_OF_TRICKS)]
    trick_won = [Int('t_%s' % i) for i in range(NUMBER_OF_TRICKS)]

    s = Solver()

    # Each card may occur only once.
    s.add(Distinct(*[card for trick in cards for card in trick]))

    for j in range(NUMBER_OF_TRICKS):

        for i in range(NUMBER_OF_PLAYERS):
            card = cards[j][i]

            # All cards must be in the valid range.
            s.add(0 < card)
            s.add(card <= CARD_MAX_VALUE)

            # Players may only play cards that they hold.
            s.add(Or([card == c for c in player_hands[i]]))

            # If a player's card is higher than all other cards in the trick,
            # that player has won the trick.
            s.add(Implies(And([card > cards[j][k] for k in range(
                NUMBER_OF_PLAYERS) if i != k]), trick_won[j] == i + 1))

    if s.check() == sat:

        m = s.model()

        for j in range(NUMBER_OF_TRICKS):
            played = [m.evaluate(cards[j][i]) for i in range(NUMBER_OF_PLAYERS)]
            winner = m.evaluate(trick_won[j])
            print_table_row(j + 1, played, winner)
    else:
        print('unsat')


if __name__ == '__main__':
    main()
