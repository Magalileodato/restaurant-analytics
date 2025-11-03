# ============================================================
# 🧮 GERADOR DE DADOS (ERP) – RESTAURANT ANALYTICS
# ============================================================
# Autor: Magali Leodato
# Projeto: Restaurant Analytics MVP
# Descrição:
#   - Popula dimensões (brands, sub_brands, stores, channels, categories,
#     products, items, payment_types) e fatos (sales, product_sales, payments)
#   - Compatível com schema_postgres.sql (SERIAL, FKs e colunas obrigatórias)
#   - Suporta LOCAL ou CLOUD (Supabase) via .env
# Observações:
#   - NÃO cria tabelas (usa o schema já aplicado no banco)
#   - Usa SQLAlchemy Core com INSERT em lote (performático)
# ============================================================

import os
import uuid
import random
from datetime import datetime, timedelta
from argparse import ArgumentParser

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text, bindparam
from sqlalchemy.engine import Engine

# 🔧 Carrega variáveis de ambiente (.env)
load_dotenv(find_dotenv(), override=False)

# ============================================================
# 🌐 SELEÇÃO DO BANCO DE DADOS (LOCAL/CLOUD)
# ============================================================
DB_MODE = os.getenv("DB_MODE", "LOCAL").upper()
DATABASE_URL_LOCAL = os.getenv("DATABASE_URL_LOCAL")
DATABASE_URL_CLOUD = os.getenv("DATABASE_URL_CLOUD")
DATABASE_URL = DATABASE_URL_CLOUD if DB_MODE == "CLOUD" else DATABASE_URL_LOCAL

if not DATABASE_URL:
    raise RuntimeError("❌ Defina DATABASE_URL_LOCAL/CLOUD no .env e DB_MODE=LOCAL/CLOUD.")

# ============================================================
# 🧠 PARÂMETROS PADRÃO
# ============================================================
RANDOM_SEED = 42
DEFAULT_ROWS = 10000           # vendas a gerar
DEFAULT_MONTHS = 3             # janela temporal (meses)
BATCH_SIZE = 1000              # tamanho do lote para inserts

# ============================================================
# 🧰 Funções auxiliares
# ============================================================
def rand_dt_within_months(months: int) -> datetime:
    """⏱️ Retorna um datetime aleatório dentro dos últimos <months> meses."""
    now = datetime.now()
    days = months * 30
    offset_days = random.randint(0, max(1, days))
    offset_secs = random.randint(0, 60 * 60 * 24 - 1)
    return now - timedelta(days=offset_days, seconds=offset_secs)

def clamp(n, minimo, maximo):
    return max(minimo, min(n, maximo))

def weighted_pick(options):
    """🎯 options = [(valor, peso), ...] -> retorna valor pela roleta ponderada."""
    total = sum(w for _, w in options)
    r = random.uniform(0, total)
    acc = 0.0
    for v, w in options:
        acc += w
        if r <= acc:
            return v
    return options[-1][0]

# ============================================================
# 🔌 Engine (conexão resiliente)
# ============================================================
def get_engine() -> Engine:
    return create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

engine = get_engine()

# ============================================================
# 🧱 SEED DAS DIMENSÕES (idempotente simples)
# ============================================================
def seed_dimensions():
    """
    🔧 Insere registros mínimos nas dimensões do ERP:
    - brands, sub_brands, stores, channels, categories, products, items, payment_types
    """
    with engine.begin() as conn:
        # brands
        conn.exec_driver_sql("""
            INSERT INTO brands (name)
            SELECT x.name FROM (VALUES ('Marca X')) AS x(name)
            WHERE NOT EXISTS (SELECT 1 FROM brands b WHERE b.name = x.name);
        """)

        # sub_brands
        conn.exec_driver_sql("""
            INSERT INTO sub_brands (brand_id, name)
            SELECT b.id, sb.name
            FROM brands b
            JOIN (VALUES ('SubMarca A'), ('SubMarca B')) AS sb(name) ON TRUE
            WHERE b.name='Marca X'
              AND NOT EXISTS (
                SELECT 1 FROM sub_brands s WHERE s.brand_id=b.id AND s.name=sb.name
              );
        """)

        # channels (P=Presencial, D=Delivery)
        conn.exec_driver_sql("""
            INSERT INTO channels (brand_id, name, description, type)
            SELECT b.id, c.name, c.description, c.t
            FROM brands b
            JOIN (VALUES
              ('Presencial','Loja física','P'),
              ('iFood','Marketplace iFood','D'),
              ('Rappi','Marketplace Rappi','D'),
              ('App Próprio','Delivery próprio','D')
            ) AS c(name, description, t) ON TRUE
            WHERE b.name='Marca X'
              AND NOT EXISTS (
                SELECT 1 FROM channels ch WHERE ch.brand_id=b.id AND ch.name=c.name
              );
        """)

        # stores
        conn.exec_driver_sql("""
            INSERT INTO stores (brand_id, sub_brand_id, name, city, state, district, is_active, is_own, creation_date)
            SELECT b.id, sb.id, s.name, s.city, s.state, s.district, TRUE, TRUE, CURRENT_DATE
            FROM brands b
            JOIN sub_brands sb ON sb.brand_id=b.id
            JOIN (VALUES
              ('Loja Centro','Rio de Janeiro','RJ','Centro'),
              ('Loja Zona Sul','Rio de Janeiro','RJ','Ipanema'),
              ('Loja Niterói','Niterói','RJ','Icaraí'),
              ('Loja Tijuca','Rio de Janeiro','RJ','Tijuca')
            ) AS s(name, city, state, district) ON TRUE
            WHERE b.name='Marca X'
              AND NOT EXISTS (
                SELECT 1 FROM stores st
                 WHERE st.brand_id=b.id AND st.sub_brand_id=sb.id AND st.name=s.name
              );
        """)

        # categories
        conn.exec_driver_sql("""
            INSERT INTO categories (brand_id, sub_brand_id, name, type)
            SELECT b.id, sb.id, c.name, 'P'
            FROM brands b
            JOIN sub_brands sb ON sb.brand_id=b.id
            JOIN (VALUES ('Lanches'), ('Bebidas'), ('Sobremesas')) AS c(name) ON TRUE
            WHERE b.name='Marca X'
              AND NOT EXISTS (
                SELECT 1 FROM categories ct
                 WHERE ct.brand_id=b.id AND ct.sub_brand_id=sb.id AND ct.name=c.name
              );
        """)

        # products
        conn.exec_driver_sql("""
            INSERT INTO products (brand_id, sub_brand_id, category_id, name)
            SELECT b.id, sb.id, ct.id, p.name
            FROM brands b
            JOIN sub_brands sb ON sb.brand_id=b.id
            JOIN categories ct ON ct.brand_id=b.id AND ct.sub_brand_id=sb.id
            JOIN (VALUES
              ('Hambúrguer Clássico'), ('Hambúrguer Duplo'), ('Batata Média'),
              ('Refrigerante Lata'), ('Milkshake Chocolate'), ('Água Mineral')
            ) AS p(name) ON TRUE
            WHERE b.name='Marca X'
              AND NOT EXISTS (
                SELECT 1 FROM products pr
                 WHERE pr.brand_id=b.id AND pr.sub_brand_id=sb.id
                   AND pr.category_id=ct.id AND pr.name=p.name
              );
        """)

        # items (adicionais)
        conn.exec_driver_sql("""
            INSERT INTO items (brand_id, sub_brand_id, category_id, name)
            SELECT b.id, sb.id, ct.id, i.name
            FROM brands b
            JOIN sub_brands sb ON sb.brand_id=b.id
            JOIN categories ct ON ct.brand_id=b.id AND ct.sub_brand_id=sb.id
            JOIN (VALUES ('Queijo Extra'), ('Bacon'), ('Molho Especial'), ('Calda Chocolate')) AS i(name) ON TRUE
            WHERE b.name='Marca X'
              AND NOT EXISTS (
                SELECT 1 FROM items it
                 WHERE it.brand_id=b.id AND it.sub_brand_id=sb.id
                   AND it.category_id=ct.id AND it.name=i.name
              );
        """)

        # payment_types  ✅ corrigido alias: desc -> descr
        conn.exec_driver_sql("""
            INSERT INTO payment_types (brand_id, description)
            SELECT b.id, pt.descr
            FROM brands b
            JOIN (VALUES ('Crédito'), ('Débito'), ('PIX'), ('Dinheiro')) AS pt(descr) ON TRUE
            WHERE b.name='Marca X'
              AND NOT EXISTS (
                SELECT 1 FROM payment_types p WHERE p.brand_id=b.id AND p.description=pt.descr
              );
        """)

# ============================================================
# 💰 SEED DE VENDAS / ITENS / PAGAMENTOS
# ============================================================
def seed_sales(rows: int, months: int):
    """
    🧾 Gera <rows> vendas distribuídas nos últimos <months> meses.
    - Preenche: sales, product_sales, payments
    - Vincula TODOS os itens gerados a cada venda (flush ajustado)
    """
    random.seed(RANDOM_SEED)

    with engine.begin() as conn:
        # 🔎 IDs auxiliares
        brand_id = conn.execute(text("SELECT id FROM brands WHERE name='Marca X' LIMIT 1")).scalar()
        sub_brand_ids = [r[0] for r in conn.execute(text("SELECT id FROM sub_brands WHERE brand_id=:b"), {"b": brand_id})]
        store_ids = [r[0] for r in conn.execute(text("SELECT id FROM stores WHERE brand_id=:b"), {"b": brand_id})]
        channels = [dict(id=r[0], name=r[1], t=r[2]) for r in conn.execute(text("SELECT id,name,type FROM channels WHERE brand_id=:b"), {"b": brand_id}).all()]
        product_ids = [r[0] for r in conn.execute(text("SELECT id FROM products WHERE brand_id=:b"), {"b": brand_id})]
        paytype_ids = [r[0] for r in conn.execute(text("SELECT id FROM payment_types WHERE brand_id=:b"), {"b": brand_id})]

        if not (sub_brand_ids and store_ids and channels and product_ids and paytype_ids):
            raise RuntimeError("❌ Dimensões insuficientes. Execute seed_dimensions primeiro.")

        # ⚖️ pesos dos canais
        chan_weights = [(c["id"], 0.45 if c["name"] == "Presencial" else 0.183333) for c in channels]

        # Buffers
        sales_buf, psales_buf, pays_buf = [], [], []

        # Índice sequencial da venda no LOTE (para mapear itens→venda)
        sale_idx_global = 0

        for _ in range(rows):
            created_at = rand_dt_within_months(months)
            store_id = random.choice(store_ids)
            sub_brand_id = random.choice(sub_brand_ids)
            channel_id = weighted_pick(chan_weights)
            is_delivery = any(c["id"] == channel_id and c["t"] == 'D' for c in channels)

            # 🧮 composição de itens
            n_items = random.randint(1, 4)
            prices = []
            for _ni in range(n_items):
                base = random.choice([18.0, 22.0, 28.0, 35.0, 12.0, 8.0, 6.0])
                base = round(base + random.uniform(-2.0, 3.0), 2)
                prices.append(clamp(base, 4.0, 49.0))

            total_items = round(sum(prices), 2)

            # taxas e ajustes
            delivery_fee = round(random.uniform(0, 9), 2) if is_delivery else 0.0
            service_tax = round(total_items * random.uniform(0.0, 0.10), 2) if not is_delivery else 0.0
            discount = round(total_items * random.choice([0.0, 0.03, 0.05, 0.10, 0.0, 0.0]), 2)
            increase = round(random.choice([0.0, 0.0, 1.0, 2.0]), 2)

            total_amount = round(total_items - discount + increase + delivery_fee + service_tax, 2)

            # 🔖 marcador único por venda (mapeio depois para id real)
            marker = uuid.uuid4().hex

            # ➕ buffer de venda (sem id; SERIAL será gerado)
            sales_buf.append({
                "store_id": store_id,
                "sub_brand_id": sub_brand_id,
                "customer_id": None,
                "channel_id": channel_id,
                "cod_sale1": marker,          # << chave única temporária
                "cod_sale2": None,
                "created_at": created_at,
                "customer_name": None,
                "sale_status_desc": "PAID",
                "total_amount_items": total_items,
                "total_discount": discount,
                "total_increase": increase,
                "delivery_fee": delivery_fee,
                "service_tax_fee": service_tax,
                "total_amount": total_amount,
                "value_paid": total_amount,
                "production_seconds": random.randint(300, 1200),
                "delivery_seconds": random.randint(0, 2400) if is_delivery else 0,
                "people_quantity": random.randint(1, 4),
                "discount_reason": None,
                "increase_reason": None,
                "origin": "DELIVERY" if is_delivery else "POS"
            })

            # 🧾 buffer de itens da venda (cada item carrega o índice da venda no lote)
            cur_sale_idx = sale_idx_global
            for p in prices:
                psales_buf.append({
                    "sale_idx": cur_sale_idx,           # << vinculação garantida no flush
                    "product_id": random.choice(product_ids),
                    "quantity": 1.0,
                    "base_price": p,
                    "total_price": p,
                    "observations": None
                })

            # 💳 buffer de pagamento (1 por venda)
            pays_buf.append({
                "payment_type_id": random.choice(paytype_ids),
                "value": total_amount,
                "is_online": is_delivery,
                "description": "Pagamento único",
                "currency": "BRL"
            })

            sale_idx_global += 1

            # 🔄 flush por lote
            if len(sales_buf) >= BATCH_SIZE:
                _flush_batch(conn, sales_buf, psales_buf, pays_buf)
                sales_buf.clear(); psales_buf.clear(); pays_buf.clear()
                sale_idx_global = 0  # reseta o índice relativo ao LOTE

        # 🔚 flush final
        if sales_buf:
            _flush_batch(conn, sales_buf, psales_buf, pays_buf)

# ============================================================
# 🔄 FLUSH EM LOTE (vincula TODOS os itens à venda correta)
# ============================================================
def _flush_batch(conn, sales_buf, psales_buf, pays_buf):
    # -----------------------------
    # 1) INSERT sales (sem RETURNING)
    # -----------------------------
    conn.execute(text("""
        INSERT INTO sales (
            store_id, sub_brand_id, customer_id, channel_id, cod_sale1, cod_sale2,
            created_at, customer_name, sale_status_desc, total_amount_items, total_discount,
            total_increase, delivery_fee, service_tax_fee, total_amount, value_paid,
            production_seconds, delivery_seconds, people_quantity, discount_reason,
            increase_reason, origin
        )
        VALUES (
            :store_id, :sub_brand_id, :customer_id, :channel_id, :cod_sale1, :cod_sale2,
            :created_at, :customer_name, :sale_status_desc, :total_amount_items, :total_discount,
            :total_increase, :delivery_fee, :service_tax_fee, :total_amount, :value_paid,
            :production_seconds, :delivery_seconds, :people_quantity, :discount_reason,
            :increase_reason, :origin
        )
    """), sales_buf)

    # 🔗 mapa posição->marker (ordem do buffer)
    idx_to_marker = {i: s["cod_sale1"] for i, s in enumerate(sales_buf)}
    markers = [s["cod_sale1"] for s in sales_buf]

    # ---------------------------------------------
    # 2) Recuperar ids via cod_sale1 (IN ... expandindo)
    # ---------------------------------------------
    sel = text("SELECT id, cod_sale1 FROM sales WHERE cod_sale1 IN :tokens") \
        .bindparams(bindparam("tokens", expanding=True))
    rows = conn.execute(sel, {"tokens": markers}).all()
    marker_to_id = {cod: sid for (sid, cod) in rows}

    # ---------------------------------
    # 3) INSERT product_sales (em lote)
    # ---------------------------------
    if psales_buf:
        ps_rows = []
        for item in psales_buf:
            d = dict(item)
            marker = idx_to_marker.get(d.pop("sale_idx"))
            sale_id = marker_to_id.get(marker)
            if sale_id is None:
                continue
            d["sale_id"] = sale_id
            ps_rows.append(d)

        if ps_rows:
            conn.execute(text("""
                INSERT INTO product_sales (
                    sale_id, product_id, quantity, base_price, total_price, observations
                )
                VALUES (
                    :sale_id, :product_id, :quantity, :base_price, :total_price, :observations
                )
            """), ps_rows)

    # ----------------------------
    # 4) INSERT payments (em lote)
    # ----------------------------
    if pays_buf:
        # preservar mesma ordem das vendas
        pay_rows = []
        for i, s in enumerate(sales_buf):
            if i >= len(pays_buf):
                break
            sale_id = marker_to_id.get(s["cod_sale1"])
            if sale_id is None:
                continue
            d = dict(pays_buf[i])
            d["sale_id"] = sale_id
            pay_rows.append(d)

        if pay_rows:
            conn.execute(text("""
                INSERT INTO payments (
                    sale_id, payment_type_id, value, is_online, description, currency
                )
                VALUES (
                    :sale_id, :payment_type_id, :value, :is_online, :description, :currency
                )
            """), pay_rows)

# ============================================================
# 🚀 CLI
# ============================================================
def main():
    random.seed(RANDOM_SEED)
    ap = ArgumentParser(description="Gerador de dados ERP compatível com schema_postgres.sql")
    ap.add_argument("--rows", type=int, default=DEFAULT_ROWS, help="Quantidade de vendas a gerar (default: 10000)")
    ap.add_argument("--months", type=int, default=DEFAULT_MONTHS, help="Janela temporal (meses) (default: 3)")
    args = ap.parse_args()

    print(f"🌍 Modo: {DB_MODE} | Conexão: {DATABASE_URL.split('@')[-1]}")
    print("🧱 Seeding dimensões...")
    seed_dimensions()
    print("✅ Dimensões OK.")

    print(f"🧾 Gerando {args.rows} vendas em {args.months} meses...")
    seed_sales(args.rows, args.months)
    print("✅ Vendas/itens/pagamentos inseridos com sucesso.")
    print("🏁 Pronto. Teste as rotas /metrics e o dashboard.")

# ============================================================
# 🔥 EXECUÇÃO DIRETA
# ============================================================
if __name__ == "__main__":
    main()
