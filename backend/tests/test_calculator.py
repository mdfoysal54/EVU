import pytest
from app.agent.tools.calculator import calculator_tool


@pytest.mark.parametrize(
    ("expression", "expected"),
    [("2 + 3", 5), ("5 * 4", 20), ("2 + 3 * 4", 14),
     ("(2 + 3) * 4", 20), ("10 / 2", 5), ("-5 + 2", -3)],
)
def test_calculator(expression, expected):
    assert calculator_tool._evaluate(expression) == expected


def test_division_by_zero():
    with pytest.raises(ValueError):
        calculator_tool._evaluate("10 / 0")


def test_rejects_code():
    with pytest.raises(ValueError):
        calculator_tool._evaluate("__import__('os')")
