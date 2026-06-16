# Tutores — Backend

API REST para a **Plataforma de Tutores Personalizados**, desenvolvida como desafio técnico da DOT Digital Group.

> Código produzido com auxílio de agentes de codificação (Claude Code — Anthropic).

---

## O que faz

Permite que um administrador cadastre **tutores** (assistentes de IA com persona, instruções e fontes de conhecimento) e os disponibilize via chat em um widget de iframe.

---

## Arquitetura

```
Cliente (iframe) ──── POST /api/v1/chat/{id} ────▶ FastAPI
                                                        │
Painel Admin ──── /api/v1/tutores/ (API Key) ────▶ FastAPI
                                                        │
                                             ┌──────────┴──────────┐
                                        SQLite (SQLModel)    Pydantic AI
                                        (Tutor, Mensagem)   (Agente LLM)
                                                                    │
                                                             Fontes externas
                                                             (fetch HTTP)
```

**Fluxo de uma mensagem:**
1. O widget envia `POST /api/v1/chat/{tutor_id}` com `{ sessao_id, mensagem }`
2. O backend recupera as instruções e fontes do tutor no SQLite
3. O agente Pydantic AI busca o conteúdo das URLs de fonte (até 3 000 chars cada)
4. O LLM gera a resposta usando instruções + fontes + histórico da sessão
5. Os dois turnos (usuário + assistente) são salvos atomicamente no banco
6. A resposta é retornada ao widget

---

## Decisões de arquitetura

| Decisão | Escolha | Por quê |
|---|---|---|
| Framework web | **FastAPI** | Rápido, tipado, gera documentação automática |
| Agente IA | **Pydantic AI** | Mais simples que LangChain para o escopo do MVP |
| Protocolo do chat | **HTTP POST** | Suficiente para o iframe; mais fácil de documentar |
| Autenticação admin | **API Key** | O PRD aceita explicitamente; sem overhead de JWT |
| Banco de dados | **SQLite** | Zero instalação; demo funciona sem dependências externas |
| Estratégia de contexto | **Fetch de URLs** | Sem RAG vetorial; sem embeddings; simples e auditável |

---

## Pré-requisitos

- Python 3.11+
- Chave de API de um LLM compatível com OpenAI SDK (ex: OpenAI, OpenRouter)

---

## Como rodar localmente

```bash
# 1. Clone o repositório
git clone https://github.com/silasluiz96-alt/tutores-backend
cd tutores-backend

# 2. Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves

# 5. Suba o servidor
uvicorn app.main:app --reload
```

O servidor estará disponível em `http://localhost:8000`.
Documentação interativa (Swagger): `http://localhost:8000/docs`.

---

## Variáveis de ambiente

```env
# Obrigatórias
ADMIN_API_KEY=chave-secreta-do-admin
LLM_API_KEY=sk-...

# Opcionais (valores padrão mostrados)
LLM_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./tutores.db
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5500
```

---

## Endpoints principais

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| GET | `/api/v1/tutores/` | API Key | Lista todos os tutores |
| POST | `/api/v1/tutores/` | API Key | Cria tutor |
| GET | `/api/v1/tutores/{id}` | API Key | Detalha tutor |
| PATCH | `/api/v1/tutores/{id}` | API Key | Atualiza tutor |
| DELETE | `/api/v1/tutores/{id}` | API Key | Desativa tutor |
| POST | `/api/v1/chat/{tutor_id}` | Pública | Envia mensagem ao tutor |

---

## Testes

```bash
pytest -v
```

10 testes automatizados cobrem: CRUD de tutores, autenticação (401/500), chat com mock do agente e validação dos modelos.

---

## Estrutura de arquivos

```
app/
├── main.py            ← entrada da aplicação (lifespan, CORS, rotas)
├── auth.py            ← validação de API Key
├── database.py        ← conexão SQLite + SQLModel
├── api/
│   ├── tutores.py     ← CRUD de tutores (protegido por API Key)
│   └── chat.py        ← rota pública de conversa
├── models/
│   ├── tutor.py       ← modelo Tutor
│   └── mensagem.py    ← modelo Mensagem (com validação de papel)
├── services/
│   └── chat.py        ← regras de negócio + commit atômico dos turnos
└── agent/
    └── tutor_agent.py ← Pydantic AI + fetch de fontes externas
tests/
├── test_tutores.py
└── test_chat.py
```

---

## Limitações do MVP

- SQLite não suporta conexões concorrentes em escala — adequado apenas para demos e uso individual
- O fetch de fontes é limitado a 3 000 caracteres por URL
- Não há rate limiting por tutor ou por sessão — omitido intencionalmente no MVP pois o demo é de uso controlado (admin único, iframe em ambiente de avaliação); para produção, `slowapi` resolve com poucas linhas (ver Próximos Passos)
- A API Key é uma string estática — sem rotação ou múltiplos admins
- Histórico de chat é armazenado indefinidamente (sem TTL ou paginação)

---

## Próximos passos para produção

### Infraestrutura
- Migrar SQLite → **Supabase** (PostgreSQL gerenciado, suporta concorrência e backups automáticos)
- **dbt** para transformações analíticas sobre o histórico de conversas

### Segurança e autenticação
- Substituir API Key estática por **JWT** com expiração e refresh token
- **Rate limiting** por tutor/sessão (ex: `slowapi`)
- Variáveis de ambiente gerenciadas via cofre de segredos (ex: AWS Secrets Manager, Doppler)

### Conformidade LGPD
- Endpoint `DELETE /api/v1/sessao/{sessao_id}` para exclusão de histórico a pedido do titular
- TTL automático de mensagens (ex: 90 dias)
- Aviso de IA na interface do widget ("Você está conversando com um assistente de IA")
- Política de privacidade vinculada ao widget

### Funcionalidades
- Auto-cadastro de tutores (multi-tenant) com sistema de aprovação
- RAG com banco vetorial (ex: pgvector) para bases de conhecimento maiores
- Streaming de respostas via Server-Sent Events

---

*Desafio técnico DOT Digital Group — Plataforma de Tutores Personalizados*
*Código produzido com auxílio de agentes de codificação (Claude Code — Anthropic)*
