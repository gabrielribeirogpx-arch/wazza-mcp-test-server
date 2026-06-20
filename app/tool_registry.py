from typing import Any

from app.mcp_tool_adapter import MCPToolAdapter


class ToolRegistry:
    """IA Agent-facing registry wrapper for MCP tools."""

    def __init__(self, adapter: MCPToolAdapter | None = None) -> None:
        self.adapter = adapter or MCPToolAdapter()

    def execute(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.adapter.call(name, arguments or {})
