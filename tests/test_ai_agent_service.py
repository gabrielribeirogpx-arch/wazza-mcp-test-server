from app.ai_agent_service import AIAgentService
from app.tool_registry import ToolRegistry


def test_mcp_calendar_create_event_structured_content_result_generates_structured_context() -> None:
    registry = ToolRegistry()
    service = AIAgentService()

    payload = registry.execute(
        "calendar_create_event",
        {"title": "Reunião com João", "date": "amanhã", "time": "14:00", "duration_minutes": 60},
    )

    context = service.build_assistant_context("calendar_create_event", payload)

    assert "Tool result:" in context
    assert "tool=calendar_create_event" in context
    assert "ok=true" in context
    assert 'text="Evento criado:' in context
    assert "structured_result=" in context
    assert '"title": "Reunião com João"' in context
    assert '"date": "amanhã"' in context
    assert '"time": "14:00"' in context


def test_final_response_uses_title_date_time_from_structured_result() -> None:
    service = AIAgentService()
    payload = {
        "content": [{"type": "text", "text": "Evento criado: texto legado."}],
        "structuredContent": {
            "ok": True,
            "tool": "calendar_create_event",
            "result": {"title": "Reunião com João", "date": "amanhã", "time": "14:00"},
        },
    }

    response = service.generate_natural_response("calendar_create_event", payload)

    assert response == "Perfeito! Agendei Reunião com João para amanhã às 14:00."


def test_mcp_calculate_keeps_correct_response() -> None:
    registry = ToolRegistry()
    service = AIAgentService()

    payload = registry.execute("calculate", {"expression": "1234 * 567"})
    response = service.generate_natural_response("calculate", payload)

    assert response == "O resultado é 699678."


def test_get_business_hours_uses_structured_result() -> None:
    registry = ToolRegistry()
    service = AIAgentService()

    payload = registry.execute("get_business_hours", {})
    response = service.generate_natural_response("get_business_hours", payload)

    assert response == "Atendemos de segunda a sexta, das 08h às 18h."


def test_structured_content_ok_false_is_not_treated_as_success() -> None:
    service = AIAgentService()
    payload = {
        "content": [{"type": "text", "text": "Evento criado: texto legado."}],
        "structuredContent": {
            "ok": False,
            "tool": "calendar_create_event",
            "error": {"code": "tool_error", "message": "horário indisponível"},
        },
    }

    context = service.build_assistant_context("calendar_create_event", payload)
    response = service.generate_natural_response("calendar_create_event", payload)

    assert "ok=false" in context
    assert "structured_error=" in context
    assert "Agendei" not in response
    assert "horário indisponível" in response


def test_legacy_mcp_text_only_response_still_works() -> None:
    service = AIAgentService()
    payload = {"content": [{"type": "text", "text": "Resposta antiga."}]}

    context = service.build_assistant_context("legacy_tool", payload)
    response = service.generate_natural_response("legacy_tool", payload)

    assert "tool=legacy_tool" in context
    assert "ok=unknown" in context
    assert "structured_result=" not in context
    assert response == "Resposta antiga."
