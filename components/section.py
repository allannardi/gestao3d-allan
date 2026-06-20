import streamlit as st
from html import escape

from components.theme import (
    PRIMARY,
    MUTED,
    BORDER,
)


def section_title(titulo, subtitulo=""):
    html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&display=swap');
    </style>

    <div style="
        width:100%;
        margin-top:22px;
        margin-bottom:18px;
        font-family:'Barlow', system-ui, sans-serif;
        box-sizing:border-box;
    ">
        <div style="
            display:flex;
            align-items:center;
            gap:12px;
            margin-bottom:8px;
        ">
            <div style="
                width:4px;
                height:18px;
                background:{PRIMARY};
                border-radius:2px;
                flex:0 0 auto;
            "></div>

            <div style="
                font-size:11px;
                font-weight:800;
                letter-spacing:3px;
                text-transform:uppercase;
                color:{PRIMARY};
                white-space:nowrap;
            ">
                {escape(str(titulo))}
            </div>

            <div style="
                height:1px;
                background:{BORDER};
                flex:1;
            "></div>
        </div>

        <div style="
            font-size:13px;
            font-weight:500;
            color:{MUTED};
            margin-left:16px;
        ">
            {escape(str(subtitulo))}
        </div>
    </div>
    """

    st.components.v1.html(html, height=84)


def small_section(titulo):
    html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&display=swap');
    </style>

    <div style="
        width:100%;
        margin-top:16px;
        margin-bottom:10px;
        font-family:'Barlow', system-ui, sans-serif;
        display:flex;
        align-items:center;
        gap:10px;
    ">
        <div style="
            font-size:11px;
            font-weight:800;
            letter-spacing:2px;
            text-transform:uppercase;
            color:{PRIMARY};
            white-space:nowrap;
        ">
            {escape(str(titulo))}
        </div>

        <div style="
            height:1px;
            background:{BORDER};
            flex:1;
        "></div>
    </div>
    """

    st.components.v1.html(html, height=42)