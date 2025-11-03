# ============================================================
# 🧭 ROTAS DE DASHBOARD
# ============================================================
# Projeto: Restaurant Analytics MVP
# Desenvolvedora: Magali Leodato
# Descrição: Endpoints para dashboards personalizados e
#             agregações de métricas
# ============================================================

from fastapi import APIRouter
from typing import List, Dict, Any
from src.services import analytics_service # ✅ import absoluto

router = APIRouter()

# ============================================================
# 🔥 ENDPOINTS
# ============================================================

@router.get("/dashboard-summary")
def get_dashboard_summary(
    sales: List[Dict[str, Any]],
    sales_items: List[Dict[str, Any]]
):
    """
    Retorna um resumo do dashboard com métricas principais:
    - Faturamento total
    - Ticket médio
    - Produtos mais vendidos
    """
    return {
        "total_revenue": analytics_service.total_revenue(sales),
        "average_ticket": analytics_service.average_ticket(sales),
        "top_products": analytics_service.top_products(sales_items),
    }

# ============================================================
# 💡 OBSERVAÇÕES
# ============================================================
# - Endpoint pronto para consumo pelo frontend (JS / HTML)
# - Permite expansão futura com filtros por canal, loja e período
# ============================================================
