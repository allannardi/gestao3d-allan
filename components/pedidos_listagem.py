"""
Listagem visual da tela Pedidos.

Este componente concentra:
- cálculo dos custos apenas dos pedidos visíveis;
- cards dos pedidos;
- alteração rápida de status;
- detalhes financeiros;
- ações de editar, duplicar e excluir.

A página `pages/5_Pedidos.py` fica responsável por filtros e paginação.
"""

from datetime import date

import streamlit as st

from components.button import secondary_button, danger_button
from components.formatters import data_br
from components.pedidos_widgets import moeda, pedido_card
from components.section import small_section
from database import conectar
from services.pedido_custos import (
    calcular_pedido,
    carregar_custos_pedidos_cache,
)
from services.pedidos import STATUS_PEDIDOS, resumo_prazo_entrega


def render_listagem_pedidos(
    *,
    pedidos,
    filamentos_pedidos,
    energia_hora,
    depreciacao_hora,
    custo_pos_processamento_hora,
    meta_lucro_hora,
    atualizar_status_pedido_func,
    limpar_cache_dados_func,
    editar_pedido_dialog_func,
    duplicar_pedido_dialog_func,
):
    # Performance:
    # A partir daqui calculamos custos apenas dos pedidos visíveis na página atual.
    # Antes, o sistema calculava custos de todos os pedidos filtrados antes da paginação.
    custos_pecas_pedidos = {}

    for pedido_custo in pedidos:
        peca_id_custo = pedido_custo[5]
        if not peca_id_custo:
            continue

        energia_pedido_custo = pedido_custo[23] if len(pedido_custo) > 23 and pedido_custo[23] is not None else energia_hora
        depreciacao_pedido_custo = pedido_custo[24] if len(pedido_custo) > 24 and pedido_custo[24] is not None else depreciacao_hora
        chave_custo = (
            peca_id_custo,
            round(float(energia_pedido_custo), 6),
            round(float(depreciacao_pedido_custo), 6),
        )

        if chave_custo not in custos_pecas_pedidos:
            custos_pecas_pedidos[chave_custo] = carregar_custos_pedidos_cache(
                tuple([peca_id_custo]),
                energia_pedido_custo,
                depreciacao_pedido_custo,
                custo_pos_processamento_hora
            ).get(peca_id_custo)


    for pedido in pedidos:

        pedido_id = pedido[0]
        codigo = pedido[1]
        cliente_id = pedido[2]
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
        canal = pedido[13] if pedido[13] else "-"
        data_pedido = data_br(pedido[14])
        data_entrega = data_br(pedido[15])
        data_final_producao = data_br(pedido[16])
        data_entrega_real = data_br(pedido[17])
        observacoes = pedido[18] if pedido[18] else ""
        impressora_id = pedido[19] if len(pedido) > 19 else None
        impressora_codigo = pedido[20] if len(pedido) > 20 and pedido[20] else "-"
        impressora_marca = pedido[21] if len(pedido) > 21 and pedido[21] else ""
        impressora_modelo = pedido[22] if len(pedido) > 22 and pedido[22] else ""
        energia_pedido = pedido[23] if len(pedido) > 23 and pedido[23] is not None else energia_hora
        depreciacao_pedido = pedido[24] if len(pedido) > 24 and pedido[24] is not None else depreciacao_hora
        impressora_nome = f"{impressora_codigo} - {impressora_marca} {impressora_modelo}".strip() if impressora_id else "Impressora padrão"
        chave_custo_pedido = (
            peca_id,
            round(float(energia_pedido), 6),
            round(float(depreciacao_pedido), 6),
        )

        calc = calcular_pedido(peca_id, quantidade, valor_unitario, desconto, frete, energia_pedido, depreciacao_pedido, custos_pecas_pedidos.get(chave_custo_pedido))
        margem_lucro = (calc["lucro"] / calc["total"]) * 100 if calc["total"] > 0 else 0
        tempo_total_estimado = calc["tempo_unitario"] * quantidade
        lucro_hora = calc["lucro"] / tempo_total_estimado if tempo_total_estimado > 0 else 0

        if lucro_hora >= meta_lucro_hora:
            cor_lucro_hora = "green"
            status_lucro_hora = "acima da meta"
        elif lucro_hora >= meta_lucro_hora * 0.6:
            cor_lucro_hora = "orange"
            status_lucro_hora = "atenção"
        else:
            cor_lucro_hora = "red"
            status_lucro_hora = "abaixo da meta"

        if margem_lucro >= 40:
            cor_margem = "green"
        elif margem_lucro >= 20:
            cor_margem = "orange"
        else:
            cor_margem = "red"

        with st.container(border=True):

            pedido_card(
                codigo=codigo,
                cliente_nome=cliente_nome,
                peca_codigo=peca_codigo,
                peca_nome=peca_nome,
                quantidade=quantidade,
                status=status,
                total=calc["total"],
                data_pedido=data_pedido,
                lucro=calc["lucro"],
                margem_lucro=margem_lucro,
                lucro_hora=lucro_hora,
            )

            status_rapido_key = f"pedido_status_rapido_{pedido_id}"
            status_atual_key = f"{status_rapido_key}_status_atual"

            if (
                st.session_state.get(status_atual_key) != status
                or st.session_state.get(status_rapido_key) not in STATUS_PEDIDOS
            ):
                st.session_state[status_rapido_key] = status
                st.session_state[status_atual_key] = status

            col_status_1, col_status_2 = st.columns([3, 1])

            with col_status_1:
                novo_status_rapido = st.selectbox(
                    "Alterar status sem abrir detalhes",
                    STATUS_PEDIDOS,
                    key=status_rapido_key
                )

            data_final_producao_status = None
            data_entrega_real_status = None

            if status == "Em Produção" and novo_status_rapido == "Pronto":
                data_final_producao_status = st.date_input(
                    "Data Final Produção",
                    value=date.today(),
                    format="DD/MM/YYYY",
                    key=f"data_final_producao_status_{pedido_id}",
                    help="Informe a data em que a produção foi finalizada."
                )

            if status == "Pronto" and novo_status_rapido == "Entregue":
                data_entrega_real_status = st.date_input(
                    "Data da Entrega",
                    value=date.today(),
                    format="DD/MM/YYYY",
                    key=f"data_entrega_real_status_{pedido_id}",
                    help="Informe a data real em que o pedido foi entregue."
                )

            with col_status_2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

                if st.button(
                    "Salvar status",
                    key=f"salvar_status_rapido_{pedido_id}",
                    use_container_width=True,
                    disabled=(novo_status_rapido == status)
                ):
                    atualizar_status_pedido_func(
                        pedido_id,
                        novo_status_rapido,
                        data_final_producao=str(data_final_producao_status) if data_final_producao_status else None,
                        data_entrega_real=str(data_entrega_real_status) if data_entrega_real_status else None,
                    )
                    st.session_state[status_atual_key] = novo_status_rapido
                    st.success(f"Status do pedido {codigo} atualizado para {novo_status_rapido}.")
                    st.rerun()

            with st.expander("Detalhes, valores e ações"):

                col_d1, col_d2, col_d3, col_d4 = st.columns(4)

                with col_d1:
                    st.write(f"**Status:** {status}")
                    st.write(f"**Canal:** {canal}")

                with col_d2:
                    st.write(f"**Cliente:** {cliente_codigo}")
                    st.write(f"**Peça:** {peca_codigo}")

                with col_d3:
                    st.write(f"**Quantidade:** {quantidade:.0f}")
                    st.write(f"**Valor unitário:** {moeda(valor_unitario)}")

                with col_d4:
                    st.write(f"**Data pedido:** {data_pedido}")
                    st.write(f"**Entrega prevista:** {data_entrega}")

                col_data1, col_data2 = st.columns(2)

                with col_data1:
                    st.write(f"**Data Final Produção:** {data_final_producao if data_final_producao else '-'}")

                with col_data2:
                    st.write(f"**Data da Entrega:** {data_entrega_real if data_entrega_real else '-'}")

                prazo_entrega = resumo_prazo_entrega(pedido[15], pedido[17])
                if prazo_entrega:
                    st.caption(prazo_entrega)

                st.write(f"**Impressora:** {impressora_nome}")

                filamentos_pedido_detalhe = filamentos_pedidos.get(pedido_id, [])

                if filamentos_pedido_detalhe:
                    small_section("Filamento deste pedido")

                    for filamento in filamentos_pedido_detalhe:
                        peso_filamento = filamento[4] if filamento[4] else 0
                        observacao_filamento = filamento[5] if filamento[5] else "-"
                        st.write(
                            f"- **{filamento[0]} - {filamento[1]}** | "
                            f"{filamento[2]} {filamento[3]} | "
                            f"{peso_filamento:.1f} g | {observacao_filamento}"
                        )
                else:
                    st.caption("Este pedido ainda não possui filamento deste pedido confirmado.")

                small_section("Dados unitários da peça")

                col_u1, col_u2, col_u3, col_u4 = st.columns(4)

                with col_u1:
                    st.write(f"**Peso unitário estimado:** {calc['peso_unitario']:.1f} g")

                with col_u2:
                    st.write(f"**Tempo total unitário estimado:** {calc['tempo_unitario']:.2f} h")

                with col_u3:
                    st.write(f"**Custo unitário:** {moeda(calc['custo_unitario'])}")

                with col_u4:
                    st.write(f"**Lucro unitário:** {moeda(calc['lucro_unitario'])}")

                small_section("Resumo financeiro")

                col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)

                with col_f1:
                    st.write(f"**Subtotal:** {moeda(calc['subtotal'])}")

                with col_f2:
                    st.write(f"**Desconto:** {moeda(desconto)}")

                with col_f3:
                    st.write(f"**Frete:** {moeda(frete)}")

                with col_f4:
                    st.write(f"**Custo:** {moeda(calc['custo_total'])}")

                with col_f5:
                    st.write(f"**Total:** {moeda(calc['total'])}")

                if observacoes:
                    st.write(f"**Observações:** {observacoes}")

                col_btn1, col_btn2, col_btn3 = st.columns(3)

                with col_btn1:
                    if secondary_button("Editar", f"editar_pedido_{pedido_id}"):
                        editar_pedido_dialog_func(pedido_id)

                with col_btn2:
                    if secondary_button("Duplicar", f"duplicar_pedido_{pedido_id}"):
                        duplicar_pedido_dialog_func(pedido_id)

                with col_btn3:
                    if danger_button("Excluir", f"excluir_pedido_{pedido_id}"):
                        conn = conectar()
                        conn.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
                        conn.commit()
                        conn.close()
                        limpar_cache_dados_func()
                        st.rerun()

        st.write("")
