"""
Componentes visuais da tela Pedidos.

Este módulo concentra renderizações e helpers visuais usados pela página Pedidos:
- formatação de moeda;
- cards visuais;
- resumo mobile;
- CSS mobile;
- resumo do novo pedido.

A regra de negócio permanece nos services de pedidos, filamentos e custos.
"""

from html import escape

import streamlit as st

from components.formatters import data_br
from services.pedidos import cor_status_hex


def moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def moeda_md(valor):
    return moeda(valor).replace("$", "\\$")


def pedidos_mobile_css():
    st.markdown(
        """
        <style>
            @media (max-width: 768px) {
                .g3d-pedido-card {
                    border-radius: 18px !important;
                    padding: 15px 15px 14px 15px !important;
                    margin-bottom: 8px !important;
                    box-shadow: 0 8px 22px rgba(10, 26, 92, 0.06) !important;
                }

                .g3d-pedido-top {
                    display: flex !important;
                    align-items: center !important;
                    justify-content: space-between !important;
                    gap: 10px !important;
                    margin-bottom: 10px !important;
                }

                .g3d-pedido-code {
                    font-size: 25px !important;
                    color: #0C65AA !important;
                }

                .g3d-pedido-status {
                    font-size: 10.5px !important;
                    padding: 5px 8px !important;
                    white-space: nowrap !important;
                }

                .g3d-pedido-main {
                    display: block !important;
                }

                .g3d-pedido-piece {
                    font-size: 15.5px !important;
                    line-height: 1.18 !important;
                    margin-bottom: 6px !important;
                }

                .g3d-pedido-client {
                    font-size: 11.5px !important;
                    margin-bottom: 11px !important;
                }

                .g3d-pedido-bottom {
                    display: grid !important;
                    grid-template-columns: 1fr 1fr 1fr !important;
                    gap: 8px !important;
                    margin-top: 10px !important;
                }

                .g3d-pedido-mini {
                    background: #F4F8FB !important;
                    border: 1px solid #DEE9EF !important;
                    border-radius: 13px !important;
                    padding: 9px 8px !important;
                    text-align: center !important;
                }

                .g3d-pedido-mini strong {
                    display: block !important;
                    font-size: 16px !important;
                    font-weight: 800 !important;
                    color: #1E3137 !important;
                    line-height: 1 !important;
                    margin-bottom: 4px !important;
                }

                .g3d-pedido-mini span {
                    display: block !important;
                    font-size: 9.5px !important;
                    font-weight: 800 !important;
                    color: #5C6C74 !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.9px !important;
                    line-height: 1 !important;
                }

                div[data-testid="stExpander"] {
                    border-radius: 16px !important;
                    overflow: hidden !important;
                    margin-bottom: 14px !important;
                }

                div[data-testid="stExpander"] summary p {
                    font-size: 12px !important;
                    font-weight: 800 !important;
                    color: #0C65AA !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def pedido_card(
    codigo,
    cliente_nome,
    peca_codigo,
    peca_nome,
    quantidade,
    status,
    total,
    data_pedido="-",
    lucro=0,
    margem_lucro=0,
    lucro_hora=0
):
    cor = cor_status_hex(status)

    codigo = escape(str(codigo))
    cliente_nome = escape(str(cliente_nome))
    peca_codigo = escape(str(peca_codigo))
    peca_nome = escape(str(peca_nome))
    status = escape(str(status))
    data_pedido = escape(data_br(data_pedido))
    total_fmt = escape(moeda(total))
    lucro_fmt = escape(moeda(lucro))
    margem_fmt = escape(f"{margem_lucro:.0f}%")
    lucro_hora_fmt = escape(f"R$ {lucro_hora:.2f}/h".replace(".", ","))

    html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&display=swap');

    @media (min-width: 769px) {{
        .g3d-pedido-card {{
            position: relative;
            border: 1px solid rgba(185,205,220,0.82) !important;
            border-top: 4px solid {cor} !important;
            border-radius: 20px !important;
            background: linear-gradient(180deg, #FFFFFF 0%, #FBFDFE 100%) !important;
            padding: 16px 17px 15px 17px !important;
            margin-bottom: 6px !important;
            font-family: 'Barlow', system-ui, sans-serif !important;
            box-shadow: 0 12px 28px rgba(10, 26, 92, 0.055);
            overflow: hidden;
        }}

        .g3d-pedido-card:after {{
            content: "";
            position: absolute;
            right: -44px;
            top: -54px;
            width: 118px;
            height: 118px;
            border-radius: 999px;
            background: {cor}10;
        }}

        .g3d-pedido-top {{
            position: relative;
            z-index: 1;
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 12px;
        }}

        .g3d-pedido-code {{
            font-size: 30px !important;
            font-weight: 800 !important;
            color: #0A1A5C !important;
            line-height: 1 !important;
            letter-spacing: -0.6px;
        }}

        .g3d-pedido-status {{
            display: inline-flex !important;
            align-items: center !important;
            gap: 7px !important;
            padding: 6px 10px !important;
            border-radius: 999px !important;
            background: transparent !important;
            border: 1px solid {cor}35 !important;
            color: {cor} !important;
            font-size: 12px !important;
            font-weight: 800 !important;
            white-space: nowrap !important;
        }}

        .g3d-pedido-status span {{
            width: 8px !important;
            height: 8px !important;
            border-radius: 50% !important;
            background: {cor} !important;
            display: inline-block !important;
        }}

        .g3d-pedido-main {{
            position: relative;
            z-index: 1;
        }}

        .g3d-pedido-piece {{
            font-size: 18px !important;
            font-weight: 800 !important;
            color: #0A1A5C !important;
            line-height: 1.18 !important;
            max-width: 100%;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .g3d-pedido-client {{
            margin-top: 5px !important;
            font-size: 12px !important;
            color: #5C6C74 !important;
            font-weight: 600 !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .g3d-pedido-bottom {{
            position: relative;
            z-index: 1;
            display: grid !important;
            grid-template-columns: repeat(5, minmax(0, 1fr)) !important;
            gap: 9px !important;
            margin-top: 14px !important;
        }}

        .g3d-pedido-mini {{
            background: #F4F8FB !important;
            border: 1px solid #DEE9EF !important;
            border-radius: 14px !important;
            padding: 9px 8px !important;
            text-align: center !important;
            min-width: 0 !important;
        }}

        .g3d-pedido-mini strong {{
            display: block !important;
            font-size: 15px !important;
            font-weight: 800 !important;
            color: #0A1A5C !important;
            line-height: 1 !important;
            margin-bottom: 4px !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .g3d-pedido-mini small {{
            display: block !important;
            font-size: 10px !important;
            font-weight: 800 !important;
            color: #1F8A4C !important;
            line-height: 1 !important;
            margin-top: -1px !important;
            margin-bottom: 4px !important;
            white-space: nowrap;
        }}

        .g3d-pedido-mini span {{
            display: block !important;
            font-size: 9.5px !important;
            font-weight: 800 !important;
            color: #5C6C74 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.9px !important;
            line-height: 1 !important;
        }}

        .g3d-pedido-peca-codigo {{
            position: relative;
            z-index: 1;
            margin-top: 10px;
            font-size: 11px;
            color: #8A8F98;
            font-weight: 700;
            letter-spacing: 0.8px;
        }}
    }}
</style>

<div class="g3d-pedido-card" style="border:1px solid #DEE9EF;border-top:4px solid {cor};border-radius:14px;background:#FFFFFF;padding:14px 16px;margin-bottom:4px;font-family:'Barlow', system-ui, sans-serif;">
    <div class="g3d-pedido-top">
        <div class="g3d-pedido-code">{codigo}</div>
        <div class="g3d-pedido-status">
            <span></span>{status}
        </div>
    </div>

    <div class="g3d-pedido-main">
        <div class="g3d-pedido-piece">{peca_nome}</div>
        <div class="g3d-pedido-client">{cliente_nome}</div>
    </div>

    <div class="g3d-pedido-bottom">
        <div class="g3d-pedido-mini">
            <strong>{data_pedido}</strong>
            <span>Data</span>
        </div>
        <div class="g3d-pedido-mini">
            <strong>{quantidade:.0f}x</strong>
            <span>Qtd.</span>
        </div>
        <div class="g3d-pedido-mini">
            <strong>{total_fmt}</strong>
            <span>Total</span>
        </div>
        <div class="g3d-pedido-mini">
            <strong>{lucro_fmt}</strong>
            <small>{margem_fmt}</small>
            <span>Lucro</span>
        </div>
        <div class="g3d-pedido-mini">
            <strong>{lucro_hora_fmt}</strong>
            <span>Lucro/hora</span>
        </div>
    </div>

    <div class="g3d-pedido-peca-codigo">{peca_codigo}</div>
</div>
"""

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)


def pedidos_resumo_mobile_css():
    st.markdown(
        """
        <style>
            .st-key-pedidos_mobile_resumo {
                display: none;
            }

            @media (min-width: 769px) {
                .st-key-pedidos_desktop_resumo {
                    display: block !important;
                }

                .st-key-pedidos_mobile_resumo {
                    display: none !important;
                }
            }

            @media (max-width: 768px) {
                .st-key-pedidos_desktop_resumo {
                    display: none !important;
                }

                .st-key-pedidos_mobile_resumo {
                    display: block !important;
                }

                .g3d-pedidos-mobile {
                    font-family: 'Barlow', system-ui, sans-serif;
                    margin-top: 8px;
                    margin-bottom: 18px;
                }

                .g3d-pedidos-hero {
                    background: linear-gradient(135deg, #0A1A5C 0%, #0C65AA 58%, #58C3F0 100%);
                    border-radius: 22px;
                    padding: 18px 18px;
                    color: #FFFFFF;
                    box-shadow: 0 14px 34px rgba(10, 26, 92, 0.18);
                    margin: 8px 0 14px 0;
                    overflow: hidden;
                    position: relative;
                }

                .g3d-pedidos-hero:after {
                    content: "";
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    background: rgba(255,255,255,0.12);
                    position: absolute;
                    right: -38px;
                    top: -48px;
                }

                .g3d-pedidos-hero-label {
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    opacity: 0.86;
                    margin-bottom: 8px;
                }

                .g3d-pedidos-hero-value {
                    font-size: 32px;
                    font-weight: 800;
                    line-height: 1;
                    margin-bottom: 6px;
                }

                .g3d-pedidos-hero-sub {
                    font-size: 13px;
                    font-weight: 500;
                    opacity: 0.92;
                }

                .g3d-pedidos-mobile-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 12px;
                }

                .g3d-pedidos-mobile-kpi {
                    background: #FFFFFF;
                    border: 1px solid #DEE9EF;
                    border-top: 4px solid #0C65AA;
                    border-radius: 18px;
                    padding: 14px 14px 13px 14px;
                    box-shadow: 0 9px 24px rgba(10, 26, 92, 0.06);
                    min-height: 108px;
                }

                .g3d-pedidos-mobile-kpi-title {
                    font-size: 9.5px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    color: #5C6C74;
                    margin-bottom: 8px;
                }

                .g3d-pedidos-mobile-kpi-value {
                    font-size: 25px;
                    font-weight: 800;
                    line-height: 1.05;
                    margin-bottom: 7px;
                }

                .g3d-pedidos-mobile-kpi-subtitle {
                    font-size: 11.5px;
                    font-weight: 500;
                    color: #5C6C74;
                    line-height: 1.22;
                }

                .g3d-pedidos-mobile-actions {
                    margin-top: 12px;
                    background: #FFFFFF;
                    border: 1px solid #DEE9EF;
                    border-radius: 18px;
                    padding: 12px 14px;
                    box-shadow: 0 9px 24px rgba(10, 26, 92, 0.05);
                    color: #5C6C74;
                    font-size: 12px;
                    font-weight: 600;
                    line-height: 1.35;
                }

                .g3d-pedidos-mobile-actions strong {
                    color: #1E3137;
                    font-weight: 800;
                }

                .st-key-btn_novo_pedido button {
                    background: #0C65AA !important;
                    color: #FFFFFF !important;
                    border-color: #0C65AA !important;
                    min-height: 48px !important;
                    font-weight: 800 !important;
                    border-radius: 15px !important;
                    box-shadow: 0 8px 20px rgba(12, 101, 170, 0.18) !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def pedidos_mobile_kpi_html(titulo, valor, subtitulo, cor="#0C65AA"):
    return f"""
    <div class="g3d-pedidos-mobile-kpi" style="border-top-color:{cor};">
        <div class="g3d-pedidos-mobile-kpi-title">{escape(str(titulo))}</div>
        <div class="g3d-pedidos-mobile-kpi-value" style="color:{cor};">{escape(str(valor))}</div>
        <div class="g3d-pedidos-mobile-kpi-subtitle">{escape(str(subtitulo))}</div>
    </div>
    """


def render_pedidos_mobile_resumo(total_pedidos, pedidos_abertos, faturamento_total, lucro_total, ticket_medio):
    html = f"""
    <div class="g3d-pedidos-mobile">
        <div class="g3d-pedidos-hero">
            <div class="g3d-pedidos-hero-label">Resumo dos pedidos</div>
            <div class="g3d-pedidos-hero-value">{escape(moeda(faturamento_total))}</div>
            <div class="g3d-pedidos-hero-sub">{total_pedidos:.0f} pedidos cadastrados · {pedidos_abertos:.0f} em aberto</div>
        </div>

        <div class="g3d-pedidos-mobile-grid">
            {pedidos_mobile_kpi_html("Em aberto", pedidos_abertos, "aguardando conclusão", "#B85C20")}
            {pedidos_mobile_kpi_html("Lucro", moeda(lucro_total), "resultado estimado", "#1F8A4C" if lucro_total >= 0 else "#D11A2A")}
            {pedidos_mobile_kpi_html("Ticket médio", moeda(ticket_medio), "por pedido", "#0C65AA")}
            {pedidos_mobile_kpi_html("Total", total_pedidos, "pedidos cadastrados", "#100690")}
        </div>

        <div class="g3d-pedidos-mobile-actions">
            <strong>Atalho:</strong> use o botão <strong>+ Novo Pedido</strong> abaixo para registrar uma nova venda.
        </div>
    </div>
    """

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)


def pedido_mobile_form_css():
    st.markdown(
        """
        <style>
            .g3d-pedido-mobile-step,
            .st-key-novo_pedido_resumo_mobile {
                display: none;
            }

            @media (min-width: 769px) {
                .st-key-novo_pedido_resumo_mobile {
                    display: none !important;
                }

                .st-key-novo_pedido_resumo_desktop {
                    display: block !important;
                }


                .g3d-pedido-mobile-step {
                    display: block !important;
                    background: linear-gradient(180deg, #FFFFFF 0%, #FBFDFE 100%);
                    border: 1px solid rgba(185, 205, 220, 0.82);
                    border-left: 4px solid #0C65AA;
                    border-radius: 17px;
                    padding: 13px 15px;
                    margin: 18px 0 12px 0;
                    box-shadow: 0 10px 24px rgba(10, 26, 92, 0.045);
                    font-family: 'Barlow', system-ui, sans-serif;
                }

                .g3d-pedido-mobile-step strong {
                    display: block;
                    font-size: 11px;
                    font-weight: 800;
                    color: #100690;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    margin-bottom: 5px;
                    line-height: 1.1;
                }

                .g3d-pedido-mobile-step span {
                    display: block;
                    font-size: 12px;
                    font-weight: 600;
                    color: #5C6C74;
                    line-height: 1.28;
                }

                .st-key-salvar_novo_pedido button {
                    background: linear-gradient(135deg, #0A1A5C 0%, #0C65AA 100%) !important;
                    color: #FFFFFF !important;
                    border-color: #0C65AA !important;
                    min-height: 48px !important;
                    border-radius: 15px !important;
                    font-size: 15px !important;
                    font-weight: 800 !important;
                    box-shadow: 0 10px 26px rgba(12, 101, 170, 0.18) !important;
                    margin-top: 8px !important;
                }
            }

            @media (max-width: 768px) {
                .g3d-pedido-mobile-step {
                    display: block !important;
                    background: #FFFFFF;
                    border: 1px solid #DEE9EF;
                    border-left: 4px solid #0C65AA;
                    border-radius: 16px;
                    padding: 12px 13px;
                    margin: 16px 0 10px 0;
                    box-shadow: 0 8px 20px rgba(10, 26, 92, 0.04);
                    font-family: 'Barlow', system-ui, sans-serif;
                }

                .g3d-pedido-mobile-step strong {
                    display: block;
                    font-size: 11px;
                    font-weight: 800;
                    color: #100690;
                    text-transform: uppercase;
                    letter-spacing: 1.8px;
                    margin-bottom: 5px;
                    line-height: 1.1;
                }

                .g3d-pedido-mobile-step span {
                    display: block;
                    font-size: 12px;
                    font-weight: 500;
                    color: #5C6C74;
                    line-height: 1.28;
                }

                .st-key-novo_pedido_resumo_desktop {
                    display: none !important;
                }

                .st-key-novo_pedido_resumo_mobile {
                    display: block !important;
                }

                .g3d-novo-pedido-resumo {
                    background: linear-gradient(135deg, #0A1A5C 0%, #0C65AA 58%, #58C3F0 100%);
                    border-radius: 22px;
                    padding: 16px 16px;
                    color: #FFFFFF;
                    box-shadow: 0 14px 34px rgba(10, 26, 92, 0.18);
                    margin: 14px 0 16px 0;
                    overflow: hidden;
                    position: relative;
                    font-family: 'Barlow', system-ui, sans-serif;
                }

                .g3d-novo-pedido-resumo:after {
                    content: "";
                    width: 118px;
                    height: 118px;
                    border-radius: 50%;
                    background: rgba(255,255,255,0.12);
                    position: absolute;
                    right: -40px;
                    top: -52px;
                }

                .g3d-novo-pedido-resumo-label {
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    opacity: 0.86;
                    margin-bottom: 8px;
                }

                .g3d-novo-pedido-resumo-total {
                    font-size: 31px;
                    font-weight: 800;
                    line-height: 1;
                    margin-bottom: 8px;
                }

                .g3d-novo-pedido-resumo-sub {
                    font-size: 13px;
                    font-weight: 500;
                    opacity: 0.92;
                    line-height: 1.25;
                }

                .g3d-novo-pedido-mini-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin-top: 12px;
                }

                .g3d-novo-pedido-mini {
                    background: rgba(255,255,255,0.14);
                    border: 1px solid rgba(255,255,255,0.20);
                    border-radius: 15px;
                    padding: 10px 10px;
                }

                .g3d-novo-pedido-mini strong {
                    display: block;
                    font-size: 15px;
                    font-weight: 800;
                    line-height: 1.05;
                    color: #FFFFFF;
                    margin-bottom: 5px;
                }

                .g3d-novo-pedido-mini span {
                    display: block;
                    font-size: 10px;
                    font-weight: 700;
                    opacity: 0.88;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }

                div[data-testid="stSelectbox"],
                div[data-testid="stNumberInput"],
                div[data-testid="stDateInput"],
                div[data-testid="stTextInput"],
                div[data-testid="stTextArea"] {
                    margin-bottom: 0.45rem !important;
                }

                div[data-testid="stSelectbox"] label,
                div[data-testid="stNumberInput"] label,
                div[data-testid="stDateInput"] label,
                div[data-testid="stTextInput"] label,
                div[data-testid="stTextArea"] label {
                    color: #1E3137 !important;
                    font-weight: 700 !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                }

                .st-key-salvar_novo_pedido button {
                    background: #0C65AA !important;
                    color: #FFFFFF !important;
                    border-color: #0C65AA !important;
                    min-height: 52px !important;
                    border-radius: 16px !important;
                    font-size: 15px !important;
                    font-weight: 800 !important;
                    box-shadow: 0 10px 26px rgba(12, 101, 170, 0.22) !important;
                    margin-top: 8px !important;
                }

                .st-key-salvar_novo_pedido button:before {
                    content: "✓ ";
                    font-weight: 800;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def pedido_mobile_step(titulo, subtitulo):
    html = f"""
    <div class="g3d-pedido-mobile-step">
        <strong>{escape(str(titulo))}</strong>
        <span>{escape(str(subtitulo))}</span>
    </div>
    """

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)


def render_novo_pedido_mobile_resumo(calc, preco_sugerido, margem_padrao):
    html = f"""
    <div class="g3d-novo-pedido-resumo">
        <div class="g3d-novo-pedido-resumo-label">Resumo do pedido</div>
        <div class="g3d-novo-pedido-resumo-total">{escape(moeda(calc["total"]))}</div>
        <div class="g3d-novo-pedido-resumo-sub">
            lucro estimado {escape(moeda(calc["lucro"]))} · venda sugerida {escape(moeda(preco_sugerido))}
        </div>

        <div class="g3d-novo-pedido-mini-grid">
            <div class="g3d-novo-pedido-mini">
                <strong>{escape(moeda(calc["custo_unitario"]))}</strong>
                <span>Custo unit.</span>
            </div>
            <div class="g3d-novo-pedido-mini">
                <strong>{escape(moeda(calc["subtotal"]))}</strong>
                <span>Subtotal</span>
            </div>
            <div class="g3d-novo-pedido-mini">
                <strong>{escape(moeda(calc["lucro_unitario"]))}</strong>
                <span>Lucro unit.</span>
            </div>
            <div class="g3d-novo-pedido-mini">
                <strong>{calc["lucro_percentual"]:.0f}%</strong>
                <span>Margem custo</span>
            </div>
        </div>
    </div>
    """

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)


def render_conferencia_pedido_operador(
    cliente_nome,
    peca_nome,
    quantidade,
    status,
    canal,
    data_entrega,
    filamentos_pedido,
    calc,
    lucro_hora,
    alertas,
):
    if alertas:
        st.warning("Antes de salvar, confira:\n\n- " + "\n- ".join(alertas))
    else:
        st.empty()
