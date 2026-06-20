# Wazza MCP Test Server

Servidor HTTP simples para validar a infraestrutura MCP do Wazza como cliente MCP. Ele expõe endpoints HTTP simples para descoberta e chamada de ferramentas e também aceita MCP JSON-RPC 2.0 via `POST /`, permitindo testar o fluxo de cadastro, `tools/list`, persistência, exibição, `tools/call`, retorno ao IA Agent e observabilidade/replay no Wazza.

## Stack

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- Docker

## Ferramentas disponíveis

- `echo`: repete o texto enviado.
- `get_business_hours`: retorna o horário de atendimento.
- `calculate`: calcula expressões aritméticas simples com `+`, `-`, `*`, `/` e parênteses, sem uso de `eval`.
- `calendar_list_events`: lista eventos simulados do calendário.
- `calendar_create_event`: cria um evento simulado no calendário em memória.
- `calendar_check_availability`: verifica horários disponíveis simulados.
- `calendar_delete_event`: remove um evento simulado pelo `event_id`.

## Instalação local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução local

```bash
PORT=8080 uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

A aplicação ficará disponível em `http://localhost:8080`.

## Deploy no Railway

1. Crie um novo projeto no Railway apontando para este repositório.
2. Confirme que o Railway detectou o `Dockerfile`.
3. Defina a variável de ambiente `PORT` se necessário. O servidor usa `PORT` e faz fallback para `8080`.
4. Faça o deploy.
5. Cadastre a URL pública gerada pelo Railway na tela de Integrações de IA do Wazza.


## Interfaces suportadas

O servidor mantém duas formas de integração:

- Endpoints HTTP simples:
  - `GET /` para health check.
  - `POST /tools/list` para listar ferramentas.
  - `POST /tools/call` para chamar uma ferramenta.
- MCP JSON-RPC 2.0 via `POST /` para clientes que enviam os métodos MCP diretamente para a raiz do servidor.

## Exemplos curl

### GET /

```bash
curl http://localhost:8080/
```

Resposta esperada:

```json
{
  "status": "ok",
  "server": "wazza-mcp-test-server"
}
```

### POST /tools/list

```bash
curl -X POST http://localhost:8080/tools/list
```

### POST /tools/call echo

```bash
curl -X POST http://localhost:8080/tools/call \
  -H 'Content-Type: application/json' \
  -d '{"name":"echo","arguments":{"text":"Olá mundo"}}'
```

### POST /tools/call get_business_hours

```bash
curl -X POST http://localhost:8080/tools/call \
  -H 'Content-Type: application/json' \
  -d '{"name":"get_business_hours","arguments":{}}'
```

### POST /tools/call calculate

```bash
curl -X POST http://localhost:8080/tools/call \
  -H 'Content-Type: application/json' \
  -d '{"name":"calculate","arguments":{"expression":"5 * (3 + 2)"}}'
```

Resposta esperada:

```json
{
  "content": [
    {
      "type": "text",
      "text": "25"
    }
  ]
}
```


### POST /tools/call calendar_list_events

```bash
curl -X POST http://localhost:8080/tools/call \
  -H 'Content-Type: application/json' \
  -d '{"name":"calendar_list_events","arguments":{"date":"amanhã"}}'
```

Resposta esperada:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Nenhum evento simulado encontrado em amanhã."
    }
  ]
}
```

### POST /tools/call calendar_create_event

```bash
curl -X POST http://localhost:8080/tools/call \
  -H 'Content-Type: application/json' \
  -d '{"name":"calendar_create_event","arguments":{"title":"Reunião com João","date":"amanhã","time":"14:00","duration_minutes":60}}'
```

Resposta esperada:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Evento criado: Reunião com João em amanhã às 14:00 por 60 minutos."
    }
  ]
}
```

### POST /tools/call calendar_check_availability

```bash
curl -X POST http://localhost:8080/tools/call \
  -H 'Content-Type: application/json' \
  -d '{"name":"calendar_check_availability","arguments":{"date":"amanhã","duration_minutes":60}}'
```

Resposta esperada:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Horários disponíveis em amanhã: 09:00, 10:30, 14:00 e 16:00."
    }
  ]
}
```

### POST /tools/call calendar_delete_event

```bash
curl -X POST http://localhost:8080/tools/call \
  -H 'Content-Type: application/json' \
  -d '{"name":"calendar_delete_event","arguments":{"event_id":"evt_1"}}'
```

Resposta esperada:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Evento evt_1 removido com sucesso."
    }
  ]
}
```

### POST / MCP JSON-RPC initialize

```bash
curl -X POST http://localhost:8080/ \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

Resposta esperada:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "wazza-mcp-test-server",
      "version": "1.0.0"
    }
  }
}
```

### POST / MCP JSON-RPC tools/list

```bash
curl -X POST http://localhost:8080/ \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

### POST / MCP JSON-RPC tools/call

```bash
curl -X POST http://localhost:8080/ \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"echo","arguments":{"text":"Olá"}}}'
```

Resposta esperada:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Olá"
      }
    ]
  }
}
```

## Erros

Erros de ferramenta retornam o formato:

```json
{
  "error": {
    "code": "tool_error",
    "message": "Descrição do erro"
  }
}
```
