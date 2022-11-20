from typing import TypeAlias

# Type alias for cards: The first integer represents the color (or suit),
# the second determines the card value.
Card: TypeAlias = tuple[int, int]

Hand: TypeAlias = tuple[Card, ...]

CardDistribution: TypeAlias = tuple[Hand, ...]

# Players are represented by integers, starting with 1.
Player: TypeAlias = int

# Colours are represented by integers, starting with 1.
# Trump cards are represented by the integer -1.
Colour: TypeAlias = int
