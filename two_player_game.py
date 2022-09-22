import random

from z3 import *

NUMBER_OF_CARDS = 12
NUMBER_OF_PLAYERS = 2
assert NUMBER_OF_CARDS % NUMBER_OF_PLAYERS == 0
NUMBER_OF_TRICKS = NUMBER_OF_CARDS // NUMBER_OF_PLAYERS


def deal_cards() -> list:
    remaining_cards = list(range(1, NUMBER_OF_CARDS + 1))
    hands = []
    for i in range(NUMBER_OF_PLAYERS):
        hand = random.sample(remaining_cards, NUMBER_OF_TRICKS)
        for card in hand:
            remaining_cards.remove(card)
        hands.append(hand)
    return hands


COLUMN_SEPARATOR = ' | '
TRICK_HEADER = 'Trick'
PLAYER_HEADER = 'P'
WINNER_HEADER = 'Winner'
COLUMN_WIDTH = max(len(str(NUMBER_OF_CARDS)), len(PLAYER_HEADER +
                                                  str(NUMBER_OF_PLAYERS)))
TRICK_COLUMN_WIDTH = max(len(str(NUMBER_OF_TRICKS)), len(TRICK_HEADER))
WINNER_COLUMN_WIDTH = max(len(str(NUMBER_OF_PLAYERS)), len(WINNER_HEADER))
TOTAL_WIDTH = TRICK_COLUMN_WIDTH + WINNER_COLUMN_WIDTH + len(COLUMN_SEPARATOR) \
              + NUMBER_OF_PLAYERS * (COLUMN_WIDTH + len(COLUMN_SEPARATOR))


def print_table_row(index: int, cards_played: list, trick_winner: int) -> None:
    def print_row(i, cs, w):
        print(COLUMN_SEPARATOR.join([f'{i!s:^{TRICK_COLUMN_WIDTH}}'] +
                                    [f'{c!s:>{COLUMN_WIDTH}}' for c in cs] +
                                    [f'{w!s:^{WINNER_COLUMN_WIDTH}}']))

    if index == 1:
        print_row(TRICK_HEADER, [f'{PLAYER_HEADER}{i + 1}' for i in range(
            NUMBER_OF_PLAYERS)], WINNER_HEADER)
        print('-' * TOTAL_WIDTH)
    print_row(index, cards_played, trick_winner)


def main():
    player_hands = deal_cards()
    print(f'Card distribution: {player_hands}')

    cards = [[Int('c_%s_%s' % (i, j)) for i in range(NUMBER_OF_PLAYERS)] for
             j in range(NUMBER_OF_TRICKS)]
    trick_won = [Bool('t_%s' % i) for i in range(NUMBER_OF_TRICKS)]

    s = Solver()

    s.add(Distinct(*[card for trick in cards for card in trick]))

    for j in range(NUMBER_OF_TRICKS):

        for i in range(NUMBER_OF_PLAYERS):
            card = cards[j][i]
            s.add(card > 0)
            s.add(card <= NUMBER_OF_CARDS)
            s.add(Or([card == c for c in player_hands[i]]))

        s.add(Implies(cards[j][0] < cards[j][1], trick_won[j]))
        s.add(Implies(cards[j][0] > cards[j][1], Not(trick_won[j])))

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
