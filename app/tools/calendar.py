from itertools import count
from typing import Any

from pydantic import BaseModel, Field

from app.schemas import TextContent, ToolCallResponse, ToolDefinition

# Armazenamento fake em memória para testes do IA Agent do Wazza.
# TODO: substituir esta camada por integração real com Google Calendar API + OAuth.
_EVENTS: dict[str, dict[str, Any]] = {}
_EVENT_COUNTER = count(1)


class CalendarListEventsArguments(BaseModel):
    date: str | None = Field(
        default=None, description="Data em YYYY-MM-DD ou texto como hoje/amanhã"
    )


class CalendarCreateEventArguments(BaseModel):
    title: str
    date: str
    time: str
    duration_minutes: int = 60
    attendees: list[str] = Field(default_factory=list)
    description: str | None = None


class CalendarCheckAvailabilityArguments(BaseModel):
    date: str
    duration_minutes: int = 60


class CalendarDeleteEventArguments(BaseModel):
    event_id: str


LIST_EVENTS_TOOL_DEFINITION = ToolDefinition(
    name="calendar_list_events",
    description="Lista eventos simulados do calendário.",
    inputSchema={
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "Data em YYYY-MM-DD ou texto como hoje/amanhã",
            }
        },
    },
)

CREATE_EVENT_TOOL_DEFINITION = ToolDefinition(
    name="calendar_create_event",
    description="Cria um evento simulado no calendário.",
    inputSchema={
        "type": "object",
        "required": ["title", "date", "time"],
        "properties": {
            "title": {"type": "string"},
            "date": {"type": "string"},
            "time": {"type": "string"},
            "duration_minutes": {"type": "integer", "default": 60},
            "attendees": {"type": "array", "items": {"type": "string"}},
            "description": {"type": "string"},
        },
    },
)

CHECK_AVAILABILITY_TOOL_DEFINITION = ToolDefinition(
    name="calendar_check_availability",
    description="Verifica horários disponíveis simulados.",
    inputSchema={
        "type": "object",
        "required": ["date"],
        "properties": {
            "date": {"type": "string"},
            "duration_minutes": {"type": "integer", "default": 60},
        },
    },
)

DELETE_EVENT_TOOL_DEFINITION = ToolDefinition(
    name="calendar_delete_event",
    description="Remove um evento simulado.",
    inputSchema={
        "type": "object",
        "required": ["event_id"],
        "properties": {"event_id": {"type": "string"}},
    },
)


def list_events(arguments: dict[str, object]) -> ToolCallResponse:
    parsed = CalendarListEventsArguments.model_validate(arguments)
    events = list(_EVENTS.values())
    if parsed.date:
        events = [event for event in events if event["date"] == parsed.date]

    if not events:
        date_text = f" em {parsed.date}" if parsed.date else ""
        return _text_response(f"Nenhum evento simulado encontrado{date_text}.")

    lines = [
        (
            f'- {event["event_id"]}: {event["title"]} em {event["date"]} '
            f'às {event["time"]} por {event["duration_minutes"]} minutos.'
        )
        for event in events
    ]
    return _text_response("Eventos simulados:\n" + "\n".join(lines))


def create_event(arguments: dict[str, object]) -> ToolCallResponse:
    parsed = CalendarCreateEventArguments.model_validate(arguments)
    event_id = f"evt_{next(_EVENT_COUNTER)}"
    _EVENTS[event_id] = {
        "event_id": event_id,
        "title": parsed.title,
        "date": parsed.date,
        "time": parsed.time,
        "duration_minutes": parsed.duration_minutes,
        "attendees": parsed.attendees,
        "description": parsed.description,
    }
    return _text_response(
        f"Evento criado: {parsed.title} em {parsed.date} às {parsed.time} por {parsed.duration_minutes} minutos."
    )


def check_availability(arguments: dict[str, object]) -> ToolCallResponse:
    parsed = CalendarCheckAvailabilityArguments.model_validate(arguments)
    # Disponibilidade fake para testes. TODO: calcular slots reais via Google Calendar API.
    return _text_response(
        f"Horários disponíveis em {parsed.date}: 09:00, 10:30, 14:00 e 16:00."
    )


def delete_event(arguments: dict[str, object]) -> ToolCallResponse:
    parsed = CalendarDeleteEventArguments.model_validate(arguments)
    _EVENTS.pop(parsed.event_id, None)
    return _text_response(f"Evento {parsed.event_id} removido com sucesso.")


def _text_response(text: str) -> ToolCallResponse:
    return ToolCallResponse(content=[TextContent(text=text)])
