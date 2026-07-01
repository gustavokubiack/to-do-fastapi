# To-Do FastAPI

API + frontend simples de lista de tarefas (to-do list), construída com **FastAPI**, **SQLAlchemy (async)** e **Pydantic**, com um frontend estático em HTML/CSS/JS puro servido pelo próprio backend.

Este projeto é implantado automaticamente na AWS pela [`trabalho-final-cloud-cli`](https://github.com/gustavokubiack/trabalho-final-cloud-cli), mas também pode ser rodado localmente para desenvolvimento.

## Índice

- [Funcionalidades](#funcionalidades)
- [Stack](#stack)
- [Pré-requisitos](#pré-requisitos)
- [Rodando localmente](#rodando-localmente)
- [Rodando com Docker](#rodando-com-docker)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Endpoints da API](#endpoints-da-api)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Testando a API pelo terminal](#testando-a-api-pelo-terminal)

## Funcionalidades

- Criar, listar, editar (título/descrição/status) e excluir tarefas
- Campo de descrição opcional em cada tarefa
- Marcar tarefas como concluídas
- Frontend responsivo servido direto pelo backend (`/`)
- Endpoints de saúde (`/health`) e status do banco (`/db-status`), usados pela CLI de diagnóstico
- Suporte a SQLite (padrão local), PostgreSQL e MySQL via variáveis de ambiente

## Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (modo assíncrono)
- [Pydantic v2](https://docs.pydantic.dev/)
- [Uvicorn](https://www.uvicorn.org/) (ASGI server)
- Drivers de banco: `aiosqlite`, `aiomysql`, `asyncpg`
- Frontend: HTML/CSS/JS vanilla (`static/index.html`)

## Pré-requisitos

- Python 3.11+
- `pip`

## Rodando localmente

```bash
# 1. Clone o repositório
git clone https://github.com/gustavokubiack/to-do-fastapi.git
cd to-do-fastapi

# 2. Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Suba o servidor em modo desenvolvimento (hot reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

Sem nenhuma variável de ambiente configurada, a aplicação usa **SQLite local** (`todos.db`, criado automaticamente na primeira execução) — não precisa de banco externo para testar.

Depois de subir, acesse:

- Frontend: http://localhost:3000
- Documentação interativa (Swagger): http://localhost:3000/docs
- Documentação alternativa (ReDoc): http://localhost:3000/redoc

Para rodar sem reload (mais próximo de produção):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3000
```

## Rodando com Docker

Não há `Dockerfile` neste repositório ainda, mas se quiser containerizar rapidamente:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 3000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
```

```bash
docker build -t to-do-fastapi .
docker run -p 3000:3000 to-do-fastapi
```

## Variáveis de ambiente

Nenhuma é obrigatória para uso local (cai em SQLite por padrão). Para conectar a um banco externo (é assim que a `trabalho-final-cloud-cli` configura a instância EC2 apontando para o RDS):

| Variável | Descrição | Padrão |
|---|---|---|
| `DB_HOST` | Host do banco de dados. Se vazio, usa SQLite local | *(vazio → SQLite)* |
| `DB_PORT` | Porta do banco | `3306` |
| `DB_USER` | Usuário do banco | `admin` |
| `DB_PASSWORD` | Senha do banco | *(vazio)* |
| `DB_NAME` | Nome do banco/schema | `appdb` |
| `DB_ENGINE` | `postgres` ou `mysql` | `mysql` |
| `APP_NAME` | Nome da aplicação (usado no endpoint raiz de fallback) | `to-do-fastapi` |

Exemplo apontando para PostgreSQL:

```bash
export DB_HOST=meu-rds.xxxxx.us-east-1.rds.amazonaws.com
export DB_PORT=5432
export DB_USER=postgres
export DB_PASSWORD=minha-senha
export DB_NAME=appdb
export DB_ENGINE=postgres

uvicorn app.main:app --host 0.0.0.0 --port 3000
```

As tabelas são criadas automaticamente na inicialização (`Base.metadata.create_all`), não é necessário rodar migrations manualmente.

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Serve o frontend (`static/index.html`) |
| `GET` | `/health` | Health check (usado por load balancers) |
| `GET` | `/hostname` | Retorna o hostname da instância que respondeu |
| `GET` | `/db-status` | Testa a conexão com o banco de dados |
| `GET` | `/todos` | Lista tarefas (paginação via `skip`/`limit`) |
| `GET` | `/todos/{id}` | Busca uma tarefa por ID |
| `POST` | `/todos` | Cria uma tarefa (`title` obrigatório, `description` opcional) |
| `PATCH` | `/todos/{id}` | Atualiza campos de uma tarefa (`title`, `description`, `completed`) |
| `DELETE` | `/todos/{id}` | Remove uma tarefa |

## Estrutura do projeto

```
to-do-fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py         # Rotas e configuração da aplicação FastAPI
│   ├── models.py        # Modelo SQLAlchemy (tabela `todos`)
│   ├── schemas.py       # Schemas Pydantic (TodoCreate, TodoUpdate, TodoOut)
│   ├── crud.py           # Funções de acesso ao banco (create/list/get/update/delete)
│   └── database.py      # Configuração do engine assíncrono e sessão
├── static/
│   └── index.html        # Frontend (HTML + CSS + JS puro)
├── requirements.txt
└── .gitignore
```

## Testando a API pelo terminal

```bash
# Criar tarefa
curl -X POST http://localhost:3000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Comprar leite", "description": "Ir ao mercado antes das 18h"}'

# Listar tarefas
curl http://localhost:3000/todos

# Marcar como concluída
curl -X PATCH http://localhost:3000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Excluir tarefa
curl -X DELETE http://localhost:3000/todos/1
```