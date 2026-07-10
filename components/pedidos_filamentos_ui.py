"""
Componentes de interface para filamentos do pedido.

Este módulo concentra a seleção do rolo/material usado em um pedido.
A consulta e o cálculo de disponibilidade continuam em services/pedido_filamentos.py.
"""

import streamlit as st

from services.pedido_filamentos import (
    carregar_disponibilidade_filamentos,
    carregar_requisitos_filamentos_peca,
)


def montar_filamentos_pedido(peca_id, quantidade, prefixo, pedido_id_atual=None, registros_existentes=None):
    requisitos = carregar_requisitos_filamentos_peca(peca_id, quantidade)
    disponibilidade = carregar_disponibilidade_filamentos(pedido_id_atual)
    registros_existentes = registros_existentes or []

    if not requisitos:
        st.warning("Não foi possível identificar a necessidade de filamento desta peça.")
        return []

    if not disponibilidade:
        st.warning("Cadastre pelo menos um filamento ativo antes de confirmar o pedido.")
        return []

    labels = []
    por_label = {}

    for item in disponibilidade:
        label = (
            f"{item['codigo']} - {item['nome']} | "
            f"{item['material']} {item['cor']} | "
            f"disp. {item['disponivel']:.1f} g"
        )
        labels.append(label)
        por_label[label] = item

    registros_saida = []

    for idx, req in enumerate(requisitos):
        uso = req["uso"]
        peso_necessario = req["peso_pedido"] if req["peso_pedido"] else 0

        st.markdown(f"**{uso}**")
        st.caption(f"Necessário para este pedido: {peso_necessario:.1f} g")

        filamento_existente_id = None

        if idx < len(registros_existentes):
            filamento_existente_id = registros_existentes[idx][0]

        for reg in registros_existentes:
            if (reg[2] or "") == uso:
                filamento_existente_id = reg[0]
                break

        index_padrao = 0

        if filamento_existente_id:
            for pos, label in enumerate(labels):
                if por_label[label]["id"] == filamento_existente_id:
                    index_padrao = pos
                    break

        selecionado_label = st.selectbox(
            f"Filamento deste pedido - {uso}",
            labels,
            index=index_padrao,
            key=f"{prefixo}_filamento_real_{idx}",
            help="Escolha o rolo/material que será realmente usado neste pedido. Isso alimenta o controle de consumo em gramas."
        )

        selecionado = por_label[selecionado_label]
        disponivel = selecionado["disponivel"]
        saldo_apos_pedido = disponivel - peso_necessario

        st.caption(
            f"Disponível estimado: {disponivel:.1f} g · "
            f"Após este pedido: {saldo_apos_pedido:.1f} g"
        )

        if saldo_apos_pedido < 0:
            st.warning(
                f"Atenção: este filamento não tem saldo estimado suficiente. "
                f"Faltam {abs(saldo_apos_pedido):.1f} g."
            )

        registros_saida.append((
            selecionado["id"],
            peso_necessario,
            uso
        ))

    return registros_saida
