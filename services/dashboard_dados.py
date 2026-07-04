"""
Consultas de dados da Dashboard.

Este módulo centraliza as leituras de banco usadas pela Dashboard.
A tela continua responsável pela interface e pelos gráficos.

Objetivo na fase 2:
- tirar SQL direto da tela;
- deixar as consultas reaproveitáveis;
- preparar uma futura migração para backend/API.
"""


def carregar_config_dashboard(conn):
    return conn.execute("""
    SELECT
        energia_hora,
        depreciacao_hora,
        margem_padrao,
        meta_lucro_hora,
        COALESCE(custo_pos_processamento_hora, 0)
    FROM configuracoes
    LIMIT 1
    """).fetchone()


def carregar_pedidos_dashboard(conn):
    return conn.execute("""
    SELECT
        ped.id,
        ped.codigo,
        ped.cliente_id,
        c.codigo,
        c.nome,
        ped.peca_id,
        pc.codigo,
        pc.nome,
        ped.quantidade,
        ped.valor_unitario,
        ped.desconto,
        ped.frete,
        ped.status,
        ped.canal,
        ped.data_pedido,
        ped.data_entrega_prevista,
        ped.data_final_producao,
        ped.data_entrega_real,
        ped.impressora_id,
        i.codigo,
        i.marca,
        i.modelo,
        i.energia_hora,
        i.depreciacao_hora
    FROM pedidos ped
    LEFT JOIN clientes c ON ped.cliente_id = c.id
    LEFT JOIN pecas pc ON ped.peca_id = pc.id
    LEFT JOIN impressoras i ON ped.impressora_id = i.id
    ORDER BY ped.id DESC
    """).fetchall()


def carregar_contadores_dashboard(conn):
    return {
        "clientes": conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0],
        "pecas": conn.execute("SELECT COUNT(*) FROM pecas").fetchone()[0],
        "filamentos": conn.execute("SELECT COUNT(*) FROM filamentos").fetchone()[0],
        "impressoras": conn.execute("SELECT COUNT(*) FROM impressoras").fetchone()[0],
    }


def carregar_impressoras_ativas_dashboard(conn):
    return conn.execute("""
    SELECT
        id,
        codigo,
        marca,
        modelo
    FROM impressoras
    WHERE status IS NULL OR status = 'Ativa'
    ORDER BY id ASC
    """).fetchall()


def carregar_impressora_padrao_dashboard(conn):
    return conn.execute("""
    SELECT
        codigo,
        marca,
        modelo,
        energia_hora,
        depreciacao_hora
    FROM impressoras
    WHERE COALESCE(is_padrao, 0) = 1
    ORDER BY id ASC
    LIMIT 1
    """).fetchone()
