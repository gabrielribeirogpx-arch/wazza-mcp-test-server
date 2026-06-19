from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.schemas import ErrorResponse, ToolCallRequest, ToolCallResponse, ToolsListResponse
from app.tools.registry import ToolExecutionError, get_tool_definitions, run_tool

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/list", response_model=ToolsListResponse)
def list_tools() -> ToolsListResponse:
    """List all tools available for Wazza discovery."""
    return ToolsListResponse(tools=get_tool_definitions())


@router.post(
    "/call",
    response_model=ToolCallResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def call_tool(request: ToolCallRequest) -> ToolCallResponse | JSONResponse:
    """Dispatch a tool call by name and return MCP-style text content."""
    try:
        return run_tool(request.name, request.arguments)
    except KeyError:
        return _error_response(f"Ferramenta não encontrada: {request.name}", status_code=404)
    except (ToolExecutionError, ValidationError, ValueError) as exc:
        return _error_response(str(exc), status_code=400)


def _error_response(message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": "tool_error", "message": message}},
    )
