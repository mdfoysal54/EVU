import ast
import operator


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluate(node):
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Only numbers are allowed.")

    if isinstance(node, ast.UnaryOp):
        operator_fn = _ALLOWED_OPERATORS.get(type(node.op))

        if operator_fn is None:
            raise ValueError("Unsupported operator.")

        return operator_fn(_evaluate(node.operand))

    if isinstance(node, ast.BinOp):
        operator_fn = _ALLOWED_OPERATORS.get(type(node.op))

        if operator_fn is None:
            raise ValueError("Unsupported operator.")

        return operator_fn(
            _evaluate(node.left),
            _evaluate(node.right),
        )

    raise ValueError("Unsupported expression.")


def safe_calculate(expression: str):
    tree = ast.parse(expression, mode="eval")

    return _evaluate(tree)


def test_addition():
    assert safe_calculate("2 + 3") == 5


def test_multiplication():
    assert safe_calculate("5 * 4") == 20


def test_operator_precedence():
    assert safe_calculate("2 + 3 * 4") == 14


def test_parentheses():
    assert safe_calculate("(2 + 3) * 4") == 20


def test_division():
    assert safe_calculate("10 / 2") == 5


def test_negative_number():
    assert safe_calculate("-5 + 2") == -3