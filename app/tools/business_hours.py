from pydantic import BaseModel, ConfigDict

from app.schemas import StructuredContent, TextContent, ToolCallResponse, ToolDefinition


class BusinessHoursArguments(BaseModel):
    model_config = ConfigDict(extra="ignore")


TOOL_DEFINITION = ToolDefinition(
    name="get_business_hours",
    description="Retorna o horário de atendimento.",
    inputSchema={"type": "object", "properties": {}},
)


def execute(arguments: dict[str, object]) -> ToolCallResponse:
    BusinessHoursArguments.model_validate(arguments)
    return ToolCallResponse(
        content=[TextContent(text="Atendemos de segunda a sexta, das 08h às 18h.")],
        structuredContent=StructuredContent(
            ok=True,
            tool="get_business_hours",
            result={
                "days": "segunda a sexta",
                "opens": "08:00",
                "closes": "18:00",
                "timezone": "America/Sao_Paulo",
            },
        ),
    )
