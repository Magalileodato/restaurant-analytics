# ============================================================
# 🧮 SERVICE DE ANÁLISE / METRICS
# ============================================================
# Projeto: Restaurant Analytics MVP
# Desenvolvedora: Magali Leodato
# Descrição: Contém funções de análise de vendas, cálculo de
#            métricas e agregações, utilizando helpers.py.
# ============================================================

from typing import List, Dict, Any, Optional
from src.utils import helpers  # ✅ import absoluto

# 🔌 Acesso direto ao banco (LOCAL ou CLOUD)
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError, OperationalError
from src.database.session import engine  # ✅ usa a mesma engine do projeto


# ============================================================
# 🔧 HELPERS INTERNOS (SQL tolerante a variações de schema)
# ============================================================

# - Colunas candidatas para filtro de data em tabelas de vendas
DATE_CANDIDATES = ["created_at", "sale_date", "date", "order_date", "sold_at"]


def _scalar(sql: str, params: dict) -> float:
    """Executa uma consulta escalar e retorna float (com fallback 0.0)."""
    with engine.connect() as conn:
        res = conn.execute(text(sql), params)
        val = res.scalar()
        return float(val or 0.0)


def _rows(sql: str, params: dict) -> List[Dict[str, Any]]:
    """Executa uma consulta e retorna lista de dicts (com chaves minúsculas)."""
    with engine.connect() as conn:
        res = conn.execute(text(sql), params)
        cols = [c.lower() for c in res.keys()]
        data = [dict(zip(cols, row)) for row in res.fetchall()]
        return data


def _build_date_clause(table_alias: str, date_col: str) -> str:
    """Cria cláusula de data usando exatamente a coluna informada."""
    return (
        f"  AND (:date_from IS NULL OR {table_alias}.{date_col} >= :date_from)\n"
        f"  AND (:date_to   IS NULL OR {table_alias}.{date_col} <= :date_to)\n"
    )


def _try_scalar_with_datecols(base_no_date: str, table_alias: str, params: dict) -> float:
    """
    Tenta executar uma consulta escalar testando várias colunas de data.
    Se nenhuma existir, executa SEM filtro de data.
    """
    last_err: Optional[Exception] = None
    for col in DATE_CANDIDATES:
        sql = base_no_date + _build_date_clause(table_alias, col)
        try:
            return _scalar(sql, params)
        except (ProgrammingError, OperationalError) as e:
            last_err = e
            continue
    # Fallback: sem filtro de data
    try:
        return _scalar(base_no_date, params)
    except Exception as e:
        raise last_err or e


def _try_rows_with_datecols(base_no_date: str, table_alias: str, params: dict) -> List[Dict[str, Any]]:
    """
    Tenta executar uma consulta de linhas testando várias colunas de data.
    Se nenhuma existir, executa SEM filtro de data.
    """
    last_err: Optional[Exception] = None
    for col in DATE_CANDIDATES:
        sql = base_no_date.replace("{DATE_FILTER}", _build_date_clause(table_alias, col))
        try:
            return _rows(sql, params)
        except (ProgrammingError, OperationalError) as e:
            last_err = e
            continue
    # Fallback: sem filtro de data
    try:
        return _rows(base_no_date.replace("{DATE_FILTER}", ""), params)
    except Exception as e:
        raise last_err or e


# ============================================================
# 📊 FUNÇÕES DE MÉTRICAS
# ============================================================

def total_revenue(
    sales: Optional[List[Dict[str, Any]]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    channel: Optional[str] = None,
    **kwargs: Any
) -> float:
    """
    Calcula o faturamento total a partir do banco de dados.
    - Tenta diversas colunas de data.
    - Filtro de canal com fallback (channel_id → channel).
    """
    params = {"date_from": date_from, "date_to": date_to, "channel": channel}

    base_no_date = """
        SELECT COALESCE(SUM(total_amount), 0) AS total
        FROM sales s
        WHERE 1=1
    """

    if not channel:
        return _try_scalar_with_datecols(base_no_date, "s", params)

    base_with_channel_id  = base_no_date + "  AND (:channel = s.channel_id)\n"
    base_with_channel_txt = base_no_date + "  AND (:channel = s.channel)\n"

    try:
        return _try_scalar_with_datecols(base_with_channel_id, "s", params)
    except (ProgrammingError, OperationalError):
        return _try_scalar_with_datecols(base_with_channel_txt, "s", params)


def average_ticket(
    sales: Optional[List[Dict[str, Any]]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    channel: Optional[str] = None,
    **kwargs: Any
) -> float:
    """
    Calcula o ticket médio diretamente do banco.
    - Tenta diversas colunas de data.
    - Filtro de canal com fallback (channel_id → channel).
    """
    params = {"date_from": date_from, "date_to": date_to, "channel": channel}

    base_no_date = """
        SELECT COALESCE(AVG(total_amount), 0) AS avg_ticket
        FROM sales s
        WHERE 1=1
    """

    if not channel:
        return _try_scalar_with_datecols(base_no_date, "s", params)

    base_with_channel_id  = base_no_date + "  AND (:channel = s.channel_id)\n"
    base_with_channel_txt = base_no_date + "  AND (:channel = s.channel)\n"

    try:
        return _try_scalar_with_datecols(base_with_channel_id, "s", params)
    except (ProgrammingError, OperationalError):
        return _try_scalar_with_datecols(base_with_channel_txt, "s", params)


# ============================================================
# ➕ NOVAS MÉTRICAS: TOTAL DE PEDIDOS e AVALIAÇÃO MÉDIA
# ============================================================

def total_orders(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    channel: Optional[str] = None,
    **kwargs: Any
) -> float:
    """
    Conta pedidos no intervalo.
    - Usa sales s (COUNT(*)::float).
    - Filtro de canal com fallback (channel_id → channel).
    - Tenta created_at / sale_date etc. como nas demais.
    """
    params = {"date_from": date_from, "date_to": date_to, "channel": channel}

    base_no_date = """
        SELECT COUNT(*)::float AS qty
        FROM sales s
        WHERE 1=1
    """

    if not channel:
        return _try_scalar_with_datecols(base_no_date, "s", params)

    base_with_channel_id  = base_no_date + "  AND (:channel = s.channel_id)\n"
    base_with_channel_txt = base_no_date + "  AND (:channel = s.channel)\n"

    try:
        return _try_scalar_with_datecols(base_with_channel_id, "s", params)
    except (ProgrammingError, OperationalError):
        return _try_scalar_with_datecols(base_with_channel_txt, "s", params)


def average_rating(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    channel: Optional[str] = None,
    **kwargs: Any
) -> float:
    """
    Calcula a avaliação média (se existir coluna de rating).
    - Tenta colunas candidatas: rating, customer_rating, score, stars.
    - Tenta tabelas candidatas: sales s, product_sales ps, delivery_sales ds.
    - Usa colunas de data candidatas conforme helper.
    - Se não existir coluna de rating, retorna 0.0 (sem erro).
    """
    RATING_COLS = ["rating", "customer_rating", "score", "stars"]
    TABLES = [
        ("sales", "s"),
        ("product_sales", "ps"),
        ("delivery_sales", "ds"),
    ]

    params = {"date_from": date_from, "date_to": date_to, "channel": channel}

    for table, alias in TABLES:
        for col in RATING_COLS:
            base_no_date = f"""
                SELECT COALESCE(AVG({alias}.{col}), 0) AS avg_rating
                FROM {table} {alias}
                WHERE 1=1
            """
            if table == "sales" and channel:
                try:
                    return _try_scalar_with_datecols(base_no_date + "  AND (:channel = s.channel_id)\n", alias, params)
                except (ProgrammingError, OperationalError):
                    try:
                        return _try_scalar_with_datecols(base_no_date + "  AND (:channel = s.channel)\n", alias, params)
                    except (ProgrammingError, OperationalError):
                        continue
            else:
                try:
                    return _try_scalar_with_datecols(base_no_date, alias, params)
                except (ProgrammingError, OperationalError):
                    continue

    # Nenhuma combinação funcionou → sem coluna de rating nas tabelas candidatas
    return 0.0


def top_products(
    sales_items: Optional[List[Dict[str, Any]]] = None,
    top_n: int = 5,
    limit: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    channel: Optional[str] = None,
    **kwargs: Any
) -> List[Dict[str, Any]]:
    """
    Retorna os produtos mais vendidos (por receita; fallback por quantidade).
    - Usa relação correta: item_product_sales → product_sales.
    - Filtro de data em product_sales (ps.created_at).
    - Fallback agrega por dia na tabela sales (garante gráfico).
    """
    n = limit if isinstance(limit, int) and limit > 0 else top_n
    params = {"date_from": date_from, "date_to": date_to, "channel": channel, "n": n}

    # ⚠️ Seu schema não mostra canal em product_sales; mantemos sem filtro de canal aqui.
    base_no_date = """
        SELECT
            si.item_id AS product_id,
            COALESCE(i.name, CONCAT('Item ', si.item_id)) AS product_name,
            COALESCE(SUM(si.quantity * si.price), 0) AS total_revenue,
            COALESCE(SUM(si.quantity), 0) AS total_sold
        FROM item_product_sales si
        JOIN product_sales ps ON ps.id = si.product_sale_id
        LEFT JOIN items i ON i.id = si.item_id
        WHERE 1=1
        {DATE_FILTER}
        GROUP BY si.item_id, COALESCE(i.name, CONCAT('Item ', si.item_id))
        ORDER BY total_revenue DESC, total_sold DESC
        LIMIT :n
    """

    data: List[Dict[str, Any]] = []
    try:
        sql_try = base_no_date.format(
            DATE_FILTER=_build_date_clause("ps", "created_at")  # ✅ ps.created_at existe
        )
        data = _rows(sql_try, params)
    except Exception:
        data = []

    # ✅ Fallback: se não houver itens, agrega por dia em sales (garante gráfico)
    if not data:
        fb_sql = """
            SELECT
                TO_CHAR(s.created_at, 'YYYY-MM-DD') AS product_name,
                COALESCE(SUM(total_amount), 0) AS total_revenue,
                COUNT(*) AS total_sold
            FROM sales s
            WHERE (:date_from IS NULL OR s.created_at >= :date_from)
              AND (:date_to   IS NULL OR s.created_at <= :date_to)
            GROUP BY 1
            ORDER BY total_revenue DESC
            LIMIT :n
        """
        data = _rows(fb_sql, params)

    out = []
    for r in data:
        out.append({
            "product_id": r.get("product_id"),
            "product_name": r.get("product_name"),
            "total_sold": float(r.get("total_sold") or 0),
            "total_revenue": float(r.get("total_revenue") or 0),
        })
    return out


# ============================================================
# 🔄 FUNÇÕES DE AGRUPAMENTO E FILTROS
# ============================================================

def group_sales_by_store(sales: List[Dict[str, Any]]) -> dict[Any, List[Dict[str, Any]]]:
    """Agrupa vendas por 'store_id'."""
    return helpers.group_sales_by_key(sales, "store_id")


def group_sales_by_channel(sales: List[Dict[str, Any]]) -> dict[Any, List[Dict[str, Any]]]:
    """Agrupa vendas por 'channel_id'."""
    return helpers.group_sales_by_key(sales, "channel_id")
