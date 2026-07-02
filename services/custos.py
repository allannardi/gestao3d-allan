"""
Regras de cálculo do Gestão 3D.

Este módulo inicia a separação das regras internas do app.
A ideia é manter as telas Streamlit mais simples e concentrar aqui as fórmulas
de custo, preço, lucro e indicadores.
"""


def numero(valor, padrao=0):
    """Normaliza números vindos do banco ou da interface."""
    if valor is None:
        return padrao

    try:
        return float(valor)
    except Exception:
        return padrao


def calcular_custos_peca(
    peso_g,
    tempo_impressao_h,
    tempo_pos_processamento_min,
    embalagem_custo,
    custo_grama,
    acessorios_selecionados,
    energia_hora,
    depreciacao_hora,
    custo_pos_processamento_hora,
    margem_padrao,
    meta_lucro_hora,
    quantidade_lote=1,
    filamentos_lote=None,
):
    """
    Calcula custo, preço sugerido e rentabilidade de uma peça/lote.

    Usado inicialmente pela tela Peças.
    """

    quantidade = int(quantidade_lote) if quantidade_lote else 1
    if quantidade <= 0:
        quantidade = 1

    peso_g = numero(peso_g)
    tempo_impressao_h = numero(tempo_impressao_h)
    tempo_pos_processamento_min = numero(tempo_pos_processamento_min)
    embalagem_custo = numero(embalagem_custo)
    custo_grama = numero(custo_grama)
    energia_hora = numero(energia_hora)
    depreciacao_hora = numero(depreciacao_hora)
    custo_pos_processamento_hora = numero(custo_pos_processamento_hora)
    margem_padrao = numero(margem_padrao)
    meta_lucro_hora = numero(meta_lucro_hora)

    acessorios_selecionados = acessorios_selecionados or []
    filamentos_lote = filamentos_lote or []

    tempo_pos_h = tempo_pos_processamento_min / 60
    tempo_total_h = tempo_impressao_h + tempo_pos_h

    if filamentos_lote:
        peso_g = sum(numero(f[2]) for f in filamentos_lote)
        custo_material = sum(numero(f[1]) * numero(f[2]) for f in filamentos_lote)
    else:
        custo_material = peso_g * custo_grama

    custo_energia = tempo_impressao_h * energia_hora
    custo_depreciacao = tempo_impressao_h * depreciacao_hora
    custo_pos_processamento = tempo_pos_h * custo_pos_processamento_hora
    custo_acessorios = sum(numero(valor) * numero(qtd) for _, valor, qtd in acessorios_selecionados)

    custo_total_lote = (
        custo_material
        + custo_energia
        + custo_depreciacao
        + custo_pos_processamento
        + embalagem_custo
        + custo_acessorios
    )

    preco_sugerido_lote = custo_total_lote * (1 + margem_padrao / 100)
    lucro_lote = preco_sugerido_lote - custo_total_lote

    custo_unitario = custo_total_lote / quantidade
    preco_unitario = preco_sugerido_lote / quantidade
    lucro_unitario = lucro_lote / quantidade
    peso_unitario = peso_g / quantidade
    tempo_unitario = tempo_total_h / quantidade if quantidade > 0 else 0

    lucro_percentual = (lucro_lote / custo_total_lote) * 100 if custo_total_lote > 0 else 0
    lucro_hora = lucro_lote / tempo_total_h if tempo_total_h > 0 else 0

    if lucro_hora >= meta_lucro_hora:
        status = "Recomendado"
        cor = "green"
    elif lucro_hora >= meta_lucro_hora * 0.6:
        status = "Atenção"
        cor = "orange"
    else:
        status = "Baixa rentabilidade"
        cor = "red"

    return {
        "quantidade": quantidade,
        "material": custo_material,
        "energia": custo_energia,
        "depreciacao": custo_depreciacao,
        "pos_processamento": custo_pos_processamento,
        "tempo_pos_h": tempo_pos_h,
        "tempo_total_h": tempo_total_h,
        "acessorios": custo_acessorios,
        "embalagem": embalagem_custo,
        "total": custo_total_lote,
        "preco": preco_sugerido_lote,
        "lucro": lucro_lote,
        "lucro_percentual": lucro_percentual,
        "lucro_hora": lucro_hora,
        "custo_unitario": custo_unitario,
        "preco_unitario": preco_unitario,
        "lucro_unitario": lucro_unitario,
        "peso_unitario": peso_unitario,
        "tempo_unitario": tempo_unitario,
        "status": status,
        "cor": cor,
    }


def calcular_resultado_pedido(custo_peca, quantidade, valor_unitario, desconto, frete):
    """
    Calcula subtotal, total, custo, lucro e indicadores de um pedido.

    Usado inicialmente por Pedidos e Dashboard.
    """

    custo_peca = custo_peca or {}

    quantidade = numero(quantidade)
    valor_unitario = numero(valor_unitario)
    desconto = numero(desconto)
    frete = numero(frete)

    custo_unitario = numero(custo_peca.get("custo_unitario"))
    peso_unitario = numero(custo_peca.get("peso_unitario"))
    tempo_unitario = numero(custo_peca.get("tempo_unitario"))

    subtotal = quantidade * valor_unitario
    total = subtotal - desconto + frete
    custo_total = quantidade * custo_unitario
    lucro = total - custo_total
    tempo_total = quantidade * tempo_unitario

    lucro_percentual = (lucro / custo_total) * 100 if custo_total > 0 else 0
    lucro_unitario = lucro / quantidade if quantidade > 0 else 0
    margem_venda = (lucro / total) * 100 if total > 0 else 0
    lucro_hora = lucro / tempo_total if tempo_total > 0 else 0

    return {
        "custo_unitario": custo_unitario,
        "peso_unitario": peso_unitario,
        "tempo_unitario": tempo_unitario,
        "subtotal": subtotal,
        "total": total,
        "custo_total": custo_total,
        "lucro": lucro,
        "lucro_percentual": lucro_percentual,
        "lucro_unitario": lucro_unitario,
        "tempo_total": tempo_total,
        "margem_venda": margem_venda,
        "lucro_hora": lucro_hora,
    }
