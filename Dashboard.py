import streamlit as st
from html import escape
from datetime import date

from database import conectar, inicializar_banco
from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.desktop_visual import inject_desktop_visual
from components.desktop_hero import render_desktop_hero
from components.header import header
from components.section import section_title
from components.auth import require_login
from components.dashboard_widgets import (
    moeda,
    render_ranking_faturamento_visual,
    render_status_visual,
    render_tabela,
    render_vendas_mes_chart,
    render_utilizacao_impressoras_chart,
    render_ranking_pecas_faturamento,
    render_distribuicao_faturamento_chart,
    cor_status_hex,
    nome_curto,
    mobile_kpi_html,
    mobile_section_header,
    mobile_status_chip,
    mobile_dashboard_css,
)
from services.dashboard_custos import (
    precalcular_custos_pedidos_dashboard as _svc_dashboard_precalcular_custos_pedidos,
)
from services.dashboard_dados import (
    carregar_config_dashboard as _svc_carregar_config_dashboard,
    carregar_pedidos_dashboard as _svc_carregar_pedidos_dashboard,
    carregar_contadores_dashboard as _svc_carregar_contadores_dashboard,
    carregar_impressoras_ativas_dashboard as _svc_carregar_impressoras_ativas_dashboard,
    carregar_impressora_padrao_dashboard as _svc_carregar_impressora_padrao_dashboard,
)
from services.dashboard_resumos import (
    montar_resumos_dashboard as _svc_montar_resumos_dashboard,
    listar_meses_pedidos_dashboard as _svc_listar_meses_pedidos_dashboard,
    filtrar_pedidos_por_meses_dashboard as _svc_filtrar_pedidos_por_meses_dashboard,
)


st.set_page_config(
    page_title="Gestão 3D",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data(ttl=3600, show_spinner=False)
def carregar_css_base_cache():
    with open("assets/style.css", encoding="utf-8") as f:
        return f.read()


st.markdown(f"<style>{carregar_css_base_cache()}</style>", unsafe_allow_html=True)

require_login()






















































def render_mobile_dashboard(
    pedidos_abertos,
    faturamento_total,
    lucro_total,
    margem_media,
    horas_total,
    lucro_hora,
    meta_lucro,
    pedidos_fechados_mes,
    faturamento_mes,
    pedidos_abertos_lista,
    pecas_resumo,
    status_resumo,
):
    """
    Dashboard mobile recriada.

    Mantém a assinatura antiga para não quebrar a chamada existente.
    Usa variáveis globais já calculadas na Dashboard:
    - vendas_mes_grafico
    - clientes_resumo
    """
    status_ordem = ["Orçamento", "Encomendado", "Em Produção", "Pronto", "Entregue", "Cancelado"]
    vendas_mobile = globals().get("vendas_mes_grafico", [])
    clientes_mobile = globals().get("clientes_resumo", {})
    impressoras_mobile = globals().get("impressoras_resumo", {})
    distribuicao_mobile = globals().get("distribuicao_faturamento", {})
    utilizacao_mobile = globals().get("utilizacao_impressoras_grafico", [])

    def card_empty(texto):
        return f'<div class="g3d-mobile-empty">{escape(str(texto))}</div>'

    def ranking_faturamento_mobile(itens_resumo, tipo="pecas", limite=5):
        ranking = sorted(
            itens_resumo.items(),
            key=lambda item: item[1]["faturamento"],
            reverse=True
        )[:limite]

        if not ranking:
            return card_empty("Nenhum dado cadastrado ainda.")

        max_faturamento = max([dados["faturamento"] for _, dados in ranking], default=1)
        if max_faturamento <= 0:
            max_faturamento = 1

        cards = ""

        for posicao, (nome, dados) in enumerate(ranking, start=1):
            faturamento = dados.get("faturamento", 0)
            lucro = dados.get("lucro", 0)
            largura = max(6, int((faturamento / max_faturamento) * 100))
            margem = (lucro / faturamento * 100) if faturamento > 0 else 0

            if tipo == "pecas":
                qtd = dados.get("quantidade", 0)
                qtd_txt = f"{qtd:.0f} un vendidas"
            else:
                qtd = dados.get("pedidos", 0)
                qtd_txt = f"{qtd:.0f} pedidos"

            cards += f"""
            <div class="g3d-mobile-rank-card">
                <div class="g3d-mobile-rank-head">
                    <div class="g3d-mobile-rank-title">{posicao}. {escape(nome_curto(nome, 44))}</div>
                    <div class="g3d-mobile-rank-value">{escape(moeda(faturamento))}</div>
                </div>
                <div class="g3d-mobile-order-meta" style="margin-bottom:8px;">
                    <span>{escape(qtd_txt)}</span>
                    <span>Lucro {escape(moeda(lucro))}</span>
                </div>
                <div class="g3d-mobile-order-meta" style="margin-bottom:8px;">
                    <span>Margem {margem:.0f}%</span>
                    <span></span>
                </div>
                <div class="g3d-mobile-progress"><span style="width:{largura}%;"></span></div>
            </div>
            """

        return cards

    total_status = sum(dados["pedidos"] for dados in status_resumo.values())
    status_cards = ""

    for status in status_ordem:
        dados = status_resumo.get(status)
        if not dados:
            continue

        quantidade = dados.get("pedidos", 0)
        percentual = int((quantidade / total_status) * 100) if total_status else 0
        cor = cor_status_hex(status)

        status_cards += f"""
        <div class="g3d-mobile-status-row">
            <div class="g3d-mobile-status-row-head">
                <span>{mobile_status_chip(status)}</span>
                <strong>{quantidade:.0f} · {percentual}%</strong>
            </div>
            <div class="g3d-mobile-progress"><span style="width:{percentual}%;background:{cor};"></span></div>
        </div>
        """

    if not status_cards:
        status_cards = card_empty("Nenhum pedido cadastrado ainda.")

    pedidos_cards = ""

    for item in pedidos_abertos_lista[:5]:
        codigo, peca, qtd, status, data = item
        pedidos_cards += f"""
        <div class="g3d-mobile-order-card">
            <div class="g3d-mobile-order-top">
                <div class="g3d-mobile-order-code">{escape(str(codigo))}</div>
                {mobile_status_chip(status)}
            </div>
            <div class="g3d-mobile-order-piece">{escape(nome_curto(peca, 44))}</div>
            <div class="g3d-mobile-order-meta">
                <span>Qtd. {escape(str(qtd))}</span>
                <span>{escape(str(data))}</span>
            </div>
        </div>
        """

    if not pedidos_cards:
        pedidos_cards = card_empty("Nenhum pedido aberto no momento.")

    pecas_cards = ranking_faturamento_mobile(pecas_resumo, tipo="pecas", limite=5)
    clientes_cards = ranking_faturamento_mobile(clientes_mobile, tipo="clientes", limite=5)

    html_topo = f"""
    <style>
        @media (max-width: 768px) {{
            .g3d-mobile-dashboard-v2 {{
                font-family: 'Barlow', system-ui, sans-serif;
                padding-bottom: 8px;
                width: 100%;
            }}

            .g3d-mobile-dashboard-v2 .g3d-mobile-list {{
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}

            .g3d-mobile-dashboard-v2 .g3d-mobile-rank-card,
            .g3d-mobile-dashboard-v2 .g3d-mobile-order-card,
            .g3d-mobile-dashboard-v2 .g3d-mobile-status-row {{
                width: 100%;
                box-sizing: border-box;
            }}
        }}
    </style>

    <div class="g3d-mobile-dashboard g3d-mobile-dashboard-v2">
        <div class="g3d-mobile-hero">
            <div class="g3d-mobile-hero-label">Resumo do período</div>
            <div class="g3d-mobile-hero-value">{escape(moeda(faturamento_mes))}</div>
            <div class="g3d-mobile-hero-sub">{pedidos_fechados_mes:.0f} pedidos entregues no período</div>
        </div>

        <div class="g3d-mobile-grid">
            {mobile_kpi_html("Abertos", pedidos_abertos, "pedidos aguardando ação", "blue")}
            {mobile_kpi_html("Faturamento", moeda(faturamento_total), "pedidos não cancelados", "green")}
            {mobile_kpi_html("Lucro", moeda(lucro_total), f"margem {margem_media:.0f}%", "green" if lucro_total >= 0 else "red")}
            {mobile_kpi_html("Lucro/Hora", f"R$ {lucro_hora:.2f}".replace(".", ","), f"meta {moeda(meta_lucro)}/h", "green" if lucro_hora >= meta_lucro else "gray")}
        </div>

        {mobile_section_header("Pedidos por status", "Distribuição atual")}
        <div class="g3d-mobile-list">{status_cards}</div>

        {mobile_section_header("Pedidos abertos por peça", "O que precisa de atenção agora")}
        <div class="g3d-mobile-list">{pedidos_cards}</div>

        {mobile_section_header("Vendas por mês", "Vendas, lucro e margem")}
    </div>
    """

    try:
        st.html(html_topo)
    except AttributeError:
        st.markdown(html_topo, unsafe_allow_html=True)

    render_vendas_mes_chart(vendas_mobile)

    html_meio = f"""
    <div class="g3d-mobile-dashboard g3d-mobile-dashboard-v2">
        {mobile_section_header("Faturamento por impressora", "Ranking por faturamento e lucro")}
    </div>
    """
    try:
        st.html(html_meio)
    except AttributeError:
        st.markdown(html_meio, unsafe_allow_html=True)

    render_ranking_faturamento_visual(impressoras_mobile, label_quantidade="pedidos", limite=8)

    html_distribuicao = f"""
    <div class="g3d-mobile-dashboard g3d-mobile-dashboard-v2">
        {mobile_section_header("Distribuição do faturamento", "Custos e lucro no período")}
    </div>
    """
    try:
        st.html(html_distribuicao)
    except AttributeError:
        st.markdown(html_distribuicao, unsafe_allow_html=True)

    render_distribuicao_faturamento_chart(distribuicao_mobile)

    html_utilizacao = f"""
    <div class="g3d-mobile-dashboard g3d-mobile-dashboard-v2">
        {mobile_section_header("Utilização das impressoras por mês", "Horas usadas por máquina")}
    </div>
    """
    try:
        st.html(html_utilizacao)
    except AttributeError:
        st.markdown(html_utilizacao, unsafe_allow_html=True)

    render_utilizacao_impressoras_chart(utilizacao_mobile)

    html_base = f"""
    <div class="g3d-mobile-dashboard g3d-mobile-dashboard-v2">
        {mobile_section_header("Peças com maior faturamento", "Ranking por faturamento")}
        <div class="g3d-mobile-list">{pecas_cards}</div>

        {mobile_section_header("Clientes com maior faturamento", "Ranking por faturamento")}
        <div class="g3d-mobile-list">{clientes_cards}</div>

        <div class="g3d-mobile-foot">
            Horas vendidas: <strong>{horas_total:.1f}h</strong> ·
            Faturamento total: <strong>{escape(moeda(faturamento_total))}</strong>
        </div>
    </div>
    """

    try:
        st.html(html_base)
    except AttributeError:
        st.markdown(html_base, unsafe_allow_html=True)



inicializar_banco()
conn = conectar()

config = _svc_carregar_config_dashboard(conn)

energia = config[0]
depreciacao = config[1]
margem = config[2]
meta_lucro = config[3]
custo_pos_processamento_hora = config[4] if len(config) > 4 else 0

pedidos = _svc_carregar_pedidos_dashboard(conn)

contadores_dashboard = _svc_carregar_contadores_dashboard(conn)
total_clientes = contadores_dashboard.get("clientes", 0)
total_pecas = contadores_dashboard.get("pecas", 0)
total_filamentos = contadores_dashboard.get("filamentos", 0)
total_impressoras = contadores_dashboard.get("impressoras", 0)

impressoras_ativas_dashboard = _svc_carregar_impressoras_ativas_dashboard(conn)

impressora_padrao = _svc_carregar_impressora_padrao_dashboard(conn)

if impressora_padrao:
    impressora_padrao_nome = f"{impressora_padrao[0]} - {impressora_padrao[1]} {impressora_padrao[2]}"
else:
    impressora_padrao_nome = "Impressora padrão"


sidebar()

mobile_bottom_nav("dashboard")
inject_desktop_visual()
header(
    "Início",
    "Visão geral da operação"
)

meses_dashboard = _svc_listar_meses_pedidos_dashboard(pedidos)

labels_para_keys_dashboard = {
    item["label"]: item["key"]
    for item in meses_dashboard
}

opcoes_meses_dashboard = ["Todos"] + [item["label"] for item in meses_dashboard]

st.markdown(
    """
    <style>
        div[data-testid="stMultiSelect"] label p {
            font-family: 'Barlow', system-ui, sans-serif;
            color:#0A1A5C;
            font-size:12px;
            font-weight:800;
            letter-spacing:.08em;
            text-transform:uppercase;
        }

        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
            background-color:#0C65AA !important;
            border-color:#0C65AA !important;
            color:#FFFFFF !important;
        }

        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] span {
            color:#FFFFFF !important;
        }

        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] svg {
            color:#FFFFFF !important;
            fill:#FFFFFF !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

col_filtro_mes, col_filtro_info = st.columns([2.2, 1])

with col_filtro_mes:
    meses_selecionados_dashboard = st.multiselect(
        "Filtro por mês/ano",
        options=opcoes_meses_dashboard,
        default=["Todos"],
        help="Use Todos para ver a operação inteira ou escolha um ou mais meses para analisar.",
        key="dashboard_filtro_meses",
    )

meses_especificos_dashboard = [
    mes
    for mes in meses_selecionados_dashboard
    if mes != "Todos"
]

if meses_especificos_dashboard:
    meses_keys_selecionados_dashboard = [
        labels_para_keys_dashboard[mes]
        for mes in meses_especificos_dashboard
        if mes in labels_para_keys_dashboard
    ]
    filtro_dashboard_label = ", ".join(meses_especificos_dashboard)
else:
    meses_keys_selecionados_dashboard = []
    filtro_dashboard_label = "Todos os meses"

pedidos_para_dashboard = _svc_filtrar_pedidos_por_meses_dashboard(
    pedidos,
    meses_keys_selecionados_dashboard,
)

with col_filtro_info:
    st.markdown(
        f"""
        <div style="
            margin-top:26px;
            padding:11px 13px;
            border:1px solid rgba(185,205,220,0.78);
            background:#FFFFFF;
            border-radius:15px;
            font-family:'Barlow', system-ui, sans-serif;
            color:#5C6C74;
            font-size:12px;
            font-weight:600;
            box-shadow:0 8px 20px rgba(10,26,92,0.04);
        ">
            <strong style="color:#0A1A5C;">Período:</strong> {escape(filtro_dashboard_label)}
            <br>
            <strong style="color:#0A1A5C;">Pedidos:</strong> {len(pedidos_para_dashboard)}
        </div>
        """,
        unsafe_allow_html=True
    )

custos_pecas_dashboard = _svc_dashboard_precalcular_custos_pedidos(
    conn,
    pedidos_para_dashboard,
    energia,
    depreciacao,
    custo_pos_processamento_hora,
)

conn.close()

pedidos = pedidos_para_dashboard


_resumos_dashboard = _svc_montar_resumos_dashboard(
    pedidos=pedidos,
    custos_pecas_dashboard=custos_pecas_dashboard,
    energia=energia,
    depreciacao=depreciacao,
    custo_pos_processamento_hora=custo_pos_processamento_hora,
    impressoras_ativas_dashboard=impressoras_ativas_dashboard,
    impressora_padrao_nome=impressora_padrao_nome,
    hoje=date.today(),
)

pedidos_abertos = _resumos_dashboard["pedidos_abertos"]
faturamento_total = _resumos_dashboard["faturamento_total"]
lucro_total = _resumos_dashboard["lucro_total"]
horas_total = _resumos_dashboard["horas_total"]
quantidade_total = _resumos_dashboard["quantidade_total"]
pedidos_fechados_mes = _resumos_dashboard["pedidos_fechados_mes"]
faturamento_mes = _resumos_dashboard["faturamento_mes"]
lucro_mes = _resumos_dashboard["lucro_mes"]
lucro_hora = _resumos_dashboard["lucro_hora"]
margem_media = _resumos_dashboard["margem_media"]
ticket_medio = _resumos_dashboard["ticket_medio"]
status_resumo = _resumos_dashboard["status_resumo"]
pecas_resumo = _resumos_dashboard["pecas_resumo"]
clientes_resumo = _resumos_dashboard["clientes_resumo"]
impressoras_resumo = _resumos_dashboard["impressoras_resumo"]
vendas_mes_grafico = _resumos_dashboard["vendas_mes_grafico"]
utilizacao_impressoras_grafico = _resumos_dashboard["utilizacao_impressoras_grafico"]
pedidos_recentes = _resumos_dashboard["pedidos_recentes"]
pedidos_abertos_lista = _resumos_dashboard["pedidos_abertos_lista"]
distribuicao_faturamento = _resumos_dashboard.get("distribuicao_faturamento", {})

mobile_dashboard_css()

with st.container(key="dashboard_mobile"):
    render_mobile_dashboard(
        pedidos_abertos=pedidos_abertos,
        faturamento_total=faturamento_total,
        lucro_total=lucro_total,
        margem_media=margem_media,
        horas_total=horas_total,
        lucro_hora=lucro_hora,
        meta_lucro=meta_lucro,
        pedidos_fechados_mes=pedidos_fechados_mes,
        faturamento_mes=faturamento_mes,
        pedidos_abertos_lista=pedidos_abertos_lista,
        pecas_resumo=pecas_resumo,
        status_resumo=status_resumo,
    )

with st.container(key="dashboard_desktop"):

    render_desktop_hero(
        label="Resumo executivo",
        value=moeda(faturamento_mes),
        subtitle=f"{len(pedidos):.0f} pedidos no período · lucro estimado {moeda(lucro_mes)}",
        items=[
            {"label": "Pedidos abertos", "value": pedidos_abertos},
            {"label": "Faturamento geral", "value": moeda(faturamento_total)},
            {"label": "Peças vendidas", "value": f"{quantidade_total:.0f} un"},
            {"label": "Lucro geral", "value": moeda(lucro_total), "note": f"(margem {margem_media:.0f}%)"},
        ],
    )

    col_status, col_abertos = st.columns(2)

    with col_status:
        section_title(
            "Pedidos por status",
            "Distribuição visual dos pedidos"
        )
        status_ordem = ["Orçamento", "Encomendado", "Em Produção", "Pronto", "Entregue", "Cancelado"]
        render_status_visual(status_resumo, status_ordem)

    with col_abertos:
        section_title(
            "Pedidos abertos por peça",
            "Lista rápida do que ainda precisa de ação"
        )
        render_tabela(
            ["Pedido", "Peça", "Qtd.", "Status", "Data"],
            pedidos_abertos_lista,
            "Nenhum pedido aberto no momento."
        )

    section_title(
        "Vendas por mês",
        "Vendas e lucro em barras, com margem de lucro em linha"
    )

    render_vendas_mes_chart(vendas_mes_grafico)

    col_imp_fat, col_dist_fat = st.columns(2)

    with col_imp_fat:
        section_title(
            "Faturamento por impressora",
            "Ranking por faturamento e lucro gerado por máquina"
        )
        render_ranking_faturamento_visual(impressoras_resumo, label_quantidade="pedidos", limite=8)

    with col_dist_fat:
        section_title(
            "Distribuição do faturamento",
            "Participação de custos e lucro no faturamento selecionado"
        )
        render_distribuicao_faturamento_chart(distribuicao_faturamento)

    section_title(
        "Utilização das impressoras por mês",
        "Usa Data Final Produção; pedidos antigos sem essa data usam Data do Pedido"
    )
    render_utilizacao_impressoras_chart(utilizacao_impressoras_grafico)

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        section_title(
            "Peças com maior faturamento",
            "Ranking por faturamento; passe o mouse para ver faturamento e quantidade"
        )
        render_ranking_pecas_faturamento(pecas_resumo)

    with col_r2:
        section_title(
            "Clientes com maior faturamento",
            "Ranking por faturamento; passe o mouse para ver pedidos, lucro e margem"
        )
        render_ranking_faturamento_visual(clientes_resumo, label_quantidade="pedidos", limite=8)


    st.write("")
    st.write("")


    st.markdown(
        f"""
        <div style="
            margin-top:36px;
            padding-top:14px;
            border-top:1px solid rgba(92,108,116,0.18);
            font-family:'Barlow', system-ui, sans-serif;
            font-size:12px;
            font-weight:500;
            color:#5C6C74;
            display:flex;
            gap:8px;
            flex-wrap:wrap;
            align-items:center;
        ">
            <span style="font-weight:700;">Parâmetros atuais:</span>
            <span>Impressora padrão: {escape(impressora_padrao_nome)}</span>
            <span>·</span>
            <span>Energia padrão {moeda(energia)}/h</span>
            <span>·</span>
            <span>Depreciação padrão {moeda(depreciacao)}/h</span>
            <span>·</span>
            <span>Markup {margem:.0f}%</span>
            <span>·</span>
            <span>Meta lucro/hora {moeda(meta_lucro)}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
