# ============================================================
# 🖥️ ENTRY POINT DO BACKEND FASTAPI
# ============================================================
# Projeto: Restaurant Analytics MVP
# Desenvolvedora: Magali Leodato
# Descrição: Inicializa a API FastAPI, configura rotas,
#             middlewares e conexão com o banco PostgreSQL.
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 🔁 IMPORTS AJUSTADOS PARA PACOTE ABSOLUTO
from src.routes import metrics, dashboard
from src.database.session import engine, Base, test_connection

# ============================================================
# 🌐 INICIALIZAÇÃO DA API FASTAPI
# ============================================================
app = FastAPI(
    title="Restaurant Analytics MVP",
    description="API para dashboards e métricas de vendas de restaurantes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================
# 🔄 MIDDLEWARES (CORS)
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔧 Em produção, restrinja a origem (ex.: ['http://localhost:3000'])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 🗄️ CRIAR TABELAS NO BANCO
# ============================================================
# ⚠️ Opcional: em CLOUD geralmente o schema já existe; em LOCAL é útil.
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Base.metadata.create_all executado (se tabelas não existiam, foram criadas).")
except Exception as e:
    # Evita derrubar a API caso o banco remoto não permita DDL
    print("⚠️ create_all falhou (possível DDL bloqueada no CLOUD):", e)

# (Opcional) teste rápido de conexão no startup
try:
    ok = test_connection()
    print(f"✅ Conexão OK: {ok}")
except Exception as e:
    print("⚠️ Falha no teste de conexão (a API seguirá rodando):", e)

# ============================================================
# 🧭 INCLUIR ROTAS / ENDPOINTS
# ============================================================
# - Prefixos e tags padronizados
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# ============================================================
# 🔥 ENDPOINTS DE SAÚDE E RAIZ
# ============================================================
@app.get("/health")
def health():
    """Healthcheck simples para orquestração/monitoramento."""
    return {"status": "ok"}

@app.get("/")
def root():
    """Endpoint raiz para verificar se a API está rodando."""
    return {"message": "Restaurant Analytics MVP API está rodando!"}

# ============================================================
# 💡 OBSERVAÇÕES
# ============================================================
# - O arquivo backend/src/database/session.py deve conter a configuração
#   do SQLAlchemy (engine e sessionmaker) e a função test_connection().
# - As rotas devem ser organizadas em backend/src/routes/*.py.
# - Manter padrão de comentários e organização do projeto.
# ============================================================
