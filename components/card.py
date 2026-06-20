from html import escape

import streamlit as st


def _cor(cor):
    mapa = {
        "blue": "#0C65AA",
        "green": "#1F8A4C",
        "yellow": "#E8B900",
        "red": "#D11A2A",
        "orange": "#B85C20",
        "gray": "#8A8F98",
        "purple": "#100690",
    }
    return mapa.get(cor, "#0C65AA")


def item_card(codigo, titulo, subtitulo="", campos=None, cor="blue"):
    cor_hex = _cor(cor)

    campos = campos or []
    campos_html = ""

    if campos:
        for campo in campos:
            if isinstance(campo, (list, tuple)) and len(campo) >= 2:
                label = campo[0]
                valor = campo[1]
            else:
                label = ""
                valor = campo

            campos_html += f"""
            <div class="g3d-item-card-mini">
                <span>{escape(str(label))}</span>
                <strong>{escape(str(valor))}</strong>
            </div>
            """

        campos_html = f'<div class="g3d-item-card-grid">{campos_html}</div>'

    html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&display=swap');

        .g3d-item-card {{
            position: relative;
            box-sizing: border-box;
            width: 100%;
            min-height: 86px;
            background:
                linear-gradient(180deg, #FFFFFF 0%, #FBFDFE 100%);
            border: 1px solid rgba(185,205,220,0.80);
            border-top: 4px solid {cor_hex};
            border-radius: 18px;
            padding: 14px 16px 13px 16px;
            font-family: 'Barlow', system-ui, sans-serif;
            overflow: hidden;
        }}

        .g3d-item-card:after {{
            content: "";
            position: absolute;
            right: -42px;
            top: -52px;
            width: 110px;
            height: 110px;
            border-radius: 999px;
            background: {cor_hex}10;
        }}

        .g3d-item-code {{
            position: relative;
            z-index: 1;
            color: #5C6C74;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.8px;
            text-transform: uppercase;
            margin-bottom: 5px;
            line-height: 1.1;
        }}

        .g3d-item-title {{
            position: relative;
            z-index: 1;
            color: #0A1A5C;
            font-size: 22px;
            font-weight: 800;
            line-height: 1.08;
            letter-spacing: -0.35px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 5px;
        }}

        .g3d-item-subtitle {{
            position: relative;
            z-index: 1;
            color: #5C6C74;
            font-size: 12px;
            font-weight: 600;
            line-height: 1.25;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .g3d-item-card-grid {{
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 8px;
            margin-top: 11px;
        }}

        .g3d-item-card-mini {{
            background: #F4F8FB;
            border: 1px solid #DEE9EF;
            border-radius: 12px;
            padding: 8px 9px;
        }}

        .g3d-item-card-mini span {{
            display: block;
            color: #5C6C74;
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 3px;
        }}

        .g3d-item-card-mini strong {{
            display: block;
            color: #0A1A5C;
            font-size: 13px;
            font-weight: 800;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        @media (max-width: 768px) {{
            .g3d-item-card {{
                min-height: 84px;
                border-radius: 17px;
                padding: 13px 14px 12px 14px;
            }}

            .g3d-item-title {{
                font-size: 21px;
            }}

            .g3d-item-subtitle {{
                font-size: 12px;
            }}

            .g3d-item-card-grid {{
                grid-template-columns: 1fr 1fr;
            }}
        }}
    </style>

    <div class="g3d-item-card">
        <div class="g3d-item-code">{escape(str(codigo))}</div>
        <div class="g3d-item-title">{escape(str(titulo))}</div>
        <div class="g3d-item-subtitle">{escape(str(subtitulo))}</div>
        {campos_html}
    </div>
    """

    altura = 96 if not campos else 150

    st.components.v1.html(
        html,
        height=altura,
        scrolling=False
    )
