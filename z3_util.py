from z3 import *

# returns a Z3 formular which evaluates to true if exactly one of given bools is true
def Exactly_one(list_of_bools):
    return Or([And([list_of_bools[n] if n == m else Not(list_of_bools[n]) for n in range(len(list_of_bools))]) for m in range(len(list_of_bools))])

