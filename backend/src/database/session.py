"""
📄 session.py
Módulo responsável pela configuração da conexão com o banco de dados PostgreSQL
usando SQLAlchemy para gerenciamento de sessões e engine.

👉 Padrão seguido:
- Código limpo, comentado e modular
- Facilidade de integração com os serviços e modelos do projeto
- Suporta conexão LOCAL ou CLOUD (Supabase)
- Importa automaticamente o schema do banco (schema_postgres.sql) **APENAS QUANDO CHAMADO**
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv, find_dotenv
import os

# 🔧 Carrega variáveis de ambiente do arquivo .env (robusto, funciona a partir de subpastas)
load_dotenv(find_dotenv(), override=False)

# ============================================================
# 🌐 SELEÇÃO DO BANCO DE DADOS
# ============================================================
DB_MODE = os.getenv("DB_MODE", "LOCAL").upper()

# URLs definidas no .env
DATABASE_URL_LOCAL = os.getenv(
    "DATABASE_URL_LOCAL",
    "postgresql://postgres:senha@localhost:5432/restaurant_analytics"
)
DATABASE_URL_CLOUD = os.getenv(
    "DATABASE_URL_CLOUD",
    "postgresql://postgres:senha@host.supabase.co:5432/postgres?sslmode=require"
)

# Seleciona a URL de conexão com base no modo
DATABASE_URL = DATABASE_URL_CLOUD if DB_MODE == "CLOUD" else DATABASE_URL_LOCAL

# ============================================================
# ⚙️ Criação da engine do SQLAlchemy
# ============================================================
# Observação:
# - Para Supabase, o parâmetro 'sslmode=require' já está embutido na URL.
# - Mantenha echo=False para não poluir logs; ligue para depuração.
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,  # melhora resiliência a conexões ociosas
)

# ============================================================
# 🧱 Base declarativa usada pelos modelos ORM (models.py)
# ============================================================
Base = declarative_base()

# ============================================================
# 🧩 Criação da sessão para interação com o banco
# ============================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ============================================================
# 🔄 Dependência FastAPI para fornecer sessão de banco
# ============================================================
def get_db():
    """
    🔄 Fornece sessão do banco para rotas FastAPI
    Fecha automaticamente após o uso
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# 🧪 Função auxiliar para testar a conexão
# ============================================================
def test_connection():
    """
    🔧 Testa a conexão com o banco de dados ativo
    Retorna ✅ se OK, ❌ se houver erro
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexão OK:", result.scalar())
    except Exception as e:
        print("❌ Erro de conexão:", e)

# ============================================================
# 📄 Função para importar schema do banco
# ============================================================
def import_schema(schema_file: str = "data/schema_postgres.sql"):
    """
    🔧 Importa o schema SQL no banco selecionado (LOCAL ou CLOUD)
    ⚠️ schema_file: caminho relativo ao arquivo .sql
    - Usa exec_driver_sql para permitir múltiplas instruções em um único arquivo
    - NÃO é chamada automaticamente na importação do módulo
    """
    if not os.path.exists(schema_file):
        print(f"❌ Arquivo de schema não encontrado: {schema_file}")
        return

    print(f"📂 Importando schema do arquivo: {schema_file}")
    try:
        with open(schema_file, "r", encoding="utf-8") as f:
            sql_commands = f.read()

        # Dica: para schemas idempotentes, use IF NOT EXISTS nas DDLs.
        with engine.connect() as conn:
            conn.exec_driver_sql(sql_commands)
            conn.commit()

        print("✅ Schema importado com sucesso!")
    except Exception as e:
        print("❌ Erro ao importar schema:", e)
