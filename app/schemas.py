from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    name: str
    description: str
    inputSchema: dict[str, Any]


class ToolsListResponse(BaseModel):
    tools: list[ToolDefinition]


class ToolCallRequest(BaseModel):
    name: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class TextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ToolCallResponse(BaseModel):
    content: list[TextContent]


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
