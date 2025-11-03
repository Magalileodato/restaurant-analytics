# 🍽️ Restaurant Analytics — Alternância de Banco (LOCAL ↔ CLOUD)

Documento prático com **estrutura de pastas**, **comandos**, **saídas esperadas** e **diagnóstico** para alternar entre **PostgreSQL LOCAL (Docker)** e **Supabase (CLOUD)** usando apenas a variável de ambiente `DB_MODE`, **sem alterar o código** ou o `docker-compose.yml`.


## ⚙️ Variáveis Principais (no `.env`)

* `DB_MODE=LOCAL` → usa **Postgres do Docker** (`host=db`)
* `DB_MODE=CLOUD` → usa **Supabase** (`DATABASE_URL_CLOUD`)

### URLs típicas

```env
DATABASE_URL_LOCAL=postgresql://postgres:postgres@db:5432/appdb
DATABASE_URL_CLOUD=postgresql://postgres:<SENHA>@<host>.supabase.co:5432/postgres?sslmode=require
```

> **Importante:** não altere o `docker-compose.yml`. Toda a escolha é feita pelo **valor de `DB_MODE` no start**.


## ▶️ Start no **Modo LOCAL** (Docker)

Na pasta `infra/`:

```bash
DB_MODE=LOCAL docker compose up -d backend
```

**Retornos esperados (logs do backend):**

```
🔌 Modo: LOCAL | Host detectado: Docker (db)
🗄️ Usando banco de dados: LOCAL
✅ Base.metadata.create_all executado (se tabelas não existiam, foram criadas)
✅ Conexão OK: 1
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verificação:**

```bash
curl -s http://localhost:8000/health
# {"status":"ok"}
```

**Checar que o serviço está “Up”:**

```bash
docker compose ps
# restaurant-analytics-backend   Up ...  0.0.0.0:8000->8000/tcp
# restaurant-analytics-db        Up (healthy)  5432/tcp
```

---

## ☁️ Start no **Modo CLOUD** (Supabase)

Na pasta `infra/`:

```bash
DB_MODE=CLOUD docker compose up -d backend
```

Verificar o modo de banco:

```bash
docker compose exec backend printenv | grep DB_MODE
# DB_MODE=CLOUD
```

**Retornos esperados (logs do backend):**

```
🔌 Modo: CLOUD | Host detectado: Supabase
🗄️ Usando banco de dados: CLOUD
✅ Conexão OK: True
```

**Verificação:**

```bash
curl -s http://localhost:8000/health
# {"status":"ok"}
```


## 🌐 Subir o **Frontend** (Nginx)

Na pasta `infra/`:

```bash
docker compose up -d frontend
```

**Verificação:**

```bash
docker compose ps
# Esperado: 0.0.0.0:3000->80/tcp
```

**Teste HTTP:**

```bash
curl -I http://localhost:3000
# HTTP/1.1 200 OK
```

Se alterou `VITE_API_BASE_URL`, refaça o build:

```bash
docker compose build frontend
docker compose up -d frontend
```


## 🔎 Diagnóstico e Comandos Úteis

### Ver serviços ativos

```bash
docker compose ps
```

### Ver logs

```bash
docker compose logs -n 100 backend
docker compose logs -n 100 frontend
```

### Conferir o `DB_MODE` no container

```bash
docker compose exec backend printenv | grep DB_MODE
# DB_MODE=LOCAL  ou  DB_MODE=CLOUD
```

### Checar saúde da API

```bash
curl -s http://localhost:8000/health
# {"status":"ok","db_mode":"LOCAL"}  ou  {"status":"ok","db_mode":"CLOUD"}
```


## 🧰 Casos Comuns e Correções

### 1️⃣ Frontend não carrega

1. Ver se está “Up” e porta mapeada:

   ```bash
   docker compose ps
   ```
2. Logs do Nginx:

   ```bash
   docker compose logs -n 100 frontend
   ```
3. Ver arquivos estáticos:

   ```bash
   docker compose exec frontend ls -la /usr/share/nginx/html
   ```
4. Se faltam arquivos:

   ```bash
   docker compose build frontend
   docker compose up -d frontend
   ```
5. Teste HTTP:

   ```bash
   curl -I http://localhost:3000
   # HTTP/1.1 200 OK
   ```

### 2️⃣ API sobe, mas sem dados

* Ver `/health`:

  ```bash
  curl -s http://localhost:8000/health
  ```
* Alternar modo:

  ```bash
  DB_MODE=LOCAL docker compose up -d backend
  DB_MODE=CLOUD docker compose up -d backend
  ```
* Logs:

  ```
  🗄️ Usando banco de dados: LOCAL ou CLOUD
  ✅ Conexão OK
  ```

### 3️⃣ “service backend is not running”

```bash
cd <repo>/infra
DB_MODE=LOCAL docker compose up -d backend
docker compose ps
```

### 4️⃣ Frontend abre, mas sem dados (erro de API)

* Testar backend:

  ```bash
  curl -s http://localhost:8000/health
  ```
* Ver console do navegador (F12 → Network):

  * **CORS:** backend já com `allow_origins=["*"]`.
  * **404/500:** testar via `curl`:

    ```bash
    curl -I http://localhost:8000/metrics/...
    ```


## 🧪 Fluxo de Teste (Fim a Fim)

**LOCAL**

```bash
cd <repo>/infra
DB_MODE=LOCAL docker compose up -d backend
docker compose up -d frontend
curl -s http://localhost:8000/health
curl -I http://localhost:3000
```

**CLOUD**

```bash
cd <repo>/infra
DB_MODE=CLOUD docker compose up -d backend
curl -s http://localhost:8000/health
```

Ver qual banco está usando:

```bash
docker compose exec backend printenv | grep DB_MODE
# DB_MODE=CLOUD
```


## 📝 Observações Finais

* A seleção é feita **somente** via `DB_MODE`.
* O frontend continua apontando para `http://localhost:8000`.
* Use os comandos de diagnóstico se houver falha.



## ⚡ **Resumo Rápido**

✅ **Use porta 6543 (pooler)** para rodar normalmente.
⚙️ **Use 5432 (direto)** apenas para **criar tabelas (DDL)** — containers sem IPv6 podem falhar.
💡 **Solução estável:** utilizar `host.pooler.supabase.com` na **porta 6543**.


**Alternância LOCAL ↔ CLOUD confiável usando apenas `DB_MODE`, com logs e validações consistentes. ✅**
