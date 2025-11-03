# ============================================================

# 🍽️ RESTAURANT ANALYTICS — DOCUMENTAÇÃO DE TESTE DE CONEXÃO

# ============================================================

## 🧭 Objetivo

Guia passo a passo para validar a **conexão do backend com o banco de dados**, tanto em ambiente **LOCAL (Docker)** quanto **CLOUD (Supabase)**.



## 🔹 1. PRÉ-REQUISITOS

Antes de testar a conexão:

* Estar na pasta **infra** do projeto:

  ```bash
  cd ~/Desktop/restaurant-analytics/infra
  ```
* Ter os containers configurados no `docker-compose.yml` (backend, frontend e db).
* Garantir que o backend carrega o arquivo `.env` desta pasta.

---

## 🔸 2. TESTE LOCAL (Banco no Docker)

### 🧩 Etapa 1 — Configurar o `.env`

No arquivo `infra/.env`:

```env
DB_MODE=LOCAL

POSTGRES_USER_LOCAL=postgres
POSTGRES_PASSWORD_LOCAL=TpXBFBy7uyECP7MD
POSTGRES_DB_LOCAL=restaurant_analytics
DB_PORT_LOCAL=5432
DATABASE_URL_LOCAL=postgresql://postgres:TpXBFBy7uyECP7MD@db:5432/restaurant_analytics
```

### 🧩 Etapa 2 — Subir o ambiente local

```bash
docker compose down -v
docker compose --env-file .env up -d --build
docker compose ps
```

> Verifique se `restaurant-analytics-db` e `restaurant-analytics-backend` estão **Up**.

### 🧩 Etapa 3 — Ajustar senha e criar banco (se necessário)

```bash
docker compose exec db psql -U postgres -d postgres
ALTER USER postgres WITH PASSWORD 'TpXBFBy7uyECP7MD';
CREATE DATABASE restaurant_analytics;
\q
```

### 🧩 Etapa 4 — Testar conexão

```bash
docker compose exec backend python -c "from src.database.session import test_connection; test_connection()"
```

✅ Saída esperada:

```
Conexão OK: 1
```

### 🧩 Etapa 5 — Aplicar migrações (opcional)

```bash
docker compose exec backend alembic upgrade head
```

### 🧩 Etapa 6 — Verificar tabelas (opcional)

```bash
docker compose exec db psql -U postgres -d restaurant_analytics -c "\\dt"
```

---

## 🔸 3. TESTE CLOUD (Supabase)

### ☁️ Etapa 1 — Configurar o `.env`

No `infra/.env`, altere:

```env
DB_MODE=CLOUD

DATABASE_URL_CLOUD=postgresql://postgres:TpXBFBy7uyECP7MD@qqipdesjjtmerjurlykv.supabase.co:5432/postgres?sslmode=require
DATABASE_URL=postgresql://postgres:TpXBFBy7uyECP7MD@qqipdesjjtmerjurlykv.supabase.co:5432/postgres?sslmode=require

SUPABASE_URL=https://qqipdesjjtmerjurlykv.supabase.co
SUPABASE_ANON_KEY=<sua_anon_key>
SUPABASE_SERVICE_ROLE_KEY=<sua_service_role_key>
```

### ☁️ Etapa 2 — Subir com nova configuração

```bash
docker compose down
docker compose --env-file .env up -d --build
docker compose ps
```

### ☁️ Etapa 3 — Testar conexão com Supabase

```bash
docker compose exec backend python -c "from src.database.session import test_connection; test_connection()"
```

✅ Saída esperada:

```
Conexão OK: 1
```

### ☁️ Etapa 4 — Criar estrutura no Supabase (se vazio)

```bash
docker compose exec backend alembic upgrade head
```

### ☁️ Etapa 5 — (Opcional) Popular dados iniciais

```bash
docker compose exec backend python -m src.scripts.seed
```



## 🔍 4. TROUBLESHOOTING (Problemas Comuns)

| Sintoma                                 | Causa provável                                      | Solução                                                                     |
| --------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------------------- |
| `password authentication failed`        | Senha do usuário `postgres` divergente              | Rodar `ALTER USER postgres WITH PASSWORD '...'` no banco correto            |
| `Connection refused`                    | Host errado (`host.docker.internal` em vez de `db`) | Trocar para `DB_HOST=db` no `.env`                                          |
| `test_connection()` falha no modo CLOUD | `sslmode` ausente ou URL incorreta                  | Usar `?sslmode=require` na URL do Supabase                                  |
| Backend ignora `_LOCAL` ou `_CLOUD`     | Código lê só `DATABASE_URL`                         | Definir também `DATABASE_URL=` no `.env`                                    |
| Variáveis não atualizaram               | Containers usam cache antigo                        | Rodar `docker compose down && docker compose --env-file .env up -d --build` |



## 🧾 5. RESUMO FINAL

| Ambiente  | DB_MODE | URL usada                                                    | Teste esperado    |
| --------- | ------- | ------------------------------------------------------------ | ----------------- |
| **LOCAL** | LOCAL   | `postgresql://...@db:5432/restaurant_analytics`              | ✅ `Conexão OK: 1` |
| **CLOUD** | CLOUD   | `postgresql://...@supabase.co:5432/postgres?sslmode=require` | ✅ `Conexão OK: 1` |



