from database import conectar
from components.formatters import data_br


def _valor(valor, padrao=0):
    return valor if valor is not None else padrao


def carregar_configuracoes_resultados():
    conn = conectar()

    try:
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
    except Exception:
        config = None

    conn.close()

    if config is None:
        return 0.15, 0.75, 150, 5, 0

    return (
        _valor(config[0], 0.15),
        _valor(config[1], 0.75),
        _valor(config[2], 150),
        _valor(config[3], 5),
        _valor(config[4], 0) if len(config) > 4 else 0,
    )


def tabela_existe(conn, nome_tabela):
    try:
        resultado = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (nome_tabela,)
        ).fetchone()
        return resultado is not None
    except Exception:
        return False


def calcular_custo_unitario_peca_conn(conn, peca_id, energia_hora, depreciacao_hora, custo_pos_processamento_hora=0):
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
        return {
            "quantidade_lote": 1,
            "peso_unitario": 0,
            "tempo_unitario": 0,
            "custo_lote": 0,
            "custo_unitario": 0,
        }

    peso_g = _valor(peca[0], 0)
    tempo_h = _valor(peca[1], 0)
    tempo_pos_h = _valor(peca[2], 0) / 60
    embalagem = _valor(peca[3], 0)
    quantidade_lote = _valor(peca[4], 1) or 1
    custo_grama_padrao = _valor(peca[5], 0)

    if quantidade_lote <= 0:
        quantidade_lote = 1

    custo_material = peso_g * custo_grama_padrao

    if tabela_existe(conn, "peca_filamentos"):
        filamentos = conn.execute("""
        SELECT
            f.custo_grama,
            pf.peso_g
        FROM peca_filamentos pf
        LEFT JOIN filamentos f ON pf.filamento_id = f.id
        WHERE pf.peca_id = ?
        """, (peca_id,)).fetchall()

        if filamentos:
            peso_g = sum(_valor(f[1], 0) for f in filamentos)
            custo_material = sum(_valor(f[0], 0) * _valor(f[1], 0) for f in filamentos)

    custo_acessorios = 0

    if tabela_existe(conn, "peca_acessorios"):
        acessorios = conn.execute("""
        SELECT
            a.custo_unitario,
            pa.quantidade
        FROM peca_acessorios pa
        LEFT JOIN acessorios a ON pa.acessorio_id = a.id
        WHERE pa.peca_id = ?
        """, (peca_id,)).fetchall()

        custo_acessorios = sum(_valor(a[0], 0) * _valor(a[1], 0) for a in acessorios)

    custo_energia = tempo_h * energia_hora
    custo_depreciacao = tempo_h * depreciacao_hora
    custo_pos_processamento = tempo_pos_h * custo_pos_processamento_hora

    custo_lote = (
        custo_material
        + custo_energia
        + custo_depreciacao
        + custo_pos_processamento
        + embalagem
        + custo_acessorios
    )

    return {
        "quantidade_lote": quantidade_lote,
        "peso_unitario": peso_g / quantidade_lote if quantidade_lote > 0 else 0,
        "tempo_unitario": (tempo_h + tempo_pos_h) / quantidade_lote if quantidade_lote > 0 else 0,
        "custo_lote": custo_lote,
        "custo_unitario": custo_lote / quantidade_lote if quantidade_lote > 0 else 0,
    }


def calcular_pedido_conn(conn, peca_id, quantidade, valor_unitario, desconto, frete, energia_hora, depreciacao_hora, custo_pos_processamento_hora=0):
    custo_peca = calcular_custo_unitario_peca_conn(conn, peca_id, energia_hora, depreciacao_hora, custo_pos_processamento_hora)

    quantidade = _valor(quantidade, 0)
    valor_unitario = _valor(valor_unitario, 0)
    desconto = _valor(desconto, 0)
    frete = _valor(frete, 0)

    subtotal = quantidade * valor_unitario
    total = subtotal - desconto + frete
    custo_total = quantidade * custo_peca["custo_unitario"]
    lucro = total - custo_total
    lucro_percentual = (lucro / custo_total) * 100 if custo_total > 0 else 0
    lucro_unitario = lucro / quantidade if quantidade > 0 else 0

    return {
        "custo_unitario": custo_peca["custo_unitario"],
        "peso_unitario": custo_peca["peso_unitario"],
        "tempo_unitario": custo_peca["tempo_unitario"],
        "subtotal": subtotal,
        "total": total,
        "custo_total": custo_total,
        "lucro": lucro,
        "lucro_percentual": lucro_percentual,
        "lucro_unitario": lucro_unitario,
    }


def _resumo_inicial():
    return {
        "pedidos_total": 0,
        "pedidos_abertos": 0,
        "quantidade_total": 0,
        "faturamento": 0,
        "lucro": 0,
        "ticket_medio": 0,
        "pedidos": [],
    }


def _finalizar_resumo(resumo):
    pedidos_validos = [
        p for p in resumo["pedidos"]
        if p["status"] != "Cancelado"
    ]

    resumo["ticket_medio"] = (
        resumo["faturamento"] / len(pedidos_validos)
        if pedidos_validos else 0
    )

    return resumo


def carregar_resultados_cliente(cliente_id):
    energia_hora, depreciacao_hora, _, _, custo_pos_processamento_hora = carregar_configuracoes_resultados()
    conn = conectar()
    resumo = _resumo_inicial()

    pedidos = conn.execute("""
    SELECT
        ped.codigo,
        ped.peca_id,
        pc.codigo,
        pc.nome,
        ped.quantidade,
        ped.valor_unitario,
        ped.desconto,
        ped.frete,
        ped.status,
        ped.data_pedido
    FROM pedidos ped
    LEFT JOIN pecas pc ON ped.peca_id = pc.id
    WHERE ped.cliente_id = ?
    ORDER BY ped.id DESC
    """, (cliente_id,)).fetchall()

    for pedido in pedidos:
        codigo = pedido[0]
        peca_id = pedido[1]
        peca_codigo = pedido[2] or "-"
        peca_nome = pedido[3] or "-"
        quantidade = _valor(pedido[4], 0)
        valor_unitario = _valor(pedido[5], 0)
        desconto = _valor(pedido[6], 0)
        frete = _valor(pedido[7], 0)
        status = pedido[8] or "Orçamento"
        data_pedido = data_br(pedido[9])

        calc = calcular_pedido_conn(
            conn,
            peca_id,
            quantidade,
            valor_unitario,
            desconto,
            frete,
            energia_hora,
            depreciacao_hora,
            custo_pos_processamento_hora,
        )

        resumo["pedidos_total"] += 1

        if status not in ["Entregue", "Cancelado"]:
            resumo["pedidos_abertos"] += 1

        if status != "Cancelado":
            resumo["quantidade_total"] += quantidade
            resumo["faturamento"] += calc["total"]
            resumo["lucro"] += calc["lucro"]

        resumo["pedidos"].append({
            "codigo": codigo,
            "peca_codigo": peca_codigo,
            "peca_nome": peca_nome,
            "quantidade": quantidade,
            "status": status,
            "data_pedido": data_pedido,
            "total": calc["total"],
            "lucro": calc["lucro"],
        })

    conn.close()
    return _finalizar_resumo(resumo)


def carregar_resultados_filamento(filamento_id):
    energia_hora, depreciacao_hora, _, _, custo_pos_processamento_hora = carregar_configuracoes_resultados()
    conn = conectar()
    resumo = _resumo_inicial()
    resumo["peso_consumido_g"] = 0
    resumo["pecas_vinculadas"] = 0

    pedidos = conn.execute("""
    SELECT
        ped.codigo,
        ped.peca_id,
        pc.codigo,
        pc.nome,
        c.nome,
        ped.quantidade,
        ped.valor_unitario,
        ped.desconto,
        ped.frete,
        ped.status,
        ped.data_pedido,
        COALESCE(pf.peso_g, 0),
        COALESCE(pf.observacao, '')
    FROM pedido_filamentos pf
    LEFT JOIN pedidos ped ON pf.pedido_id = ped.id
    LEFT JOIN pecas pc ON ped.peca_id = pc.id
    LEFT JOIN clientes c ON ped.cliente_id = c.id
    WHERE pf.filamento_id = ?
    ORDER BY ped.id DESC
    """, (filamento_id,)).fetchall()

    pecas_vinculadas = conn.execute("""
    SELECT COUNT(DISTINCT ped.peca_id)
    FROM pedido_filamentos pf
    LEFT JOIN pedidos ped ON pf.pedido_id = ped.id
    WHERE pf.filamento_id = ?
      AND COALESCE(ped.status, '') <> 'Cancelado'
    """, (filamento_id,)).fetchone()[0]

    resumo["pecas_vinculadas"] = pecas_vinculadas or 0

    for pedido in pedidos:
        codigo = pedido[0]
        peca_id = pedido[1]
        peca_codigo = pedido[2] or "-"
        peca_nome = pedido[3] or "-"
        cliente_nome = pedido[4] or "-"
        quantidade = _valor(pedido[5], 0)
        valor_unitario = _valor(pedido[6], 0)
        desconto = _valor(pedido[7], 0)
        frete = _valor(pedido[8], 0)
        status = pedido[9] or "Orçamento"
        data_pedido = data_br(pedido[10])
        peso_consumido = _valor(pedido[11], 0)

        calc = calcular_pedido_conn(
            conn,
            peca_id,
            quantidade,
            valor_unitario,
            desconto,
            frete,
            energia_hora,
            depreciacao_hora,
            custo_pos_processamento_hora,
        )

        resumo["pedidos_total"] += 1

        if status not in ["Entregue", "Cancelado"]:
            resumo["pedidos_abertos"] += 1

        if status != "Cancelado":
            resumo["quantidade_total"] += quantidade
            resumo["peso_consumido_g"] += peso_consumido
            resumo["faturamento"] += calc["total"]
            resumo["lucro"] += calc["lucro"]

        resumo["pedidos"].append({
            "codigo": codigo,
            "cliente_nome": cliente_nome,
            "peca_codigo": peca_codigo,
            "peca_nome": peca_nome,
            "quantidade": quantidade,
            "status": status,
            "data_pedido": data_pedido,
            "total": calc["total"],
            "lucro": calc["lucro"],
            "peso_consumido_g": peso_consumido,
        })

    conn.close()
    return _finalizar_resumo(resumo)

