import streamlit as st


def kpi_card(titulo, valor, subtitulo="", cor="blue"):
    cores = {
        "blue": "#0C65AA",
        "green": "#1F8A4C",
        "yellow": "#E8B900",
        "red": "#D11A2A",
        "orange": "#B85C20",
        "gray": "#8A8F98"
    }

    cor_topo = cores.get(cor, "#0C65AA")

    html = f"""
    <div style="
        background:#FFFFFF;
        border:1px solid #DEE9EF;
        border-radius:14px;
        padding:18px;
        border-top:4px solid {cor_topo};
        box-shadow:0 4px 12px rgba(0,0,0,0.04);
        margin-bottom:12px;
        min-height:120px;
    ">
        <p style="
            font-size:10px;
            font-weight:700;
            text-transform:uppercase;
            letter-spacing:1.5px;
            color:#5C6C74;
            margin:0;
        ">{titulo}</p>

        <p style="
            font-size:28px;
            font-weight:800;
            color:{cor_topo};
            margin:8px 0 0 0;
            line-height:1;
        ">{valor}</p>

        <p style="
            font-size:11px;
            color:#5C6C74;
            margin:6px 0 0 0;
        ">{subtitulo}</p>
    </div>
    """

    st.components.v1.html(html, height=150)