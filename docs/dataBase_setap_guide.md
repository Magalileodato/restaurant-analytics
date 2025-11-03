# 🍽️ Restaurant Analytics MVP

## 🧭 Database Setup Guide (PostgreSQL + Docker)

Este documento explica **como configurar e popular o banco de dados** do projeto **Restaurant Analytics MVP**, garantindo que o ambiente funcione corretamente tanto no backend (FastAPI) quanto no frontend (Dashboard JS).



## 📘 1. Introdução

O projeto utiliza **PostgreSQL** dentro de um contêiner Docker chamado `restaurant-analytics-db`.
O banco principal é `appdb` e armazena dados de vendas, produtos e métricas analíticas que alimentam os dashboards.

**Objetivo:**
Permitir que qualquer pessoa consiga recriar o banco de dados e testar todos os endpoints do backend do zero.



## 🧱 2. Conexão com o Banco

Execute o comando abaixo para acessar o PostgreSQL dentro do contêiner:

```bash
docker exec -it restaurant-analytics-db psql -U postgres -d appdb
```

Ao entrar, você verá o prompt:

```
appdb=#
```


## 🗃️ 3. Estrutura das Tabelas Principais

| Tabela                                    | Descrição                                               |
| ----------------------------------------- | ------------------------------------------------------- |
| **sales**                                 | Armazena as vendas realizadas, valores totais e status  |
| **product_sales**                         | Registra os produtos vendidos por cada venda            |
| **item_product_sales**                    | Detalha os itens (opções, complementos) de cada produto |
| **delivery_sales**                        | Informações de entregas associadas às vendas            |
| **items / products / customers / stores** | Tabelas auxiliares com relacionamentos                  |


## 🧩 4. Principais Comandos de Verificação

Ver estrutura da tabela:

```sql
\d sales;
\d product_sales;
\d item_product_sales;
```

Visualizar registros:

```sql
SELECT * FROM sales LIMIT 5;
SELECT * FROM product_sales LIMIT 5;
SELECT * FROM item_product_sales LIMIT 5;
```

Contar registros:

```sql
SELECT COUNT(*) FROM sales;
```


## 🧮 5. Ajustes Importantes nas Tabelas

Adicionar coluna **rating** (caso não exista) e preencher com notas aleatórias entre 0 e 5 para permitir cálculo de avaliação média:

```sql
ALTER TABLE sales ADD COLUMN rating numeric(3,2);
UPDATE sales SET rating = ROUND((RANDOM() * 5)::numeric, 2);
```


## 🧰 6. População de Dados de Teste

O banco pode ser populado manualmente via SQL ou por scripts Python.

### Exemplo de inserção mínima:

```sql
INSERT INTO sales (id, store_id, channel_id, created_at, sale_status_desc, total_amount_items, total_amount)
VALUES (1, 1, 1, NOW(), 'COMPLETED', 3, 85.50);

INSERT INTO product_sales (id, sale_id, product_id, quantity, base_price, total_price)
VALUES (1, 1, 10, 2, 40.00, 80.00);
```


## 📊 7. Testando os Endpoints (Backend)

Com o backend rodando em `http://localhost:8000`, execute:

```bash
curl -s "http://localhost:8000/metrics/total-revenue?date_from=2000-01-01&date_to=2100-01-01" | python -m json.tool
curl -s "http://localhost:8000/metrics/average-ticket?date_from=2000-01-01&date_to=2100-01-01" | python -m json.tool
curl -s "http://localhost:8000/metrics/total-orders?date_from=2000-01-01&date_to=2100-01-01" | python -m json.tool
curl -s "http://localhost:8000/metrics/average-rating?date_from=2000-01-01&date_to=2100-01-01" | python -m json.tool
curl -s "http://localhost:8000/metrics/top-products?limit=5&date_from=2000-01-01&date_to=2100-01-01" | python -m json.tool
```

✅ **Respostas esperadas:**

```json
{
  "total": 12500.50
}
{
  "avg_ticket": 42.75
}
{
  "total_orders": 293
}
{
  "average_rating": 3.74
}
{
  "data": [
    {"product_id": 1, "product_name": "Pizza Calabresa", "total_sold": 120, "total_revenue": 5400.0}
  ]
}
```


## 🧩 11. Execução e Verificação do Ambiente Docker

### 1️⃣ Verifique o modo do banco

Abra `infra/.env`
Escolha:

```bash
DB_MODE=LOCAL     # ou CLOUD
```

Isso define se o backend usa o banco **local (Postgres Docker)** ou o **Supabase**.

---

### 🐳 2️⃣ Suba os containers

Na pasta `infra`, execute:

```bash
docker compose down -v
docker compose up -d --build
```

Isso recompila e sobe **frontend + backend + db** com o ambiente atualizado.

---

### 📋 3️⃣ Confirme o status

```bash
docker compose ps
```

✅ Esperado:

```
restaurant-analytics-frontend   Up   0.0.0.0:3000->80/tcp
restaurant-analytics-backend    Up   0.0.0.0:8000->8000/tcp
restaurant-analytics-db         Up   5432/tcp
```


### 🧠 4️⃣ Verifique logs do backend

```bash
docker compose logs -f backend
```

✅ Deve aparecer:

```
✅ Conexão OK: 1
Application startup complete
```


### 🌐 5️⃣ Acesse o dashboard

Abra no navegador:

```
http://localhost:3000
```

✅ O dashboard deve carregar com os valores reais do banco e o gráfico de produtos.


### 🧾 6️⃣ Teste direto via terminal (opcional)

```bash
curl "http://localhost:8000/metrics/total-revenue?date_from=2000-01-01&date_to=2100-01-01"
```

✅ Deve retornar:

```json
{"total_revenue": 12345.67}
```


### 🔁 7️⃣ Testar alternância LOCAL ↔ CLOUD

Pare tudo:

```bash
docker compose down
```

Edite `.env`:

```bash
DB_MODE=CLOUD
```

Suba novamente:

```bash
docker compose up -d --build
```

Reabra o dashboard e veja se os dados vêm do **Supabase**.


### 🧩 Testes rápidos de backend

Após ajustes:

```bash
docker compose build --no-cache backend
docker compose up -d backend
docker compose logs -f backend
```

Valide as rotas:

```bash
curl -s "http://localhost:8000/metrics/total-revenue" | python -m json.tool
curl -s "http://localhost:8000/metrics/average-ticket" | python -m json.tool
curl -s "http://localhost:8000/metrics/top-products?limit=5" | python -m json.tool
```


## ✅ Conclusão

Se o dashboard abrir e as métricas aparecerem sem erro, o ambiente está **100% integrado** — backend, frontend e banco (local ou cloud).
Este guia cobre toda a configuração necessária para que novos desenvolvedores iniciem o projeto do zero com sucesso.
