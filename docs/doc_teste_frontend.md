============================================================
🌐 TESTE DO FRONTEND – RESTAURANT ANALYTICS
============================================================
Autor: Magali Leodato
Projeto: Restaurant Analytics MVP
Descrição:
- Verificação do frontend (interface React/Vite ou Next.js)
- Passos separados para ambiente LOCAL e SUPABASE (CLOUD)
============================================================


============================================================
🧩 1️⃣ TESTE NO AMBIENTE LOCAL
============================================================
🧱 Passo 1 – Verificar containers ativos

Abra o terminal na pasta infra e execute:

cd ~/Desktop/restaurant-analytics/infra
docker compose ps


✅ Deve aparecer algo como:

NAME                 COMMAND                  STATE   PORTS
infra-backend-1      "uvicorn src.main:app…"  Up      0.0.0.0:8000->8000/tcp
infra-frontend-1     "npm run dev"            Up      0.0.0.0:5173->5173/tcp
infra-db-1           "docker-entrypoint.s…"   Up      5432/tcp

🧠 Passo 2 – Verificar backend antes do front

Abra o navegador e acesse:

http://localhost:8000/


Se aparecer:

{"message": "API Restaurant Analytics - OK"}


➡️ O backend está pronto.

💻 Passo 3 – Abrir o frontend

Abra:

http://localhost:5173/


✅ Verifique:

O dashboard carrega sem erro.

Gráficos ou cards mostram valores (ex: Receita, Ticket Médio etc.).

Não aparece erro 500 ou “Failed to fetch”.

Se os dados não aparecerem:

Atualize a página (F5).

Confira se o generate_sales.py foi rodado com sucesso (ver doc do DB).

Veja o console do navegador (F12 → aba Console):

Se aparecer CORS error → backend pode não estar com localhost:5173 liberado.

Se aparecer Network Error → verifique se http://localhost:8000 está acessível.

⚙️ Passo 4 – Testar endpoints diretamente

Para confirmar que o frontend lê do backend corretamente:

curl -X POST http://localhost:8000/metrics/total-revenue \
     -H "Content-Type: application/json" \
     -d '{"date_from":"2025-05-01","date_to":"2025-05-31"}'


Deve retornar um valor numérico (ex: {"total_revenue": 12345.67}).

🎯 Resultado esperado

Dashboard carrega.

Cards mostram valores.

Backend responde corretamente às requisições /metrics e /dashboard.

============================================================
☁️ 2️⃣ TESTE NO AMBIENTE SUPABASE (CLOUD)
============================================================
🔧 Passo 1 – Ajustar .env para MODO CLOUD
cd ~/Desktop/restaurant-analytics/infra
sed -i 's/^DB_MODE=.*/DB_MODE=CLOUD/' .env


Exemplo da URL no .env:

DATABASE_URL_CLOUD=postgresql://postgres:SEU_TOKEN@NOMEDOPROJETO.supabase.co:5432/postgres?sslmode=require


Recrie a stack:

docker compose --env-file .env up -d --build

🌍 Passo 2 – Confirmar backend conectado ao Supabase

Acesse:

http://localhost:8000/


Se aparecer:

{"message": "API Restaurant Analytics - OK"}


→ API está rodando.

Agora teste:

curl -X POST http://localhost:8000/metrics/total-revenue \
     -H "Content-Type: application/json" \
     -d '{"date_from":"2025-05-01","date_to":"2025-05-31"}'


✅ Se retornar valores → backend está conectado ao banco do Supabase.

💻 Passo 3 – Abrir o frontend

Acesse novamente:

http://localhost:5173/


✅ Verifique:

O dashboard carrega dados (mesmos gráficos do local).

O console do navegador (F12 → Console) não mostra erro de conexão.

Os cards de receita e vendas exibem valores do Supabase.

🧩 Passo 4 – Testes rápidos

Filtre o dashboard por período diferente (ex: últimos 30 dias).

Atualize a página.

Veja se os números mudam conforme os dados do Supabase (indicando leitura real da cloud).

🚦 Resultado esperado

Frontend renderiza normalmente.

API responde com dados do Supabase.

Métricas e dashboards exibem valores consistentes.

============================================================
🧭 3️⃣ RESUMO FINAL
Ambiente	Banco	Verificação	URL Front	Resultado Esperado
LOCAL	Postgres (Docker)	python generate_sales.py	http://localhost:5173
	Dashboard com dados simulados
CLOUD	Supabase	SQL Editor + seed SQL	http://localhost:5173
	Dashboard com dados reais do Supabase
============================================================
🧹 4️⃣ LIMPEZA E REBUILD (opcional)
docker compose down -v
docker system prune -a --volumes
docker compose --env-file .env up -d --build

============================================================
✅ CONCLUSÃO

Se o frontend carrega corretamente nas duas URLs (localhost:5173 e backend :8000), o sistema está 100% operacional.

Diferença principal:

LOCAL → banco rodando no container db.

SUPABASE → banco remoto na nuvem.