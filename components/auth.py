import base64
import hashlib
import hmac
import secrets as secrets_lib
from datetime import datetime
from pathlib import Path

import streamlit as st

from database import conectar


ITERACOES_HASH_SENHA = 200_000
PERFIL_ADMIN = "Admin"
PERFIL_OPERADOR = "Operador"
PERFIL_ADMIN_LABEL = "Admin da Empresa"
PERFIL_OPERADOR_LABEL = "Operador"
PERFIL_ADMIN_GERAL_FUTURO = "Admin Geral Gestão 3D"
STATUS_ATIVO = "Ativo"
STATUS_INATIVO = "Inativo"


PERMISSOES_PERFIL = {
    PERFIL_ADMIN: {
        "ver_dashboard",
        "usar_pedidos",
        "usar_cadastros",
        "usar_configuracoes",
        "ver_ajustes_admin",
        "gerenciar_usuarios",
    },
    PERFIL_OPERADOR: {
        "ver_dashboard",
        "usar_pedidos",
        "usar_cadastros",
        "usar_configuracoes",
    },
}


MENSAGEM_ACESSO_RESTRITO = "Acesso restrito a Admin da Empresa."


CHAVES_SESSAO_USUARIO = [
    "usuario_id",
    "usuario_nome",
    "usuario_email",
    "usuario_perfil",
    "usuario_status",
    "usuario_origem",
]


PERFIL_LABELS = {
    PERFIL_ADMIN: PERFIL_ADMIN_LABEL,
    PERFIL_OPERADOR: PERFIL_OPERADOR_LABEL,
}


def label_perfil(perfil):
    """Retorna o nome amigável do perfil para a interface.

    Mantemos o valor técnico `Admin` no banco para compatibilidade com as
    versões já validadas, mas mostramos `Admin da Empresa` para evitar
    confusão com o futuro `Admin Geral Gestão 3D`.
    """
    return PERFIL_LABELS.get(str(perfil or ""), str(perfil or ""))


def _auth_secret(chave, padrao=""):
    try:
        return str(st.secrets["auth"][chave])
    except Exception:
        return padrao


def _agora_sql():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _normalizar_login(valor):
    return str(valor or "").strip()


def garantir_tabela_auth():
    """Garante a tabela de senha antiga do app sem depender da inicialização completa."""
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


def garantir_tabela_usuarios():
    """Garante a tabela multiusuário da v15 sem alterar dados existentes."""
    try:
        conn = conectar()
        conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            perfil TEXT DEFAULT 'Operador',
            status TEXT DEFAULT 'Ativo',
            data_criacao TEXT,
            ultimo_login TEXT
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


def _gerar_senha_hash_usuario(senha):
    salt = secrets_lib.token_hex(16)
    senha_hash = _hash_senha(senha, salt)
    return f"pbkdf2_sha256${ITERACOES_HASH_SENHA}${salt}${senha_hash}"


def gerar_senha_hash_usuario(senha):
    """Gera hash seguro para senhas de usuários cadastrados na v15."""
    return _gerar_senha_hash_usuario(senha)


def _gerar_senha_hash_legacy_auth_config(senha_hash, salt):
    return f"legacy_auth_config${salt}${senha_hash}"


def _verificar_senha_hash_usuario(senha_digitada, senha_hash_salvo):
    senha_digitada = str(senha_digitada or "")
    senha_hash_salvo = str(senha_hash_salvo or "")

    partes = senha_hash_salvo.split("$")

    if len(partes) == 4 and partes[0] == "pbkdf2_sha256":
        try:
            iteracoes = int(partes[1])
            salt = partes[2]
            hash_correto = partes[3]
            hash_digitado = hashlib.pbkdf2_hmac(
                "sha256",
                senha_digitada.encode("utf-8"),
                salt.encode("utf-8"),
                iteracoes,
            ).hex()
            return hmac.compare_digest(hash_digitado, hash_correto)
        except Exception:
            return False

    if len(partes) == 3 and partes[0] == "legacy_auth_config":
        salt = partes[1]
        hash_correto = partes[2]
        return hmac.compare_digest(_hash_senha(senha_digitada, salt), hash_correto)

    return False


def usuario_auth_atual():
    usuario_sessao = st.session_state.get("usuario_email")
    if usuario_sessao:
        return usuario_sessao

    row = _buscar_auth_config()
    usuario_padrao = _auth_secret("username", "admin")

    if row and row[0]:
        return row[0]

    return usuario_padrao


def senha_personalizada_ativa():
    usuario_atual = get_usuario_atual()
    if usuario_atual and usuario_atual.get("senha_hash"):
        return True

    row = _buscar_auth_config()
    return bool(row and row[1] and row[2])


def _contar_usuarios():
    garantir_tabela_usuarios()

    try:
        conn = conectar()
        total = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        conn.close()
        return int(total or 0)
    except Exception:
        return 0


def _senha_hash_admin_inicial():
    row = _buscar_auth_config()

    if row and row[1] and row[2]:
        return _gerar_senha_hash_legacy_auth_config(row[1], row[2])

    senha_padrao = _auth_secret("password", "")
    return _gerar_senha_hash_usuario(senha_padrao)


def garantir_admin_inicial():
    """
    Cria um Admin da Empresa inicial a partir do login já existente.

    Preserva a senha atual do auth_config quando ela já foi personalizada.
    Se ainda estiver usando st.secrets, usa a senha definida nos secrets.
    """
    garantir_tabela_usuarios()

    try:
        conn = conectar()
        total = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]

        if int(total or 0) == 0:
            usuario_padrao = _normalizar_login(usuario_auth_atual()) or "admin"
            nome_padrao = "Administrador da Empresa"
            senha_hash = _senha_hash_admin_inicial()
            agora = _agora_sql()

            conn.execute("""
            INSERT INTO usuarios
            (
                nome,
                email,
                senha_hash,
                perfil,
                status,
                data_criacao,
                ultimo_login
            )
            VALUES (?, ?, ?, ?, ?, ?, NULL)
            """, (
                nome_padrao,
                usuario_padrao,
                senha_hash,
                PERFIL_ADMIN,
                STATUS_ATIVO,
                agora,
            ))
            conn.commit()

        conn.close()
    except Exception:
        pass


def _buscar_usuario_por_login(login):
    garantir_tabela_usuarios()
    login = _normalizar_login(login)

    if not login:
        return None

    try:
        conn = conectar()
        row = conn.execute("""
        SELECT
            id,
            nome,
            email,
            senha_hash,
            perfil,
            status,
            data_criacao,
            ultimo_login
        FROM usuarios
        WHERE LOWER(email) = LOWER(?)
        LIMIT 1
        """, (login,)).fetchone()
        conn.close()
        return row
    except Exception:
        return None


def _registrar_ultimo_login(usuario_id):
    if not usuario_id:
        return

    try:
        conn = conectar()
        conn.execute("""
        UPDATE usuarios
        SET ultimo_login = ?
        WHERE id = ?
        """, (_agora_sql(), usuario_id))
        conn.commit()
        conn.close()
    except Exception:
        pass


def _salvar_usuario_sessao(row, origem="usuarios"):
    st.session_state["logado"] = True

    if row:
        st.session_state["usuario_id"] = row[0]
        st.session_state["usuario_nome"] = row[1]
        st.session_state["usuario_email"] = row[2]
        st.session_state["usuario_perfil"] = row[4] or PERFIL_OPERADOR
        st.session_state["usuario_status"] = row[5] or STATUS_ATIVO
        st.session_state["usuario_origem"] = origem
        _registrar_ultimo_login(row[0])
    else:
        usuario = usuario_auth_atual()
        st.session_state["usuario_id"] = None
        st.session_state["usuario_nome"] = usuario
        st.session_state["usuario_email"] = usuario
        st.session_state["usuario_perfil"] = PERFIL_ADMIN
        st.session_state["usuario_status"] = STATUS_ATIVO
        st.session_state["usuario_origem"] = origem


def _limpar_usuario_sessao():
    st.session_state["logado"] = False
    for chave in CHAVES_SESSAO_USUARIO:
        st.session_state.pop(chave, None)


def get_usuario_atual():
    usuario_id = st.session_state.get("usuario_id")
    usuario_nome = st.session_state.get("usuario_nome")
    usuario_email = st.session_state.get("usuario_email")
    usuario_perfil = st.session_state.get("usuario_perfil")
    usuario_status = st.session_state.get("usuario_status")
    usuario_origem = st.session_state.get("usuario_origem")

    if not st.session_state.get("logado"):
        return None

    if not usuario_email and not usuario_nome:
        return None

    row = None
    if usuario_email and usuario_id:
        row = _buscar_usuario_por_login(usuario_email)

    senha_hash = row[3] if row else None

    return {
        "id": usuario_id,
        "nome": usuario_nome or usuario_email,
        "email": usuario_email or usuario_nome,
        "perfil": usuario_perfil or PERFIL_OPERADOR,
        "status": usuario_status or STATUS_ATIVO,
        "origem": usuario_origem or "sessao",
        "senha_hash": senha_hash,
    }


def perfil_usuario_atual():
    usuario = get_usuario_atual()
    return usuario.get("perfil") if usuario else None


def permissoes_usuario_atual():
    perfil = perfil_usuario_atual()
    return PERMISSOES_PERFIL.get(perfil, set())


def tem_permissao(chave):
    return chave in permissoes_usuario_atual()


def is_admin():
    return perfil_usuario_atual() == PERFIL_ADMIN


def is_operador():
    return perfil_usuario_atual() == PERFIL_OPERADOR


def require_permissao(chave, mensagem=MENSAGEM_ACESSO_RESTRITO, destino_negado="Dashboard.py"):
    require_login()

    if tem_permissao(chave):
        return

    st.session_state["aviso_acesso_restrito"] = mensagem

    if destino_negado:
        try:
            st.switch_page(destino_negado)
        except Exception:
            st.error(mensagem)
            st.stop()

    st.error(mensagem)
    st.stop()


def require_admin():
    require_permissao("gerenciar_usuarios")


def verificar_login(usuario, senha):
    usuario_digitado = _normalizar_login(usuario)
    senha_digitada = str(senha or "")

    garantir_admin_inicial()

    row_usuario = _buscar_usuario_por_login(usuario_digitado)
    if row_usuario:
        status = row_usuario[5] or STATUS_ATIVO
        senha_hash = row_usuario[3]

        if status != STATUS_ATIVO:
            return False

        if _verificar_senha_hash_usuario(senha_digitada, senha_hash):
            _salvar_usuario_sessao(row_usuario, origem="usuarios")
            return True

        return False

    # Fallback seguro para compatibilidade com a v14.
    # Mantém o acesso antigo caso o banco ainda não tenha usuário correspondente.
    row = _buscar_auth_config()

    if row and row[1] and row[2]:
        usuario_correto = str(row[0] or _auth_secret("username", "admin"))
        senha_hash_correta = str(row[1])
        salt = str(row[2])

        usuario_ok = hmac.compare_digest(usuario_digitado, usuario_correto)
        senha_ok = hmac.compare_digest(_hash_senha(senha_digitada, salt), senha_hash_correta)

        if usuario_ok and senha_ok:
            _salvar_usuario_sessao(None, origem="auth_config")
            return True

        return False

    usuario_correto = _auth_secret("username", "admin")
    senha_correta = _auth_secret("password", "")

    usuario_ok = hmac.compare_digest(usuario_digitado, usuario_correto)
    senha_ok = hmac.compare_digest(senha_digitada, senha_correta)

    if usuario_ok and senha_ok:
        _salvar_usuario_sessao(None, origem="secrets")
        return True

    return False


def _verificar_login_legacy_sem_alterar_sessao(usuario, senha):
    """Valida a senha do login legado sem alterar a sessão atual."""
    usuario = _normalizar_login(usuario)
    senha = str(senha or "")

    row = _buscar_auth_config()

    if row and row[1] and row[2]:
        usuario_correto = str(row[0] or _auth_secret("username", "admin"))
        senha_hash_correta = str(row[1])
        salt = str(row[2])

        usuario_ok = hmac.compare_digest(usuario.lower(), usuario_correto.lower())
        senha_ok = hmac.compare_digest(_hash_senha(senha, salt), senha_hash_correta)
        return usuario_ok and senha_ok

    usuario_correto = _auth_secret("username", "admin")
    senha_correta = _auth_secret("password", "")

    usuario_ok = hmac.compare_digest(usuario, usuario_correto)
    senha_ok = hmac.compare_digest(senha, senha_correta)
    return usuario_ok and senha_ok


def alterar_senha_app(usuario, senha_atual, nova_senha):
    """
    Altera a senha do usuário logado.

    Na v15, a troca de senha deve atuar primeiro na tabela `usuarios`,
    sem chamar `verificar_login()`, porque aquela função também recria a
    sessão. Isso evita efeitos colaterais quando Admin da Empresa e
    Operador trocam a própria senha pela tela Configurações.
    """
    usuario_atual = get_usuario_atual()
    usuario = _normalizar_login(usuario) or usuario_auth_atual()
    senha_atual = str(senha_atual or "")
    nova_senha = str(nova_senha or "")

    if usuario_atual and usuario_atual.get("email"):
        login_sessao = _normalizar_login(usuario_atual.get("email"))
        if usuario and login_sessao and usuario.lower() != login_sessao.lower():
            return False, "Você só pode alterar a senha do usuário logado."
        usuario = login_sessao

    if len(nova_senha) < 4:
        return False, "A nova senha precisa ter pelo menos 4 caracteres."

    row_usuario = _buscar_usuario_por_login(usuario)

    if row_usuario:
        status = row_usuario[5] or STATUS_ATIVO
        if status != STATUS_ATIVO:
            return False, "Usuário inativo. Não foi possível alterar a senha."

        senha_hash_atual = row_usuario[3]
        if not _verificar_senha_hash_usuario(senha_atual, senha_hash_atual):
            return False, "Senha atual inválida."

        novo_hash_usuario = _gerar_senha_hash_usuario(nova_senha)
        conn = conectar()
        conn.execute("""
        UPDATE usuarios
        SET senha_hash = ?
        WHERE id = ?
        """, (novo_hash_usuario, row_usuario[0]))
        conn.commit()
        conn.close()

        st.session_state["usuario_id"] = row_usuario[0]
        st.session_state["usuario_nome"] = row_usuario[1]
        st.session_state["usuario_email"] = row_usuario[2]
        st.session_state["usuario_perfil"] = row_usuario[4] or PERFIL_OPERADOR
        st.session_state["usuario_status"] = row_usuario[5] or STATUS_ATIVO
        st.session_state["usuario_origem"] = "usuarios"

        return True, "Senha alterada com sucesso."

    # Fallback para sessões antigas/legadas, mantido para compatibilidade.
    if not _verificar_login_legacy_sem_alterar_sessao(usuario, senha_atual):
        return False, "Senha atual inválida."

    salt = secrets_lib.token_hex(16)
    senha_hash = _hash_senha(nova_senha, salt)
    atualizado_em = _agora_sql()

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

    st.session_state["usuario_email"] = usuario

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
        garantir_admin_inicial()

        if not st.session_state.get("usuario_email"):
            usuario_legado = usuario_auth_atual()
            row_usuario = _buscar_usuario_por_login(usuario_legado)
            if row_usuario:
                _salvar_usuario_sessao(row_usuario, origem="usuarios")
            else:
                _salvar_usuario_sessao(None, origem="sessao_legada")

        return

    garantir_admin_inicial()

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
                st.switch_page("Dashboard.py")
            else:
                st.error("Usuário ou senha inválidos.")

    st.stop()


def logout_button(label="Sair", key="logout_app", use_container_width=True):
    if st.button(label, key=key, use_container_width=use_container_width):
        _limpar_usuario_sessao()
        st.switch_page("Dashboard.py")
