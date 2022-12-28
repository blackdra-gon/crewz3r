from typing import Any

from hypothesis import given
from hypothesis import strategies as st

from crew_logic.crew_utils import Validator


class NoneV(Validator):
    """Concrete subclass of Validator that doesn't do any actual validation."""

    def validate(self, value: Any) -> None:
        pass


class UsesValidator:
    """Stub class using a validator field."""

    field = NoneV()


@given(value=st.integers())
def test_set_get(value: Any) -> None:
    inst = UsesValidator()
    inst.field = value
    assert inst.field == value, value
