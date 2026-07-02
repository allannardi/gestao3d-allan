"""
Consultas e gravações de filamentos vinculados a pedidos.

Este módulo concentra regras de dados do consumo real de filamentos por pedido.
A interface de escolha dos filamentos continua na tela Pedidos.
"""

import streamlit as st

from database import conectar


@st.cache_data(ttl=30, show_spinner=False)
def carregar_filamentos_ativos():
    conn = conectar()
    filamentos = conn.execute("""
    SELECT
        id,
        codigo,
        nome,
        material,
        cor,
        peso_original,
        custo_grama
    FROM filamentos
    WHERE status IS NULL OR status = 'Ativo'
    ORDER BY nome ASC, cor ASC
    """).fetchall()
    conn.close()
    return [tuple(f) for f in filamentos]


def carregar_consumo_filamentos(excluir_pedido_id=None):
    conn = conectar()

    filtro_excluir = ""
    params = []

    if excluir_pedido_id:
        filtro_excluir = "AND ped.id <> ?"
        params.append(excluir_pedido_id)

    consumo_rows = conn.execute(f"""
    SELECT
        pf.filamento_id,
        COALESCE(SUM(COALESCE(pf.peso_g, 0)), 0)
    FROM pedido_filamentos pf
    LEFT JOIN pedidos ped ON pf.pedido_id = ped.id
    WHERE COALESCE(ped.status, '') <> 'Cancelado'
      {filtro_excluir}
    GROUP BY pf.filamento_id
    """, params).fetchall()

    conn.close()
    return {row[0]: row[1] for row in consumo_rows}


def carregar_disponibilidade_filamentos(excluir_pedido_id=None):
    filamentos = carregar_filamentos_ativos()
    consumo = carregar_consumo_filamentos(excluir_pedido_id)

    disponibilidade = []

    for f in filamentos:
        filamento_id = f[0]
        peso_original = f[5] if f[5] else 0
        consumido = consumo.get(filamento_id, 0) or 0
        disponivel = peso_original - consumido

        disponibilidade.append({
            "id": filamento_id,
            "codigo": f[1],
            "nome": f[2],
            "material": f[3],
            "cor": f[4],
            "peso_original": peso_original,
            "custo_grama": f[6] if f[6] else 0,
            "consumido": consumido,
            "disponivel": disponivel,
        })

    return disponibilidade


def carregar_requisitos_filamentos_peca(peca_id, quantidade):
    conn = conectar()

    peca = conn.execute("""
    SELECT
        peso_g,
        COALESCE(quantidade_lote, 1)
    FROM pecas
    WHERE id = ?
    """, (peca_id,)).fetchone()

    if peca is None:
        conn.close()
        return []

    peso_total_lote = peca[0] if peca[0] else 0
    quantidade_lote = peca[1] if peca[1] and peca[1] > 0 else 1

    referencias = conn.execute("""
    SELECT
        COALESCE(observacao, ''),
        COALESCE(peso_g, 0)
    FROM peca_filamentos
    WHERE peca_id = ?
    ORDER BY id ASC
    """, (peca_id,)).fetchall()

    conn.close()

    requisitos = []

    if referencias:
        for idx, ref in enumerate(referencias, start=1):
            uso = ref[0] if ref[0] else f"Filamento {idx}"
            peso_lote = ref[1] if ref[1] else 0
            peso_pedido = (peso_lote / quantidade_lote) * quantidade if quantidade_lote > 0 else 0

            requisitos.append({
                "uso": uso,
                "peso_lote": peso_lote,
                "peso_pedido": peso_pedido,
            })
    else:
        peso_pedido = (peso_total_lote / quantidade_lote) * quantidade if quantidade_lote > 0 else 0
        requisitos.append({
            "uso": "Principal",
            "peso_lote": peso_total_lote,
            "peso_pedido": peso_pedido,
        })

    return requisitos


def carregar_filamentos_pedido_registros(pedido_id):
    conn = conectar()
    registros = conn.execute("""
    SELECT
        filamento_id,
        COALESCE(peso_g, 0),
        COALESCE(observacao, '')
    FROM pedido_filamentos
    WHERE pedido_id = ?
    ORDER BY id ASC
    """, (pedido_id,)).fetchall()
    conn.close()
    return [tuple(r) for r in registros]


def salvar_filamentos_pedido(conn, pedido_id, filamentos_pedido):
    conn.execute("DELETE FROM pedido_filamentos WHERE pedido_id = ?", (pedido_id,))

    for item in filamentos_pedido:
        if len(item) == 3:
            filamento_id, peso_g, observacao = item
        else:
            filamento_id, observacao = item
            peso_g = 0

        if filamento_id:
            conn.execute("""
            INSERT INTO pedido_filamentos
            (
                pedido_id,
                filamento_id,
                peso_g,
                observacao
            )
            VALUES (?, ?, ?, ?)
            """, (
                pedido_id,
                filamento_id,
                peso_g if peso_g else 0,
                observacao
            ))


def carregar_filamentos_pedido(pedido_id):
    conn = conectar()
    filamentos = conn.execute("""
    SELECT
        f.id,
        f.codigo,
        f.nome,
        f.material,
        f.cor,
        COALESCE(pf.peso_g, 0),
        COALESCE(pf.observacao, '')
    FROM pedido_filamentos pf
    LEFT JOIN filamentos f ON pf.filamento_id = f.id
    WHERE pf.pedido_id = ?
    ORDER BY pf.id ASC
    """, (pedido_id,)).fetchall()
    conn.close()
    return [tuple(f) for f in filamentos]
