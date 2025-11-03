"""
🧱 init_db.py
Script para inicializar o banco de dados PostgreSQL.

👉 Este script cria todas as tabelas definidas em database/models.py
   utilizando as configurações e engine de database/session.py.
"""

from database.session import engine, Base
from database import models


def init_database():
    """
    ⚙️ Cria as tabelas no banco de dados, se ainda não existirem.
    """
    print("🚀 Iniciando criação das tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")


if __name__ == "__main__":
    init_database()
