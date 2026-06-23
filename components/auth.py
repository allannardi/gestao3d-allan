import base64
import hashlib
import hmac
import secrets as secrets_lib
from datetime import datetime
from pathlib import Path

import streamlit as st

from database import conectar


ITERACOES_HASH_SENHA = 200_000


def _auth_secret(chave, padrao=""):
    try:
        return str(st.secrets["auth"][chave])
    except Exception:
        return padrao


def garantir_tabela_auth():
    """Garante a tabela de senha do app sem depender da inicialização completa."""
    try:
        conn = conectar()
        conn.execute("""
        CREATE TABLE IF NOT EXISTS auth_config (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password_hash TEXT,
            password_salt TEXT,
            updated_at TEXT
        )
        """)
        conn.commit()
        conn.close()
    except Exception:
        pass


def _buscar_auth_config():
    garantir_tabela_auth()

    try:
        conn = conectar()
        row = conn.execute("""
        SELECT username, password_hash, password_salt, updated_at
        FROM auth_config
        WHERE id = 1
        """).fetchone()
        conn.close()
        return row
    except Exception:
        return None


def _hash_senha(senha, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        str(senha).encode("utf-8"),
        str(salt).encode("utf-8"),
        ITERACOES_HASH_SENHA,
    ).hex()


def usuario_auth_atual():
    row = _buscar_auth_config()
    usuario_padrao = _auth_secret("username", "admin")

    if row and row[0]:
        return row[0]

    return usuario_padrao


def senha_personalizada_ativa():
    row = _buscar_auth_config()
    return bool(row and row[1] and row[2])


def verificar_login(usuario, senha):
    usuario_digitado = str(usuario or "")
    senha_digitada = str(senha or "")

    row = _buscar_auth_config()

    if row and row[1] and row[2]:
        usuario_correto = str(row[0] or _auth_secret("username", "admin"))
        senha_hash_correta = str(row[1])
        salt = str(row[2])

        usuario_ok = hmac.compare_digest(usuario_digitado, usuario_correto)
        senha_ok = hmac.compare_digest(_hash_senha(senha_digitada, salt), senha_hash_correta)

        return usuario_ok and senha_ok

    usuario_correto = _auth_secret("username", "admin")
    senha_correta = _auth_secret("password", "")

    usuario_ok = hmac.compare_digest(usuario_digitado, usuario_correto)
    senha_ok = hmac.compare_digest(senha_digitada, senha_correta)

    return usuario_ok and senha_ok


def alterar_senha_app(usuario, senha_atual, nova_senha):
    usuario = str(usuario or "").strip() or usuario_auth_atual()
    senha_atual = str(senha_atual or "")
    nova_senha = str(nova_senha or "")

    if not verificar_login(usuario, senha_atual):
        return False, "Senha atual inválida."

    if len(nova_senha) < 4:
        return False, "A nova senha precisa ter pelo menos 4 caracteres."

    salt = secrets_lib.token_hex(16)
    senha_hash = _hash_senha(nova_senha, salt)
    atualizado_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    garantir_tabela_auth()
    conn = conectar()
    conn.execute("""
    INSERT INTO auth_config
    (
        id,
        username,
        password_hash,
        password_salt,
        updated_at
    )
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        username = excluded.username,
        password_hash = excluded.password_hash,
        password_salt = excluded.password_salt,
        updated_at = excluded.updated_at
    """, (
        1,
        usuario,
        senha_hash,
        salt,
        atualizado_em,
    ))
    conn.commit()
    conn.close()

    return True, "Senha alterada com sucesso."


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

            div[data-testid="stForm"] div[data-baseweb="base-input"],
            div[data-testid="stForm"] div[data-baseweb="base-input"] > div,
            div[data-testid="stForm"] div[data-baseweb="input"],
            div[data-testid="stForm"] div[data-baseweb="input"] > div,
            div[data-testid="stForm"] div[data-baseweb="select"] > div,
            div[data-testid="stForm"] div[data-baseweb="textarea"],
            div[data-testid="stForm"] div[data-baseweb="textarea"] > div {
                border-radius: 12px !important;
                overflow: hidden !important;
                border-color: #B9CDDC !important;
                background: #FFFFFF !important;
            }

            div[data-testid="stForm"] input,
            div[data-testid="stForm"] textarea {
                border-radius: 12px !important;
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
        

            div[data-testid="stForm"] {
                transition: border 0.15s ease, box-shadow 0.15s ease;
            }

            div[data-testid="stForm"]:hover {
                border-color: #A9C8DA !important;
                box-shadow: 0 10px 28px rgba(16, 6, 144, 0.10) !important;
            }

            div[data-testid="stForm"] input::placeholder {
                color: #8A8F98 !important;
                opacity: 0.82 !important;
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
