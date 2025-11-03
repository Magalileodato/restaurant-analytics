# ============================================================
# 🐳 DOCKERFILE PARA FRONTEND (NGINX)
# ============================================================
# Projeto: Restaurant Analytics MVP
# Desenvolvedora: Magali Leodato
# Descrição: Container do frontend estático (HTML, CSS, JS)
#             servido via Nginx.
# ============================================================

# 🧩 Imagem base
FROM nginx:latest

# ============================================================
# 📂 COPIAR ARQUIVOS DO FRONTEND
# ============================================================
COPY ./frontend /usr/share/nginx/html

# ============================================================
# 🌐 EXPOR PORTA PADRÃO HTTP
# ============================================================
EXPOSE 80

# ============================================================
# 💡 OBSERVAÇÕES
# ============================================================
# - Este Dockerfile serve os arquivos HTML/CSS/JS do dashboard.
# - O Nginx é usado apenas como servidor estático.
# ============================================================
