from pydantic import BaseModel

from app.schemas import StructuredContent, TextContent, ToolCallResponse, ToolDefinition


class EchoArguments(BaseModel):
    text: str


TOOL_DEFINITION = ToolDefinition(
    name="echo",
    description="Repete o texto enviado.",
    inputSchema={
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    },
)


def execute(arguments: dict[str, object]) -> ToolCallResponse:
    parsed = EchoArguments.model_validate(arguments)
    return ToolCallResponse(
        content=[TextContent(text=parsed.text)],
        structuredContent=StructuredContent(ok=True, tool="echo", result={"text": parsed.text}),
    )
