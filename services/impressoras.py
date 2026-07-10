"""
Regras e consultas de impressoras do Gestão 3D.

Este módulo separa da tela Configurações as funções relacionadas a:
- presets de impressoras;
- cálculo de energia/hora;
- criação/garantia da tabela de impressoras;
- carregamento da impressora padrão;
- sincronização da impressora padrão com configurações gerais.
"""

from datetime import date

from database import conectar


PRESETS_IMPRESSORAS = {
    "Bambu Lab A1 Mini": {
        "marca": "Bambu Lab",
        "modelo": "A1 Mini",
        "consumo_w": 150.0,
        "depreciacao_hora": 0.75,
    },
    "Bambu Lab A1": {
        "marca": "Bambu Lab",
        "modelo": "A1",
        "consumo_w": 200.0,
        "depreciacao_hora": 0.90,
    },
    "Creality Ender-3 V3 SE": {
        "marca": "Creality",
        "modelo": "Ender-3 V3 SE",
        "consumo_w": 270.0,
        "depreciacao_hora": 0.75,
    },
    "Creality Ender-3 V3 KE": {
        "marca": "Creality",
        "modelo": "Ender-3 V3 KE",
        "consumo_w": 350.0,
        "depreciacao_hora": 0.85,
    },
    "Anycubic Kobra 2 Neo": {
        "marca": "Anycubic",
        "modelo": "Kobra 2 Neo",
        "consumo_w": 400.0,
        "depreciacao_hora": 0.80,
    },
    "Personalizada": {
        "marca": "",
        "modelo": "",
        "consumo_w": 200.0,
        "depreciacao_hora": 0.75,
    },
}


def calcular_energia_hora(consumo_w, valor_kwh):
    consumo_w = consumo_w if consumo_w else 0
    valor_kwh = valor_kwh if valor_kwh else 0
    return (consumo_w / 1000) * valor_kwh


def garantir_coluna_configuracoes_valor_kwh():
    conn = conectar()
    colunas = conn.execute("PRAGMA table_info(configuracoes)").fetchall()
    nomes_colunas = [item[1] for item in colunas]

    if "valor_kwh" not in nomes_colunas:
        conn.execute("ALTER TABLE configuracoes ADD COLUMN valor_kwh REAL DEFAULT 0.65")
        conn.commit()

    conn.close()


def garantir_impressoras_configuracoes():
    """
    Garante a tabela de impressoras diretamente na tela Configurações.

    Desde a v15.14, esta função NÃO cria impressora automaticamente.
    Em uma base nova, a primeira impressora deve ser cadastrada pelo
    Admin da Empresa durante a trilha inicial. Isso evita que uma nova
    empresa comece com uma impressora fictícia ou herdada do projeto original.
    """
    conn = conectar()

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


def gerar_codigo_impressora(conn):
    ultimo = conn.execute("SELECT MAX(id) FROM impressoras").fetchone()[0]
    proximo = 1 if ultimo is None else ultimo + 1
    return f"IMP-{proximo:03d}"


def carregar_impressoras():
    conn = conectar()
    impressoras = conn.execute("""
    SELECT
        id,
        codigo,
        marca,
        modelo,
        status,
        consumo_w,
        valor_kwh,
        energia_hora,
        depreciacao_hora,
        observacoes,
        COALESCE(is_padrao, 0),
        data_cadastro
    FROM impressoras
    ORDER BY COALESCE(is_padrao, 0) DESC, id ASC
    """).fetchall()
    conn.close()
    return impressoras


def carregar_impressora_padrao():
    conn = conectar()
    impressora = conn.execute("""
    SELECT
        id,
        codigo,
        marca,
        modelo,
        status,
        consumo_w,
        valor_kwh,
        energia_hora,
        depreciacao_hora,
        observacoes,
        COALESCE(is_padrao, 0),
        data_cadastro
    FROM impressoras
    WHERE COALESCE(is_padrao, 0) = 1
    ORDER BY id ASC
    LIMIT 1
    """).fetchone()

    if impressora is None:
        impressora = conn.execute("""
        SELECT
            id,
            codigo,
            marca,
            modelo,
            status,
            consumo_w,
            valor_kwh,
            energia_hora,
            depreciacao_hora,
            observacoes,
            COALESCE(is_padrao, 0),
            data_cadastro
        FROM impressoras
        ORDER BY id ASC
        LIMIT 1
        """).fetchone()

    conn.close()
    return impressora


def sincronizar_configuracao_com_impressora_padrao(conn, impressora_id):
    impressora = conn.execute("""
    SELECT energia_hora, depreciacao_hora
    FROM impressoras
    WHERE id = ?
    """, (impressora_id,)).fetchone()

    if impressora:
        conn.execute("""
        UPDATE configuracoes
        SET
            energia_hora = ?,
            depreciacao_hora = ?
        """, (
            impressora[0],
            impressora[1],
        ))
