/* ============================================================
   ⚡ APP.JS - LÓGICA DE INTERATIVIDADE E DASHBOARD
   Desenvolvido por Magali Leodato (2025)
   ============================================================ */

/* ------------------------------------------------------------
   🌐 CONFIGURAÇÕES INICIAIS DA API
   ------------------------------------------------------------ */
const API_BASE_URL = "http://localhost:8000"; // URL do backend FastAPI

/* ------------------------------------------------------------
   🧩 HELPERS (datas, moeda, fetch)
   ------------------------------------------------------------ */
const BRL = (v) =>
  typeof v === "number"
    ? v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
    : "R$ 0,00";

function rangeUltimosNDias(n = 30) {
  const dtTo = new Date();
  const dtFrom = new Date();
  dtFrom.setDate(dtFrom.getDate() - (n - 1));
  const iso = (d) => d.toISOString().slice(0, 10);
  return { from: iso(dtFrom), to: iso(dtTo) };
}

async function getJSON(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status} em ${url}`);
    return res.json();
  } catch (err) {
    console.error("❌ Erro ao buscar:", url, err);
    throw err;
  }
}

function setError(msg) {
  const $err = document.getElementById("error");
  if ($err) $err.textContent = msg || "";
  if (msg) console.error(msg);
}

/* ------------------------------------------------------------
   📊 BUSCA MÉTRICAS VIA GET (query string)
   - total-revenue
   - average-ticket
   - total-orders
   - average-rating
   - top-products (usado no gráfico)
   ------------------------------------------------------------ */
async function carregarMetricas() {
  setError(""); // limpa erro se existir

  const { from, to } = rangeUltimosNDias(30);

  // Endpoints GET (compatíveis com metrics.py)
  const urlRevenue = `${API_BASE_URL}/metrics/total-revenue?date_from=${from}&date_to=${to}`;
  const urlTicket  = `${API_BASE_URL}/metrics/average-ticket?date_from=${from}&date_to=${to}`;
  const urlOrders  = `${API_BASE_URL}/metrics/total-orders?date_from=${from}&date_to=${to}`;
  const urlRating  = `${API_BASE_URL}/metrics/average-rating?date_from=${from}&date_to=${to}`;
  const urlTop     = `${API_BASE_URL}/metrics/top-products?limit=5&date_from=${from}&date_to=${to}`;

  try {
    const [revenueData, ticketData, ordersData, ratingData, topData] = await Promise.all([
      getJSON(urlRevenue),
      getJSON(urlTicket),
      getJSON(urlOrders),
      getJSON(urlRating),
      getJSON(urlTop),
    ]);

    console.log("📊 Revenue:", revenueData);
    console.log("🎟️ Ticket:", ticketData);
    console.log("🛍️ Orders:", ordersData);
    console.log("⭐ Rating:", ratingData);
    console.log("📈 Top Products:", topData);

    atualizarCards({ revenueData, ticketData, ordersData, ratingData });
    gerarGraficoTopProdutos(topData);
  } catch (e) {
    setError(
      "Não foi possível carregar as métricas agora. Verifique se o backend está ativo e acessível."
    );
  }
}

/* ------------------------------------------------------------
   📈 ATUALIZA OS VALORES NOS CARDS DO DASHBOARD
   - Campos do HTML: #revenue, #orders, #rating
   ------------------------------------------------------------ */
function atualizarCards({ revenueData, ticketData, ordersData, ratingData }) {
  const $revenue = document.getElementById("revenue");
  const $orders  = document.getElementById("orders");
  const $rating  = document.getElementById("rating");

  // Aceita ambos formatos do backend:
  // { "total_revenue": number } ou { "total": number }
  // { "average_ticket": number } ou { "avg_ticket": number }
  // { "total_orders": number } ou { "qty": number }
  // { "average_rating": number } ou { "avg_rating": number }
  const totalRevenue =
    Number(revenueData?.total_revenue ?? revenueData?.total ?? 0);
  const avgTicket =
    Number(ticketData?.average_ticket ?? ticketData?.avg_ticket ?? 0);
  const totalOrders =
    Number(ordersData?.total_orders ?? ordersData?.qty ?? 0);
  const avgRating =
    Number(ratingData?.average_rating ?? ratingData?.avg_rating ?? 0);

  if ($revenue)
    $revenue.textContent = `${BRL(totalRevenue)} (Ticket médio: ${BRL(avgTicket)})`;
  if ($orders)
    $orders.textContent = isFinite(totalOrders) ? totalOrders.toString() : "—";
  if ($rating)
    $rating.textContent = isFinite(avgRating) && avgRating > 0
      ? avgRating.toFixed(2)
      : "—";
}

/* ------------------------------------------------------------
   📉 GRÁFICO (Chart.js) – TOP PRODUTOS (barra)
   - Usa /metrics/top-products (GET)
   - Espera: { data: [{product_name, total_sold, total_revenue}, ...] }
   ------------------------------------------------------------ */
let chartRef = null;

function gerarGraficoTopProdutos(topData) {
  const ctx = document.getElementById("salesChart")?.getContext("2d");
  if (!ctx) return;

  const arr = Array.isArray(topData?.data) ? topData.data : [];

  const labels = arr.map((x) => x.product_name ?? "Item");
  const values = arr.map((x) =>
    typeof x.total_revenue === "number"
      ? x.total_revenue
      : typeof x.total_sold === "number"
      ? x.total_sold
      : 0
  );

  if (chartRef) chartRef.destroy();

  chartRef = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Top produtos (últimos 30 dias)",
          data: values,
          backgroundColor: "rgba(56, 189, 248, 0.4)",
          borderColor: "#38bdf8",
          borderWidth: 1.5,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } },
      scales: {
        x: { ticks: { autoSkip: true } },
        y: { beginAtZero: true },
      },
    },
  });
}

/* ------------------------------------------------------------
   🚀 INICIALIZAÇÃO AUTOMÁTICA
   ------------------------------------------------------------ */
document.addEventListener("DOMContentLoaded", () => {
  carregarMetricas(); // Busca métricas ao abrir a página
  setInterval(carregarMetricas, 60_000); // Atualiza a cada 60s
});
