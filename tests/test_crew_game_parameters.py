import pytest
from hypothesis import given
from hypothesis import strategies as st

from crew_logic.crew_utils import CrewGameParameters

player_numbers = st.integers(min_value=2)
colour_numbers = st.integers(min_value=1)
card_values = st.integers(min_value=1)
trump_card_values = st.integers(min_value=0)


@given(
    number_of_players=st.integers(max_value=1),
    number_of_colours=colour_numbers,
    max_card_value=card_values,
    max_trump_value=trump_card_values,
)
def test_number_of_players_minimum(
    number_of_players: int,
    number_of_colours: int,
    max_card_value: int,
    max_trump_value: int,
) -> None:
    with pytest.raises(ValueError):
        CrewGameParameters(
            number_of_players, number_of_colours, max_card_value, max_trump_value
        )


@given(
    number_of_players=player_numbers,
    number_of_colours=st.integers(max_value=0),
    max_card_value=card_values,
    max_trump_value=trump_card_values,
)
def test_number_of_colours_minimum(
    number_of_players: int,
    number_of_colours: int,
    max_card_value: int,
    max_trump_value: int,
) -> None:
    with pytest.raises(ValueError):
        CrewGameParameters(
            number_of_players, number_of_colours, max_card_value, max_trump_value
        )


@given(
    number_of_players=player_numbers,
    number_of_colours=colour_numbers,
    max_card_value=st.integers(max_value=0),
    max_trump_value=trump_card_values,
)
def test_max_card_value_minimum(
    number_of_players: int,
    number_of_colours: int,
    max_card_value: int,
    max_trump_value: int,
) -> None:
    with pytest.raises(ValueError):
        CrewGameParameters(
            number_of_players, number_of_colours, max_card_value, max_trump_value
        )


@given(
    number_of_players=player_numbers,
    number_of_colours=colour_numbers,
    max_card_value=card_values,
    max_trump_value=st.integers(max_value=-1),
)
def test_max_trump_card_value_minimum(
    number_of_players: int,
    number_of_colours: int,
    max_card_value: int,
    max_trump_value: int,
) -> None:
    with pytest.raises(ValueError):
        CrewGameParameters(
            number_of_players, number_of_colours, max_card_value, max_trump_value
        )
