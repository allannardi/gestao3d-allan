import streamlit as st
from html import escape

from components.theme import (
    BRIGHT_BLUE,
    SUCCESS,
    WARNING,
    DANGER,
    ORANGE,
    GRAY,
    MUTED,
    DEEP_BLUE,
)


def item_card(codigo, titulo, subtitulo="", campos=None, cor="blue"):
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
        border-top:3px solid {cor_destaque};
        padding:14px 14px 0px 14px;
        box-sizing:border-box;
        width:100%;
    ">
        <div style="
            font-size:10px;
            font-weight:800;
            letter-spacing:2px;
            text-transform:uppercase;
            color:{MUTED};
            margin-bottom:7px;
        ">
            {escape(str(codigo))}
        </div>

        <div style="
            font-size:24px;
            font-weight:800;
            color:{DEEP_BLUE};
            line-height:1.05;
            margin-bottom:5px;
            letter-spacing:-0.4px;
        ">
            {escape(str(titulo))}
        </div>

        <div style="
            font-size:13px;
            font-weight:500;
            color:{MUTED};
            margin-bottom:0px;
        ">
            {escape(str(subtitulo))}
        </div>
    </div>
    """

    st.components.v1.html(html, height=90)