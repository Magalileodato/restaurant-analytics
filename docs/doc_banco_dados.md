# ============================================================
# 🗄️ GUIA DE BANCO DE DADOS – RESTAURANT ANALYTICS
# ============================================================
# Autor: Magali Leodato
# Projeto: Restaurant Analytics MVP
# Descrição:
#   - Como criar e popular o banco **LOCAL** (Docker/Postgres)
#   - Como criar e popular o banco **CLOUD** (Supabase)
#   - Testes rápidos de API e dicas de troubleshooting
# Observações:
#   - O schema está em `data/schema_postgres.sql`
#   - O gerador está em `data/generate_sales.py`
# ============================================================


## ============================================================
## 📂 Estrutura relevante do projeto
## ============================================================
- `infra/docker-compose.yml`  → Stack (backend, frontend, db)
- `infra/.env`                → Config do ambiente (DB_MODE e URLs)
- `data/schema_postgres.sql`  → DDL (criação de tabelas)
- `data/generate_sales.py`    → Seed de dimensões + vendas/itens/pagamentos


## ============================================================
## ✅ Pré-requisitos
## ============================================================
- Docker + Docker Compose
- Git Bash (Windows) ou Terminal
- VS Code (opcional)
- **Não** commitar chaves em `.env`


## ============================================================
## 🧪 MODO LOCAL (Docker/Postgres interno)
## ============================================================

### 1) Entrar na pasta do compose
```bash
cd ~/Desktop/restaurant-analytics/infra

2) Garantir .env para LOCAL
sed -i 's/^DB_MODE=.*/DB_MODE=LOCAL/' .env
sed -i 's#^DATABASE_URL_LOCAL=.*#DATABASE_URL_LOCAL=postgresql://postgres:postgres@db:5432/appdb#' .env

3) Subir/Recriar a stack
docker compose down
docker compose --env-file .env up -d --build

4) Aplicar o schema (DDL) no banco LOCAL

Roda dentro do container do backend, usando a função auxiliar.

MSYS_NO_PATHCONV=1 docker compose exec backend \
  python -c "from src.database.session import import_schema; import_schema('data/schema_postgres.sql')"

5) Popular com dados (dimensões + 50 vendas)
MSYS_NO_PATHCONV=1 docker compose exec backend \
  python /app/data/generate_sales.py --rows 50 --months 6


Saída esperada:

🌍 Modo: LOCAL | Conexão: db:5432/appdb
🧱 Seeding dimensões...
✅ Dimensões OK.
🧾 Gerando 50 vendas em 6 meses...
✅ Vendas/itens/pagamentos inseridos com sucesso.
🏁 Pronto. Teste as rotas /metrics e o dashboard.

============================================================
☁️ MODO CLOUD (Supabase)
============================================================
1) Ajustar .env para CLOUD

Use a DATABASE_URL_CLOUD do Supabase com sslmode=require.

cd ~/Desktop/restaurant-analytics/infra
sed -i 's/^DB_MODE=.*/DB_MODE=CLOUD/' .env
# Exemplo (NÃO cole credenciais reais aqui):
# sed -i 's#^DATABASE_URL_CLOUD=.*#DATABASE_URL_CLOUD=postgresql://postgres:*****@PROJECTREF.supabase.co:5432/postgres?sslmode=require#' .env
docker compose --env-file .env up -d --build

2) Criar o schema no Supabase (SQL Editor)

Abra Supabase Studio → SQL Editor → New query

Cole e rode o conteúdo de data/schema_postgres.sql (criação das tabelas).

3) Popular dados no Supabase (SQL Editor)

Ainda no SQL Editor, cole e rode em ordem:

3.1) Dimensões mínimas (idempotente):

-- brands / sub_brands / channels / stores / categories / products / items / payment_types
INSERT INTO brands (name)
SELECT 'Marca X'
WHERE NOT EXISTS (SELECT 1 FROM brands WHERE name='Marca X');

INSERT INTO sub_brands (brand_id, name)
SELECT b.id, x.name
FROM brands b
JOIN (VALUES ('SubMarca A'), ('SubMarca B')) AS x(name) ON TRUE
WHERE b.name='Marca X'
  AND NOT EXISTS (
    SELECT 1 FROM sub_brands s WHERE s.brand_id=b.id AND s.name=x.name
  );

INSERT INTO channels (brand_id, name, description, type)
SELECT b.id, c.name, c.descr, c.t
FROM brands b
JOIN (VALUES
  ('Presencial','Loja física','P'),
  ('iFood','Marketplace iFood','D'),
  ('Rappi','Marketplace Rappi','D'),
  ('App Próprio','Delivery próprio','D')
) AS c(name, descr, t) ON TRUE
WHERE b.name='Marca X'
  AND NOT EXISTS (
    SELECT 1 FROM channels ch WHERE ch.brand_id=b.id AND ch.name=c.name
  );

INSERT INTO stores (brand_id, sub_brand_id, name, city, state, district, is_active, is_own, creation_date)
SELECT b.id, sb.id, s.name, s.city, s.state, s.district, TRUE, TRUE, CURRENT_DATE
FROM brands b
JOIN sub_brands sb ON sb.brand_id=b.id
JOIN (VALUES
  ('Loja Centro','Rio de Janeiro','RJ','Centro'),
  ('Loja Zona Sul','Rio de Janeiro','RJ','Ipanema'),
  ('Loja Niterói','Niterói','RJ','Icaraí'),
  ('Loja Tijuca','Rio de Janeiro','RJ','Tijuca')
) AS s(name, city, state, district) ON TRUE
WHERE b.name='Marca X'
  AND NOT EXISTS (
    SELECT 1 FROM stores st
     WHERE st.brand_id=b.id AND st.sub_brand_id=sb.id AND st.name=s.name
  );

INSERT INTO categories (brand_id, sub_brand_id, name, type)
SELECT b.id, sb.id, c.name, 'P'
FROM brands b
JOIN sub_brands sb ON sb.brand_id=b.id
JOIN (VALUES ('Lanches'), ('Bebidas'), ('Sobremesas')) AS c(name) ON TRUE
WHERE b.name='Marca X'
  AND NOT EXISTS (
    SELECT 1 FROM categories ct
     WHERE ct.brand_id=b.id AND ct.sub_brand_id=sb.id AND ct.name=c.name
  );

-- Products Lanches
INSERT INTO products (brand_id, sub_brand_id, category_id, name)
SELECT b.id, sb.id, ct.id, p.name
FROM brands b
JOIN sub_brands sb ON sb.brand_id=b.id
JOIN categories ct ON ct.brand_id=b.id AND ct.sub_brand_id=sb.id AND ct.name='Lanches'
JOIN (VALUES ('Hambúrguer Clássico'), ('Hambúrguer Duplo'), ('Batata Média')) AS p(name) ON TRUE
WHERE b.name='Marca X'
  AND NOT EXISTS (
    SELECT 1 FROM products pr
     WHERE pr.brand_id=b.id AND pr.sub_brand_id=sb.id AND pr.category_id=ct.id AND pr.name=p.name
  );

-- Products Bebidas
INSERT INTO products (brand_id, sub_brand_id, category_id, name)
SELECT b.id, sb.id, ct.id, p.name
FROM brands b
JOIN sub_brands sb ON sb.brand_id=b.id
JOIN categories ct ON ct.brand_id=b.id AND ct.sub_brand_id=sb.id AND ct.name='Bebidas'
JOIN (VALUES ('Refrigerante Lata'), ('Água Mineral'), ('Suco Natural')) AS p(name) ON TRUE
WHERE b.name='Marca X'
  AND NOT EXISTS (
    SELECT 1 FROM products pr
     WHERE pr.brand_id=b.id AND pr.sub_brand_id=sb.id AND pr.category_id=ct.id AND pr.name=p.name
  );

-- Products Sobremesas
INSERT INTO products (brand_id, sub_brand_id, category_id, name)
SELECT b.id, sb.id, ct.id, p.name
FROM brands b
JOIN sub_brands sb ON sb.brand_id=b.id
JOIN categories ct ON ct.brand_id=b.id AND ct.sub_brand_id=sb.id AND ct.name='Sobremesas'
JOIN (VALUES ('Milkshake Chocolate'), ('Pudim da Casa')) AS p(name) ON TRUE
WHERE b.name='Marca X'
  AND NOT EXISTS (
    SELECT 1 FROM products pr
     WHERE pr.brand_id=b.id AND pr.sub_brand_id=sb.id AND pr.category_id=ct.id AND pr.name=p.name
  );

-- Items (adicionais)
INSERT INTO items (brand_id, sub_brand_id, category_id, name)
SELECT b.id, sb.id, ct.id, i.name
FROM brands b
JOIN sub_brands sb ON sb.brand_id=b.id
JOIN categories ct ON ct.brand_id=b.id AND ct.sub_brand_id=sb.id AND ct.name='Lanches'
JOIN (VALUES ('Queijo Extra'), ('Bacon'), ('Molho Especial')) AS i(name) ON TRUE
WHERE b.name='Marca X'
  AND NOT EXISTS (
    SELECT 1 FROM items it
     WHERE it.brand_id=b.id AND it.sub_brand_id=sb.id AND it.category_id=ct.id AND it.name=i.name
  );

-- Payment Types
INSERT INTO payment_types (brand_id, description)
SELECT b.id, pt.pt_descr
FROM brands b
JOIN (VALUES ('Crédito'), ('Débito'), ('PIX'), ('Dinheiro')) AS pt(pt_descr) ON TRUE
WHERE b.name='Marca X'
  AND NOT EXISTS (
    SELECT 1 FROM payment_types p WHERE p.brand_id=b.id AND p.description=pt.pt_descr
  );


3.2) Gerar 50 vendas (sales + product_sales + payments):
Use o script completo “Seed 50 Vendas (SQL)” que preparamos (com tabelas temporárias).

Arquivo sugerido: docs/sql/seed_50_vendas.sql
(Cole no SQL Editor e execute após as dimensões.)

============================================================
🔍 Testes rápidos de API (Local)
============================================================
Liveness
curl -s http://localhost:8000/

Endpoints principais (POST)

Git Bash (curl ≥ 7.82):

curl --json '{"date_from":"2025-05-01","date_to":"2025-05-31"}' \
  http://localhost:8000/metrics/total-revenue

curl --json '{"date_from":"2025-05-01","date_to":"2025-05-31"}' \
  http://localhost:8000/metrics/average-ticket

curl --json '{"date_from":"2025-05-01","date_to":"2025-05-31","limit":5}' \
  http://localhost:8000/metrics/top-products

curl --json '{"current_from":"2025-05-01","current_to":"2025-05-31","prev_from":"2025-04-01","prev_to":"2025-04-30"}' \
  http://localhost:8000/dashboard/dashboard-summary


PowerShell:

$b=@{date_from='2025-05-01';date_to='2025-05-31'}|ConvertTo-Json
Invoke-RestMethod -Uri 'http://localhost:8000/metrics/total-revenue' -Method POST -ContentType 'application/json' -Body $b

============================================================
🛠️ Troubleshooting rápido
============================================================

password authentication failed for user "postgres"
→ Verifique POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB no docker-compose.yml e a DATABASE_URL_LOCAL no .env.

could not translate host name "db.PROJECTREF.supabase.co"
→ Use o host correto do Supabase no .env (...@PROJECTREF.supabase.co:5432/postgres?sslmode=require). Não adicione db. antes do domínio do Supabase.

relation "brands" does not exist
→ Rode o passo 

4) Aplicar o schema (DDL) antes de popular.

Frontend vazio
→ Confirme se existem vendas no período; ajuste date_from/date_to na chamada.

============================================================
✅ Conclusão
============================================================

LOCAL: subir stack → aplicar schema → rodar generate_sales.py → testar rotas.

CLOUD (Supabase): aplicar schema_postgres.sql no SQL Editor → rodar os 2 scripts (dimensões e “Seed 50 Vendas (SQL)”) → apontar DB_MODE=CLOUD no .env para o backend consumir.
