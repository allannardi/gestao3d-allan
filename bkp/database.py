import sqlite3


def conectar():
    return sqlite3.connect("database/atelie.db")


def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    # Configurações
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuracoes (
        id INTEGER PRIMARY KEY,
        energia_hora REAL,
        depreciacao_hora REAL,
        margem_padrao REAL,
        meta_lucro_hora REAL
    )
    """)

    # Acessórios
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

    # Peças
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
        observacoes TEXT
    )
    """)

    # Relação Peças x Acessórios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS peca_acessorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        peca_id INTEGER,
        acessorio_id INTEGER,
        quantidade REAL
    )
    """)
    
    # Filamentos
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
        custo_grama REAL
    )
    """)

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
            meta_lucro_hora
        )
        VALUES (0.15, 0.75, 150, 5)
        """)

    conn.commit()
    conn.close()