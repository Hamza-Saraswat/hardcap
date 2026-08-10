"""The calculator the model gets to use, and the safe evaluator behind it.

Error analysis said tool use fixes arithmetic, not grounding -- so this tool exists to take
the multiplication and summation away from the weights entirely. The model does what it is
good at (which rule applies, which threshold governs) and delegates every product and total
here, where the answer is exact by construction.

Evaluation walks a parsed AST and permits only arithmetic on numbers. `eval()` is never
called, so an expression arriving from a model -- or later from a stranger on the internet
using the playground -- cannot reach the filesystem, the network, or the interpreter.
"""

from __future__ import annotations

import ast
import operator
from dataclasses import dataclass

# Long enough to sum a full 20-man roster in one call, which is the single most
# error-prone arithmetic step in the domain and therefore the one that most needs the tool.
MAX_EXPRESSION_LENGTH = 500
MAX_ABS_VALUE = 10**15

_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}

# The tool definition handed to the model, in the shape chat templates expect.
TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "calc",
        "description": (
            "Evaluate an arithmetic expression exactly. Use this for every multiplication, "
            "sum, or difference involving salary figures -- never compute them mentally. "
            "Supports + - * / and parentheses on plain numbers."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "e.g. '6064000 * 1.25' or '59033114 + 50105628'",
                }
            },
            "required": ["expression"],
        },
    },
}


class CalcError(ValueError):
    """The expression was rejected. The message is shown to the model so it can retry."""


@dataclass
class CalcResult:
    expression: str
    value: int | float

    @property
    def rendered(self) -> str:
        """Whole dollars are formatted with commas; rates keep two decimals."""
        if isinstance(self.value, int) or float(self.value).is_integer():
            return f"{int(self.value):,}"
        return f"{self.value:,.2f}"


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise CalcError("only numbers are allowed")
        return node.value
    if isinstance(node, ast.BinOp):
        op = _BINARY.get(type(node.op))
        if op is None:
            raise CalcError(f"unsupported operator: {type(node.op).__name__}")
        left, right = _evaluate(node.left), _evaluate(node.right)
        if op is operator.truediv and right == 0:
            raise CalcError("division by zero")
        return op(left, right)
    if isinstance(node, ast.UnaryOp):
        op = _UNARY.get(type(node.op))
        if op is None:
            raise CalcError(f"unsupported unary operator: {type(node.op).__name__}")
        return op(_evaluate(node.operand))
    raise CalcError(f"unsupported expression element: {type(node).__name__}")


def calc(expression: str) -> CalcResult:
    """Evaluate an arithmetic expression, or raise CalcError explaining why not."""
    cleaned = expression.strip().replace(",", "").replace("$", "")
    if not cleaned:
        raise CalcError("empty expression")
    if len(cleaned) > MAX_EXPRESSION_LENGTH:
        raise CalcError(f"expression longer than {MAX_EXPRESSION_LENGTH} characters")

    try:
        tree = ast.parse(cleaned, mode="eval")
    except SyntaxError as exc:
        raise CalcError(f"could not parse: {exc.msg}") from None

    value = _evaluate(tree)
    if abs(value) > MAX_ABS_VALUE:
        raise CalcError("result out of range")

    # Money lands on whole dollars; keep floats only when a genuine fraction survives.
    if isinstance(value, float) and abs(value - round(value)) < 1e-6:
        value = round(value)
    return CalcResult(expression=cleaned, value=value)


def run_tool(arguments: dict) -> str:
    """Execute a tool call and render the result the way the model will read it back."""
    expression = (arguments or {}).get("expression", "")
    try:
        return calc(expression).rendered
    except CalcError as exc:
        return f"error: {exc}"
