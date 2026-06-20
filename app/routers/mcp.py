from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.schemas import StructuredContent, StructuredError, TextContent, ToolCallRequest, ToolCallResponse, ToolsListResponse
from app.tools.registry import ToolExecutionError, get_tool_definitions, run_tool

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/list", response_model=ToolsListResponse)
def list_tools() -> ToolsListResponse:
    """List all tools available for Wazza discovery."""
    return ToolsListResponse(tools=get_tool_definitions())


@router.post(
    "/call",
    response_model=ToolCallResponse,
    responses={400: {"model": ToolCallResponse}, 404: {"model": ToolCallResponse}},
)
def call_tool(request: ToolCallRequest) -> ToolCallResponse | JSONResponse:
    """Dispatch a tool call by name and return MCP-style text content."""
    try:
        return run_tool(request.name, request.arguments)
    except KeyError:
        return _error_response(request.name, "tool_not_found", f"Ferramenta não encontrada: {request.name}", status_code=404)
    except (ToolExecutionError, ValidationError, ValueError) as exc:
        return _error_response(request.name, "tool_error", str(exc), status_code=400)


def _error_response(tool: str, code: str, message: str, status_code: int) -> JSONResponse:
    response = ToolCallResponse(
        content=[TextContent(text=f"Não foi possível executar a ferramenta: {message}")],
        structuredContent=StructuredContent(
            ok=False,
            tool=tool,
            error=StructuredError(code=code, message=message),
        ),
    )
    return JSONResponse(status_code=status_code, content=response.model_dump(exclude_none=True))
