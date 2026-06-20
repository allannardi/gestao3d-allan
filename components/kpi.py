import streamlit as st

from components.theme import (
    BRIGHT_BLUE,
    SUCCESS,
    WARNING,
    DANGER,
    ORANGE,
    GRAY,
    BORDER,
    CARD,
    MUTED,
    DEEP_BLUE,
)


def kpi_card(titulo, valor, subtitulo="", cor="blue"):
    cores = {
        "blue": BRIGHT_BLUE,
        "green": SUCCESS,
        "yellow": WARNING,
        "red": DANGER,
        "orange": ORANGE,
        "gray": GRAY,
    }

    cor_destaque = cores.get(cor, BRIGHT_BLUE)

    html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&display=swap');
    </style>

    <div style="
        font-family:'Barlow', system-ui, sans-serif;
        background:{CARD};
        border:1px solid {BORDER};
        border-radius:12px;
        padding:20px;
        border-top:3px solid {cor_destaque};
        box-shadow:0 4px 12px rgba(16,6,144,0.05);
        min-height:118px;
        box-sizing:border-box;
        transition:all .15s ease-in-out;
    ">
        <div style="
            font-size:10px;
            font-weight:800;
            text-transform:uppercase;
            letter-spacing:2px;
            color:{MUTED};
        ">
            {titulo}
        </div>

        <div style="
            font-size:30px;
            font-weight:800;
            color:{cor_destaque};
            margin-top:8px;
            line-height:1;
            white-space:nowrap;
        ">
            {valor}
        </div>

        <div style="
            font-size:11px;
            color:{MUTED};
            margin-top:8px;
            font-weight:500;
        ">
            {subtitulo}
        </div>
    </div>
    """

    st.components.v1.html(html, height=138)