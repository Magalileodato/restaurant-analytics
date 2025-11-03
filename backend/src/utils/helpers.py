# ============================================================
# 🧰 HELPERS / FUNÇÕES UTILITÁRIAS EXTENDIDAS
# ============================================================
# Projeto: Restaurant Analytics MVP
# Desenvolvedora: Magali Leodato
# Descrição: Funções utilitárias reutilizáveis em todo o backend,
#             incluindo suporte a métricas de vendas, produtos,
#             clientes e dashboards.
# ============================================================

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# ============================================================
# 📅 FORMATAÇÃO DE DATAS
# ============================================================
def format_datetime(dt: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Converte datetime para string formatada"""
    if dt is None:
        return ""
    return dt.strftime(fmt)

def parse_datetime(date_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Converte string formatada para datetime"""
    try:
        return datetime.strptime(date_str, fmt)
    except ValueError:
        return None

def date_range(days: int = 7) -> tuple[datetime, datetime]:
    """
    Retorna um intervalo de datas do dia atual até 'days' atrás
    """
    end = datetime.now()
    start = end - timedelta(days=days)
    return start, end

# ============================================================
# 🧮 CÁLCULOS FINANCEIROS E MÉTRICAS
# ============================================================
def calculate_total(items: List[Dict[str, Any]]) -> float:
    """Calcula o total a partir de uma lista de itens com 'quantity' e 'price'"""
    return sum(item.get("quantity", 0) * item.get("price", 0.0) for item in items)

def calculate_discounted_total(total: float, discount: float = 0.0) -> float:
    """Aplica desconto percentual sobre o total"""
    return total * (1 - discount / 100)

def calculate_ticket_average(sales: List[Dict[str, Any]]) -> float:
    """Calcula o ticket médio a partir de uma lista de vendas"""
    if not sales:
        return 0.0
    total_amount = sum(sale.get("total_amount", 0.0) for sale in sales)
    return total_amount / len(sales)

def sum_by_key(data: List[Dict[str, Any]], key: str) -> float:
    """Soma os valores de uma lista de dicionários por uma chave específica"""
    return sum(d.get(key, 0.0) for d in data)

# ============================================================
# 🔍 FUNÇÕES AUXILIARES
# ============================================================
def safe_get(d: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Acessa um dicionário com segurança, retornando default se a chave não existir"""
    return d.get(key, default)

def is_valid_email(email: str) -> bool:
    """Valida email simples"""
    return "@" in email and "." in email

def top_selling_products(sales_items: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Retorna os produtos mais vendidos a partir de uma lista de itens de vendas
    Cada item deve ter 'product_id', 'name' e 'quantity'
    """
    from collections import defaultdict

    counter: dict[int, float] = defaultdict(float)
    product_info: dict[int, dict[str, Any]] = {}
    for item in sales_items:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 0)
        if product_id is None:
            continue
        counter[product_id] += quantity
        if product_id not in product_info:
            product_info[product_id] = {"product_id": product_id, "name": item.get("name", "")}

    # Ordena e retorna os top N
    sorted_products = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:top_n]
    result: List[Dict[str, Any]] = []
    for product_id, qty in sorted_products:
        info = product_info.get(product_id, {})
        info["quantity_sold"] = qty
        result.append(info)
    return result

def group_sales_by_key(sales: List[Dict[str, Any]], key: str) -> dict[Any, List[Dict[str, Any]]]:
    """
    Agrupa vendas ou itens por uma chave específica
    """
    grouped: dict[Any, List[Dict[str, Any]]] = {}
    for sale in sales:
        k = sale.get(key)
        if k not in grouped:
            grouped[k] = []
        grouped[k].append(sale)
    return grouped

# ============================================================
# 💡 OBSERVAÇÕES
# ============================================================
# - Compatível com Python 3.11+ usando tuple[...] e X | None
# - Use este arquivo para funções que serão reutilizadas em
#   analytics_service.py e routes/*.py
# ============================================================
