from z3 import *

NUMBER_OF_CARDS = 8
NUMBER_OF_PLAYERS = 2
NUMBER_OF_TRICKS = NUMBER_OF_CARDS // NUMBER_OF_PLAYERS

# hand_of_player = [Const('a', SetSort(IntSort())), Const('b', SetSort(IntSort()))]
# SetAdd(hand_of_player[0], 1)
# SetAdd(hand_of_player[0], 3)
# SetAdd(hand_of_player[0], 5)
# SetAdd(hand_of_player[0], 6)
#
# SetAdd(hand_of_player[1], 2)
# SetAdd(hand_of_player[1], 4)
# SetAdd(hand_of_player[1], 7)
# SetAdd(hand_of_player[1], 8)
#
# print(hand_of_player[0])

cards_played = [ [ Int( "c_%s_%s" % (i, j)) for i in range(NUMBER_OF_PLAYERS) ] for j in range(NUMBER_OF_TRICKS) ]

print(cards_played)

s = Solver()

print(*[card for trick in cards_played for card in trick])

s.add(Distinct(*[card for trick in cards_played for card in trick]))

p = [ (1,3,5,6), (2,4,7,8)]

for j in range(NUMBER_OF_TRICKS):
    for i in range(NUMBER_OF_PLAYERS):
        s.add(cards_played[j][i] > 0)
        s.add(cards_played[j][i] <= NUMBER_OF_CARDS)
        #s.add(IsMember(cards_played[j][i], hand_of_player[i]))
        s.add(Or([cards_played[j][i] == card for card in p[i]]))




trick_won = [ Bool( "t_%s" % i) for i in range(NUMBER_OF_TRICKS)]

for j in range(NUMBER_OF_TRICKS):
    s.add(Implies(cards_played[j][0] < cards_played[j][1], trick_won[j]))
    s.add(Implies(cards_played[j][0] > cards_played[j][1], Not(trick_won[j])))

if s.check() == sat:
    m = s.model()

    for j in range(NUMBER_OF_TRICKS):
        print(f'Trick {j}:')
        print(f'{m.evaluate(cards_played[j][0])}\t{m.evaluate(cards_played[j][1])}')
        if m.evaluate(trick_won[j]):
            print('Player 1 won')
        else:
            print('Player 0 won')
else:
    print('unsat')
