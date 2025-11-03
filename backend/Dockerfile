# ============================================================
# 🐳 DOCKERFILE PARA BACKEND FASTAPI
# ============================================================
# Projeto: Restaurant Analytics MVP
# Desenvolvedora: Magali Leodato
# Descrição: Container do backend FastAPI, Python 3.11,
#             com SQLAlchemy, PostgreSQL e scripts de geração
#             de vendas fictícias.
# ============================================================

# 🧩 Imagem base com Python 3.11
FROM python:3.11-slim

# ============================================================
# 🌐 DEFINIÇÃO DE VARIÁVEIS DE AMBIENTE
# ============================================================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ============================================================
# 📂 CRIAR DIRETÓRIO DO APP
# ============================================================
WORKDIR /app

# ============================================================
# 📦 COPIAR ARQUIVOS DE DEPENDÊNCIAS
# ============================================================
COPY requirements.txt .

# ============================================================
# 🔧 INSTALAR DEPENDÊNCIAS
# ============================================================
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ============================================================
# 📂 COPIAR CÓDIGO DO BACKEND
#   (o docker-compose monta ../backend -> /app, mas manter COPY
#    garante build em ambientes sem bind-mount)
# ============================================================
COPY src ./src

# (Opcional) Se quiser embutir scripts/SQL no image:
# COPY data ./data

# ============================================================
# 🌐 DEFINIR PORTA DE EXPOSIÇÃO
# ============================================================
EXPOSE 8000

# ============================================================
# 🔥 COMANDO PARA RODAR A API FASTAPI (sem --reload)
# ============================================================
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================================
# 💡 OBSERVAÇÕES
# ============================================================
# - Para desenvolvimento com hot-reload, use override no docker-compose:
#   command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
# - Em produção, mantenha este CMD sem --reload.
# ============================================================
