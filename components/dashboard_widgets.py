"""
Componentes visuais da Dashboard.

Este módulo concentra funções de renderização usadas pela página inicial:
- rankings;
- tabelas;
- gráficos;
- cards mobile;
- formatações visuais.

A regra de negócio continua nos services/dashboard_*.
"""

import json
from html import escape

import streamlit as st


def moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def cor_status_hex(status):
    mapa = {
        "Orçamento": "#B85C20",
        "Encomendado": "#0C65AA",
        "Em Produção": "#100690",
        "Pronto": "#1F8A4C",
        "Entregue": "#1F8A4C",
        "Cancelado": "#D11A2A",
    }
    return mapa.get(status, "#8A8F98")


def render_ranking_faturamento_visual(itens_resumo, label_quantidade="pedidos", limite=8):
    ranking = sorted(
        itens_resumo.items(),
        key=lambda item: item[1]["faturamento"],
        reverse=True
    )[:limite]

    if not ranking:
        st.caption("Nenhum dado cadastrado ainda.")
        return

    max_faturamento = max([dados["faturamento"] for _, dados in ranking], default=1)
    if max_faturamento <= 0:
        max_faturamento = 1

    cards = ""

    for posicao, (nome, dados) in enumerate(ranking, start=1):
        faturamento = dados["faturamento"]
        lucro = dados["lucro"]
        qtd = dados.get(label_quantidade, dados.get("pedidos", dados.get("quantidade", 0)))
        largura = max(6, int((faturamento / max_faturamento) * 100))
        margem = (lucro / faturamento * 100) if faturamento > 0 else 0
        tooltip = (
            f"Faturamento: {moeda(faturamento)} | "
            f"{label_quantidade.capitalize()}: {qtd:.0f} | "
            f"Lucro: {moeda(lucro)} | Margem: {margem:.0f}%"
        )

        if label_quantidade == "quantidade":
            qtd_texto = f"{qtd:.0f} un vendidas"
        else:
            qtd_texto = f"{qtd:.0f} pedidos"

        cards += f"""
        <div class="g3d-rank-row" title="{escape(tooltip)}">
            <div class="g3d-rank-top">
                <div class="g3d-rank-name">
                    <span>{posicao}</span>
                    <strong>{escape(nome_curto(nome, 46))}</strong>
                </div>
                <div class="g3d-rank-value">{escape(moeda(faturamento))}</div>
            </div>
            <div class="g3d-rank-meta">
                <span>{qtd_texto}</span>
                <span>Lucro {escape(moeda(lucro))}</span>
            </div>
            <div class="g3d-rank-bar">
                <i style="width:{largura}%;"></i>
            </div>
        </div>
        """

    html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&display=swap');

        .g3d-rank-wrap {{
            font-family: 'Barlow', system-ui, sans-serif;
            display: flex;
            flex-direction: column;
            gap: 10px;
            background: #FFFFFF;
            border: 1px solid rgba(185, 205, 220, 0.78);
            border-radius: 20px;
            padding: 14px;
            min-height: 290px;
            box-shadow: 0 14px 32px rgba(10, 26, 92, 0.065);
        }}

        .g3d-rank-row {{
            border: 1px solid #E6EEF3;
            border-radius: 16px;
            padding: 12px 13px;
            background: linear-gradient(180deg, #FFFFFF 0%, #FBFDFE 100%);
        }}

        .g3d-rank-row:hover {{
            background: #F7FBFE;
        }}

        .g3d-rank-top {{
            display: flex;
            justify-content: space-between;
            gap: 14px;
            align-items: center;
            margin-bottom: 7px;
        }}

        .g3d-rank-name {{
            display: flex;
            align-items: center;
            gap: 8px;
            min-width: 0;
        }}

        .g3d-rank-name span {{
            width: 24px;
            height: 24px;
            border-radius: 999px;
            background: #F0F7FC;
            color: #0C65AA;
            font-weight: 800;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            flex: 0 0 auto;
        }}

        .g3d-rank-name strong {{
            color: #0A1A5C;
            font-size: 13px;
            line-height: 1.18;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .g3d-rank-value {{
            color: #0A1A5C;
            font-size: 13px;
            font-weight: 800;
            white-space: nowrap;
        }}

        .g3d-rank-meta {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            color: #5C6C74;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
        }}

        .g3d-rank-bar {{
            height: 8px;
            background: #EAF3F9;
            border-radius: 999px;
            overflow: hidden;
        }}

        .g3d-rank-bar i {{
            display: block;
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #0C65AA 0%, #58C3F0 100%);
        }}
    </style>

    <div class="g3d-rank-wrap">
        {cards}
    </div>
    """

    # Mantém o card visualmente alinhado ao gráfico de rosca ao lado,
    # mas sem criar barra de rolagem quando há poucos itens.
    altura = max(325, min(520, 36 + len(ranking) * 83))
    st.components.v1.html(html, height=altura, scrolling=False)


def render_status_visual(status_resumo, status_ordem):
    total_status = sum(dados["pedidos"] for dados in status_resumo.values())
    if total_status <= 0:
        st.caption("Nenhum pedido cadastrado ainda.")
        return
    for status in status_ordem:
        dados = status_resumo.get(status)
        if not dados:
            continue
        quantidade = dados["pedidos"]
        percentual = (quantidade / total_status) * 100 if total_status > 0 else 0
        cor = cor_status_hex(status)
        st.markdown(
            f"""
            <div style="margin-bottom:12px;font-family:'Barlow', system-ui, sans-serif;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;gap:10px;">
                    <div style="font-size:13px;font-weight:800;color:#1E3137;display:flex;align-items:center;gap:7px;">
                        <span style="width:10px;height:10px;border-radius:50%;background:{cor};display:inline-block;"></span>{status}
                    </div>
                    <div style="font-size:12px;font-weight:700;color:#5C6C74;">{quantidade:.0f} pedidos · {percentual:.0f}%</div>
                </div>
                <div style="height:9px;background:#DEE9EF;border-radius:999px;overflow:hidden;">
                    <div style="height:9px;width:{percentual:.0f}%;background:{cor};border-radius:999px;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def largura_coluna(header):
    larguras = {
        "Pedido": "120px",
        "Cliente": "220px",
        "Peça": "340px",
        "Qtd.": "80px",
        "Status": "130px",
        "Total": "130px",
        "Faturamento": "150px",
        "Lucro": "130px",
        "Pedidos": "100px",
        "Mês": "110px",
        "Peças": "100px",
    }

    return larguras.get(str(header), "160px")


def coluna_numerica(header):
    return str(header) in [
        "Qtd.",
        "Pedidos",
        "Peças",
        "Faturamento",
        "Lucro",
        "Total",
    ]


def status_chip_html(status):
    cor = cor_status_hex(status)
    return f"""
    <span class="g3d-status-text" style="color:{cor};">
        {escape(str(status))}
    </span>
    """


def tabela_html(headers, rows, empty_message):
    if not rows:
        return f"""
        <div style="
            border:1px solid rgba(185,205,220,0.78);
            background:#FFFFFF;
            border-radius:18px;
            padding:20px;
            font-family:'Barlow', system-ui, sans-serif;
            color:#5C6C74;
            font-size:13px;
            box-shadow:0 12px 28px rgba(10,26,92,0.055);
        ">
            {escape(empty_message)}
        </div>
        """

    colgroup = "".join([
        f'<col style="width:{largura_coluna(header)};">'
        for header in headers
    ])

    thead = "".join([
        f"""
        <th style="
            text-align:center;
            padding:14px 16px;
            border-bottom:1px solid #D7E4EC;
            color:#0A1A5C;
            font-weight:800;
            letter-spacing:1.7px;
            font-size:10.5px;
            text-transform:uppercase;
            white-space:nowrap;
            background:linear-gradient(180deg, #F7FBFE 0%, #EDF5FA 100%);
            position:sticky;
            top:0;
            z-index:2;
        ">{escape(str(header))}</th>
        """
        for header in headers
    ])

    linhas = ""

    for row in rows:
        tds = ""

        for idx, value in enumerate(row):
            header = headers[idx]

            if header == "Status":
                cell_value = status_chip_html(value)
            else:
                cell_value = escape(str(value))

            if coluna_numerica(header):
                align = "center"
                weight = "800"
                color = "#0A1A5C" if header in ["Total", "Faturamento", "Lucro"] else "#1E3137"
            else:
                align = "left"
                weight = "800" if idx == 0 else "600"
                color = "#0A1A5C" if idx == 0 else "#1E3137"

            tds += f"""
            <td style="
                padding:13px 16px;
                border-bottom:1px solid #E6EEF3;
                color:{color};
                font-weight:{weight};
                text-align:{align};
                white-space:nowrap;
                font-size:13px;
                vertical-align:middle;
            ">{cell_value}</td>
            """

        linhas += f"<tr>{tds}</tr>"

    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&display=swap');

        .g3d-table-wrap,
        .g3d-table,
        .g3d-table th,
        .g3d-table td {{
            font-family: 'Barlow', system-ui, sans-serif !important;
        }}

        .g3d-status-text {{
            font-family: 'Barlow', system-ui, sans-serif !important;
            font-weight: 800;
            white-space: nowrap;
        }}
    </style>

    <div class="g3d-table-wrap">
        <table class="g3d-table">
            <colgroup>
                {colgroup}
            </colgroup>
            <thead>
                <tr>{thead}</tr>
            </thead>
            <tbody>
                {linhas}
            </tbody>
        </table>
    </div>
    """


def render_tabela(headers, rows, empty_message):
    html = tabela_html(headers, rows, empty_message)

    if not rows:
        altura = 90
    else:
        altura = min(430, 82 + (len(rows) * 44))

    st.components.v1.html(
        html,
        height=altura,
        scrolling=True
    )


def render_vendas_mes_chart(vendas_rows):
    if not vendas_rows:
        st.caption("Nenhuma venda com data registrada ainda.")
        return

    labels = [item["mes"] for item in vendas_rows]
    faturamento = [round(float(item["faturamento"]), 2) for item in vendas_rows]
    lucro = [round(float(item["lucro"]), 2) for item in vendas_rows]
    margem = [round(float(item["margem"]), 1) for item in vendas_rows]
    pedidos = [int(item["pedidos"]) for item in vendas_rows]
    quantidade = [int(item["quantidade"]) for item in vendas_rows]

    html = f"""
    <style>
        .g3d-chart-card {{
            background:#FFFFFF;
            border:1px solid rgba(185, 205, 220, 0.78);
            border-radius:20px;
            padding:18px 18px 8px 18px;
            box-shadow:0 14px 32px rgba(10, 26, 92, 0.065);
        }}

        .g3d-chart-card canvas {{
            width:100%;
            height:340px;
        }}

        @media (max-width: 768px) {{
            .g3d-chart-card {{
                border-radius:17px;
                padding:14px 10px 6px 10px;
                margin-top: 0;
            }}

            .g3d-chart-card canvas {{
                height:300px;
            }}
        }}
    </style>

    <div class="g3d-chart-card">
        <canvas id="g3d-vendas-mes-chart"></canvas>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const labels = {json.dumps(labels)};
        const faturamento = {json.dumps(faturamento)};
        const lucro = {json.dumps(lucro)};
        const margem = {json.dumps(margem)};
        const pedidos = {json.dumps(pedidos)};
        const quantidade = {json.dumps(quantidade)};

        const formatarMoeda = (valor) => new Intl.NumberFormat('pt-BR', {{
            style: 'currency',
            currency: 'BRL'
        }}).format(valor || 0);

        const canvas = document.getElementById('g3d-vendas-mes-chart');
        const chartExistente = Chart.getChart(canvas);
        if (chartExistente) {{
            chartExistente.destroy();
        }}

        new Chart(canvas, {{
            type: 'bar',
            data: {{
                labels: labels,
                datasets: [
                    {{
                        type: 'bar',
                        label: 'Vendas',
                        data: faturamento,
                        backgroundColor: 'rgba(12, 101, 170, 0.88)',
                        borderColor: '#0C65AA',
                        borderWidth: 1,
                        borderRadius: 10,
                        borderSkipped: false,
                        barThickness: 22,
                        order: 2
                    }},
                    {{
                        type: 'bar',
                        label: 'Lucro',
                        data: lucro,
                        backgroundColor: 'rgba(31, 138, 76, 0.88)',
                        borderColor: '#1F8A4C',
                        borderWidth: 1,
                        borderRadius: 10,
                        borderSkipped: false,
                        barThickness: 22,
                        order: 2
                    }},
                    {{
                        type: 'line',
                        label: 'Margem %',
                        data: margem,
                        yAxisID: 'y1',
                        borderColor: '#100690',
                        backgroundColor: '#100690',
                        tension: 0.35,
                        pointRadius: 4,
                        pointHoverRadius: 5,
                        pointBackgroundColor: '#FFFFFF',
                        pointBorderColor: '#100690',
                        pointBorderWidth: 2,
                        order: 1
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    mode: 'index',
                    intersect: false
                }},
                layout: {{
                    padding: {{ top: 10, right: 10, bottom: 0, left: 4 }}
                }},
                plugins: {{
                    legend: {{
                        position: 'top',
                        align: 'start',
                        labels: {{
                            boxWidth: 14,
                            boxHeight: 14,
                            color: '#1E3137',
                            font: {{
                                family: 'Inter, system-ui, sans-serif',
                                size: 12,
                                weight: '600'
                            }}
                        }}
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(10, 26, 92, 0.96)',
                        titleFont: {{ family: 'Inter, system-ui, sans-serif', size: 13, weight: '700' }},
                        bodyFont: {{ family: 'Inter, system-ui, sans-serif', size: 12 }},
                        padding: 12,
                        callbacks: {{
                            label: function(context) {{
                                const idx = context.dataIndex;
                                if (context.dataset.label === 'Margem %') {{
                                    return 'Margem: ' + margem[idx].toFixed(1) + '%';
                                }}
                                return context.dataset.label + ': ' + formatarMoeda(context.parsed.y);
                            }},
                            afterBody: function(items) {{
                                if (!items.length) return [];
                                const idx = items[0].dataIndex;
                                return [
                                    'Pedidos: ' + pedidos[idx],
                                    'Peças vendidas: ' + quantidade[idx]
                                ];
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{
                            color: '#5C6C74',
                            font: {{ family: 'Inter, system-ui, sans-serif', size: 11, weight: '600' }}
                        }}
                    }},
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: '#E6EEF3' }},
                        ticks: {{
                            color: '#5C6C74',
                            font: {{ family: 'Inter, system-ui, sans-serif', size: 11 }},
                            callback: function(value) {{
                                return formatarMoeda(value);
                            }}
                        }}
                    }},
                    y1: {{
                        beginAtZero: true,
                        position: 'right',
                        grid: {{ drawOnChartArea: false }},
                        suggestedMax: 100,
                        ticks: {{
                            color: '#100690',
                            font: {{ family: 'Inter, system-ui, sans-serif', size: 11, weight: '600' }},
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
    """

    st.components.v1.html(html, height=420, scrolling=False)


def render_utilizacao_impressoras_chart(utilizacao_rows):
    if not utilizacao_rows:
        st.caption("Nenhuma utilização de impressora registrada ainda.")
        return

    meses = []
    impressoras = []

    for item in utilizacao_rows:
        if item["mes"] not in meses:
            meses.append(item["mes"])
        if item["impressora"] not in impressoras:
            impressoras.append(item["impressora"])

    if not meses or not impressoras:
        st.caption("Nenhuma utilização de impressora registrada ainda.")
        return

    valores = {
        impressora: []
        for impressora in impressoras
    }

    horas_por_chave = {}
    capacidade_por_chave = {}
    pedidos_por_chave = {}

    def chave_json(mes, impressora):
        return f"{mes}||{impressora}"

    for item in utilizacao_rows:
        chave = chave_json(item["mes"], item["impressora"])
        horas_por_chave[chave] = round(float(item["horas_usadas"]), 1)
        capacidade_por_chave[chave] = round(float(item["capacidade_horas"]), 1)
        pedidos_por_chave[chave] = int(item["pedidos"])

    for impressora in impressoras:
        for mes in meses:
            chave = chave_json(mes, impressora)
            horas = horas_por_chave.get(chave, 0)
            capacidade = capacidade_por_chave.get(chave, 0)
            percentual = (horas / capacidade * 100) if capacidade > 0 else 0
            valores[impressora].append(round(percentual, 1))

    datasets = []
    for impressora in impressoras:
        datasets.append({
            "label": impressora,
            "data": valores[impressora],
            "borderWidth": 1,
            "borderRadius": 8,
            "borderSkipped": False,
            "barThickness": 22,
            "maxBarThickness": 32,
        })

    altura_canvas = 380

    html = f"""
    <style>
        .g3d-chart-card {{
            background:#FFFFFF;
            border:1px solid rgba(185, 205, 220, 0.78);
            border-radius:20px;
            padding:18px 18px 8px 18px;
            box-shadow:0 14px 32px rgba(10, 26, 92, 0.065);
        }}

        .g3d-chart-card canvas {{
            width:100%;
            height:{altura_canvas}px;
        }}

        @media (max-width: 768px) {{
            .g3d-chart-card {{
                border-radius:17px;
                padding:14px 10px 6px 10px;
                margin-top: 0;
            }}

            .g3d-chart-card canvas {{
                height:340px;
            }}
        }}
    </style>

    <div class="g3d-chart-card">
        <canvas id="g3d-utilizacao-impressoras-mes-chart"></canvas>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const labelsUtilizacaoMes = {json.dumps(meses)};
        const datasetsUtilizacaoMes = {json.dumps(datasets)};
        const horasUtilizacao = {json.dumps(horas_por_chave)};
        const capacidadeUtilizacao = {json.dumps(capacidade_por_chave)};
        const pedidosUtilizacao = {json.dumps(pedidos_por_chave)};

        const coresUtilizacao = [
            'rgba(12, 101, 170, 0.88)',
            'rgba(88, 195, 240, 0.88)',
            'rgba(10, 26, 92, 0.88)',
            'rgba(16, 6, 144, 0.78)',
            'rgba(31, 138, 76, 0.78)',
            'rgba(184, 92, 32, 0.78)'
        ];

        const bordasUtilizacao = [
            '#0C65AA',
            '#58C3F0',
            '#0A1A5C',
            '#100690',
            '#1F8A4C',
            '#B85C20'
        ];

        datasetsUtilizacaoMes.forEach((dataset, index) => {{
            dataset.backgroundColor = coresUtilizacao[index % coresUtilizacao.length];
            dataset.borderColor = bordasUtilizacao[index % bordasUtilizacao.length];
        }});

        const canvasUtilizacaoMes = document.getElementById('g3d-utilizacao-impressoras-mes-chart');
        const chartUtilizacaoMesExistente = Chart.getChart(canvasUtilizacaoMes);
        if (chartUtilizacaoMesExistente) {{
            chartUtilizacaoMesExistente.destroy();
        }}

        new Chart(canvasUtilizacaoMes, {{
            type: 'bar',
            data: {{
                labels: labelsUtilizacaoMes,
                datasets: datasetsUtilizacaoMes
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    mode: 'index',
                    intersect: false
                }},
                layout: {{
                    padding: {{ top: 10, right: 16, bottom: 0, left: 4 }}
                }},
                plugins: {{
                    legend: {{
                        position: 'top',
                        align: 'start',
                        labels: {{
                            boxWidth: 14,
                            boxHeight: 14,
                            color: '#1E3137',
                            font: {{
                                family: 'Inter, system-ui, sans-serif',
                                size: 12,
                                weight: '600'
                            }}
                        }}
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(10, 26, 92, 0.96)',
                        titleFont: {{ family: 'Inter, system-ui, sans-serif', size: 13, weight: '700' }},
                        bodyFont: {{ family: 'Inter, system-ui, sans-serif', size: 12 }},
                        padding: 12,
                        callbacks: {{
                            label: function(context) {{
                                const mes = context.label;
                                const impressora = context.dataset.label;
                                const chave = mes + '||' + impressora;
                                const horas = horasUtilizacao[chave] || 0;
                                const capacidade = capacidadeUtilizacao[chave] || 0;
                                const pedidos = pedidosUtilizacao[chave] || 0;

                                return [
                                    impressora + ': ' + context.parsed.y.toFixed(1) + '%',
                                    'Horas usadas: ' + horas.toFixed(1) + 'h',
                                    'Capacidade do mês: ' + capacidade.toFixed(0) + 'h',
                                    'Pedidos: ' + pedidos
                                ];
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{
                            color: '#5C6C74',
                            font: {{ family: 'Inter, system-ui, sans-serif', size: 11, weight: '600' }}
                        }}
                    }},
                    y: {{
                        beginAtZero: true,
                        suggestedMax: 100,
                        grid: {{ color: '#E6EEF3' }},
                        ticks: {{
                            color: '#5C6C74',
                            font: {{ family: 'Inter, system-ui, sans-serif', size: 11 }},
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
    """

    st.components.v1.html(html, height=altura_canvas + 105, scrolling=False)


def render_ranking_pecas_faturamento(pecas_resumo):
    pecas_ranking = sorted(
        pecas_resumo.items(),
        key=lambda item: item[1]["faturamento"],
        reverse=True
    )[:8]

    if not pecas_ranking:
        st.caption("Nenhuma peça vendida ainda.")
        return

    max_faturamento = max([dados["faturamento"] for _, dados in pecas_ranking], default=1)
    if max_faturamento <= 0:
        max_faturamento = 1

    cards = ""

    for posicao, (nome, dados) in enumerate(pecas_ranking, start=1):
        faturamento = dados["faturamento"]
        quantidade = dados["quantidade"]
        lucro = dados["lucro"]
        largura = max(6, int((faturamento / max_faturamento) * 100))
        tooltip = (
            f"Faturamento: {moeda(faturamento)} | "
            f"Quantidade: {quantidade:.0f} un | "
            f"Lucro: {moeda(lucro)}"
        )

        cards += f"""
        <div class="g3d-rank-row" title="{escape(tooltip)}">
            <div class="g3d-rank-top">
                <div class="g3d-rank-name">
                    <span>{posicao}</span>
                    <strong>{escape(nome_curto(nome, 46))}</strong>
                </div>
                <div class="g3d-rank-value">{escape(moeda(faturamento))}</div>
            </div>
            <div class="g3d-rank-meta">
                <span>{quantidade:.0f} un vendidas</span>
                <span>Lucro {escape(moeda(lucro))}</span>
            </div>
            <div class="g3d-rank-bar">
                <i style="width:{largura}%;"></i>
            </div>
        </div>
        """

    html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&display=swap');

        .g3d-rank-wrap {{
            font-family: 'Barlow', system-ui, sans-serif;
            display: flex;
            flex-direction: column;
            gap: 10px;
            background: #FFFFFF;
            border: 1px solid rgba(185, 205, 220, 0.78);
            border-radius: 20px;
            padding: 14px;
            box-shadow: 0 14px 32px rgba(10, 26, 92, 0.065);
        }}

        .g3d-rank-row {{
            border: 1px solid #E6EEF3;
            border-radius: 16px;
            padding: 12px 13px;
            background: linear-gradient(180deg, #FFFFFF 0%, #FBFDFE 100%);
        }}

        .g3d-rank-row:hover {{
            background: #F7FBFE;
        }}

        .g3d-rank-top {{
            display: flex;
            justify-content: space-between;
            gap: 14px;
            align-items: center;
            margin-bottom: 7px;
        }}

        .g3d-rank-name {{
            display: flex;
            gap: 9px;
            align-items: center;
            min-width: 0;
        }}

        .g3d-rank-name span {{
            width: 25px;
            height: 25px;
            border-radius: 999px;
            background: #EDF5FA;
            color: #0C65AA;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 800;
            flex: 0 0 auto;
        }}

        .g3d-rank-name strong {{
            color: #0A1A5C;
            font-size: 13px;
            font-weight: 800;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .g3d-rank-value {{
            color: #1F8A4C;
            font-size: 14px;
            font-weight: 800;
            white-space: nowrap;
        }}

        .g3d-rank-meta {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            color: #5C6C74;
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 8px;
        }}

        .g3d-rank-bar {{
            height: 9px;
            border-radius: 999px;
            overflow: hidden;
            background: #EDF5FA;
        }}

        .g3d-rank-bar i {{
            display: block;
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #0C65AA 0%, #58C3F0 100%);
        }}
    </style>

    <div class="g3d-rank-wrap">
        {cards}
    </div>
    """

    altura = min(520, 38 + len(pecas_ranking) * 82)

    st.components.v1.html(
        html,
        height=altura,
        scrolling=True
    )


def render_distribuicao_faturamento_chart(distribuicao_faturamento):
    """
    Renderiza gráfico de rosca com a distribuição do faturamento.
    """
    distribuicao_faturamento = distribuicao_faturamento or {}

    ordem = [
        "Filamento",
        "Energia",
        "Depreciação",
        "Pós-processamento",
        "Acessórios",
        "Embalagem",
        "Custos",
        "Lucro",
        "Prejuízo",
    ]

    labels = []
    valores = []

    for item in ordem:
        valor = float(distribuicao_faturamento.get(item, 0) or 0)
        if valor > 0.005:
            labels.append(item)
            valores.append(round(valor, 2))

    total = sum(valores)

    if total <= 0:
        html_empty = """
        <div style="
            background:#FFFFFF;
            border:1px solid rgba(185,205,220,0.78);
            border-radius:20px;
            padding:24px;
            min-height:290px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-family:'Barlow', system-ui, sans-serif;
            color:#5C6C74;
            font-size:13px;
            box-shadow:0 14px 32px rgba(10,26,92,0.065);
        ">
            Nenhum faturamento no período selecionado.
        </div>
        """
        try:
            st.html(html_empty)
        except AttributeError:
            st.markdown(html_empty, unsafe_allow_html=True)
        return

    percentuais = [(valor / total) * 100 if total > 0 else 0 for valor in valores]

    legenda = ""
    for label, valor, percentual in zip(labels, valores, percentuais):
        legenda += f"""
        <div class="g3d-donut-row">
            <div class="g3d-donut-label">
                <span></span>
                <strong>{escape(label)}</strong>
            </div>
            <div class="g3d-donut-value">
                {escape(moeda(valor))}
                <small>{percentual:.0f}%</small>
            </div>
        </div>
        """

    html = f"""
    <style>
        .g3d-donut-card {{
            font-family:'Barlow', system-ui, sans-serif;
            background:#FFFFFF;
            border:1px solid rgba(185,205,220,0.78);
            border-radius:20px;
            padding:14px;
            min-height:290px;
            box-shadow:0 14px 32px rgba(10,26,92,0.065);
            display:grid;
            grid-template-columns: 45% 55%;
            gap:12px;
            align-items:center;
        }}

        .g3d-donut-canvas {{
            position:relative;
            width:100%;
            min-height:220px;
        }}

        .g3d-donut-total {{
            position:absolute;
            inset:0;
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            pointer-events:none;
            text-align:center;
        }}

        .g3d-donut-total strong {{
            color:#0A1A5C;
            font-size:17px;
            font-weight:800;
            line-height:1.05;
        }}

        .g3d-donut-total span {{
            color:#5C6C74;
            font-size:10px;
            font-weight:700;
            text-transform:uppercase;
            letter-spacing:.08em;
            margin-top:4px;
        }}

        .g3d-donut-list {{
            display:flex;
            flex-direction:column;
            gap:7px;
            min-width:0;
        }}

        .g3d-donut-row {{
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:10px;
            padding:8px 9px;
            border:1px solid #E6EEF3;
            border-radius:13px;
            background:#FBFDFE;
        }}

        .g3d-donut-label {{
            display:flex;
            align-items:center;
            gap:8px;
            min-width:0;
        }}

        .g3d-donut-label span {{
            width:9px;
            height:9px;
            border-radius:99px;
            background:#0C65AA;
            flex:0 0 auto;
        }}

        .g3d-donut-label strong {{
            font-size:12px;
            color:#1E3137;
            font-weight:800;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;
        }}

        .g3d-donut-value {{
            text-align:right;
            color:#0A1A5C;
            font-size:12px;
            font-weight:800;
            white-space:nowrap;
        }}

        .g3d-donut-value small {{
            display:block;
            color:#5C6C74;
            font-size:10px;
            font-weight:700;
            margin-top:1px;
        }}

        @media (max-width: 768px) {{
            .g3d-donut-card {{
                grid-template-columns: 1fr;
                min-height:0;
            }}

            .g3d-donut-canvas {{
                min-height:230px;
            }}
        }}
    </style>

    <div class="g3d-donut-card">
        <div class="g3d-donut-canvas">
            <canvas id="g3d-distribuicao-faturamento-chart"></canvas>
            <div class="g3d-donut-total">
                <strong>{escape(moeda(total))}</strong>
                <span>total analisado</span>
            </div>
        </div>
        <div class="g3d-donut-list">
            {legenda}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const labelsDistribuicao = {json.dumps(labels)};
        const valoresDistribuicao = {json.dumps(valores)};

        const canvasDistribuicao = document.getElementById('g3d-distribuicao-faturamento-chart');
        const chartDistribuicaoExistente = Chart.getChart(canvasDistribuicao);
        if (chartDistribuicaoExistente) {{
            chartDistribuicaoExistente.destroy();
        }}

        new Chart(canvasDistribuicao, {{
            type: 'doughnut',
            data: {{
                labels: labelsDistribuicao,
                datasets: [{{
                    data: valoresDistribuicao,
                    backgroundColor: [
                        '#0C65AA',
                        '#58C3F0',
                        '#0A1A5C',
                        '#72D2B6',
                        '#F59E0B',
                        '#A78BFA',
                        '#94A3B8',
                        '#1F8A4C',
                        '#D11A2A'
                    ],
                    borderColor: '#FFFFFF',
                    borderWidth: 3,
                    hoverOffset: 5
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                cutout: '68%',
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const valor = context.raw || 0;
                                const total = valoresDistribuicao.reduce((a, b) => a + b, 0);
                                const percentual = total > 0 ? (valor / total * 100) : 0;
                                const moeda = new Intl.NumberFormat('pt-BR', {{
                                    style: 'currency',
                                    currency: 'BRL'
                                }}).format(valor);
                                return `${{context.label}}: ${{moeda}} (${{percentual.toFixed(1)}}%)`;
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
    """

    st.components.v1.html(
        html,
        height=325,
        scrolling=False
    )


def nome_curto(texto, limite=42):
    texto = str(texto) if texto is not None else "-"
    if " - " in texto:
        texto = texto.split(" - ", 1)[1]
    if len(texto) <= limite:
        return texto
    return texto[:limite - 3] + "..."


def rotulo_mes_grafico(data_pedido_dt):
    meses = {
        1: "jan",
        2: "fev",
        3: "mar",
        4: "abr",
        5: "mai",
        6: "jun",
        7: "jul",
        8: "ago",
        9: "set",
        10: "out",
        11: "nov",
        12: "dez",
    }
    if not data_pedido_dt:
        return "-"
    return f"{meses.get(data_pedido_dt.month, str(data_pedido_dt.month).zfill(2))}/{str(data_pedido_dt.year)[-2:]}"


def mobile_cor(nome):
    mapa = {
        "blue": "#0C65AA",
        "green": "#1F8A4C",
        "orange": "#B85C20",
        "red": "#D11A2A",
        "gray": "#8A8F98",
        "purple": "#100690",
    }
    return mapa.get(nome, "#0C65AA")


def mobile_kpi_html(titulo, valor, subtitulo, cor="blue"):
    cor_hex = mobile_cor(cor)
    return f"""
    <div class="g3d-mobile-kpi" style="border-top-color:{cor_hex};">
        <div class="g3d-mobile-kpi-title">{escape(str(titulo))}</div>
        <div class="g3d-mobile-kpi-value" style="color:{cor_hex};">{escape(str(valor))}</div>
        <div class="g3d-mobile-kpi-subtitle">{escape(str(subtitulo))}</div>
    </div>
    """


def mobile_section_header(titulo, subtitulo=""):
    return f"""
    <div class="g3d-mobile-section-title">
        <div>
            <span>{escape(str(titulo))}</span>
            <small>{escape(str(subtitulo))}</small>
        </div>
    </div>
    """


def mobile_status_chip(status):
    cor = cor_status_hex(status)
    return f"""
    <span class="g3d-mobile-status-chip" style="background:{cor}18;color:{cor};border-color:{cor}30;">
        <i style="background:{cor};"></i>{escape(str(status))}
    </span>
    """


def mobile_dashboard_css():
    st.markdown(
        """
        <style>
            .st-key-dashboard_mobile {
                display: none;
            }

            @media (min-width: 769px) {
                .st-key-dashboard_desktop {
                    display: block !important;
                }

                .st-key-dashboard_mobile {
                    display: none !important;
                }
            }

            @media (max-width: 768px) {
                .st-key-dashboard_desktop {
                    display: none !important;
                }

                .st-key-dashboard_mobile {
                    display: block !important;
                }

                .g3d-mobile-dashboard {
                    font-family: 'Barlow', system-ui, sans-serif;
                    padding-bottom: 6px;
                    width: 100%;
                }

                .g3d-mobile-hero {
                    background: linear-gradient(135deg, #0A1A5C 0%, #0C65AA 60%, #58C3F0 100%);
                    border-radius: 22px;
                    padding: 18px 18px;
                    color: #FFFFFF;
                    box-shadow: 0 14px 34px rgba(10, 26, 92, 0.18);
                    margin: 10px 0 18px 0;
                    overflow: hidden;
                    position: relative;
                }

                .g3d-mobile-hero:after {
                    content: "";
                    width: 130px;
                    height: 130px;
                    border-radius: 50%;
                    background: rgba(255,255,255,0.12);
                    position: absolute;
                    right: -42px;
                    top: -52px;
                }

                .g3d-mobile-hero-label {
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    opacity: 0.86;
                    margin-bottom: 8px;
                }

                .g3d-mobile-hero-value {
                    font-size: 32px;
                    font-weight: 800;
                    line-height: 1;
                    margin-bottom: 6px;
                }

                .g3d-mobile-hero-sub {
                    font-size: 13px;
                    font-weight: 500;
                    opacity: 0.92;
                }

                .g3d-mobile-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 12px;
                    margin-bottom: 18px;
                }

                .g3d-mobile-kpi {
                    background: #FFFFFF;
                    border: 1px solid #DEE9EF;
                    border-top: 4px solid #0C65AA;
                    border-radius: 18px;
                    padding: 14px 14px 13px 14px;
                    box-shadow: 0 9px 24px rgba(10, 26, 92, 0.06);
                    min-height: 114px;
                }

                .g3d-mobile-kpi-title {
                    font-size: 9.5px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    color: #5C6C74;
                    margin-bottom: 8px;
                }

                .g3d-mobile-kpi-value {
                    font-size: 25px;
                    font-weight: 800;
                    line-height: 1.05;
                    margin-bottom: 7px;
                }

                .g3d-mobile-kpi-subtitle {
                    font-size: 11.5px;
                    font-weight: 500;
                    color: #5C6C74;
                    line-height: 1.22;
                }

                .g3d-mobile-section-title {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin: 22px 0 10px 0;
                    border-left: 4px solid #100690;
                    padding-left: 10px;
                }

                .g3d-mobile-section-title span {
                    display: block;
                    font-size: 11px;
                    font-weight: 800;
                    letter-spacing: 2.2px;
                    color: #100690;
                    text-transform: uppercase;
                    line-height: 1.1;
                }

                .g3d-mobile-section-title small {
                    display: block;
                    font-size: 12px;
                    font-weight: 500;
                    color: #5C6C74;
                    margin-top: 5px;
                    line-height: 1.25;
                }

                .g3d-mobile-list {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }

                .g3d-mobile-order-card {
                    background: #FFFFFF;
                    border: 1px solid #DEE9EF;
                    border-radius: 17px;
                    padding: 13px 14px;
                    box-shadow: 0 8px 20px rgba(10, 26, 92, 0.05);
                }

                .g3d-mobile-order-top {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    gap: 12px;
                    margin-bottom: 8px;
                }

                .g3d-mobile-order-code {
                    font-size: 18px;
                    font-weight: 800;
                    color: #0C65AA;
                    line-height: 1;
                }

                .g3d-mobile-order-piece {
                    font-size: 14px;
                    font-weight: 800;
                    color: #1E3137;
                    margin-bottom: 7px;
                    line-height: 1.2;
                }

                .g3d-mobile-order-meta {
                    display: flex;
                    justify-content: space-between;
                    gap: 10px;
                    font-size: 12px;
                    font-weight: 600;
                    color: #5C6C74;
                }

                .g3d-mobile-status-chip {
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    border: 1px solid;
                    border-radius: 999px;
                    padding: 5px 8px;
                    font-size: 10.5px;
                    font-weight: 800;
                    white-space: nowrap;
                }

                .g3d-mobile-status-chip i {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    display: inline-block;
                }

                .g3d-mobile-rank-card {
                    background: #FFFFFF;
                    border: 1px solid #DEE9EF;
                    border-radius: 17px;
                    padding: 13px 14px;
                    box-shadow: 0 8px 20px rgba(10, 26, 92, 0.05);
                }

                .g3d-mobile-rank-head {
                    display: flex;
                    justify-content: space-between;
                    gap: 12px;
                    align-items: flex-start;
                    margin-bottom: 8px;
                }

                .g3d-mobile-rank-title {
                    font-size: 13.5px;
                    font-weight: 800;
                    color: #1E3137;
                    line-height: 1.18;
                }

                .g3d-mobile-rank-value {
                    font-size: 15px;
                    font-weight: 800;
                    color: #0C65AA;
                    white-space: nowrap;
                }

                .g3d-mobile-progress {
                    width: 100%;
                    height: 9px;
                    background: #EDF5FA;
                    border-radius: 999px;
                    overflow: hidden;
                }

                .g3d-mobile-progress span {
                    display: block;
                    height: 100%;
                    border-radius: 999px;
                    background: linear-gradient(90deg, #0C65AA 0%, #58C3F0 100%);
                }

                .g3d-mobile-status-row {
                    background: #FFFFFF;
                    border: 1px solid #DEE9EF;
                    border-radius: 16px;
                    padding: 12px 13px;
                    margin-bottom: 8px;
                    box-shadow: 0 8px 20px rgba(10, 26, 92, 0.04);
                }

                .g3d-mobile-status-row-head {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    gap: 10px;
                    margin-bottom: 8px;
                    font-size: 12.5px;
                    font-weight: 800;
                    color: #1E3137;
                }

                .g3d-mobile-status-row-head strong {
                    color: #5C6C74;
                    font-size: 11.5px;
                    font-weight: 700;
                }

                .g3d-mobile-empty {
                    background: #FFFFFF;
                    border: 1px solid #DEE9EF;
                    border-radius: 16px;
                    padding: 16px;
                    font-size: 13px;
                    color: #5C6C74;
                    box-shadow: 0 8px 20px rgba(10, 26, 92, 0.04);
                }

                .g3d-mobile-foot {
                    margin-top: 20px;
                    padding: 12px 0 0 0;
                    border-top: 1px solid rgba(92,108,116,0.16);
                    font-size: 11px;
                    font-weight: 600;
                    color: #5C6C74;
                    line-height: 1.45;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )

