import streamlit as st
import pandas as pd
import json
from html import escape
from collections import defaultdict
from datetime import date, datetime

from database import conectar, inicializar_banco
from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.desktop_visual import inject_desktop_visual
from components.desktop_hero import render_desktop_hero
from components.header import header
from components.kpi import kpi_card
from components.section import section_title
from components.auth import require_login
from components.formatters import data_br, data_para_date


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
    status_ordem = ["Orçamento", "Encomendado", "Em Produção", "Pronto", "Entregue", "Cancelado"]
    pecas_ranking = sorted(pecas_resumo.items(), key=lambda item: item[1]["quantidade"], reverse=True)[:5]
    max_qtd = max([dados["quantidade"] for _, dados in pecas_ranking], default=1)

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
        pedidos_cards = '<div class="g3d-mobile-empty">Nenhum pedido aberto no momento.</div>'

    ranking_cards = ""
    for nome, dados in pecas_ranking:
        largura = int((dados["quantidade"] / max_qtd) * 100) if max_qtd else 0
        ranking_cards += f"""
        <div class="g3d-mobile-rank-card">
            <div class="g3d-mobile-rank-head">
                <div class="g3d-mobile-rank-title">{escape(nome_curto(nome, 46))}</div>
                <div class="g3d-mobile-rank-value">{dados["quantidade"]:.0f} un.</div>
            </div>
            <div class="g3d-mobile-progress"><span style="width:{largura}%;"></span></div>
        </div>
        """

    if not ranking_cards:
        ranking_cards = '<div class="g3d-mobile-empty">Nenhuma peça vendida ainda.</div>'

    total_status = sum(dados["pedidos"] for dados in status_resumo.values())
    status_cards = ""
    for status in status_ordem:
        dados = status_resumo.get(status)
        if not dados:
            continue
        quantidade = dados["pedidos"]
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
        status_cards = '<div class="g3d-mobile-empty">Nenhum pedido cadastrado ainda.</div>'

    html = f"""
    <div class="g3d-mobile-dashboard">
        <div class="g3d-mobile-hero">
            <div class="g3d-mobile-hero-label">Resumo do mês</div>
            <div class="g3d-mobile-hero-value">{escape(moeda(faturamento_mes))}</div>
            <div class="g3d-mobile-hero-sub">{pedidos_fechados_mes:.0f} pedidos fechados no mês</div>
        </div>

        <div class="g3d-mobile-grid">
            {mobile_kpi_html("Abertos", pedidos_abertos, "pedidos aguardando ação", "blue")}
            {mobile_kpi_html("Faturamento", moeda(faturamento_total), "pedidos não cancelados", "green")}
            {mobile_kpi_html("Lucro", moeda(lucro_total), f"margem {margem_media:.0f}%", "green" if lucro_total >= 0 else "red")}
            {mobile_kpi_html("Lucro/Hora", f"R$ {lucro_hora:.2f}".replace(".", ","), f"meta {moeda(meta_lucro)}/h", "green" if lucro_hora >= meta_lucro else "gray")}
        </div>

        {mobile_section_header("Pedidos abertos", "O que precisa de atenção agora")}
        <div class="g3d-mobile-list">{pedidos_cards}</div>

        {mobile_section_header("Peças mais vendidas", "Ranking por quantidade")}
        <div class="g3d-mobile-list">{ranking_cards}</div>

        {mobile_section_header("Status dos pedidos", "Distribuição atual")}
        <div>{status_cards}</div>

        <div class="g3d-mobile-foot">
            Horas vendidas: <strong>{horas_total:.1f}h</strong> ·
            Faturamento total: <strong>{escape(moeda(faturamento_total))}</strong>
        </div>
    </div>
    """

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)


inicializar_banco()



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

    altura = min(520, 36 + len(ranking) * 83)
    st.components.v1.html(html, height=altura, scrolling=True)


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


def garantir_tabelas_dashboard():
    conn = conectar()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nome TEXT NOT NULL,
        tipo TEXT,
        documento TEXT,
        telefone TEXT,
        email TEXT,
        cidade TEXT,
        estado TEXT,
        instagram TEXT,
        origem TEXT,
        observacoes TEXT,
        status TEXT DEFAULT 'Ativo',
        data_cadastro TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        cliente_id INTEGER,
        peca_id INTEGER,
        quantidade REAL DEFAULT 1,
        valor_unitario REAL DEFAULT 0,
        desconto REAL DEFAULT 0,
        frete REAL DEFAULT 0,
        status TEXT DEFAULT 'Orçamento',
        canal TEXT,
        data_pedido TEXT,
        data_entrega_prevista TEXT,
        observacoes TEXT
    )
    """)

    colunas_pecas = conn.execute("PRAGMA table_info(pecas)").fetchall()
    nomes_colunas_pecas = [coluna[1] for coluna in colunas_pecas]

    if "quantidade_lote" not in nomes_colunas_pecas:
        conn.execute("ALTER TABLE pecas ADD COLUMN quantidade_lote REAL DEFAULT 1")

    conn.commit()
    conn.close()


def carregar_acessorios_da_peca(conn, peca_id):
    return conn.execute("""
    SELECT
        a.custo_unitario,
        pa.quantidade
    FROM peca_acessorios pa
    LEFT JOIN acessorios a ON pa.acessorio_id = a.id
    WHERE pa.peca_id = ?
    """, (peca_id,)).fetchall()


def carregar_filamentos_da_peca(conn, peca_id):
    return conn.execute("""
    SELECT
        f.custo_grama,
        pf.peso_g
    FROM peca_filamentos pf
    LEFT JOIN filamentos f ON pf.filamento_id = f.id
    WHERE pf.peca_id = ?
    ORDER BY pf.id ASC
    """, (peca_id,)).fetchall()


def calcular_custo_unitario_peca(peca_id, energia_hora, depreciacao_hora, custo_pos_processamento_hora=0):
    conn = conectar()

    peca = conn.execute("""
    SELECT
        p.peso_g,
        p.tempo_impressao_h,
        p.tempo_pos_processamento_min,
        p.embalagem_custo,
        COALESCE(p.quantidade_lote, 1),
        f.custo_grama
    FROM pecas p
    LEFT JOIN filamentos f ON p.filamento_id = f.id
    WHERE p.id = ?
    """, (peca_id,)).fetchone()

    if peca is None:
        conn.close()
        return {
            "custo_unitario": 0,
            "peso_unitario": 0,
            "tempo_unitario": 0,
        }

    acessorios = carregar_acessorios_da_peca(conn, peca_id)
    filamentos_peca = carregar_filamentos_da_peca(conn, peca_id)
    conn.close()

    peso_g = peca[0] if peca[0] else 0
    tempo_h = peca[1] if peca[1] else 0
    tempo_pos_h = (peca[2] if peca[2] else 0) / 60
    embalagem = peca[3] if peca[3] else 0
    quantidade_lote = peca[4] if peca[4] and peca[4] > 0 else 1
    custo_grama = peca[5] if peca[5] else 0

    if filamentos_peca:
        peso_g = sum((f[1] if f[1] else 0) for f in filamentos_peca)
        custo_material = sum((f[0] if f[0] else 0) * (f[1] if f[1] else 0) for f in filamentos_peca)
    else:
        custo_material = peso_g * custo_grama

    custo_energia = tempo_h * energia_hora
    custo_depreciacao = tempo_h * depreciacao_hora
    custo_pos_processamento = tempo_pos_h * custo_pos_processamento_hora
    custo_acessorios = sum(
        (a[0] if a[0] else 0) * (a[1] if a[1] else 0)
        for a in acessorios
    )

    custo_lote = (
        custo_material
        + custo_energia
        + custo_depreciacao
        + custo_pos_processamento
        + embalagem
        + custo_acessorios
    )

    custo_unitario = custo_lote / quantidade_lote if quantidade_lote > 0 else custo_lote
    peso_unitario = peso_g / quantidade_lote if quantidade_lote > 0 else peso_g
    tempo_total_h = tempo_h + tempo_pos_h
    tempo_unitario = tempo_total_h / quantidade_lote if quantidade_lote > 0 else tempo_total_h

    return {
        "custo_unitario": custo_unitario,
        "peso_unitario": peso_unitario,
        "tempo_unitario": tempo_unitario,
    }

def calcular_custos_pecas_lote(conn, peca_ids, energia_hora, depreciacao_hora, custo_pos_processamento_hora=0):
    """
    Calcula custos de várias peças em lote.

    Evita fazer 2 a 3 consultas no banco para cada pedido da Dashboard.
    No Turso/cloud isso reduz bastante o número de chamadas remotas.
    """
    peca_ids = sorted({int(pid) for pid in peca_ids if pid})

    if not peca_ids:
        return {}

    placeholders = ",".join(["?"] * len(peca_ids))

    pecas = conn.execute(f"""
    SELECT
        p.id,
        p.peso_g,
        p.tempo_impressao_h,
        p.tempo_pos_processamento_min,
        p.embalagem_custo,
        COALESCE(p.quantidade_lote, 1),
        f.custo_grama
    FROM pecas p
    LEFT JOIN filamentos f ON p.filamento_id = f.id
    WHERE p.id IN ({placeholders})
    """, peca_ids).fetchall()

    acessorios_rows = conn.execute(f"""
    SELECT
        pa.peca_id,
        a.custo_unitario,
        pa.quantidade
    FROM peca_acessorios pa
    LEFT JOIN acessorios a ON pa.acessorio_id = a.id
    WHERE pa.peca_id IN ({placeholders})
    """, peca_ids).fetchall()

    filamentos_rows = conn.execute(f"""
    SELECT
        pf.peca_id,
        f.custo_grama,
        pf.peso_g
    FROM peca_filamentos pf
    LEFT JOIN filamentos f ON pf.filamento_id = f.id
    WHERE pf.peca_id IN ({placeholders})
    ORDER BY pf.id ASC
    """, peca_ids).fetchall()

    acessorios_por_peca = {}
    for peca_id, custo_unitario, quantidade in acessorios_rows:
        acessorios_por_peca.setdefault(peca_id, []).append((
            custo_unitario if custo_unitario else 0,
            quantidade if quantidade else 0,
        ))

    filamentos_por_peca = {}
    for peca_id, custo_grama, peso_g in filamentos_rows:
        filamentos_por_peca.setdefault(peca_id, []).append((
            custo_grama if custo_grama else 0,
            peso_g if peso_g else 0,
        ))

    custos = {}

    for peca in pecas:
        peca_id = peca[0]
        peso_g = peca[1] if peca[1] else 0
        tempo_h = peca[2] if peca[2] else 0
        tempo_pos_h = (peca[3] if peca[3] else 0) / 60
        embalagem = peca[4] if peca[4] else 0
        quantidade_lote = peca[5] if peca[5] and peca[5] > 0 else 1
        custo_grama = peca[6] if peca[6] else 0

        filamentos_peca = filamentos_por_peca.get(peca_id, [])
        acessorios_peca = acessorios_por_peca.get(peca_id, [])

        if filamentos_peca:
            peso_g = sum(peso for _, peso in filamentos_peca)
            custo_material = sum(custo * peso for custo, peso in filamentos_peca)
        else:
            custo_material = peso_g * custo_grama

        custo_energia = tempo_h * energia_hora
        custo_depreciacao = tempo_h * depreciacao_hora
        custo_pos_processamento = tempo_pos_h * custo_pos_processamento_hora
        custo_acessorios = sum(custo * quantidade for custo, quantidade in acessorios_peca)

        custo_lote = (
            custo_material
            + custo_energia
            + custo_depreciacao
            + custo_pos_processamento
            + embalagem
            + custo_acessorios
        )

        custos[peca_id] = {
            "custo_unitario": custo_lote / quantidade_lote if quantidade_lote > 0 else custo_lote,
            "peso_unitario": peso_g / quantidade_lote if quantidade_lote > 0 else peso_g,
            "tempo_unitario": (tempo_h + tempo_pos_h) / quantidade_lote if quantidade_lote > 0 else (tempo_h + tempo_pos_h),
        }

    return custos


def calcular_pedido(peca_id, quantidade, valor_unitario, desconto, frete, energia_hora, depreciacao_hora, custo_peca=None, custo_pos_processamento_hora=0):
    if custo_peca is None:
        custo_peca = calcular_custo_unitario_peca(peca_id, energia_hora, depreciacao_hora, custo_pos_processamento_hora)

    quantidade = quantidade if quantidade else 0
    valor_unitario = valor_unitario if valor_unitario else 0
    desconto = desconto if desconto else 0
    frete = frete if frete else 0

    subtotal = quantidade * valor_unitario
    total = subtotal - desconto + frete
    custo_total = quantidade * custo_peca["custo_unitario"]
    lucro = total - custo_total
    tempo_total = quantidade * custo_peca["tempo_unitario"]

    margem_venda = (lucro / total) * 100 if total > 0 else 0
    lucro_hora = lucro / tempo_total if tempo_total > 0 else 0

    return {
        "subtotal": subtotal,
        "total": total,
        "custo_total": custo_total,
        "lucro": lucro,
        "tempo_total": tempo_total,
        "margem_venda": margem_venda,
        "lucro_hora": lucro_hora,
    }


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
    <div style="
        background:#FFFFFF;
        border:1px solid rgba(185, 205, 220, 0.78);
        border-radius:20px;
        padding:18px 18px 8px 18px;
        box-shadow:0 14px 32px rgba(10, 26, 92, 0.065);
    ">
        <canvas id="g3d-vendas-mes-chart" style="width:100%;height:340px;"></canvas>
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
    status_ordem = ["Orçamento", "Encomendado", "Em Produção", "Pronto", "Entregue", "Cancelado"]
    pecas_ranking = sorted(pecas_resumo.items(), key=lambda item: item[1]["quantidade"], reverse=True)[:5]
    max_qtd = max([dados["quantidade"] for _, dados in pecas_ranking], default=1)

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
        pedidos_cards = '<div class="g3d-mobile-empty">Nenhum pedido aberto no momento.</div>'

    ranking_cards = ""
    for nome, dados in pecas_ranking:
        largura = int((dados["quantidade"] / max_qtd) * 100) if max_qtd else 0
        ranking_cards += f"""
        <div class="g3d-mobile-rank-card">
            <div class="g3d-mobile-rank-head">
                <div class="g3d-mobile-rank-title">{escape(nome_curto(nome, 46))}</div>
                <div class="g3d-mobile-rank-value">{dados["quantidade"]:.0f} un.</div>
            </div>
            <div class="g3d-mobile-progress"><span style="width:{largura}%;"></span></div>
        </div>
        """

    if not ranking_cards:
        ranking_cards = '<div class="g3d-mobile-empty">Nenhuma peça vendida ainda.</div>'

    total_status = sum(dados["pedidos"] for dados in status_resumo.values())
    status_cards = ""
    for status in status_ordem:
        dados = status_resumo.get(status)
        if not dados:
            continue
        quantidade = dados["pedidos"]
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
        status_cards = '<div class="g3d-mobile-empty">Nenhum pedido cadastrado ainda.</div>'

    html = f"""
    <div class="g3d-mobile-dashboard">
        <div class="g3d-mobile-hero">
            <div class="g3d-mobile-hero-label">Resumo do mês</div>
            <div class="g3d-mobile-hero-value">{escape(moeda(faturamento_mes))}</div>
            <div class="g3d-mobile-hero-sub">{pedidos_fechados_mes:.0f} pedidos fechados no mês</div>
        </div>

        <div class="g3d-mobile-grid">
            {mobile_kpi_html("Abertos", pedidos_abertos, "pedidos aguardando ação", "blue")}
            {mobile_kpi_html("Faturamento", moeda(faturamento_total), "pedidos não cancelados", "green")}
            {mobile_kpi_html("Lucro", moeda(lucro_total), f"margem {margem_media:.0f}%", "green" if lucro_total >= 0 else "red")}
            {mobile_kpi_html("Lucro/Hora", f"R$ {lucro_hora:.2f}".replace(".", ","), f"meta {moeda(meta_lucro)}/h", "green" if lucro_hora >= meta_lucro else "gray")}
        </div>

        {mobile_section_header("Pedidos abertos", "O que precisa de atenção agora")}
        <div class="g3d-mobile-list">{pedidos_cards}</div>

        {mobile_section_header("Peças mais vendidas", "Ranking por quantidade")}
        <div class="g3d-mobile-list">{ranking_cards}</div>

        {mobile_section_header("Status dos pedidos", "Distribuição atual")}
        <div>{status_cards}</div>

        <div class="g3d-mobile-foot">
            Horas vendidas: <strong>{horas_total:.1f}h</strong> ·
            Faturamento total: <strong>{escape(moeda(faturamento_total))}</strong>
        </div>
    </div>
    """

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)


inicializar_banco()
conn = conectar()

config = conn.execute("""
SELECT
    energia_hora,
    depreciacao_hora,
    margem_padrao,
    meta_lucro_hora,
    COALESCE(custo_pos_processamento_hora, 0)
FROM configuracoes
LIMIT 1
""").fetchone()

energia = config[0]
depreciacao = config[1]
margem = config[2]
meta_lucro = config[3]
custo_pos_processamento_hora = config[4] if len(config) > 4 else 0

pedidos = conn.execute("""
SELECT
    ped.id,
    ped.codigo,
    ped.cliente_id,
    c.codigo,
    c.nome,
    ped.peca_id,
    pc.codigo,
    pc.nome,
    ped.quantidade,
    ped.valor_unitario,
    ped.desconto,
    ped.frete,
    ped.status,
    ped.canal,
    ped.data_pedido,
    ped.data_entrega_prevista
FROM pedidos ped
LEFT JOIN clientes c ON ped.cliente_id = c.id
LEFT JOIN pecas pc ON ped.peca_id = pc.id
ORDER BY ped.id DESC
""").fetchall()

peca_ids_dashboard = sorted({pedido[5] for pedido in pedidos if pedido[5]})
custos_pecas_dashboard = calcular_custos_pecas_lote(
    conn,
    peca_ids_dashboard,
    energia,
    depreciacao,
    custo_pos_processamento_hora
)

total_clientes = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
total_pecas = conn.execute("SELECT COUNT(*) FROM pecas").fetchone()[0]
total_filamentos = conn.execute("SELECT COUNT(*) FROM filamentos").fetchone()[0]

conn.close()


pedidos_abertos = 0
faturamento_total = 0
lucro_total = 0
horas_total = 0
quantidade_total = 0
pedidos_fechados_mes = 0
faturamento_mes = 0
lucro_mes = 0
hoje = date.today()

status_resumo = defaultdict(lambda: {
    "pedidos": 0,
    "faturamento": 0,
    "lucro": 0,
})

pecas_resumo = defaultdict(lambda: {
    "quantidade": 0,
    "faturamento": 0,
    "lucro": 0,
})

clientes_resumo = defaultdict(lambda: {
    "pedidos": 0,
    "faturamento": 0,
    "lucro": 0,
})

vendas_mes_resumo = defaultdict(lambda: {
    "mes": "",
    "pedidos": 0,
    "quantidade": 0,
    "faturamento": 0,
    "lucro": 0,
})

pedidos_recentes = []
pedidos_abertos_lista = []

for pedido in pedidos:
    codigo = pedido[1]
    cliente_codigo = pedido[3] if pedido[3] else "-"
    cliente_nome = pedido[4] if pedido[4] else "-"
    peca_id = pedido[5]
    peca_codigo = pedido[6] if pedido[6] else "-"
    peca_nome = pedido[7] if pedido[7] else "-"
    quantidade = pedido[8] if pedido[8] else 0
    valor_unitario = pedido[9] if pedido[9] else 0
    desconto = pedido[10] if pedido[10] else 0
    frete = pedido[11] if pedido[11] else 0
    status = pedido[12] if pedido[12] else "Orçamento"
    data_pedido = pedido[14] if pedido[14] else ""
    data_pedido_dt = data_para_date(data_pedido)

    calc = calcular_pedido(
        peca_id,
        quantidade,
        valor_unitario,
        desconto,
        frete,
        energia,
        depreciacao,
        custos_pecas_dashboard.get(peca_id),
    )

    if status not in ["Entregue", "Cancelado"]:
        pedidos_abertos += 1

    if status != "Cancelado":
        faturamento_total += calc["total"]
        lucro_total += calc["lucro"]
        horas_total += calc["tempo_total"]
        quantidade_total += quantidade

        if data_pedido_dt and data_pedido_dt.month == hoje.month and data_pedido_dt.year == hoje.year:
            faturamento_mes += calc["total"]
            lucro_mes += calc["lucro"]
            if status == "Entregue":
                pedidos_fechados_mes += 1

        pecas_key = f"{peca_codigo} - {peca_nome}"
        pecas_resumo[pecas_key]["quantidade"] += quantidade
        pecas_resumo[pecas_key]["faturamento"] += calc["total"]
        pecas_resumo[pecas_key]["lucro"] += calc["lucro"]

        clientes_key = f"{cliente_codigo} - {cliente_nome}"
        clientes_resumo[clientes_key]["pedidos"] += 1
        clientes_resumo[clientes_key]["faturamento"] += calc["total"]
        clientes_resumo[clientes_key]["lucro"] += calc["lucro"]

        if data_pedido_dt:
            mes_key = data_pedido_dt.strftime("%Y-%m")
            vendas_mes_resumo[mes_key]["mes"] = rotulo_mes_grafico(data_pedido_dt)
            vendas_mes_resumo[mes_key]["pedidos"] += 1
            vendas_mes_resumo[mes_key]["quantidade"] += quantidade
            vendas_mes_resumo[mes_key]["faturamento"] += calc["total"]
            vendas_mes_resumo[mes_key]["lucro"] += calc["lucro"]

    status_resumo[status]["pedidos"] += 1
    status_resumo[status]["faturamento"] += calc["total"] if status != "Cancelado" else 0
    status_resumo[status]["lucro"] += calc["lucro"] if status != "Cancelado" else 0

    if len(pedidos_recentes) < 5:
        pedidos_recentes.append([
            codigo,
            cliente_nome,
            peca_nome,
            f"{quantidade:.0f}",
            status,
            moeda(calc["total"]),
        ])

    if status not in ["Entregue", "Cancelado"] and len(pedidos_abertos_lista) < 8:
        pedidos_abertos_lista.append([
            codigo,
            peca_nome,
            f"{quantidade:.0f}",
            status,
            data_br(data_pedido),
        ])


lucro_hora = lucro_total / horas_total if horas_total > 0 else 0
margem_media = (lucro_total / faturamento_total) * 100 if faturamento_total > 0 else 0
ticket_medio = faturamento_total / len(pedidos) if len(pedidos) > 0 else 0

vendas_mes_grafico = []
for mes_key, dados in sorted(vendas_mes_resumo.items())[-12:]:
    faturamento_mes_item = float(dados["faturamento"])
    lucro_mes_item = float(dados["lucro"])
    margem_mes_item = (lucro_mes_item / faturamento_mes_item * 100) if faturamento_mes_item > 0 else 0
    vendas_mes_grafico.append({
        "mes": dados["mes"],
        "pedidos": dados["pedidos"],
        "quantidade": dados["quantidade"],
        "faturamento": faturamento_mes_item,
        "lucro": lucro_mes_item,
        "margem": margem_mes_item,
    })


sidebar()

mobile_bottom_nav("dashboard")
inject_desktop_visual()
header(
    "Início",
    "Visão geral da operação"
)

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
        subtitle=f"{pedidos_fechados_mes:.0f} pedidos fechados no mês · lucro estimado {moeda(lucro_mes)}",
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
            <span>Energia {moeda(energia)}/h</span>
            <span>·</span>
            <span>Depreciação {moeda(depreciacao)}/h</span>
            <span>·</span>
            <span>Margem padrão {margem:.0f}%</span>
            <span>·</span>
            <span>Meta lucro/hora {moeda(meta_lucro)}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
