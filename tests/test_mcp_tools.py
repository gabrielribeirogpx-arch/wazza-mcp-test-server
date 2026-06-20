import json

from fastapi.responses import JSONResponse

from app.routers.mcp import call_tool, list_tools
from app.schemas import ToolCallRequest, ToolCallResponse


def response_payload(response: ToolCallResponse | JSONResponse) -> dict[str, object]:
    if isinstance(response, JSONResponse):
        return json.loads(response.body)
    return response.model_dump(exclude_none=True)


def call_tool_payload(name: str, arguments: dict[str, object]) -> dict[str, object]:
    response = call_tool(ToolCallRequest(name=name, arguments=arguments))
    assert isinstance(response, ToolCallResponse)
    return response.model_dump(exclude_none=True)


def test_tools_list_continues_working() -> None:
    response = list_tools()

    tool_names = {tool.name for tool in response.tools}
    assert "calculate" in tool_names
    assert "calendar_create_event" in tool_names


def test_calculate_returns_content_and_structured_content() -> None:
    payload = call_tool_payload("calculate", {"expression": "1234 * 567"})

    assert payload["content"] == [{"type": "text", "text": "O resultado é 699678."}]
    assert payload["structuredContent"] == {
        "ok": True,
        "tool": "calculate",
        "result": {"expression": "1234 * 567", "value": 699678},
    }


def test_calendar_create_event_returns_event_id_in_structured_result() -> None:
    payload = call_tool_payload(
        "calendar_create_event",
        {"title": "Reunião com João", "date": "amanhã", "time": "14:00", "duration_minutes": 60},
    )

    result = payload["structuredContent"]["result"]
    assert result["event_id"].startswith("evt_")
    assert result["title"] == "Reunião com João"
    assert result["duration_minutes"] == 60


def test_calendar_list_events_returns_events_array() -> None:
    call_tool_payload(
        "calendar_create_event",
        {"title": "Daily", "date": "amanhã", "time": "10:00", "duration_minutes": 30},
    )

    payload = call_tool_payload("calendar_list_events", {"date": "amanhã"})

    events = payload["structuredContent"]["result"]["events"]
    assert isinstance(events, list)
    assert any(event["title"] == "Daily" for event in events)


def test_tool_error_returns_ok_false() -> None:
    response = call_tool(ToolCallRequest(name="calculate", arguments={"expression": "1 / 0"}))

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    payload = response_payload(response)
    assert payload["content"][0]["text"].startswith("Não foi possível executar a ferramenta:")
    assert payload["structuredContent"]["ok"] is False
    assert payload["structuredContent"]["tool"] == "calculate"
    assert payload["structuredContent"]["error"]["code"] == "tool_error"
