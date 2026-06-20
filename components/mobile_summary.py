from html import escape

import streamlit as st


def mobile_summary_css(page_key):
    st.markdown(
        f"""
        <style>
            .st-key-{page_key}_mobile_resumo {{
                display: none;
            }}

            @media (min-width: 769px) {{
                .st-key-{page_key}_desktop_resumo {{
                    display: block !important;
                }}

                .st-key-{page_key}_mobile_resumo {{
                    display: none !important;
                }}
            }}

            @media (max-width: 768px) {{
                h1 {{
                    color: #0A1A5C !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                    font-weight: 800 !important;
                }}

                .st-key-{page_key}_desktop_resumo {{
                    display: none !important;
                }}

                .st-key-{page_key}_mobile_resumo {{
                    display: block !important;
                }}

                .g3d-mobile-summary {{
                    font-family: 'Barlow', system-ui, sans-serif;
                    margin-top: 8px;
                    margin-bottom: 18px;
                }}

                .g3d-mobile-summary-hero {{
                    background: linear-gradient(135deg, #0A1A5C 0%, #0C65AA 58%, #58C3F0 100%);
                    border-radius: 22px;
                    padding: 18px 18px;
                    color: #FFFFFF;
                    box-shadow: 0 14px 34px rgba(10, 26, 92, 0.18);
                    margin: 8px 0 14px 0;
                    overflow: hidden;
                    position: relative;
                }}

                .g3d-mobile-summary-hero:after {{
                    content: "";
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    background: rgba(255,255,255,0.12);
                    position: absolute;
                    right: -38px;
                    top: -48px;
                }}

                .g3d-mobile-summary-label {{
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    opacity: 0.86;
                    margin-bottom: 8px;
                }}

                .g3d-mobile-summary-value {{
                    font-size: 32px;
                    font-weight: 800;
                    line-height: 1;
                    margin-bottom: 6px;
                }}

                .g3d-mobile-summary-sub {{
                    font-size: 13px;
                    font-weight: 500;
                    opacity: 0.92;
                    line-height: 1.25;
                }}

                .g3d-mobile-summary-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 12px;
                }}

                .g3d-mobile-summary-kpi {{
                    background: #FFFFFF;
                    border: 1px solid #DEE9EF;
                    border-top: 4px solid #0C65AA;
                    border-radius: 18px;
                    padding: 14px 14px 13px 14px;
                    box-shadow: 0 9px 24px rgba(10, 26, 92, 0.06);
                    min-height: 108px;
                }}

                .g3d-mobile-summary-kpi-title {{
                    font-size: 9.5px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    color: #5C6C74;
                    margin-bottom: 8px;
                }}

                .g3d-mobile-summary-kpi-value {{
                    font-size: 25px;
                    font-weight: 800;
                    line-height: 1.05;
                    margin-bottom: 7px;
                }}

                .g3d-mobile-summary-kpi-sub {{
                    font-size: 11.5px;
                    font-weight: 500;
                    color: #5C6C74;
                    line-height: 1.22;
                }}

                .g3d-mobile-summary-note {{
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
                }}

                .g3d-mobile-summary-note strong {{
                    color: #1E3137;
                    font-weight: 800;
                }}

                .st-key-btn_nova_peca button,
                .st-key-btn_novo_cliente button,
                .st-key-btn_novo_filamento button,
                .st-key-btn_novo_acessorio button {{
                    background: #0C65AA !important;
                    color: #FFFFFF !important;
                    border-color: #0C65AA !important;
                    min-height: 48px !important;
                    font-weight: 800 !important;
                    border-radius: 15px !important;
                    box-shadow: 0 8px 20px rgba(12, 101, 170, 0.18) !important;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True
    )


def _kpi_html(titulo, valor, subtitulo, cor):
    return f"""
    <div class="g3d-mobile-summary-kpi" style="border-top-color:{cor};">
        <div class="g3d-mobile-summary-kpi-title">{escape(str(titulo))}</div>
        <div class="g3d-mobile-summary-kpi-value" style="color:{cor};">{escape(str(valor))}</div>
        <div class="g3d-mobile-summary-kpi-sub">{escape(str(subtitulo))}</div>
    </div>
    """


def render_mobile_summary(hero_label, hero_value, hero_subtitle, kpis, note=None):
    kpis_html = ""

    for kpi in kpis:
        titulo = kpi.get("titulo", "")
        valor = kpi.get("valor", "")
        subtitulo = kpi.get("subtitulo", "")
        cor = kpi.get("cor", "#0C65AA")
        kpis_html += _kpi_html(titulo, valor, subtitulo, cor)

    note_html = ""
    if note:
        note_html = f'<div class="g3d-mobile-summary-note">{note}</div>'

    html = f"""
    <div class="g3d-mobile-summary">
        <div class="g3d-mobile-summary-hero">
            <div class="g3d-mobile-summary-label">{escape(str(hero_label))}</div>
            <div class="g3d-mobile-summary-value">{escape(str(hero_value))}</div>
            <div class="g3d-mobile-summary-sub">{escape(str(hero_subtitle))}</div>
        </div>

        <div class="g3d-mobile-summary-grid">
            {kpis_html}
        </div>

        {note_html}
    </div>
    """

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)
