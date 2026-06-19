from fastapi import FastAPI

from app.routers.mcp import router as mcp_router

app = FastAPI(
    title="Wazza MCP Test Server",
    description="Servidor HTTP simples para validar descoberta e chamada de ferramentas MCP no Wazza.",
    version="1.0.0",
)


@app.get("/")
def health_check() -> dict[str, str]:
    """Return basic server health information."""
    return {"status": "ok", "server": "wazza-mcp-test-server"}


app.include_router(mcp_router)
