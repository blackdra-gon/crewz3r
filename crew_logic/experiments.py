from z3 import And, ArithRef, BoolRef, Int, pp

# Create list [1, ..., 5]
print([x + 1 for x in range(5)])

# Create two lists containing 5 integer variables
X: list[ArithRef] = [Int(f"x{i}") for i in range(5)]
Y: list[ArithRef] = [Int(f"y{i}") for i in range(5)]
print(X)

# Create a list containing X[i]+Y[i]
X_plus_Y: list[ArithRef] = [X[i] + Y[i] for i in range(5)]
print(X_plus_Y)

# Create a list containing X[i] > Y[i]
X_gt_Y: list[BoolRef] = [X[i] > Y[i] for i in range(5)]
print(X_gt_Y)

print(And(X_gt_Y))

# Create a 3x3 "matrix" (list of lists) of integer variables
X3: list[list[ArithRef]] = [
    [Int(f"x_{i + 1}_{j + 1}") for j in range(3)] for i in range(3)
]
pp(X3)
