"""
Validações operacionais da tela Pedidos.

Este service concentra alertas e regras de conferência antes de salvar um pedido.
"""


def _moeda_md(valor):
    return f"R$ {valor:.2f}".replace(".", ",").replace("$", "\\$")


def montar_alertas_pedido_operador(
    cliente_selecionado,
    opcao_novo_cliente,
    novo_cliente_nome,
    filamentos_pedido,
    calc,
    valor_unitario,
    quantidade,
    lucro_hora,
    meta_lucro_hora,
    tempo_total_estimado,
    desconto,
    frete,
):
    alertas = []

    if cliente_selecionado == opcao_novo_cliente and not novo_cliente_nome:
        alertas.append("Informe o nome do novo cliente antes de salvar.")

    if not filamentos_pedido:
        alertas.append("Selecione o filamento/rolo usado neste pedido.")

    if quantidade <= 0:
        alertas.append("Informe a quantidade vendida.")

    if valor_unitario <= 0:
        alertas.append("Informe o valor unitário de venda.")

    if calc["custo_unitario"] <= 0:
        alertas.append("A peça está sem custo calculado. Confira peso, tempo, filamento e acessórios no cadastro da peça.")

    if calc["tempo_unitario"] <= 0:
        alertas.append("A peça está sem tempo calculado. Confira o tempo de impressão no cadastro da peça.")

    if calc["lucro"] < 0:
        alertas.append(f"Este pedido está com prejuízo estimado de {_moeda_md(abs(calc['lucro']))}.")

    elif tempo_total_estimado > 0 and meta_lucro_hora > 0 and lucro_hora < meta_lucro_hora:
        preco_minimo_meta = (
            calc["custo_total"] + (meta_lucro_hora * tempo_total_estimado) + desconto - frete
        ) / quantidade if quantidade > 0 else 0

        if preco_minimo_meta > valor_unitario:
            alertas.append(
                f"Lucro por hora abaixo da meta. Para atingir a meta, o preço mínimo estimado seria {_moeda_md(preco_minimo_meta)} por unidade."
            )
        else:
            alertas.append("Lucro por hora abaixo da meta configurada.")

    return alertas
