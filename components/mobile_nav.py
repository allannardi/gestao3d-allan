import streamlit as st


def _nav_button(label, destino, key):
    if st.button(label, key=key, use_container_width=True):
        st.switch_page(destino)


def mobile_bottom_nav(active=""):
    """
    Menu inferior mobile com botões posicionados via CSS.

    Estratégia:
    - Usa st.button + st.switch_page para preservar o login.
    - Não usa st.columns, porque o Streamlit empilha colunas no celular.
    - Não usa st.radio/segmented_control, porque o visual fica limitado.
    - Os 5 botões são posicionados horizontalmente por CSS absoluto.
    """

    active_key = {
        "dashboard": "mobile_nav_inicio",
        "pedidos": "mobile_nav_pedidos",
        "pecas": "mobile_nav_pecas",
        "clientes": "mobile_nav_clientes",
        "mais": "mobile_nav_mais",
    }.get(active, "mobile_nav_inicio")

    active_selector = f".st-key-{active_key} button"

    st.markdown(
        f"""
        <style>
            .st-key-g3d_mobile_nav_container {{
                display: none;
            }}

            @media (max-width: 768px) {{

                section[data-testid="stSidebar"] {{
                    display: none !important;
                }}

                [data-testid="collapsedControl"] {{
                    display: none !important;
                }}

                .block-container {{
                    padding-left: 0.85rem !important;
                    padding-right: 0.85rem !important;
                    padding-top: 1.4rem !important;
                    padding-bottom: 104px !important;
                    max-width: 100% !important;
                }}

                h1 {{
                    color: #0A1A5C !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                    font-weight: 800 !important;
                    font-size: 1.55rem !important;
                    line-height: 1.15 !important;
                    margin-bottom: 0.15rem !important;
                }}

                .stButton > button {{
                    min-height: 44px !important;
                    border-radius: 13px !important;
                    font-size: 14px !important;
                }}

                input, textarea, select {{
                    font-size: 16px !important;
                }}

                .st-key-g3d_mobile_nav_container {{
                    position: fixed !important;
                    left: 12px !important;
                    right: 12px !important;
                    bottom: 12px !important;
                    z-index: 999999 !important;
                    height: 66px !important;
                    background: rgba(255, 255, 255, 0.96) !important;
                    border: 1px solid rgba(185, 205, 220, 0.85) !important;
                    border-radius: 24px !important;
                    box-shadow: 0 14px 34px rgba(10, 26, 92, 0.18) !important;
                    display: block !important;
                    padding: 0 !important;
                    backdrop-filter: blur(14px);
                    -webkit-backdrop-filter: blur(14px);
                    font-family: 'Barlow', system-ui, sans-serif;
                    overflow: hidden !important;
                }}

                .st-key-g3d_mobile_nav_container [data-testid="stVerticalBlock"] {{
                    position: relative !important;
                    height: 66px !important;
                    gap: 0 !important;
                }}

                .st-key-g3d_mobile_nav_container .stElementContainer {{
                    margin: 0 !important;
                    padding: 0 !important;
                }}

                .st-key-g3d_mobile_nav_container .st-key-mobile_nav_inicio,
                .st-key-g3d_mobile_nav_container .st-key-mobile_nav_pedidos,
                .st-key-g3d_mobile_nav_container .st-key-mobile_nav_pecas,
                .st-key-g3d_mobile_nav_container .st-key-mobile_nav_clientes,
                .st-key-g3d_mobile_nav_container .st-key-mobile_nav_mais {{
                    position: absolute !important;
                    top: 8px !important;
                    width: calc((100% - 16px) / 5) !important;
                    height: 50px !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }}

                .st-key-g3d_mobile_nav_container .st-key-mobile_nav_inicio {{
                    left: 8px !important;
                }}

                .st-key-g3d_mobile_nav_container .st-key-mobile_nav_pedidos {{
                    left: calc(8px + ((100% - 16px) / 5) * 1) !important;
                }}

                .st-key-g3d_mobile_nav_container .st-key-mobile_nav_pecas {{
                    left: calc(8px + ((100% - 16px) / 5) * 2) !important;
                }}

                .st-key-g3d_mobile_nav_container .st-key-mobile_nav_clientes {{
                    left: calc(8px + ((100% - 16px) / 5) * 3) !important;
                }}

                .st-key-g3d_mobile_nav_container .st-key-mobile_nav_mais {{
                    left: calc(8px + ((100% - 16px) / 5) * 4) !important;
                }}

                .st-key-g3d_mobile_nav_container .stButton {{
                    width: 100% !important;
                    height: 50px !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }}

                .st-key-g3d_mobile_nav_container .stButton > button {{
                    width: 100% !important;
                    height: 50px !important;
                    min-height: 50px !important;
                    border-radius: 18px !important;
                    border: 1px solid transparent !important;
                    background: transparent !important;
                    color: #5C6C74 !important;
                    box-shadow: none !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                    font-size: 10.5px !important;
                    font-weight: 800 !important;
                    line-height: 1 !important;
                    letter-spacing: 0.1px !important;
                    text-align: center !important;
                    white-space: nowrap !important;
                    overflow: hidden !important;
                    text-overflow: ellipsis !important;
                }}

                .st-key-g3d_mobile_nav_container .stButton > button p {{
                    margin: 0 !important;
                    padding: 0 !important;
                    line-height: 1 !important;
                    white-space: nowrap !important;
                    overflow: hidden !important;
                    text-overflow: ellipsis !important;
                }}

                .st-key-g3d_mobile_nav_container .stButton > button:hover,
                .st-key-g3d_mobile_nav_container .stButton > button:focus {{
                    background: #F4F8FB !important;
                    color: #0C65AA !important;
                    border: 1px solid rgba(12, 101, 170, 0.12) !important;
                    box-shadow: none !important;
                }}

                .st-key-g3d_mobile_nav_container {active_selector} {{
                    background: linear-gradient(180deg, #EDF5FA 0%, #E6F2FA 100%) !important;
                    color: #0C65AA !important;
                    border: 1px solid rgba(12, 101, 170, 0.16) !important;
                    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.55) !important;
                }}
            }}

            @media (min-width: 769px) {{
                .st-key-g3d_mobile_nav_container {{
                    display: none !important;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.container(key="g3d_mobile_nav_container"):
        _nav_button("Início", "Dashboard.py", "mobile_nav_inicio")
        _nav_button("Pedidos", "pages/5_Pedidos.py", "mobile_nav_pedidos")
        _nav_button("Peças", "pages/3_Pecas.py", "mobile_nav_pecas")
        _nav_button("Clientes", "pages/4_Clientes.py", "mobile_nav_clientes")
        _nav_button("Mais", "pages/6_Mais.py", "mobile_nav_mais")
