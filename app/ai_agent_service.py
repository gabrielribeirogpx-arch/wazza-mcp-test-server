import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class AIAgentService:
    """Helpers used by Wazza's IA Agent to prepare MCP tool results for the LLM."""

    def extract_tool_result(self, tool_result: dict[str, Any]) -> dict[str, Any]:
        """Extract text and structured MCP fields while remaining compatible with legacy MCP responses."""
        content = tool_result.get("content") or []
        result_text = "\n".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text" and item.get("text")
        )

        structured_content = tool_result.get("structuredContent") or {}
        if not isinstance(structured_content, dict):
            structured_content = {}

        extracted = {
            "result_text": result_text,
            "structured_result": structured_content.get("result"),
            "structured_ok": structured_content.get("ok"),
            "structured_tool": structured_content.get("tool"),
            "structured_error": structured_content.get("error"),
        }

        if extracted["structured_ok"] is False:
            logger.info("AI_AGENT_TOOL_STRUCTURED_ERROR", extra={"tool_result": extracted})
        elif extracted["structured_result"] is not None:
            logger.info("AI_AGENT_TOOL_STRUCTURED_RESULT", extra={"tool_result": extracted})

        return extracted

    def build_assistant_context(self, tool_name: str, tool_result: dict[str, Any]) -> str:
        """Build the final tool context sent to the LLM."""
        extracted = self.extract_tool_result(tool_result)
        structured_tool = extracted["structured_tool"] or tool_name
        structured_ok = extracted["structured_ok"]
        ok_text = "unknown" if structured_ok is None else str(structured_ok).lower()
        text = json.dumps(extracted["result_text"], ensure_ascii=False)

        lines = [
            "Tool result:",
            f"tool={structured_tool}",
            f"ok={ok_text}",
            f"text={text}",
        ]
        if extracted["structured_result"] is not None:
            lines.append(
                "structured_result="
                + json.dumps(extracted["structured_result"], ensure_ascii=False, sort_keys=True)
            )
        if extracted["structured_error"] is not None:
            lines.append(
                "structured_error="
                + json.dumps(extracted["structured_error"], ensure_ascii=False, sort_keys=True)
            )
        return "\n".join(lines)

    def generate_natural_response(self, tool_name: str, tool_result: dict[str, Any]) -> str:
        """Small deterministic responder mirroring the instruction given to the LLM in tests/fallback flows."""
        extracted = self.extract_tool_result(tool_result)
        text = extracted["result_text"]
        structured_result = extracted["structured_result"]
        structured_ok = extracted["structured_ok"]
        structured_error = extracted["structured_error"]
        structured_tool = extracted["structured_tool"] or tool_name

        if structured_ok is False:
            message = ""
            if isinstance(structured_error, dict):
                message = str(structured_error.get("message") or "")
            return f"Desculpe, não consegui executar {structured_tool}. {message}".strip()

        if isinstance(structured_result, dict):
            if structured_tool == "calendar_create_event":
                title = structured_result.get("title")
                date = structured_result.get("date")
                time = structured_result.get("time")
                if title and date and time:
                    return f"Perfeito! Agendei {title} para {date} às {time}."
            if structured_tool == "calculate" and "value" in structured_result:
                return f"O resultado é {structured_result['value']}."
            if structured_tool == "get_business_hours":
                days = structured_result.get("days") or "segunda a sexta"
                opens = (
                    structured_result.get("opens_at")
                    or structured_result.get("opens")
                    or structured_result.get("open")
                    or "08h"
                )
                closes = (
                    structured_result.get("closes_at")
                    or structured_result.get("closes")
                    or structured_result.get("close")
                    or "18h"
                )
                return f"Atendemos de {days}, das {self._format_hour(opens)} às {self._format_hour(closes)}."

        return text

    @staticmethod
    def _format_hour(value: object) -> str:
        text = str(value)
        if len(text) == 5 and text[2] == ":" and text.endswith(":00"):
            return text[:2] + "h"
        return text
