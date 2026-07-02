"""
Regras e operações básicas de pedidos do Gestão 3D.

Este módulo inicia a separação das regras de pedido da tela Streamlit.
A tela continua responsável pela interface; este arquivo concentra regras de negócio
e operações simples de banco relacionadas ao pedido.
"""

import streamlit as st

from components.formatters import data_para_date
from database import conectar


STATUS_PEDIDOS = [
    "Orçamento",
    "Encomendado",
    "Em Produção",
    "Pronto",
    "Entregue",
    "Cancelado",
]


def gerar_codigo_pedido(conn):
    ultimo = conn.execute("""
        SELECT MAX(id)
        FROM pedidos
    """).fetchone()[0]

    proximo = 1 if ultimo is None else ultimo + 1
    return f"PED-{proximo:04d}"


def atualizar_status_pedido_db(pedido_id, novo_status, data_final_producao=None, data_entrega_real=None):
    campos = ["status = ?"]
    valores = [novo_status]

    if data_final_producao:
        campos.append("data_final_producao = ?")
        valores.append(str(data_final_producao))

    if data_entrega_real:
        campos.append("data_entrega_real = ?")
        valores.append(str(data_entrega_real))

    valores.append(pedido_id)

    conn = None

    try:
        conn = conectar()
        conn.execute(
            f"""
            UPDATE pedidos
            SET {", ".join(campos)}
            WHERE id = ?
            """,
            valores
        )
        conn.commit()
    finally:
        if conn is not None:
            conn.close()


def resumo_prazo_entrega(data_prevista, data_real):
    prevista = data_para_date(data_prevista)
    real = data_para_date(data_real)

    if not prevista or not real:
        return None

    diferenca = (real - prevista).days

    if diferenca == 0:
        return "Entregue na data prevista."

    if diferenca < 0:
        dias = abs(diferenca)
        return f"Entregue {dias} dia(s) antes do previsto."

    return f"Entregue com {diferenca} dia(s) de atraso."

@st.cache_data(ttl=30, show_spinner=False)
def carregar_pedidos_listagem_cache():
    """
    Carrega pedidos e filamentos dos pedidos em lote.

    Mantém a consulta fora da tela Streamlit, deixando a página de Pedidos
    mais simples internamente.
    """
    conn = conectar()

    pedidos = conn.execute("""
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
        ped.observacoes,
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

    pedido_ids = sorted({pedido[0] for pedido in pedidos if pedido[0]})
    filamentos_por_pedido = {}

    if pedido_ids:
        placeholders = ",".join(["?"] * len(pedido_ids))

        filamentos_rows = conn.execute(f"""
        SELECT
            pf.pedido_id,
            f.codigo,
            f.nome,
            f.material,
            f.cor,
            COALESCE(pf.peso_g, 0),
            COALESCE(pf.observacao, '')
        FROM pedido_filamentos pf
        LEFT JOIN filamentos f ON pf.filamento_id = f.id
        WHERE pf.pedido_id IN ({placeholders})
        ORDER BY pf.id ASC
        """, pedido_ids).fetchall()

        for row in filamentos_rows:
            pedido_id = row[0]
            filamentos_por_pedido.setdefault(pedido_id, []).append(tuple(row[1:]))

    conn.close()

    return [tuple(p) for p in pedidos], filamentos_por_pedido

@st.cache_data(ttl=30, show_spinner=False)
def carregar_impressoras_pedidos():
    conn = conectar()

    impressoras = conn.execute("""
    SELECT
        id,
        codigo,
        marca,
        modelo,
        status,
        COALESCE(energia_hora, 0),
        COALESCE(depreciacao_hora, 0),
        COALESCE(is_padrao, 0)
    FROM impressoras
    WHERE status IS NULL OR status = 'Ativa' OR COALESCE(is_padrao, 0) = 1
    ORDER BY COALESCE(is_padrao, 0) DESC, id ASC
    """).fetchall()

    conn.close()

    return [tuple(i) for i in impressoras]


def selecionar_impressora_padrao(impressoras):
    if not impressoras:
        return None

    for impressora in impressoras:
        if impressora[7]:
            return impressora

    return impressoras[0]


def label_impressora(impressora):
    if not impressora:
        return "Impressora padrão"

    codigo = impressora[1] or "-"
    marca = impressora[2] or ""
    modelo = impressora[3] or ""
    sufixo = " · Padrão" if impressora[7] else ""
    return f"{codigo} - {marca} {modelo}{sufixo}".strip()


@st.cache_data(ttl=30, show_spinner=False)
def carregar_clientes():
    conn = conectar()

    clientes = conn.execute("""
    SELECT
        id,
        codigo,
        nome,
        telefone,
        cidade,
        estado
    FROM clientes
    WHERE status IS NULL OR status = 'Ativo'
    ORDER BY nome ASC
    """).fetchall()

    conn.close()

    return [tuple(c) for c in clientes]


@st.cache_data(ttl=30, show_spinner=False)
def carregar_pecas():
    conn = conectar()

    pecas = conn.execute("""
    SELECT
        p.id,
        p.codigo,
        p.nome,
        p.categoria,
        p.peso_g,
        p.tempo_impressao_h,
        p.tempo_pos_processamento_min,
        p.embalagem_custo,
        COALESCE(p.quantidade_lote, 1),
        f.codigo,
        f.nome,
        f.custo_grama
    FROM pecas p
    LEFT JOIN filamentos f ON p.filamento_id = f.id
    ORDER BY p.nome ASC
    """).fetchall()

    conn.close()

    return [tuple(p) for p in pecas]


def cor_status(status):
    if status in ["Entregue", "Pronto"]:
        return "green"
    if status in ["Encomendado", "Em Produção"]:
        return "blue"
    if status == "Orçamento":
        return "orange"
    if status == "Cancelado":
        return "red"
    return "gray"


def cor_status_hex(status):
    mapa = {
        "Orçamento": "#B85C20",
        "Encomendado": "#0C65AA",
        "Em Produção": "#100690",
        "Pronto": "#1F8A4C",
        "Entregue": "#1F8A4C",
        "Cancelado": "#D11A2A",
    }
    return mapa.get(status, "#8A8F98")

