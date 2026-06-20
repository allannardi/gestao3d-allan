import streamlit as st

from database import inicializar_banco
from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.desktop_visual import inject_desktop_visual
from components.mobile_summary import mobile_summary_css
from components.header import header
from components.section import section_title
from components.auth import require_login, logout_button


def card_atalho(titulo, subtitulo, destino, key):
    with st.container(border=True):
        st.markdown(f"**{titulo}**")
        st.caption(subtitulo)

        if st.button("Acessar", key=key, use_container_width=True):
            st.switch_page(destino)


def mais_css():
    st.markdown(
        """
        <style>
            .st-key-mais_btn_filamentos button,
            .st-key-mais_btn_acessorios button,
            .st-key-mais_btn_configuracoes button {
                background: #FFFFFF !important;
                color: #0C65AA !important;
                border: 1px solid #B9CDDC !important;
                border-radius: 13px !important;
                font-weight: 800 !important;
                min-height: 42px !important;
            }

            .st-key-mais_btn_filamentos button:hover,
            .st-key-mais_btn_acessorios button:hover,
            .st-key-mais_btn_configuracoes button:hover {
                background: #EDF5FA !important;
                color: #0A1A5C !important;
                border-color: #0C65AA !important;
            }

            @media (max-width: 768px) {
                .st-key-mais_cards [data-testid="column"] {
                    width: 100% !important;
                    flex: 1 1 100% !important;
                    min-width: 100% !important;
                }

                .st-key-mais_cards [data-testid="stVerticalBlock"] {
                    gap: 0.75rem !important;
                }

                .st-key-mais_cards div[data-testid="stVerticalBlockBorderWrapper"] {
                    border-radius: 18px !important;
                    border-color: #DEE9EF !important;
                    box-shadow: 0 8px 22px rgba(10, 26, 92, 0.05) !important;
                    background: #FFFFFF !important;
                }

                .st-key-mais_cards strong {
                    color: #1E3137 !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                    font-size: 16px !important;
                    font-weight: 800 !important;
                }

                .st-key-mais_cards [data-testid="stCaptionContainer"] {
                    color: #5C6C74 !important;
                    font-size: 12px !important;
                    line-height: 1.35 !important;
                }

                .st-key-mais_sair div[data-testid="stVerticalBlockBorderWrapper"] {
                    border-radius: 18px !important;
                    border-color: #DEE9EF !important;
                    box-shadow: 0 8px 22px rgba(10, 26, 92, 0.05) !important;
                    background: #FFFFFF !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()

sidebar()
mobile_bottom_nav("mais")
inject_desktop_visual()
mobile_summary_css("mais")
mais_css()

header("Mais", "Acessos complementares do Gestão 3D")


section_title(
    "Cadastros e sistema",
    "Acesse as páginas que ficam fora do menu principal mobile"
)


with st.container(key="mais_cards"):
    col1, col2 = st.columns(2)

    with col1:
        card_atalho(
            "Filamentos",
            "Rolos, materiais, cores e custos por grama.",
            "pages/1_Filamentos.py",
            "mais_btn_filamentos",
        )

        card_atalho(
            "Acessórios",
            "Argolas, embalagens, imãs e outros itens.",
            "pages/2_Acessorios.py",
            "mais_btn_acessorios",
        )

    with col2:
        card_atalho(
            "Configurações",
            "Energia, depreciação, margem e meta de lucro/hora.",
            "pages/Configuracoes.py",
            "mais_btn_configuracoes",
        )

        with st.container(border=True, key="mais_sair"):
            st.markdown("**Sair**")
            st.caption("Encerrar o acesso neste dispositivo.")
            logout_button()
