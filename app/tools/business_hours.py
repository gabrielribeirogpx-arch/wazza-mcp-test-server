from pydantic import BaseModel, ConfigDict

from app.schemas import TextContent, ToolCallResponse, ToolDefinition


class BusinessHoursArguments(BaseModel):
    model_config = ConfigDict(extra="ignore")


TOOL_DEFINITION = ToolDefinition(
    name="get_business_hours",
    description="Retorna o horário de atendimento.",
    inputSchema={"type": "object", "properties": {}},
)


def execute(arguments: dict[str, object]) -> ToolCallResponse:
    BusinessHoursArguments.model_validate(arguments)
    return ToolCallResponse(content=[TextContent(text="Segunda a sexta das 08h às 18h.")])
