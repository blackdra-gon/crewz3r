from z3 import Bool, BoolRef, ModelRef, Not, Or, Solver

from z3_util import Exactly_one

number_of_vertices: int = 10

edges: list[tuple[int, int]] = [
    (0, 7),
    (0, 8),
    (0, 9),
    (1, 2),
    (1, 3),
    (1, 4),
    (2, 4),
    (2, 5),
    (3, 4),
    (3, 5),
    (3, 6),
    (3, 9),
    (4, 5),
    (5, 6),
    (5, 8),
    (6, 7),
    (6, 9),
    (7, 8),
]

# representing the colour of vertices
# first index: number of vertex
# second index: colour
colors: list[list[BoolRef]] = [
    [Bool(f"c_{i}_{j}") for j in range(4)] for i in range(number_of_vertices)
]

# pp(colors)

s: Solver = Solver()

# s.add(Or([And([f"c_{i}_1" for i in range(4)]) for ]))

# inner clause

# inner_clause: BoolRef = And([f"c_{i}_1" for i in range(4)])

# exactly one color for each vertex
for n in range(number_of_vertices):
    # only_one_color: BoolRef = Or(
    #     [
    #         And([colors[n][i] if i == j else Not(colors[n][i]) for i in range(4)])
    #         for j in range(4)
    #     ]
    # )

    s.add(Exactly_one(colors[n]))

# different colours for each edge

for (x, y) in edges:
    for c in range(4):
        s.add(Or(Not(colors[x][c]), Not(colors[y][c])))

# only_one_color: BoolRef = Or(
#     [
#         And([Not(colors[0][i]) if i == j else colors[0][i] for i in range(4)])
#         for j in range(4)
#     ]
# )
# inner_clause: BoolRef = And(
#     [Not(colors[0][i]) if i == 1 else colors[0][i] for i in range(4)]
# )
# print(only_one_color)
# s.add(only_one_color)
s.check()
m: ModelRef = s.model()
# Printing result
for n in range(number_of_vertices):
    for i in range(4):
        if m.evaluate(colors[n][i]):
            print(f"Vertex {n} has color {i}")
