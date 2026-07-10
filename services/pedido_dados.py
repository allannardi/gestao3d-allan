"""
Dados auxiliares da tela Pedidos.

Este service concentra consultas e garantias estruturais que ainda estavam
dentro da página `pages/5_Pedidos.py`.
"""

import streamlit as st

from database import conectar


def garantir_tabelas_pedidos():
    conn = conectar()

    conn.execute("""
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

    conn.execute("""
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
        data_final_producao TEXT,
        data_entrega_real TEXT,
        observacoes TEXT,
        impressora_id INTEGER
    )
    """)

    colunas_pecas = conn.execute("PRAGMA table_info(pecas)").fetchall()
    nomes_colunas_pecas = [coluna[1] for coluna in colunas_pecas]

    if "quantidade_lote" not in nomes_colunas_pecas:
        conn.execute("ALTER TABLE pecas ADD COLUMN quantidade_lote REAL DEFAULT 1")

    colunas_pedidos = conn.execute("PRAGMA table_info(pedidos)").fetchall()
    nomes_colunas_pedidos = [coluna[1] for coluna in colunas_pedidos]

    if "impressora_id" not in nomes_colunas_pedidos:
        conn.execute("ALTER TABLE pedidos ADD COLUMN impressora_id INTEGER")

    if "data_final_producao" not in nomes_colunas_pedidos:
        conn.execute("ALTER TABLE pedidos ADD COLUMN data_final_producao TEXT")

    if "data_entrega_real" not in nomes_colunas_pedidos:
        conn.execute("ALTER TABLE pedidos ADD COLUMN data_entrega_real TEXT")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS impressoras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        marca TEXT,
        modelo TEXT,
        status TEXT DEFAULT 'Ativa',
        consumo_w REAL DEFAULT 200,
        valor_kwh REAL DEFAULT 0.65,
        energia_hora REAL DEFAULT 0,
        depreciacao_hora REAL DEFAULT 0.75,
        observacoes TEXT,
        is_padrao INTEGER DEFAULT 0,
        data_cadastro TEXT
    )
    """)

    conn.commit()
    conn.close()


def gerar_codigo_cliente(conn):
    ultimo = conn.execute("""
        SELECT MAX(id)
        FROM clientes
    """).fetchone()[0]

    proximo = 1 if ultimo is None else ultimo + 1
    return f"CLI-{proximo:04d}"


@st.cache_data(ttl=30, show_spinner=False)
def carregar_configuracoes_pedidos():
    conn = conectar()

    config = conn.execute("""
    SELECT
        energia_hora,
        depreciacao_hora,
        margem_padrao,
        meta_lucro_hora,
        COALESCE(custo_pos_processamento_hora, 0)
    FROM configuracoes
    LIMIT 1
    """).fetchone()

    conn.close()

    return tuple(config) if config else None
