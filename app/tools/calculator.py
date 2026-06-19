import ast
import operator
import re
from decimal import Decimal, DivisionByZero, InvalidOperation

from pydantic import BaseModel

from app.schemas import TextContent, ToolCallResponse, ToolDefinition

_ALLOWED_PATTERN = re.compile(r"^[0-9\s+\-*/().]+$")
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


class CalculatorArguments(BaseModel):
    expression: str


TOOL_DEFINITION = ToolDefinition(
    name="calculate",
    description="Calcula expressões aritméticas simples com +, -, *, / e parênteses.",
    inputSchema={
        "type": "object",
        "properties": {"expression": {"type": "string"}},
        "required": ["expression"],
    },
)


def execute(arguments: dict[str, object]) -> ToolCallResponse:
    parsed = CalculatorArguments.model_validate(arguments)
    result = calculate(parsed.expression)
    return ToolCallResponse(content=[TextContent(text=_format_decimal(result))])


def calculate(expression: str) -> Decimal:
    if not expression.strip():
        raise ValueError("Expressão inválida: informe uma expressão aritmética.")

    if not _ALLOWED_PATTERN.fullmatch(expression):
        raise ValueError("Expressão inválida: use apenas números, espaços, +, -, *, /, parênteses e ponto decimal.")

    try:
        tree = ast.parse(expression, mode="eval")
        return _evaluate_node(tree.body)
    except (SyntaxError, InvalidOperation):
        raise ValueError("Expressão inválida: verifique a sintaxe informada.") from None
    except DivisionByZero:
        raise ValueError("Expressão inválida: divisão por zero não é permitida.") from None


def _evaluate_node(node: ast.AST) -> Decimal:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return Decimal(str(node.value))

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate_node(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value

    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)
        return Decimal(str(_OPERATORS[type(node.op)](left, right)))

    raise ValueError("Expressão inválida: operação não permitida.")


def _format_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal("1")))
    return format(normalized, "f")
