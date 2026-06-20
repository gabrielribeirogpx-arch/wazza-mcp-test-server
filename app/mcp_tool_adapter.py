from typing import Any

from app.schemas import ToolCallResponse
from app.tools.registry import run_tool


class MCPToolAdapter:
    """Adapter that calls MCP tools and preserves structuredContent in the returned payload."""

    def call(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        response = run_tool(name, arguments or {})
        if isinstance(response, ToolCallResponse):
            return response.model_dump(exclude_none=True)
        return response  # type: ignore[return-value]
