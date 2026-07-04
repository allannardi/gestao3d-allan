"""
Custos usados pela Dashboard.

Este módulo continua a fase 2 do roadmap:
simplificar e separar regras internas sem alterar a interface.

Aqui ficam as regras de custo usadas para calcular:
- custo unitário da peça no contexto da Dashboard;
- custos de peças em lote;
- resultado financeiro de cada pedido.
"""

from database import conectar
from services.custos import calcular_resultado_pedido


def carregar_acessorios_da_peca(conn, peca_id):
    return conn.execute("""
    SELECT
        a.custo_unitario,
        pa.quantidade
    FROM peca_acessorios pa
    LEFT JOIN acessorios a ON pa.acessorio_id = a.id
    WHERE pa.peca_id = ?
    """, (peca_id,)).fetchall()


def carregar_filamentos_da_peca(conn, peca_id):
    return conn.execute("""
    SELECT
        f.custo_grama,
        pf.peso_g
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
            "custo_unitario": 0,
            "peso_unitario": 0,
            "tempo_unitario": 0,
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
        peso_g = sum((f[1] if f[1] else 0) for f in filamentos_peca)
        custo_material = sum((f[0] if f[0] else 0) * (f[1] if f[1] else 0) for f in filamentos_peca)
    else:
        custo_material = peso_g * custo_grama

    custo_energia = tempo_h * energia_hora
    custo_depreciacao = tempo_h * depreciacao_hora
    custo_pos_processamento = tempo_pos_h * custo_pos_processamento_hora
    custo_acessorios = sum(
        (a[0] if a[0] else 0) * (a[1] if a[1] else 0)
        for a in acessorios
    )

    custo_lote = (
        custo_material
        + custo_energia
        + custo_depreciacao
        + custo_pos_processamento
        + embalagem
        + custo_acessorios
    )

    return {
        "custo_unitario": custo_lote / quantidade_lote if quantidade_lote > 0 else custo_lote,
        "peso_unitario": peso_g / quantidade_lote if quantidade_lote > 0 else peso_g,
        "tempo_unitario": (tempo_h + tempo_pos_h) / quantidade_lote if quantidade_lote > 0 else (tempo_h + tempo_pos_h),
        "material_unitario": custo_material / quantidade_lote if quantidade_lote > 0 else custo_material,
        "energia_unitaria": custo_energia / quantidade_lote if quantidade_lote > 0 else custo_energia,
        "depreciacao_unitaria": custo_depreciacao / quantidade_lote if quantidade_lote > 0 else custo_depreciacao,
        "pos_processamento_unitario": custo_pos_processamento / quantidade_lote if quantidade_lote > 0 else custo_pos_processamento,
        "acessorios_unitario": custo_acessorios / quantidade_lote if quantidade_lote > 0 else custo_acessorios,
        "embalagem_unitaria": embalagem / quantidade_lote if quantidade_lote > 0 else embalagem,
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
            "custo_unitario": custo_lote / quantidade_lote if quantidade_lote > 0 else custo_lote,
            "peso_unitario": peso_g / quantidade_lote if quantidade_lote > 0 else peso_g,
            "tempo_unitario": (tempo_h + tempo_pos_h) / quantidade_lote if quantidade_lote > 0 else (tempo_h + tempo_pos_h),
            "material_unitario": custo_material / quantidade_lote if quantidade_lote > 0 else custo_material,
            "energia_unitaria": custo_energia / quantidade_lote if quantidade_lote > 0 else custo_energia,
            "depreciacao_unitaria": custo_depreciacao / quantidade_lote if quantidade_lote > 0 else custo_depreciacao,
            "pos_processamento_unitario": custo_pos_processamento / quantidade_lote if quantidade_lote > 0 else custo_pos_processamento,
            "acessorios_unitario": custo_acessorios / quantidade_lote if quantidade_lote > 0 else custo_acessorios,
            "embalagem_unitaria": embalagem / quantidade_lote if quantidade_lote > 0 else embalagem,
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



def precalcular_custos_pedidos_dashboard(
    conn,
    pedidos,
    energia_padrao,
    depreciacao_padrao,
    custo_pos_processamento_hora=0,
):
    """
    Pré-calcula custos dos pedidos da Dashboard em lotes.

    Antes, a Dashboard calculava custos chamando o cálculo por peça várias vezes,
    uma vez para cada combinação de peça/impressora.

    Agora, os pedidos são agrupados por energia/depreciação da impressora.
    Para cada grupo, calculamos várias peças de uma vez.
    """
    grupos = {}

    for pedido in pedidos:
        peca_id = pedido[5] if len(pedido) > 5 else None
        if not peca_id:
            continue

        energia_pedido = (
            pedido[22]
            if len(pedido) > 22 and pedido[22] is not None
            else energia_padrao
        )
        depreciacao_pedido = (
            pedido[23]
            if len(pedido) > 23 and pedido[23] is not None
            else depreciacao_padrao
        )

        chave_grupo = (
            round(float(energia_pedido), 6),
            round(float(depreciacao_pedido), 6),
        )

        grupos.setdefault(chave_grupo, set()).add(int(peca_id))

    custos_por_pedido_chave = {}

    for (energia_pedido, depreciacao_pedido), peca_ids in grupos.items():
        custos_grupo = calcular_custos_pecas_lote(
            conn,
            sorted(peca_ids),
            energia_pedido,
            depreciacao_pedido,
            custo_pos_processamento_hora,
        )

        for peca_id, custo in custos_grupo.items():
            chave_custo = (
                peca_id,
                round(float(energia_pedido), 6),
                round(float(depreciacao_pedido), 6),
            )
            custos_por_pedido_chave[chave_custo] = custo

    return custos_por_pedido_chave
