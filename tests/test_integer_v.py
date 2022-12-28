import pytest
from hypothesis import given
from hypothesis import strategies as st

from crew_logic.crew_utils import IntegerV


class UsesIntegerV:
    """Stub class using an integer validator field."""

    def __init__(
        self, min_value: int | None = None, max_value: int | None = None
    ) -> None:
        self.field = IntegerV(min_value=min_value, max_value=max_value)


def set_get(value: int, inst: UsesIntegerV = UsesIntegerV()) -> None:
    inst.field = value
    assert inst.field == value, value


@given(value=st.integers())
def test_set_get(value):
    set_get(value)


# @given(min_value=st.integers())
# def test_min_value(min_value: int) -> None:
#     @given(value=st.integers(max_value=min_value - 1))
#     def test_min_value_error(value: int) -> None:
#         with pytest.raises(ValueError):
#             set_get(value, UsesIntegerV(min_value=min_value))
#
#     test_min_value_error()

# @given(value=st.integers())
# def test_max_lower_than_min():
#     pass
