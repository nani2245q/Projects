let revenueChart = null;
let attrRevenueChart = null;
let attrConversionChart = null;
let topProductsChart = null;

const CHART_COLORS = ['#2563eb', '#7c3aed', '#db2777', '#ea580c', '#16a34a', '#0891b2'];

const COMPACT_OPTS = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 1.8,
  plugins: {
    legend: { labels: { font: { size: 11 }, boxWidth: 12 } }
  }
};

async function apiFetch(endpoint) {
  const res = await fetch(`${API_BASE}${endpoint}`, { headers: authHeaders() });
  if (res.status === 401 || res.status === 403) {
    document.getElementById('login-prompt').classList.remove('hidden');
    document.getElementById('dashboard-content').style.opacity = '0.3';
    document.getElementById('dashboard-content').style.pointerEvents = 'none';
    throw new Error('Unauthorized');
  }
  return res.json();
}

// ─── Dashboard KPIs ─────────────────────────────────────────────────
async function loadKPIs() {
  try {
    const data = await apiFetch('/analytics/dashboard');
    const { kpis, topProducts } = data;

    const kpiGrid = document.getElementById('kpi-grid');
    kpiGrid.innerHTML = `
      <div class="kpi-card">
        <div class="kpi-label">30-Day Revenue</div>
        <div class="kpi-value">$${kpis.last30DaysRevenue.toLocaleString()}</div>
        <div class="kpi-change ${kpis.revenueGrowth >= 0 ? 'positive' : 'negative'}">
          ${kpis.revenueGrowth >= 0 ? '+' : ''}${kpis.revenueGrowth}%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">30-Day Orders</div>
        <div class="kpi-value">${kpis.last30DaysOrders}</div>
        <div class="kpi-change">${kpis.todayOrders} today</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Avg Order Value</div>
        <div class="kpi-value">$${kpis.avgOrderValue.toFixed(2)}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Total Customers</div>
        <div class="kpi-value">${kpis.totalCustomers}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Events Tracked</div>
        <div class="kpi-value">${kpis.last30DaysEvents.toLocaleString()}</div>
      </div>
    `;

    renderTopProducts(topProducts);
  } catch (err) {
    if (err.message !== 'Unauthorized') console.error('KPI load error:', err);
  }
}

// ─── Conversion Funnel ──────────────────────────────────────────────
async function loadFunnel() {
  try {
    const data = await apiFetch('/analytics/funnel');
    const container = document.getElementById('funnel-chart');

    const maxUsers = Math.max(...data.funnel.map(s => s.uniqueUsers), 1);

    container.innerHTML = data.funnel.map(stage => {
      const width = Math.max((stage.uniqueUsers / maxUsers) * 100, 5);
      return `
        <div class="funnel-stage">
          <div class="funnel-label">${stage.label}</div>
          <div class="funnel-bar-wrapper">
            <div class="funnel-bar" style="width: ${width}%">
              ${stage.uniqueUsers}
            </div>
            ${parseFloat(stage.dropOffRate) > 0 ? `<span class="funnel-dropoff">${stage.dropOffRate}%</span>` : ''}
          </div>
        </div>
      `;
    }).join('');

    document.getElementById('overall-conversion').textContent = `${data.overallConversionRate}%`;
  } catch (err) {
    if (err.message !== 'Unauthorized') console.error('Funnel load error:', err);
  }
}

// ─── Revenue Time Series ────────────────────────────────────────────
async function loadRevenue(granularity = 'month') {
  try {
    const data = await apiFetch(`/analytics/revenue?granularity=${granularity}`);

    const ctx = document.getElementById('revenue-chart').getContext('2d');
    if (revenueChart) revenueChart.destroy();

    revenueChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.timeSeries.map(t => t.period),
        datasets: [
          {
            label: 'Revenue ($)',
            data: data.timeSeries.map(t => t.revenue),
            backgroundColor: '#2563eb',
            borderRadius: 3,
            yAxisID: 'y'
          },
          {
            label: 'Orders',
            data: data.timeSeries.map(t => t.orderCount),
            type: 'line',
            borderColor: '#db2777',
            backgroundColor: 'transparent',
            tension: 0.3,
            pointRadius: 2,
            borderWidth: 2,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        ...COMPACT_OPTS,
        interaction: { mode: 'index', intersect: false },
        scales: {
          x: { ticks: { font: { size: 10 }, maxRotation: 45 } },
          y: {
            type: 'linear',
            position: 'left',
            title: { display: true, text: 'Revenue ($)', font: { size: 10 } },
            ticks: { font: { size: 10 } }
          },
          y1: {
            type: 'linear',
            position: 'right',
            title: { display: true, text: 'Orders', font: { size: 10 } },
            ticks: { font: { size: 10 } },
            grid: { drawOnChartArea: false }
          }
        }
      }
    });
  } catch (err) {
    if (err.message !== 'Unauthorized') console.error('Revenue load error:', err);
  }
}

// ─── Marketing Attribution ──────────────────────────────────────────
async function loadAttribution() {
  try {
    const data = await apiFetch('/analytics/attribution');

    const revCtx = document.getElementById('attribution-revenue-chart').getContext('2d');
    if (attrRevenueChart) attrRevenueChart.destroy();

    attrRevenueChart = new Chart(revCtx, {
      type: 'doughnut',
      data: {
        labels: data.attribution.map(a => a.channel),
        datasets: [{
          data: data.attribution.map(a => a.revenue),
          backgroundColor: CHART_COLORS
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 1.4,
        plugins: {
          title: { display: true, text: 'Revenue by Channel', font: { size: 12 } },
          legend: { position: 'bottom', labels: { font: { size: 10 }, boxWidth: 10, padding: 8 } }
        }
      }
    });

    const convCtx = document.getElementById('attribution-conversion-chart').getContext('2d');
    if (attrConversionChart) attrConversionChart.destroy();

    attrConversionChart = new Chart(convCtx, {
      type: 'bar',
      data: {
        labels: data.attribution.map(a => a.channel),
        datasets: [{
          label: 'Conv. Rate (%)',
          data: data.attribution.map(a => parseFloat(a.conversionRate)),
          backgroundColor: CHART_COLORS
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 1.4,
        plugins: {
          title: { display: true, text: 'Conversion Rate by Channel', font: { size: 12 } },
          legend: { display: false }
        },
        scales: {
          x: { ticks: { font: { size: 10 } } },
          y: { title: { display: true, text: '%', font: { size: 10 } }, ticks: { font: { size: 10 } } }
        }
      }
    });

    // Attribution table
    const tbody = document.querySelector('#attribution-table tbody');
    tbody.innerHTML = data.attribution.map(a => `
      <tr>
        <td><strong>${a.channel}</strong></td>
        <td>${a.sessions}</td>
        <td>${a.orders}</td>
        <td>$${a.revenue.toLocaleString()}</td>
        <td>$${a.avgOrderValue}</td>
        <td>${a.conversionRate}%</td>
        <td>$${a.revenuePerSession}</td>
      </tr>
    `).join('');
  } catch (err) {
    if (err.message !== 'Unauthorized') console.error('Attribution load error:', err);
  }
}

// ─── Category Performance ───────────────────────────────────────────
async function loadCategories() {
  try {
    const data = await apiFetch('/analytics/categories');

    const tbody = document.querySelector('#category-table tbody');
    tbody.innerHTML = data.categories.map(c => `
      <tr>
        <td><strong>${c.category}</strong></td>
        <td>${c.totalViews.toLocaleString()}</td>
        <td>${c.totalAddToCarts.toLocaleString()}</td>
        <td>${c.totalPurchases.toLocaleString()}</td>
        <td>${c.viewToCartRate}%</td>
        <td>$${c.totalRevenue.toLocaleString()}</td>
      </tr>
    `).join('');
  } catch (err) {
    if (err.message !== 'Unauthorized') console.error('Category load error:', err);
  }
}

// ─── Top Products Chart ─────────────────────────────────────────────
function renderTopProducts(products) {
  const ctx = document.getElementById('top-products-chart').getContext('2d');
  if (topProductsChart) topProductsChart.destroy();

  topProductsChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: products.map(p => p.name.length > 20 ? p.name.substring(0, 20) + '...' : p.name),
      datasets: [
        {
          label: 'Views',
          data: products.map(p => p.viewCount),
          backgroundColor: '#93c5fd'
        },
        {
          label: 'Purchases',
          data: products.map(p => p.purchaseCount),
          backgroundColor: '#2563eb'
        }
      ]
    },
    options: {
      ...COMPACT_OPTS,
      indexAxis: 'y',
      scales: {
        x: { stacked: false, ticks: { font: { size: 10 } } },
        y: { ticks: { font: { size: 10 } } }
      }
    }
  });
}

// ─── Load All Dashboard Data ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const user = getUser();
  if (!user || user.role !== 'admin') {
    document.getElementById('login-prompt').classList.remove('hidden');
    document.getElementById('dashboard-content').style.opacity = '0.3';
    document.getElementById('dashboard-content').style.pointerEvents = 'none';
    return;
  }

  loadKPIs();
  loadFunnel();
  loadRevenue('month');
  loadAttribution();
  loadCategories();
});
