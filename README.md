# tutores-backend

API e agente conversacional da Plataforma de Tutores Personalizados.

> Código produzido com auxílio de agentes de codificação (Claude Code).

## Como subir localmente

```bash
# 1. Copie o arquivo de variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves reais

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute as migrations
# (instruções serão adicionadas)

# 4. Suba o servidor
# (instruções serão adicionadas)
```

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `LLM_API_KEY` | Chave da API do modelo de linguagem |
| `LLM_MODEL` | Modelo a usar (ex: `gpt-4o`) |
| `DATABASE_URL` | URL de conexão com o banco de dados |
| `ADMIN_API_KEY` | Chave de autenticação do administrador |
| `SECRET_KEY` | Chave para geração de tokens JWT |
| `ALLOWED_ORIGINS` | Domínios permitidos no CORS (separados por vírgula) |

## Decisões de arquitetura

> Seção a ser preenchida durante o desenvolvimento.

- **Framework do agente:** a definir (LangChain ou Pydantic AI)
- **Protocolo do chat:** a definir (HTTP ou WebSocket)
- **Autenticação admin:** a definir (JWT ou API key)
- **Banco de dados:** a definir (SQLite ou PostgreSQL)

## Fluxo embed ponta a ponta

> A ser documentado após implementação do widget.

## Próximos passos para produção

> A ser preenchido ao final do MVP.
