from z3 import *

NUMBER_OF_CARDS = 12
NUMBER_OF_PLAYERS = 2
assert NUMBER_OF_CARDS % NUMBER_OF_PLAYERS == 0
NUMBER_OF_TRICKS = NUMBER_OF_CARDS // NUMBER_OF_PLAYERS

PLAYER_HANDS = ((1, 3, 5, 6, 9, 10), (2, 4, 7, 8, 11, 12))


def print_table_row(index: int, cards_played: list, winner: int):
    column_separator = '  |  '

    def print_row(index, cards_played, winner):
        print(column_separator.join([f'{index!s:^5}'] +
                                    [f'{card!s:>2}' for card in cards_played] +
                                    [f'{winner!s:^6}']))

    if index == 1:
        print_row('Trick', [f'P{i + 1}' for i in range(NUMBER_OF_PLAYERS)],
                  'Winner')
        print('-' * (16 + NUMBER_OF_PLAYERS * (2 + len(column_separator))))
    print_row(index, cards_played, winner)


cards = [[Int("c_%s_%s" % (i, j)) for i in range(NUMBER_OF_PLAYERS)] for
         j in range(NUMBER_OF_TRICKS)]
trick_won = [Bool("t_%s" % i) for i in range(NUMBER_OF_TRICKS)]

s = Solver()

s.add(Distinct(*[card for trick in cards for card in trick]))

for j in range(NUMBER_OF_TRICKS):

    for i in range(NUMBER_OF_PLAYERS):
        card = cards[j][i]
        s.add(card > 0)
        s.add(card <= NUMBER_OF_CARDS)
        s.add(Or([card == c for c in PLAYER_HANDS[i]]))

    s.add(Implies(cards[j][0] < cards[j][1], trick_won[j]))
    s.add(Implies(cards[j][0] > cards[j][1], Not(trick_won[j])))

if s.check() == sat:

    m = s.model()

    for j in range(NUMBER_OF_TRICKS):
        played = [m.evaluate(cards[j][i]) for i in range(NUMBER_OF_PLAYERS)]
        trick_winner = m.evaluate(trick_won[j])
        print_table_row(j + 1, played, trick_winner)
else:
    print('unsat')
