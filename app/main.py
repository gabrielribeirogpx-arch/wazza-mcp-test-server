from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.routers.mcp import router as mcp_router
from app.schemas import ToolCallRequest
from app.tools.registry import ToolExecutionError, get_tool_definitions, run_tool

app = FastAPI(
    title="Wazza MCP Test Server",
    description="Servidor HTTP simples para validar descoberta e chamada de ferramentas MCP no Wazza.",
    version="1.0.0",
)


@app.get("/")
def health_check() -> dict[str, str]:
    """Return basic server health information."""
    return {"status": "ok", "server": "wazza-mcp-test-server"}


@app.post("/")
def json_rpc_endpoint(request: dict[str, Any]) -> dict[str, Any] | JSONResponse:
    """Handle MCP JSON-RPC requests sent to the server root."""
    request_id = request.get("id")
    method = request.get("method")

    if method == "initialize":
        return _json_rpc_result(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "wazza-mcp-test-server", "version": "1.0.0"},
            },
        )

    if method == "tools/list":
        return _json_rpc_result(
            request_id,
            {"tools": [tool.model_dump() for tool in get_tool_definitions()]},
        )

    if method == "tools/call":
        try:
            tool_call = ToolCallRequest.model_validate(request.get("params", {}))
            result = run_tool(tool_call.name, tool_call.arguments)
        except KeyError:
            return _json_rpc_error(request_id, -32602, "Tool not found")
        except (ToolExecutionError, ValidationError, ValueError) as exc:
            return _json_rpc_error(request_id, -32602, str(exc))

        return _json_rpc_result(request_id, result.model_dump())

    return _json_rpc_error(request_id, -32601, "Method not found")


def _json_rpc_result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _json_rpc_error(request_id: Any, code: int, message: str) -> JSONResponse:
    return JSONResponse(
        content={
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }
    )


app.include_router(mcp_router)
