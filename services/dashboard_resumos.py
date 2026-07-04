"""
Resumos e agregações da Dashboard.

Este módulo concentra a montagem dos indicadores da Dashboard a partir dos pedidos,
custos já pré-calculados, impressoras e parâmetros atuais.

A tela Streamlit continua responsável por renderizar cards, tabelas e gráficos.
"""

import calendar
from collections import defaultdict
from datetime import date

from components.formatters import data_br, data_para_date
from services.dashboard_custos import calcular_pedido


def rotulo_mes_dashboard(data_pedido_dt):
    meses = {
        1: "jan",
        2: "fev",
        3: "mar",
        4: "abr",
        5: "mai",
        6: "jun",
        7: "jul",
        8: "ago",
        9: "set",
        10: "out",
        11: "nov",
        12: "dez",
    }
    if not data_pedido_dt:
        return "-"
    return f"{meses.get(data_pedido_dt.month, str(data_pedido_dt.month).zfill(2))}/{str(data_pedido_dt.year)[-2:]}"


def listar_meses_pedidos_dashboard(pedidos):
    """
    Retorna os meses/anos disponíveis a partir da Data do Pedido.
    """
    meses = {}

    for pedido in pedidos:
        data_pedido = pedido[14] if len(pedido) > 14 and pedido[14] else ""
        data_pedido_dt = data_para_date(data_pedido)

        if not data_pedido_dt:
            continue

        key = data_pedido_dt.strftime("%Y-%m")
        meses[key] = {
            "key": key,
            "label": rotulo_mes_dashboard(data_pedido_dt),
            "ordem": data_pedido_dt.year * 100 + data_pedido_dt.month,
        }

    return sorted(meses.values(), key=lambda item: item["ordem"], reverse=True)


def filtrar_pedidos_por_meses_dashboard(pedidos, meses_selecionados):
    """
    Filtra pedidos por Data do Pedido.

    Se nenhum mês específico for informado, retorna todos os pedidos.
    """
    if not meses_selecionados:
        return list(pedidos)

    meses_selecionados = set(meses_selecionados)
    pedidos_filtrados = []

    for pedido in pedidos:
        data_pedido = pedido[14] if len(pedido) > 14 and pedido[14] else ""
        data_pedido_dt = data_para_date(data_pedido)

        if not data_pedido_dt:
            continue

        if data_pedido_dt.strftime("%Y-%m") in meses_selecionados:
            pedidos_filtrados.append(pedido)

    return pedidos_filtrados


def gerar_meses_utilizacao(hoje=None):
    hoje = hoje or date.today()
    meses_utilizacao = []
    ano_mes_atual = hoje.year * 12 + hoje.month

    for offset in range(11, -1, -1):
        total_meses = ano_mes_atual - offset
        ano_mes = (total_meses - 1) // 12
        mes_num = (total_meses - 1) % 12 + 1
        data_mes = date(ano_mes, mes_num, 1)
        mes_key = data_mes.strftime("%Y-%m")
        mes_label = rotulo_mes_dashboard(data_mes)
        capacidade_mes = calendar.monthrange(ano_mes, mes_num)[1] * 24

        meses_utilizacao.append({
            "key": mes_key,
            "label": mes_label,
            "capacidade": capacidade_mes,
        })

    return meses_utilizacao


def somar_distribuicao_faturamento(distribuicao, custo_peca, quantidade, calc):
    """
    Soma a composição do faturamento para o gráfico de rosca.

    Componentes de custo vêm do cadastro da peça.
    Lucro vem do resultado real do pedido, considerando preço, desconto e frete.
    """
    custo_peca = custo_peca or {}
    quantidade = quantidade or 0

    componentes = [
        ("Filamento", "material_unitario"),
        ("Energia", "energia_unitaria"),
        ("Depreciação", "depreciacao_unitaria"),
        ("Pós-processamento", "pos_processamento_unitario"),
        ("Acessórios", "acessorios_unitario"),
        ("Embalagem", "embalagem_unitaria"),
    ]

    tem_componentes = any(chave in custo_peca for _, chave in componentes)

    if tem_componentes:
        for label, chave in componentes:
            valor = (custo_peca.get(chave) or 0) * quantidade
            if valor:
                distribuicao[label] += valor
    else:
        custo_total = calc.get("custo_total", 0) if calc else 0
        if custo_total:
            distribuicao["Custos"] += custo_total

    lucro = calc.get("lucro", 0) if calc else 0
    if lucro >= 0:
        distribuicao["Lucro"] += lucro
    else:
        distribuicao["Prejuízo"] += abs(lucro)


def montar_resumos_dashboard(
    pedidos,
    custos_pecas_dashboard,
    energia,
    depreciacao,
    custo_pos_processamento_hora,
    impressoras_ativas_dashboard,
    impressora_padrao_nome,
    hoje=None,
):
    """
    Monta os resumos usados pelos blocos mobile e desktop da Dashboard.
    """
    hoje = hoje or date.today()

    pedidos_abertos = 0
    faturamento_total = 0
    lucro_total = 0
    horas_total = 0
    quantidade_total = 0
    pedidos_fechados_mes = 0
    faturamento_mes = 0
    lucro_mes = 0

    distribuicao_faturamento = defaultdict(float)

    status_resumo = defaultdict(lambda: {
        "pedidos": 0,
        "faturamento": 0,
        "lucro": 0,
    })

    pecas_resumo = defaultdict(lambda: {
        "quantidade": 0,
        "faturamento": 0,
        "lucro": 0,
    })

    clientes_resumo = defaultdict(lambda: {
        "pedidos": 0,
        "faturamento": 0,
        "lucro": 0,
    })

    impressoras_resumo = defaultdict(lambda: {
        "pedidos": 0,
        "faturamento": 0,
        "lucro": 0,
        "horas": 0,
    })

    vendas_mes_resumo = defaultdict(lambda: {
        "mes": "",
        "pedidos": 0,
        "quantidade": 0,
        "faturamento": 0,
        "lucro": 0,
    })

    pedidos_recentes = []
    pedidos_abertos_lista = []

    meses_utilizacao = gerar_meses_utilizacao(hoje)
    capacidade_horas_mes = meses_utilizacao[-1]["capacidade"] if meses_utilizacao else 0

    utilizacao_impressoras_mes = defaultdict(lambda: {
        "horas_usadas": 0,
        "capacidade_horas": 0,
        "pedidos": 0,
    })

    for mes_info in meses_utilizacao:
        for impressora in impressoras_ativas_dashboard:
            impressora_label = f"{impressora[1]} - {impressora[2]} {impressora[3]}".strip()
            chave_utilizacao = (mes_info["key"], mes_info["label"], impressora_label)
            utilizacao_impressoras_mes[chave_utilizacao]["horas_usadas"] += 0
            utilizacao_impressoras_mes[chave_utilizacao]["capacidade_horas"] = mes_info["capacidade"]
            utilizacao_impressoras_mes[chave_utilizacao]["pedidos"] += 0

    for pedido in pedidos:
        codigo = pedido[1]
        cliente_codigo = pedido[3] if pedido[3] else "-"
        cliente_nome = pedido[4] if pedido[4] else "-"
        peca_id = pedido[5]
        peca_codigo = pedido[6] if pedido[6] else "-"
        peca_nome = pedido[7] if pedido[7] else "-"
        quantidade = pedido[8] if pedido[8] else 0
        valor_unitario = pedido[9] if pedido[9] else 0
        desconto = pedido[10] if pedido[10] else 0
        frete = pedido[11] if pedido[11] else 0
        status = pedido[12] if pedido[12] else "Orçamento"
        data_pedido = pedido[14] if pedido[14] else ""
        data_pedido_dt = data_para_date(data_pedido)
        data_final_producao = pedido[16] if len(pedido) > 16 and pedido[16] else ""
        data_producao_dt = data_para_date(data_final_producao) or data_pedido_dt
        impressora_id = pedido[18] if len(pedido) > 18 else None
        impressora_codigo = pedido[19] if len(pedido) > 19 and pedido[19] else "-"
        impressora_marca = pedido[20] if len(pedido) > 20 and pedido[20] else ""
        impressora_modelo = pedido[21] if len(pedido) > 21 and pedido[21] else ""
        energia_pedido = pedido[22] if len(pedido) > 22 and pedido[22] is not None else energia
        depreciacao_pedido = pedido[23] if len(pedido) > 23 and pedido[23] is not None else depreciacao
        impressora_key = f"{impressora_codigo} - {impressora_marca} {impressora_modelo}".strip() if impressora_id else impressora_padrao_nome
        chave_custo_pedido = (
            peca_id,
            round(float(energia_pedido), 6),
            round(float(depreciacao_pedido), 6),
        )

        custo_peca_pedido = custos_pecas_dashboard.get(chave_custo_pedido)

        calc = calcular_pedido(
            peca_id,
            quantidade,
            valor_unitario,
            desconto,
            frete,
            energia_pedido,
            depreciacao_pedido,
            custo_peca_pedido,
            custo_pos_processamento_hora,
        )

        if status not in ["Entregue", "Cancelado"]:
            pedidos_abertos += 1

        if status != "Cancelado":
            faturamento_total += calc["total"]
            lucro_total += calc["lucro"]
            horas_total += calc["tempo_total"]
            quantidade_total += quantidade

            faturamento_mes += calc["total"]
            lucro_mes += calc["lucro"]
            if status == "Entregue":
                pedidos_fechados_mes += 1

            somar_distribuicao_faturamento(
                distribuicao_faturamento,
                custo_peca_pedido,
                quantidade,
                calc,
            )

            if data_producao_dt:
                mes_key_utilizacao = data_producao_dt.strftime("%Y-%m")
                mes_label_utilizacao = rotulo_mes_dashboard(data_producao_dt)
                capacidade_mes_utilizacao = calendar.monthrange(data_producao_dt.year, data_producao_dt.month)[1] * 24
                chave_utilizacao = (mes_key_utilizacao, mes_label_utilizacao, impressora_key)

                if chave_utilizacao in utilizacao_impressoras_mes:
                    utilizacao_impressoras_mes[chave_utilizacao]["horas_usadas"] += calc["tempo_total"]
                    utilizacao_impressoras_mes[chave_utilizacao]["capacidade_horas"] = capacidade_mes_utilizacao
                    utilizacao_impressoras_mes[chave_utilizacao]["pedidos"] += 1

            pecas_key = f"{peca_codigo} - {peca_nome}"
            pecas_resumo[pecas_key]["quantidade"] += quantidade
            pecas_resumo[pecas_key]["faturamento"] += calc["total"]
            pecas_resumo[pecas_key]["lucro"] += calc["lucro"]

            clientes_key = f"{cliente_codigo} - {cliente_nome}"
            clientes_resumo[clientes_key]["pedidos"] += 1
            clientes_resumo[clientes_key]["faturamento"] += calc["total"]
            clientes_resumo[clientes_key]["lucro"] += calc["lucro"]

            impressoras_resumo[impressora_key]["pedidos"] += 1
            impressoras_resumo[impressora_key]["faturamento"] += calc["total"]
            impressoras_resumo[impressora_key]["lucro"] += calc["lucro"]
            impressoras_resumo[impressora_key]["horas"] += calc["tempo_total"]

            if data_pedido_dt:
                mes_key = data_pedido_dt.strftime("%Y-%m")
                vendas_mes_resumo[mes_key]["mes"] = rotulo_mes_dashboard(data_pedido_dt)
                vendas_mes_resumo[mes_key]["pedidos"] += 1
                vendas_mes_resumo[mes_key]["quantidade"] += quantidade
                vendas_mes_resumo[mes_key]["faturamento"] += calc["total"]
                vendas_mes_resumo[mes_key]["lucro"] += calc["lucro"]

        status_resumo[status]["pedidos"] += 1
        status_resumo[status]["faturamento"] += calc["total"] if status != "Cancelado" else 0
        status_resumo[status]["lucro"] += calc["lucro"] if status != "Cancelado" else 0

        if len(pedidos_recentes) < 5:
            pedidos_recentes.append([
                codigo,
                cliente_nome,
                peca_nome,
                f"{quantidade:.0f}",
                status,
                f"R$ {calc['total']:.2f}",
            ])

        if status not in ["Entregue", "Cancelado"] and len(pedidos_abertos_lista) < 8:
            pedidos_abertos_lista.append([
                codigo,
                peca_nome,
                f"{quantidade:.0f}",
                status,
                data_br(data_pedido),
            ])

    lucro_hora = lucro_total / horas_total if horas_total > 0 else 0
    margem_media = (lucro_total / faturamento_total) * 100 if faturamento_total > 0 else 0
    ticket_medio = faturamento_total / len(pedidos) if len(pedidos) > 0 else 0

    vendas_mes_grafico = []
    for mes_key, dados in sorted(vendas_mes_resumo.items())[-12:]:
        faturamento_mes_item = float(dados["faturamento"])
        lucro_mes_item = float(dados["lucro"])
        margem_mes_item = (lucro_mes_item / faturamento_mes_item * 100) if faturamento_mes_item > 0 else 0
        vendas_mes_grafico.append({
            "mes": dados["mes"],
            "pedidos": dados["pedidos"],
            "quantidade": dados["quantidade"],
            "faturamento": faturamento_mes_item,
            "lucro": lucro_mes_item,
            "margem": margem_mes_item,
        })

    utilizacao_impressoras_grafico = []
    for chave, dados in sorted(utilizacao_impressoras_mes.items(), key=lambda item: item[0][0]):
        mes_key, mes_label, impressora_nome = chave
        capacidade = dados["capacidade_horas"] if dados["capacidade_horas"] > 0 else capacidade_horas_mes
        horas_usadas = float(dados["horas_usadas"])
        utilizacao_percentual = (horas_usadas / capacidade) * 100 if capacidade > 0 else 0

        utilizacao_impressoras_grafico.append({
            "mes_key": mes_key,
            "mes": mes_label,
            "impressora": impressora_nome,
            "horas_usadas": horas_usadas,
            "capacidade_horas": capacidade,
            "utilizacao_percentual": utilizacao_percentual,
            "pedidos": dados["pedidos"],
        })

    ordem_distribuicao = [
        "Filamento",
        "Energia",
        "Depreciação",
        "Pós-processamento",
        "Acessórios",
        "Embalagem",
        "Custos",
        "Lucro",
        "Prejuízo",
    ]

    distribuicao_ordenada = {
        chave: float(distribuicao_faturamento.get(chave, 0))
        for chave in ordem_distribuicao
        if abs(float(distribuicao_faturamento.get(chave, 0))) > 0.005
    }

    return {
        "pedidos_abertos": pedidos_abertos,
        "faturamento_total": faturamento_total,
        "lucro_total": lucro_total,
        "horas_total": horas_total,
        "quantidade_total": quantidade_total,
        "pedidos_fechados_mes": pedidos_fechados_mes,
        "faturamento_mes": faturamento_mes,
        "lucro_mes": lucro_mes,
        "lucro_hora": lucro_hora,
        "margem_media": margem_media,
        "ticket_medio": ticket_medio,
        "status_resumo": status_resumo,
        "pecas_resumo": pecas_resumo,
        "clientes_resumo": clientes_resumo,
        "impressoras_resumo": impressoras_resumo,
        "vendas_mes_grafico": vendas_mes_grafico,
        "utilizacao_impressoras_grafico": utilizacao_impressoras_grafico,
        "pedidos_recentes": pedidos_recentes,
        "pedidos_abertos_lista": pedidos_abertos_lista,
        "distribuicao_faturamento": distribuicao_ordenada,
    }
