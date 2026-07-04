"""
Custos e resumos financeiros da tela Pedidos.

Este módulo concentra regras de custo usadas em Pedidos:
- custo unitário da peça;
- custo de várias peças em lote;
- cálculo financeiro do pedido;
- resumo financeiro superior da tela;
- cache de custos usados na listagem.

A tela Streamlit continua responsável pela interface.
"""

import streamlit as st

from database import conectar
from services.custos import calcular_resultado_pedido


def carregar_acessorios_da_peca(conn, peca_id):
    return conn.execute("""
    SELECT
        a.id,
        a.nome,
        a.custo_unitario,
        pa.quantidade
    FROM peca_acessorios pa
    LEFT JOIN acessorios a ON pa.acessorio_id = a.id
    WHERE pa.peca_id = ?
    """, (peca_id,)).fetchall()


def carregar_filamentos_da_peca(conn, peca_id):
    return conn.execute("""
    SELECT
        f.codigo,
        f.nome,
        f.material,
        f.cor,
        f.custo_grama,
        pf.peso_g,
        pf.observacao
    FROM peca_filamentos pf
    LEFT JOIN filamentos f ON pf.filamento_id = f.id
    WHERE pf.peca_id = ?
    ORDER BY pf.id ASC
    """, (peca_id,)).fetchall()


def calcular_custo_unitario_peca(peca_id, energia_hora, depreciacao_hora, custo_pos_processamento_hora=0):
    conn = conectar()

    peca = conn.execute("""
    SELECT
        p.peso_g,
        p.tempo_impressao_h,
        p.tempo_pos_processamento_min,
        p.embalagem_custo,
        COALESCE(p.quantidade_lote, 1),
        f.custo_grama
    FROM pecas p
    LEFT JOIN filamentos f ON p.filamento_id = f.id
    WHERE p.id = ?
    """, (peca_id,)).fetchone()

    if peca is None:
        conn.close()
        return {
            "quantidade_lote": 1,
            "peso_unitario": 0,
            "tempo_unitario": 0,
            "custo_lote": 0,
            "custo_unitario": 0,
        }

    acessorios = carregar_acessorios_da_peca(conn, peca_id)
    filamentos_peca = carregar_filamentos_da_peca(conn, peca_id)
    conn.close()

    peso_g = peca[0] if peca[0] else 0
    tempo_h = peca[1] if peca[1] else 0
    tempo_pos_h = (peca[2] if peca[2] else 0) / 60
    embalagem = peca[3] if peca[3] else 0
    quantidade_lote = peca[4] if peca[4] and peca[4] > 0 else 1
    custo_grama = peca[5] if peca[5] else 0

    if filamentos_peca:
        peso_g = sum((f[5] if f[5] else 0) for f in filamentos_peca)
        custo_material = sum((f[4] if f[4] else 0) * (f[5] if f[5] else 0) for f in filamentos_peca)
    else:
        custo_material = peso_g * custo_grama

    custo_energia = tempo_h * energia_hora
    custo_depreciacao = tempo_h * depreciacao_hora
    custo_pos_processamento = tempo_pos_h * custo_pos_processamento_hora
    custo_acessorios = sum((a[2] if a[2] else 0) * (a[3] if a[3] else 0) for a in acessorios)

    custo_lote = custo_material + custo_energia + custo_depreciacao + custo_pos_processamento + embalagem + custo_acessorios
    custo_unitario = custo_lote / quantidade_lote if quantidade_lote > 0 else custo_lote
    peso_unitario = peso_g / quantidade_lote if quantidade_lote > 0 else peso_g
    tempo_total_h = tempo_h + tempo_pos_h
    tempo_unitario = tempo_total_h / quantidade_lote if quantidade_lote > 0 else tempo_total_h

    return {
        "quantidade_lote": quantidade_lote,
        "peso_unitario": peso_unitario,
        "tempo_unitario": tempo_unitario,
        "custo_lote": custo_lote,
        "custo_unitario": custo_unitario,
    }


def calcular_custos_pecas_lote(conn, peca_ids, energia_hora, depreciacao_hora, custo_pos_processamento_hora=0):
    """
    Calcula custos de várias peças em lote.

    Evita consultar filamentos/acessórios repetidamente para cada pedido.
    """
    peca_ids = sorted({int(pid) for pid in peca_ids if pid})

    if not peca_ids:
        return {}

    placeholders = ",".join(["?"] * len(peca_ids))

    pecas = conn.execute(f"""
    SELECT
        p.id,
        p.peso_g,
        p.tempo_impressao_h,
        p.tempo_pos_processamento_min,
        p.embalagem_custo,
        COALESCE(p.quantidade_lote, 1),
        f.custo_grama
    FROM pecas p
    LEFT JOIN filamentos f ON p.filamento_id = f.id
    WHERE p.id IN ({placeholders})
    """, peca_ids).fetchall()

    acessorios_rows = conn.execute(f"""
    SELECT
        pa.peca_id,
        a.custo_unitario,
        pa.quantidade
    FROM peca_acessorios pa
    LEFT JOIN acessorios a ON pa.acessorio_id = a.id
    WHERE pa.peca_id IN ({placeholders})
    """, peca_ids).fetchall()

    filamentos_rows = conn.execute(f"""
    SELECT
        pf.peca_id,
        f.custo_grama,
        pf.peso_g
    FROM peca_filamentos pf
    LEFT JOIN filamentos f ON pf.filamento_id = f.id
    WHERE pf.peca_id IN ({placeholders})
    ORDER BY pf.id ASC
    """, peca_ids).fetchall()

    acessorios_por_peca = {}
    for peca_id, custo_unitario, quantidade in acessorios_rows:
        acessorios_por_peca.setdefault(peca_id, []).append((
            custo_unitario if custo_unitario else 0,
            quantidade if quantidade else 0,
        ))

    filamentos_por_peca = {}
    for peca_id, custo_grama, peso_g in filamentos_rows:
        filamentos_por_peca.setdefault(peca_id, []).append((
            custo_grama if custo_grama else 0,
            peso_g if peso_g else 0,
        ))

    custos = {}

    for peca in pecas:
        peca_id = peca[0]
        peso_g = peca[1] if peca[1] else 0
        tempo_h = peca[2] if peca[2] else 0
        tempo_pos_h = (peca[3] if peca[3] else 0) / 60
        embalagem = peca[4] if peca[4] else 0
        quantidade_lote = peca[5] if peca[5] and peca[5] > 0 else 1
        custo_grama = peca[6] if peca[6] else 0

        filamentos_peca = filamentos_por_peca.get(peca_id, [])
        acessorios_peca = acessorios_por_peca.get(peca_id, [])

        if filamentos_peca:
            peso_g = sum(peso for _, peso in filamentos_peca)
            custo_material = sum(custo * peso for custo, peso in filamentos_peca)
        else:
            custo_material = peso_g * custo_grama

        custo_energia = tempo_h * energia_hora
        custo_depreciacao = tempo_h * depreciacao_hora
        custo_pos_processamento = tempo_pos_h * custo_pos_processamento_hora
        custo_acessorios = sum(custo * quantidade for custo, quantidade in acessorios_peca)

        custo_lote = (
            custo_material
            + custo_energia
            + custo_depreciacao
            + custo_pos_processamento
            + embalagem
            + custo_acessorios
        )

        custos[peca_id] = {
            "quantidade_lote": quantidade_lote,
            "peso_unitario": peso_g / quantidade_lote if quantidade_lote > 0 else peso_g,
            "tempo_unitario": (tempo_h + tempo_pos_h) / quantidade_lote if quantidade_lote > 0 else (tempo_h + tempo_pos_h),
            "custo_lote": custo_lote,
            "custo_unitario": custo_lote / quantidade_lote if quantidade_lote > 0 else custo_lote,
        }

    return custos


def calcular_pedido(peca_id, quantidade, valor_unitario, desconto, frete, energia_hora, depreciacao_hora, custo_peca=None, custo_pos_processamento_hora=0):
    if custo_peca is None:
        custo_peca = calcular_custo_unitario_peca(
            peca_id,
            energia_hora,
            depreciacao_hora,
            custo_pos_processamento_hora,
        )

    return calcular_resultado_pedido(
        custo_peca,
        quantidade,
        valor_unitario,
        desconto,
        frete,
    )


@st.cache_data(ttl=30, show_spinner=False)
def carregar_pedidos_resumo_cache(energia_hora, depreciacao_hora, custo_pos_processamento_hora):
    """
    Carrega e calcula o resumo de pedidos com cache curto.

    Evita recalcular o topo da página a cada clique simples.
    """
    conn = conectar()

    resumo = conn.execute("""
    SELECT
        id,
        peca_id,
        quantidade,
        valor_unitario,
        desconto,
        frete,
        status
    FROM pedidos
    """).fetchall()

    peca_ids_resumo = sorted({item[1] for item in resumo if item[1]})
    custos_pecas_resumo = calcular_custos_pecas_lote(
        conn,
        peca_ids_resumo,
        energia_hora,
        depreciacao_hora,
        custo_pos_processamento_hora
    )

    conn.close()

    total_pedidos = len(resumo)
    pedidos_abertos = 0
    faturamento_total = 0
    lucro_total = 0

    for r in resumo:
        peca_id = r[1]
        quantidade = r[2] if r[2] else 0
        valor_unitario = r[3] if r[3] else 0
        desconto = r[4] if r[4] else 0
        frete = r[5] if r[5] else 0
        status = r[6] if r[6] else "Orçamento"

        calc = calcular_pedido(
            peca_id,
            quantidade,
            valor_unitario,
            desconto,
            frete,
            energia_hora,
            depreciacao_hora,
            custos_pecas_resumo.get(peca_id),
        )

        if status not in ["Entregue", "Cancelado"]:
            pedidos_abertos += 1

        if status != "Cancelado":
            faturamento_total += calc["total"]
            lucro_total += calc["lucro"]

    ticket_medio = faturamento_total / total_pedidos if total_pedidos > 0 else 0

    return {
        "total_pedidos": total_pedidos,
        "pedidos_abertos": pedidos_abertos,
        "faturamento_total": faturamento_total,
        "lucro_total": lucro_total,
        "ticket_medio": ticket_medio,
    }


@st.cache_data(ttl=30, show_spinner=False)
def carregar_custos_pedidos_cache(peca_ids, energia_hora, depreciacao_hora, custo_pos_processamento_hora):
    """
    Calcula custos das peças usadas nos pedidos com cache curto.
    """
    conn = conectar()
    custos = calcular_custos_pecas_lote(
        conn,
        list(peca_ids),
        energia_hora,
        depreciacao_hora,
        custo_pos_processamento_hora
    )
    conn.close()
    return custos
