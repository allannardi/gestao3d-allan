import os
import sqlite3
from pathlib import Path


LOCAL_DB_PATH = "database/atelie.db"
SCHEMA_VERSION = "v10_02_pos_processamento"


def _get_secret(section, key, default=None):
    """Lê configuração do st.secrets, se existir, com fallback para variável de ambiente."""
    try:
        import streamlit as st

        if section in st.secrets and key in st.secrets[section]:
            return st.secrets[section][key]

        env_key = f"{section}_{key}".upper()
        if env_key in st.secrets:
            return st.secrets[env_key]

    except Exception:
        pass

    env_key = f"{section}_{key}".upper()
    return os.getenv(env_key, default)


def _usar_turso():
    modo = str(_get_secret("database", "mode", "local")).lower().strip()
    url = _get_secret("database", "url", None) or os.getenv("TURSO_DATABASE_URL") or os.getenv("LIBSQL_URL")
    token = _get_secret("database", "auth_token", None) or os.getenv("TURSO_AUTH_TOKEN") or os.getenv("LIBSQL_AUTH_TOKEN")

    if modo in ["turso", "cloud", "libsql"] and url and token:
        return True, url, token

    if url and token:
        return True, url, token

    return False, url, token


def _mascarar_token(token):
    if not token:
        return ""
    return f"{token[:6]}...{token[-6:]}" if len(token) > 12 else "***"


class _ConexaoTursoSessao:
    """
    Proxy para conexão Turso/libSQL.

    As páginas existentes chamam conn.close() muitas vezes.
    No modo cloud, fechar e reabrir conexão remota em cada clique deixa o app lento.
    Por isso, este proxy ignora close() e mantém uma conexão por sessão do Streamlit.
    """

    def __init__(self, conn):
        self._conn = conn

    def execute(self, *args, **kwargs):
        return self._conn.execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return self._conn.executemany(*args, **kwargs)

    def executescript(self, *args, **kwargs):
        return self._conn.executescript(*args, **kwargs)

    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)

    def commit(self, *args, **kwargs):
        return self._conn.commit(*args, **kwargs)

    def rollback(self, *args, **kwargs):
        return self._conn.rollback(*args, **kwargs)

    def close(self):
        # Mantém a conexão remota aberta durante a sessão.
        pass

    def __getattr__(self, item):
        return getattr(self._conn, item)


def _conectar_turso(url, token):
    import libsql

    try:
        import streamlit as st

        chave = f"{url}|{_mascarar_token(token)}"

        if (
            "_g3d_turso_conn" not in st.session_state
            or st.session_state.get("_g3d_turso_chave") != chave
        ):
            st.session_state["_g3d_turso_conn"] = libsql.connect(
                database=url,
                auth_token=token
            )
            st.session_state["_g3d_turso_chave"] = chave

        return _ConexaoTursoSessao(st.session_state["_g3d_turso_conn"])

    except Exception:
        # Fallback para execução fora do Streamlit.
        return libsql.connect(database=url, auth_token=token)


def conectar():
    """
    Conexão única do Gestão 3D.

    Local:
        usa database/atelie.db com sqlite3.

    Cloud:
        usa Turso/libSQL quando houver secrets:
        [database]
        mode = "turso"
        url = "libsql://..."
        auth_token = "..."
    """
    usar_turso, url, token = _usar_turso()

    if usar_turso:
        return _conectar_turso(url, token)

    Path("database").mkdir(exist_ok=True)

    conn = sqlite3.connect(
        LOCAL_DB_PATH,
        check_same_thread=False
    )

    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA cache_size=-32000")
    except Exception:
        pass

    return conn


def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuracoes (
        id INTEGER PRIMARY KEY,
        energia_hora REAL,
        depreciacao_hora REAL,
        margem_padrao REAL,
        meta_lucro_hora REAL,
        custo_pos_processamento_hora REAL DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS acessorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nome TEXT NOT NULL,
        categoria TEXT,
        custo_unitario REAL NOT NULL,
        observacoes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pecas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nome TEXT NOT NULL,
        categoria TEXT,
        peso_g REAL NOT NULL,
        tempo_impressao_h REAL NOT NULL,
        tempo_pos_processamento_min REAL,
        filamento_id INTEGER,
        embalagem_custo REAL,
        link_stl TEXT,
        link_modelo TEXT,
        pasta_google_drive TEXT,
        observacoes TEXT,
        quantidade_lote REAL DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS peca_acessorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        peca_id INTEGER,
        acessorio_id INTEGER,
        quantidade REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS peca_filamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        peca_id INTEGER,
        filamento_id INTEGER,
        peso_g REAL DEFAULT 0,
        observacao TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias_pecas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedido_filamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        filamento_id INTEGER,
        observacao TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS filamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nome TEXT NOT NULL,
        material TEXT NOT NULL,
        marca TEXT,
        cor TEXT,
        peso_original REAL NOT NULL,
        valor_compra REAL NOT NULL,
        fornecedor TEXT,
        data_compra TEXT,
        observacoes TEXT,
        custo_grama REAL,
        status TEXT DEFAULT 'Ativo',
        data_finalizacao TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nome TEXT NOT NULL,
        tipo TEXT,
        documento TEXT,
        telefone TEXT,
        email TEXT,
        cidade TEXT,
        estado TEXT,
        instagram TEXT,
        origem TEXT,
        observacoes TEXT,
        status TEXT DEFAULT 'Ativo',
        data_cadastro TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        cliente_id INTEGER,
        peca_id INTEGER,
        quantidade REAL DEFAULT 1,
        valor_unitario REAL DEFAULT 0,
        desconto REAL DEFAULT 0,
        frete REAL DEFAULT 0,
        status TEXT DEFAULT 'Orçamento',
        canal TEXT,
        data_pedido TEXT,
        data_entrega_prevista TEXT,
        observacoes TEXT
    )
    """)

    cursor.execute("""
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


def garantir_coluna(tabela, coluna, definicao):
    conn = conectar()
    colunas = conn.execute(f"PRAGMA table_info({tabela})").fetchall()
    nomes_colunas = [item[1] for item in colunas]

    if coluna not in nomes_colunas:
        conn.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")
        conn.commit()

    conn.close()


def garantir_migracoes():
    garantir_coluna("pecas", "quantidade_lote", "REAL DEFAULT 1")
    garantir_coluna("filamentos", "status", "TEXT DEFAULT 'Ativo'")
    garantir_coluna("filamentos", "data_finalizacao", "TEXT")
    garantir_coluna("configuracoes", "custo_pos_processamento_hora", "REAL DEFAULT 0")

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


def inserir_categorias_pecas_padrao():
    conn = conectar()
    categorias = [
        "Chaveiro",
        "Decoração",
        "Organizador",
        "Suporte",
        "Brinquedo",
        "Religião",
        "Outro",
    ]

    for categoria in categorias:
        conn.execute(
            "INSERT OR IGNORE INTO categorias_pecas (nome) VALUES (?)",
            (categoria,)
        )

    conn.commit()
    conn.close()


def inserir_configuracao_padrao():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM configuracoes")

    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO configuracoes
        (
            energia_hora,
            depreciacao_hora,
            margem_padrao,
            meta_lucro_hora,
            custo_pos_processamento_hora
        )
        VALUES (0.15, 0.75, 150, 5, 0)
        """)

    conn.commit()
    conn.close()


def _chave_banco_atual():
    usar_turso, url, _ = _usar_turso()
    if usar_turso:
        return f"turso::{url}::{SCHEMA_VERSION}"
    return f"local::{LOCAL_DB_PATH}::{SCHEMA_VERSION}"


def inicializar_banco(force=False):
    """
    Inicializa tabelas e migrações apenas uma vez por sessão.

    Isso é importante no modo Turso/cloud, porque CREATE TABLE, PRAGMA e ALTER TABLE
    em banco remoto a cada clique deixam o app muito lento.
    """
    chave_banco = _chave_banco_atual()

    try:
        import streamlit as st

        if (
            not force
            and st.session_state.get("_g3d_banco_inicializado") is True
            and st.session_state.get("_g3d_banco_chave") == chave_banco
        ):
            return

        criar_banco()
        garantir_migracoes()
        inserir_configuracao_padrao()
        inserir_categorias_pecas_padrao()

        st.session_state["_g3d_banco_inicializado"] = True
        st.session_state["_g3d_banco_chave"] = chave_banco

    except Exception:
        # Fallback para execução fora do Streamlit.
        criar_banco()
        garantir_migracoes()
        inserir_configuracao_padrao()
