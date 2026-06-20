from html import escape

import streamlit as st


def render_desktop_hero(
    label,
    value,
    subtitle,
    items=None,
):
    items = items or []

    chips = ""
    for item in items:
        note_html = ""
        note = item.get("note", "")
        if note:
            note_html = f'<small>{escape(str(note))}</small>'

        chips += f"""
        <div class="g3d-desktop-hero-chip">
            <strong>{escape(str(item.get("value", "")))}</strong>
            <span>{escape(str(item.get("label", "")))}</span>
            {note_html}
        </div>
        """

    html = f"""
    <div class="g3d-desktop-hero">
        <div class="g3d-desktop-hero-main">
            <div class="g3d-desktop-hero-label">{escape(str(label))}</div>
            <div class="g3d-desktop-hero-value">{escape(str(value))}</div>
            <div class="g3d-desktop-hero-subtitle">{escape(str(subtitle))}</div>
        </div>
        <div class="g3d-desktop-hero-chips">
            {chips}
        </div>
    </div>
    """

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)
