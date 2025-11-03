# ============================================================
# 📈 ROTAS DE MÉTRICAS
# ============================================================
# Projeto: Restaurant Analytics MVP
# Desenvolvedora: Magali Leodato
# Descrição: Endpoints para métricas de vendas, ticket médio
#            e produtos mais vendidos (GET com query string).
# ============================================================

from typing import Optional
from fastapi import APIRouter, Query
from src.services import analytics_service  # ✅ import absoluto

router = APIRouter()

# ============================================================
# 🔥 ENDPOINTS (GET)
# - Todos recebem date_from / date_to via query string (OPCIONAIS)
# - Parâmetro channel também é opcional
# - As respostas usam chaves esperadas pelo frontend:
#   total → {"total": ...}
#   average-ticket → {"avg_ticket": ...}
#   top-products → {"data": [...]}
# ============================================================

@router.get("/total-revenue")
def get_total_revenue(
    date_from: Optional[str] = Query(None, description="YYYY-MM-DD (opcional)"),
    date_to: Optional[str]   = Query(None, description="YYYY-MM-DD (opcional)"),
    channel: Optional[str]   = Query(None, description="P ou D (opcional)"),
):
    """Retorna o faturamento total no intervalo."""
    total = analytics_service.total_revenue(
        date_from=date_from,
        date_to=date_to,
        channel=channel,
    )
    return {"total": float(total or 0.0)}  # 👈 chave alinhada ao frontend


@router.get("/average-ticket")
def get_average_ticket(
    date_from: Optional[str] = Query(None, description="YYYY-MM-DD (opcional)"),
    date_to: Optional[str]   = Query(None, description="YYYY-MM-DD (opcional)"),
    channel: Optional[str]   = Query(None, description="P ou D (opcional)"),
):
    """Retorna o ticket médio no intervalo."""
    avg = analytics_service.average_ticket(
        date_from=date_from,
        date_to=date_to,
        channel=channel,
    )
    return {"avg_ticket": float(avg or 0.0)}  # 👈 chave alinhada ao frontend


@router.get("/top-products")
def get_top_products(
    date_from: Optional[str] = Query(None, description="YYYY-MM-DD (opcional)"),
    date_to: Optional[str]   = Query(None, description="YYYY-MM-DD (opcional)"),
    channel: Optional[str]   = Query(None, description="P ou D (opcional)"),
    limit: int               = Query(5, ge=1, le=50, description="Qtd de itens (1–50)"),
):
    """Retorna os produtos mais vendidos no intervalo."""
    rows = analytics_service.top_products(
        date_from=date_from,
        date_to=date_to,
        channel=channel,
        limit=limit,
    )
    # Normaliza saída para o frontend
    data = [
        {
            "product_id": (
                r.get("product_id") if isinstance(r, dict) else r[0]
            ),
            "product_name": (
                r.get("product_name") if isinstance(r, dict) else r[1]
            ),
            "total_sold": float(
                r.get("total_sold", 0) if isinstance(r, dict) else r[2]
            ),
            "total_revenue": float(
                r.get("total_revenue", 0) if isinstance(r, dict) else r[3]
            ),
        }
        for r in (rows or [])
    ]
    return {"data": data}

# ============================================================
# 🔥 ENDPOINTS EXTRAS (GET)
# - total-orders
# - average-rating
# ============================================================

@router.get("/total-orders")
def get_total_orders(
    date_from: str,
    date_to: str,
    channel: Optional[str] = None,
):
    qty = analytics_service.total_orders(
        date_from=date_from,
        date_to=date_to,
        channel=channel,
    )
    return {"total_orders": float(qty or 0.0)}


@router.get("/average-rating")
def get_average_rating(
    date_from: str,
    date_to: str,
    channel: Optional[str] = None,
):
    avg = analytics_service.average_rating(
        date_from=date_from,
        date_to=date_to,
        channel=channel,
    )
    return {"average_rating": float(avg or 0.0)}


# ============================================================
# 💡 OBSERVAÇÕES
# ============================================================
# - Os serviços do analytics_service NÃO recebem 'db' por parâmetro.
# - Parâmetros vêm por query string para facilitar fetch/cURL e Swagger.
# - date_from/date_to podem ser opcionais na maioria dos endpoints; os extras
#   acima foram definidos como obrigatórios conforme solicitado.
# - O serviço tenta várias colunas de data e, se não houver coluna compatível,
#   executa sem filtro de datas (comportamento tolerante).
# ============================================================
