document.addEventListener('DOMContentLoaded', () => {
  const el = document.getElementById('finance-init-data');
  let init = null;
  try {
    init = el ? JSON.parse(el.textContent) : null;
  } catch (e) {
    init = null;
  }
  const fmtBRL = (v) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v || 0);
  const colors = {
    blue: '#3b82f6',
    green: '#22c55e',
    yellow: '#eab308',
    red: '#ef4444',
    purple: '#a855f7',
    gray: '#64748b',
  };
  const charts = {};
  const ctxMethods = document.getElementById('chart-methods');
  const ctxDaily = document.getElementById('chart-daily');
  const ctxMonthly = document.getElementById('chart-monthly');
  const ctxServices = document.getElementById('chart-services');
  const ctxTicket = document.getElementById('chart-ticket');
  const commonOpts = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: { boxWidth: 12 },
      },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const v = ctx.parsed.y ?? ctx.parsed ?? 0;
            return `${ctx.dataset.label || ''} ${fmtBRL(v)}`.trim();
          },
        },
      },
    },
  };
  if (init && ctxMethods) {
    charts.methods = new Chart(ctxMethods, {
      type: 'doughnut',
      data: {
        labels: init.totais_por_metodo.labels,
        datasets: [
          {
            label: 'Totais',
            data: init.totais_por_metodo.values,
            backgroundColor: [colors.green, colors.yellow],
          },
        ],
      },
      options: commonOpts,
    });
  }
  if (init && ctxDaily) {
    charts.daily = new Chart(ctxDaily, {
      type: 'line',
      data: {
        labels: init.receita_diaria.labels,
        datasets: [
          {
            label: 'Receita diária',
            data: init.receita_diaria.values,
            borderColor: colors.blue,
            backgroundColor: 'rgba(59,130,246,0.2)',
            tension: 0.3,
            fill: true,
          },
        ],
      },
      options: {
        ...commonOpts,
        scales: {
          y: { ticks: { callback: (v) => fmtBRL(v) } },
        },
      },
    });
  }
  if (init && ctxMonthly) {
    charts.monthly = new Chart(ctxMonthly, {
      type: 'line',
      data: {
        labels: init.receita_mensal.labels,
        datasets: [
          {
            label: 'Receita mensal',
            data: init.receita_mensal.values,
            borderColor: colors.purple,
            backgroundColor: 'rgba(168,85,247,0.2)',
            tension: 0.3,
            fill: true,
          },
        ],
      },
      options: {
        ...commonOpts,
        scales: {
          y: { ticks: { callback: (v) => fmtBRL(v) } },
        },
      },
    });
  }
  if (init && ctxServices) {
    charts.services = new Chart(ctxServices, {
      type: 'bar',
      data: {
        labels: init.top_servicos.labels,
        datasets: [
          {
            label: 'Receita por serviço',
            data: init.top_servicos.values,
            backgroundColor: [colors.gray, colors.blue, colors.green],
          },
        ],
      },
      options: {
        ...commonOpts,
        indexAxis: 'y',
        scales: {
          y: { ticks: { autoSkip: false } },
          x: { ticks: { callback: (v) => fmtBRL(v) } },
        },
      },
    });
  }
  if (init && ctxTicket) {
    charts.ticket = new Chart(ctxTicket, {
      type: 'bar',
      data: {
        labels: init.ticket_medio.labels,
        datasets: [
          {
            label: 'Ticket médio',
            data: init.ticket_medio.values,
            backgroundColor: colors.red,
          },
        ],
      },
      options: {
        ...commonOpts,
        scales: {
          y: { ticks: { callback: (v) => fmtBRL(v) } },
        },
      },
    });
  }
  const updateCharts = (data) => {
    if (charts.methods) {
      charts.methods.data.labels = data.totais_por_metodo.labels;
      charts.methods.data.datasets[0].data = data.totais_por_metodo.values;
      charts.methods.update();
    }
    if (charts.daily) {
      charts.daily.data.labels = data.receita_diaria.labels;
      charts.daily.data.datasets[0].data = data.receita_diaria.values;
      charts.daily.update();
    }
    if (charts.monthly) {
      charts.monthly.data.labels = data.receita_mensal.labels;
      charts.monthly.data.datasets[0].data = data.receita_mensal.values;
      charts.monthly.update();
    }
    if (charts.services) {
      charts.services.data.labels = data.top_servicos.labels;
      charts.services.data.datasets[0].data = data.top_servicos.values;
      charts.services.update();
    }
    if (charts.ticket) {
      charts.ticket.data.labels = data.ticket_medio.labels;
      charts.ticket.data.datasets[0].data = data.ticket_medio.values;
      charts.ticket.update();
    }
  };
  const fetchMetrics = async (params = {}) => {
    const qs = new URLSearchParams(params);
    const resp = await fetch(`/admin/financeiro/api/metrics/?${qs.toString()}`);
    if (!resp.ok) return;
    const data = await resp.json();
    updateCharts(data);
  };
  const setupDownloadButtons = () => {
    document.querySelectorAll('.chart-card').forEach((card) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = 'Baixar PNG';
      btn.className = 'download-chart';
      btn.addEventListener('click', () => {
        const canvas = card.querySelector('canvas');
        if (!canvas) return;
        const link = document.createElement('a');
        link.href = canvas.toDataURL('image/png');
        link.download = `${canvas.id}.png`;
        link.click();
      });
      card.appendChild(btn);
    });
  };
  setupDownloadButtons();
  
  const btnDownloadAll = document.getElementById('download-report');
  if (btnDownloadAll) {
    btnDownloadAll.addEventListener('click', () => {
      const area = document.getElementById('charts-area');
      if (!area || typeof html2canvas === 'undefined') return;
      // Temporariamente remove gap/margins se necessário para uma imagem mais compacta,
      // ou captura como está. Vamos capturar como está.
      html2canvas(area, {
        backgroundColor: getComputedStyle(document.body).getPropertyValue('--bg') || '#ffffff',
        scale: 2 // Melhor resolução
      }).then(canvas => {
        const link = document.createElement('a');
        link.download = `relatorio-financeiro-${new Date().toISOString().slice(0,10)}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
      }).catch(err => {
        console.error(err);
        alert('Não foi possível gerar a imagem do relatório.');
      });
    });
  }

  window.financeCharts = { update: fetchMetrics };
});
