import base64
import hmac
from pathlib import Path

import streamlit as st


def verificar_login(usuario, senha):
    usuario_correto = st.secrets["auth"]["username"]
    senha_correta = st.secrets["auth"]["password"]

    usuario_ok = hmac.compare_digest(usuario, usuario_correto)
    senha_ok = hmac.compare_digest(senha, senha_correta)

    return usuario_ok and senha_ok


def logo_base64(caminho):
    arquivo = Path(caminho)

    if not arquivo.exists():
        return None

    return base64.b64encode(arquivo.read_bytes()).decode()


def require_login():
    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    if st.session_state["logado"]:
        return

    logo_64 = logo_base64("assets/logo_horizontal.png")

    st.markdown(
        """
        <style>
            .stApp {
                background: #FFFFFF !important;
            }

            section[data-testid="stSidebar"] {
                display: none !important;
            }

            [data-testid="stDeployButton"] {
                display: none !important;
            }

            [data-testid="stHeader"] {
                background: transparent !important;
            }

            .block-container {
                padding-top: 5.5rem !important;
                max-width: 1000px !important;
            }

            .login-logo-box {
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 8px;
            }

            .login-logo-box img {
                width: 360px;
                max-width: 90%;
                height: auto;
                display: block;
            }

            .login-title {
                font-family: 'Barlow', system-ui, sans-serif;
                font-size: 34px;
                font-weight: 800;
                color: #0A1A5C;
                text-align: center;
                margin-bottom: 8px;
            }

            .login-subtitle {
                font-family: 'Barlow', system-ui, sans-serif;
                font-size: 14px;
                font-weight: 500;
                color: #5C6C74;
                text-align: center;
                margin-bottom: 26px;
            }

            div[data-testid="stForm"] {
                background: #EDF5FA;
                border: 1.5px solid #B9CDDC;
                border-radius: 18px;
                padding: 26px 24px 24px 24px;
                box-shadow: 0 8px 24px rgba(16, 6, 144, 0.08);
            }

            div[data-testid="stForm"] label {
                font-family: 'Barlow', system-ui, sans-serif;
                font-size: 13px;
                font-weight: 600;
                color: #1E3137;
            }

            div[data-testid="stForm"] input {
                border-radius: 10px !important;
                border: 1.5px solid #B9CDDC !important;
                background: #FFFFFF !important;
            }

            div[data-testid="stForm"] input:focus {
                border-color: #0C65AA !important;
                box-shadow: 0 0 0 1px rgba(12, 101, 170, 0.18) !important;
            }

            div[data-testid="stFormSubmitButton"] button {
                background: #0C65AA !important;
                border: 1px solid #0C65AA !important;
                color: #FFFFFF !important;
                border-radius: 12px !important;
                font-family: 'Barlow', system-ui, sans-serif !important;
                font-weight: 700 !important;
                height: 44px !important;
            }

            div[data-testid="stFormSubmitButton"] button:hover {
                background: #0A1A5C !important;
                border-color: #0A1A5C !important;
                color: #FFFFFF !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    col_esq, col_centro, col_dir = st.columns([1, 0.72, 1])

    with col_centro:
        if logo_64:
            st.markdown(
                f"""
                <div class="login-logo-box">
                    <img src="data:image/png;base64,{logo_64}" alt="Gestão 3D">
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="login-title">Gestão 3D</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div class="login-subtitle">Acesse sua área de gestão</div>',
            unsafe_allow_html=True
        )

        with st.form("login_form"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")

            entrar = st.form_submit_button("Entrar", use_container_width=True)

        if entrar:
            if verificar_login(usuario, senha):
                st.session_state["logado"] = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    st.stop()


def logout_button():
    if st.button("Sair", use_container_width=True):
        st.session_state["logado"] = False
        st.rerun()
