import streamlit as st

APP_VERSION = "0.13"


def sidebar_section(titulo):
    st.markdown(
        f"""
        <div class="g3d-sidebar-section">
            <span>{titulo}</span>
            <i></i>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_link(page, label):
    st.page_link(page, label=label)


def sidebar():
    with st.sidebar:
        st.markdown(
            """
            <style>
                @media (min-width: 769px) {
                    section[data-testid="stSidebar"] {
                        background: #FFFFFF !important;
                        border-right: 1px solid rgba(185, 205, 220, 0.72) !important;
                        box-shadow: none !important;
                        overflow: hidden !important;
                    }

                    section[data-testid="stSidebar"] > div {
                        background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFD 100%) !important;
                        padding-top: 0.95rem !important;
                        padding-left: 1.00rem !important;
                        padding-right: 1.00rem !important;
                        height: 100vh !important;
                        overflow-y: auto !important;
                        overflow-x: hidden !important;
                    }

                    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
                        display: none !important;
                        height: 0 !important;
                        min-height: 0 !important;
                    }

                    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
                        display: none !important;
                    }

                    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
                        gap: 0.12rem !important;
                    }

                    .g3d-sidebar-brand-wrap {
                        width: 100%;
                        padding: 0.10rem 0 1.00rem 0;
                        margin: 0 auto 1.18rem auto;
                        border-bottom: 1px solid rgba(222, 233, 239, 0.95);
                        text-align: center;
                    }

                    .g3d-sidebar-logo-box {
                        width: 100%;
                        margin: 0 auto 0.56rem auto;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        background: transparent !important;
                        border: none !important;
                        box-shadow: none !important;
                    }

                    section[data-testid="stSidebar"] .g3d-sidebar-logo-box [data-testid="stImage"] {
                        width: 100% !important;
                        display: flex !important;
                        justify-content: center !important;
                        margin: 0 auto !important;
                    }

                    section[data-testid="stSidebar"] .g3d-sidebar-logo-box img {
                        display: block !important;
                        margin: 0 auto !important;
                        max-width: 84px !important;
                        height: auto !important;
                        border-radius: 0 !important;
                        background: transparent !important;
                        box-shadow: none !important;
                        filter: none !important;
                    }

                    .g3d-sidebar-title {
                        font-family: 'Barlow', system-ui, sans-serif;
                        font-size: 18px;
                        font-weight: 800;
                        color: #0A1A5C;
                        line-height: 1.08;
                        letter-spacing: -0.2px;
                        text-align: center;
                    }

                    .g3d-sidebar-section {
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        margin: 1.25rem 0 0.62rem 0;
                        font-family: 'Barlow', system-ui, sans-serif;
                    }

                    .g3d-sidebar-section span {
                        font-size: 10px;
                        font-weight: 800;
                        color: #5C6C74;
                        text-transform: uppercase;
                        letter-spacing: 1.55px;
                        white-space: nowrap;
                    }

                    .g3d-sidebar-section i {
                        display: block;
                        height: 1px;
                        flex: 1;
                        background: linear-gradient(90deg, #D7E4EC 0%, rgba(215,228,236,0.15) 100%);
                    }

                    section[data-testid="stSidebar"] [data-testid="stPageLink"] {
                        margin-bottom: 0.14rem !important;
                    }

                    section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
                        min-height: 20px !important;
                        border-radius: 12px !important;
                        padding: 6px 12px 6px 14px !important;
                        color: #1E3137 !important;
                        font-family: 'Barlow', system-ui, sans-serif !important;
                        font-size: 14px !important;
                        font-weight: 600 !important;
                        line-height: 1.18 !important;
                        letter-spacing: 0.02px !important;
                        border: 1px solid transparent !important;
                        transition: background 0.14s ease, color 0.14s ease, border 0.14s ease !important;
                    }

                    section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
                        background: #F0F7FC !important;
                        color: #0C65AA !important;
                        border-color: rgba(12, 101, 170, 0.08) !important;
                    }

                    section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
                        background: linear-gradient(90deg, #EAF5FC 0%, #F7FBFE 100%) !important;
                        color: #0A1A5C !important;
                        border: 1px solid rgba(12, 101, 170, 0.13) !important;
                        box-shadow: inset 4px 0 0 #0C65AA !important;
                        font-weight: 800 !important;
                    }

                    .g3d-sidebar-footer {
                        margin-top: 1.25rem;
                        padding-top: 0.90rem;
                        padding-bottom: 0.15rem;
                        border-top: 1px solid rgba(222, 233, 239, 0.95);
                        font-family: 'Barlow', system-ui, sans-serif;
                        font-size: 11px;
                        color: #8A8F98;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }

                    .g3d-sidebar-footer strong {
                        color: #0A1A5C;
                        font-weight: 800;
                    }
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="g3d-sidebar-brand-wrap">', unsafe_allow_html=True)
        left, center, right = st.columns([1, 2, 1])
        with center:
            st.markdown('<div class="g3d-sidebar-logo-box">', unsafe_allow_html=True)
            st.image("assets/logo.png", width=84)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="g3d-sidebar-title">Gestão 3D</div></div>', unsafe_allow_html=True)

        sidebar_section("Geral")
        sidebar_link("Dashboard.py", "Início")
        sidebar_link("pages/5_Pedidos.py", "Pedidos")

        sidebar_section("Cadastros")
        sidebar_link("pages/4_Clientes.py", "Clientes")
        sidebar_link("pages/3_Pecas.py", "Peças")
        sidebar_link("pages/2_Acessorios.py", "Acessórios")
        sidebar_link("pages/1_Filamentos.py", "Filamentos")

        sidebar_section("Sistema")
        sidebar_link("pages/Configuracoes.py", "Configurações")

        st.markdown(
            f"""
            <div class="g3d-sidebar-footer">
                <span>Versão</span>
                <strong>{APP_VERSION}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
