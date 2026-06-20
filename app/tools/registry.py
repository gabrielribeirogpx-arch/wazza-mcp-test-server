from collections.abc import Callable

from pydantic import ValidationError

from app.schemas import ToolCallResponse, ToolDefinition
from app.tools import business_hours, calculator, calendar, echo

ToolExecutor = Callable[[dict[str, object]], ToolCallResponse]


class ToolExecutionError(Exception):
    """Raised when a registered tool cannot be executed."""


_TOOLS: dict[str, tuple[ToolDefinition, ToolExecutor]] = {
    echo.TOOL_DEFINITION.name: (echo.TOOL_DEFINITION, echo.execute),
    business_hours.TOOL_DEFINITION.name: (business_hours.TOOL_DEFINITION, business_hours.execute),
    calculator.TOOL_DEFINITION.name: (calculator.TOOL_DEFINITION, calculator.execute),
    calendar.LIST_EVENTS_TOOL_DEFINITION.name: (calendar.LIST_EVENTS_TOOL_DEFINITION, calendar.list_events),
    calendar.CREATE_EVENT_TOOL_DEFINITION.name: (calendar.CREATE_EVENT_TOOL_DEFINITION, calendar.create_event),
    calendar.CHECK_AVAILABILITY_TOOL_DEFINITION.name: (
        calendar.CHECK_AVAILABILITY_TOOL_DEFINITION,
        calendar.check_availability,
    ),
    calendar.DELETE_EVENT_TOOL_DEFINITION.name: (calendar.DELETE_EVENT_TOOL_DEFINITION, calendar.delete_event),
}


def get_tool_definitions() -> list[ToolDefinition]:
    return [tool_definition for tool_definition, _ in _TOOLS.values()]


def run_tool(name: str, arguments: dict[str, object]) -> ToolCallResponse:
    if name not in _TOOLS:
        raise KeyError(name)

    _, executor = _TOOLS[name]
    try:
        return executor(arguments)
    except (ValueError, ValidationError):
        raise
    except Exception as exc:
        raise ToolExecutionError(f"Erro ao executar a ferramenta {name}: {exc}") from exc
