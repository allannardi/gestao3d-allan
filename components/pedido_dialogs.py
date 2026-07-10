"""
Dialogs da tela Pedidos.

Este módulo concentra os modais de edição e duplicação de pedido.
A página `pages/5_Pedidos.py` chama esses dialogs, mas não precisa mais carregar
todo o código interno de edição/duplicação.
"""

from datetime import date

import streamlit as st

from components.button import primary_button, secondary_button
from components.formatters import data_br, data_para_date
from components.pedidos_filamentos_ui import montar_filamentos_pedido
from components.section import small_section
from database import conectar
from services.pedido_filamentos import (
    carregar_filamentos_pedido_registros,
    salvar_filamentos_pedido,
)
from services.pedido_dados import gerar_codigo_cliente
from services.pedidos import (
    STATUS_PEDIDOS,
    carregar_clientes,
    carregar_impressoras_pedidos,
    carregar_pecas,
    gerar_codigo_pedido,
    label_impressora,
)


def _limpar_cache_dados():
    try:
        st.cache_data.clear()
    except Exception:
        pass


@st.dialog("Duplicar Pedido", width="large")
def duplicar_pedido_dialog(pedido_id):
    conn = conectar()
    pedido = conn.execute("""
    SELECT cliente_id, peca_id, quantidade, valor_unitario, desconto, frete, canal, data_entrega_prevista, observacoes, impressora_id
    FROM pedidos
    WHERE id = ?
    """, (pedido_id,)).fetchone()
    conn.close()

    if pedido is None:
        st.warning("Pedido não encontrado.")
        return

    st.caption("Escolha se o pedido duplicado será para o mesmo cliente, outro cliente ou um novo cliente.")
    clientes_atualizados = carregar_clientes()
    modo_cliente = st.radio(
        "Cliente do novo pedido",
        ["Mesmo cliente", "Selecionar outro cliente", "Cadastrar novo cliente"],
        horizontal=True,
        key=f"duplicar_modo_cliente_{pedido_id}"
    )

    cliente_id_para_salvar = pedido[0]
    novo_cliente_nome = ""
    novo_cliente_tipo = "Pessoa Física"
    novo_cliente_telefone = ""
    novo_cliente_email = ""
    novo_cliente_cidade = ""
    novo_cliente_estado = ""
    novo_cliente_origem = "WhatsApp"

    if modo_cliente == "Selecionar outro cliente":
        if not clientes_atualizados:
            st.warning("Não há clientes ativos cadastrados.")
        else:
            clientes_opcoes = {f"{c[1]} - {c[2]}": c for c in clientes_atualizados}
            cliente_label = st.selectbox("Cliente", list(clientes_opcoes.keys()), key=f"duplicar_cliente_existente_{pedido_id}")
            cliente_id_para_salvar = clientes_opcoes[cliente_label][0]

    if modo_cliente == "Cadastrar novo cliente":
        with st.container(border=True):
            small_section("Novo cliente rápido")
            novo_cliente_nome = st.text_input("Nome do cliente", key=f"duplicar_novo_cliente_nome_{pedido_id}")
            novo_cliente_tipo = st.selectbox("Tipo", ["Pessoa Física", "Pessoa Jurídica"], key=f"duplicar_novo_cliente_tipo_{pedido_id}")
            col_nc1, col_nc2 = st.columns(2)
            with col_nc1:
                novo_cliente_telefone = st.text_input("Telefone / WhatsApp", key=f"duplicar_novo_cliente_tel_{pedido_id}")
                novo_cliente_cidade = st.text_input("Cidade", key=f"duplicar_novo_cliente_cidade_{pedido_id}")
            with col_nc2:
                novo_cliente_email = st.text_input("E-mail", key=f"duplicar_novo_cliente_email_{pedido_id}")
                novo_cliente_estado = st.text_input("Estado", key=f"duplicar_novo_cliente_estado_{pedido_id}")
            novo_cliente_origem = st.selectbox(
                "Origem",
                ["Indicação", "Instagram", "WhatsApp", "Marketplace", "Feira / Evento", "Cliente recorrente", "Outro"],
                index=2,
                key=f"duplicar_novo_cliente_origem_{pedido_id}"
            )

    col_a, col_b = st.columns(2)
    with col_a:
        confirmar = primary_button("Criar pedido duplicado", f"confirmar_duplicar_pedido_{pedido_id}")
    with col_b:
        cancelar = secondary_button("Cancelar", f"cancelar_duplicar_pedido_{pedido_id}")

    if cancelar:
        _limpar_cache_dados()
        st.rerun()
    if confirmar:
        if modo_cliente == "Cadastrar novo cliente" and not novo_cliente_nome:
            st.warning("Informe o nome do novo cliente.")
            return
        conn = conectar()
        if modo_cliente == "Cadastrar novo cliente":
            codigo_cliente = gerar_codigo_cliente(conn)
            conn.execute("""
            INSERT INTO clientes (codigo, nome, tipo, telefone, email, cidade, estado, origem, status, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (codigo_cliente, novo_cliente_nome, novo_cliente_tipo, novo_cliente_telefone, novo_cliente_email, novo_cliente_cidade, novo_cliente_estado, novo_cliente_origem, "Ativo", str(date.today())))
            cliente_id_para_salvar = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        codigo = gerar_codigo_pedido(conn)
        conn.execute("""
        INSERT INTO pedidos (codigo, cliente_id, peca_id, quantidade, valor_unitario, desconto, frete, status, canal, data_pedido, data_entrega_prevista, observacoes, impressora_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (codigo, cliente_id_para_salvar, pedido[1], pedido[2], pedido[3], pedido[4], pedido[5], "Orçamento", pedido[6], str(date.today()), pedido[7], pedido[8], pedido[9]))
        novo_pedido_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        filamentos_original = conn.execute("""
        SELECT
            filamento_id,
            COALESCE(peso_g, 0),
            COALESCE(observacao, '')
        FROM pedido_filamentos
        WHERE pedido_id = ?
        ORDER BY id ASC
        """, (pedido_id,)).fetchall()

        salvar_filamentos_pedido(conn, novo_pedido_id, filamentos_original)

        conn.commit()
        conn.close()
        st.success("Pedido duplicado com sucesso!")
        _limpar_cache_dados()
        st.rerun()


@st.dialog("Editar Pedido", width="large")
def editar_pedido_dialog(pedido_id):
    conn = conectar()

    pedido = conn.execute("""
    SELECT
        id,
        cliente_id,
        peca_id,
        quantidade,
        valor_unitario,
        desconto,
        frete,
        status,
        canal,
        data_pedido,
        data_entrega_prevista,
        data_final_producao,
        data_entrega_real,
        observacoes,
        impressora_id
    FROM pedidos
    WHERE id = ?
    """, (pedido_id,)).fetchone()

    conn.close()

    if pedido is None:
        st.warning("Pedido não encontrado.")
        if st.button("Fechar", key=f"fechar_modal_pedido_{pedido_id}"):
            _limpar_cache_dados()
            st.rerun()
        return

    clientes_atualizados = carregar_clientes()
    pecas_atualizadas = carregar_pecas()
    filamentos_pedido_existentes = carregar_filamentos_pedido_registros(pedido_id)
    impressoras_editaveis = carregar_impressoras_pedidos()

    if not clientes_atualizados:
        st.warning("Cadastre pelo menos um cliente ativo antes de editar o pedido.")
        if st.button("Fechar", key=f"fechar_modal_sem_cliente_{pedido_id}"):
            _limpar_cache_dados()
            st.rerun()
        return

    if not pecas_atualizadas:
        st.warning("Cadastre pelo menos uma peça antes de editar o pedido.")
        if st.button("Fechar", key=f"fechar_modal_sem_peca_{pedido_id}"):
            _limpar_cache_dados()
            st.rerun()
        return

    st.caption("Atualize as informações comerciais e o status do pedido.")

    clientes_opcoes_edit = {f"{c[1]} - {c[2]}": c for c in clientes_atualizados}
    pecas_opcoes_edit = {f"{p[1]} - {p[2]}": p for p in pecas_atualizadas}

    cliente_labels = list(clientes_opcoes_edit.keys())
    peca_labels = list(pecas_opcoes_edit.keys())

    cliente_index = 0
    for idx, label in enumerate(cliente_labels):
        if clientes_opcoes_edit[label][0] == pedido[1]:
            cliente_index = idx

    peca_index = 0
    for idx, label in enumerate(peca_labels):
        if pecas_opcoes_edit[label][0] == pedido[2]:
            peca_index = idx

    with st.form(f"editar_pedido_form_{pedido_id}"):

        cliente_edit_label = st.selectbox(
            "Cliente",
            cliente_labels,
            index=cliente_index,
            key=f"modal_cliente_{pedido_id}"
        )

        peca_edit_label = st.selectbox(
            "Peça",
            peca_labels,
            index=peca_index,
            key=f"modal_peca_{pedido_id}"
        )

        impressora_edit_id = None

        if impressoras_editaveis:
            impressora_labels_edit = [label_impressora(i) for i in impressoras_editaveis]
            impressora_index = 0

            for idx_imp, impressora_item in enumerate(impressoras_editaveis):
                if impressora_item[0] == pedido[14]:
                    impressora_index = idx_imp
                    break
                if pedido[14] is None and impressora_item[7]:
                    impressora_index = idx_imp

            impressora_edit_label = st.selectbox(
                "Impressora",
                impressora_labels_edit,
                index=impressora_index,
                key=f"modal_impressora_{pedido_id}",
                help="Escolha a impressora usada neste pedido."
            )
            impressora_edit_id = impressoras_editaveis[impressora_labels_edit.index(impressora_edit_label)][0]

        col_e1, col_e2 = st.columns(2)

        with col_e1:
            quantidade_edit = st.number_input(
                "Quantidade vendida",
                min_value=1.0,
                value=float(pedido[3] if pedido[3] else 1),
                step=1.0,
                key=f"modal_quantidade_{pedido_id}"
            )

            desconto_edit = st.number_input(
                "Desconto total (R$)",
                min_value=0.0,
                value=float(pedido[5] if pedido[5] else 0),
                step=1.0,
                key=f"modal_desconto_{pedido_id}"
            )

            status_lista = STATUS_PEDIDOS

            status_edit = st.selectbox(
                "Status",
                status_lista,
                index=status_lista.index(pedido[7]) if pedido[7] in status_lista else 0,
                key=f"modal_status_{pedido_id}"
            )

            data_pedido_edit = st.text_input(
                "Data do pedido",
                value=data_br(pedido[9]) if pedido[9] else "",
                key=f"modal_data_pedido_{pedido_id}"
            )

        with col_e2:
            valor_unitario_edit = st.number_input(
                "Valor unitário de venda (R$)",
                min_value=0.0,
                value=float(pedido[4] if pedido[4] else 0),
                step=1.0,
                key=f"modal_valor_unitario_{pedido_id}"
            )

            frete_edit = st.number_input(
                "Frete cobrado (R$)",
                min_value=0.0,
                value=float(pedido[6] if pedido[6] else 0),
                step=1.0,
                key=f"modal_frete_{pedido_id}"
            )

            canais_lista = ["WhatsApp", "Instagram", "Marketplace", "Indicação", "Feira / Evento", "Outro"]

            canal_edit = st.selectbox(
                "Canal",
                canais_lista,
                index=canais_lista.index(pedido[8]) if pedido[8] in canais_lista else 0,
                key=f"modal_canal_{pedido_id}"
            )

            data_entrega_edit = st.text_input(
                "Entrega prevista",
                value=data_br(pedido[10]) if pedido[10] else "",
                key=f"modal_data_entrega_{pedido_id}"
            )

        data_final_producao_edit = pedido[11] or ""
        data_entrega_real_edit = pedido[12] or ""

        if status_edit in ["Pronto", "Entregue"] or pedido[11]:
            data_final_producao_data = st.date_input(
                "Data Final Produção",
                value=data_para_date(pedido[11]) or date.today(),
                format="DD/MM/YYYY",
                key=f"modal_data_final_producao_{pedido_id}",
                help="Data em que a produção foi finalizada. Usada no gráfico de utilização da impressora."
            )
            data_final_producao_edit = str(data_final_producao_data)

        if status_edit == "Entregue" or pedido[12]:
            data_entrega_real_data = st.date_input(
                "Data da Entrega",
                value=data_para_date(pedido[12]) or date.today(),
                format="DD/MM/YYYY",
                key=f"modal_data_entrega_real_{pedido_id}",
                help="Data real em que o pedido foi entregue ao cliente."
            )
            data_entrega_real_edit = str(data_entrega_real_data)

        observacoes_edit = st.text_area(
            "Observações",
            value=pedido[13] if pedido[13] else "",
            key=f"modal_observacoes_{pedido_id}"
        )

        small_section("Filamento deste pedido")
        peca_edit_para_filamento = pecas_opcoes_edit[peca_edit_label]
        filamentos_pedido_edit = montar_filamentos_pedido(
            peca_edit_para_filamento[0],
            quantidade_edit,
            f"editar_pedido_{pedido_id}",
            pedido_id_atual=pedido_id,
            registros_existentes=filamentos_pedido_existentes
        )

        salvar_edicao = st.form_submit_button("Salvar Alterações")

    if salvar_edicao:

        if not filamentos_pedido_edit:
            st.warning("Selecione o filamento deste pedido.")
            return

        cliente_edit = clientes_opcoes_edit[cliente_edit_label]
        peca_edit = pecas_opcoes_edit[peca_edit_label]

        conn = conectar()

        conn.execute("""
        UPDATE pedidos
        SET
            cliente_id = ?,
            peca_id = ?,
            quantidade = ?,
            valor_unitario = ?,
            desconto = ?,
            frete = ?,
            status = ?,
            canal = ?,
            data_pedido = ?,
            data_entrega_prevista = ?,
            data_final_producao = ?,
            data_entrega_real = ?,
            observacoes = ?,
            impressora_id = ?
        WHERE id = ?
        """,
        (
            cliente_edit[0],
            peca_edit[0],
            quantidade_edit,
            valor_unitario_edit,
            desconto_edit,
            frete_edit,
            status_edit,
            canal_edit,
            data_pedido_edit,
            data_entrega_edit,
            data_final_producao_edit,
            data_entrega_real_edit,
            observacoes_edit,
            impressora_edit_id,
            pedido_id,
        ))

        salvar_filamentos_pedido(conn, pedido_id, filamentos_pedido_edit)

        conn.commit()
        conn.close()

        st.success("Pedido atualizado!")
        _limpar_cache_dados()
        st.rerun()

    if st.button("Cancelar", key=f"cancelar_modal_pedido_{pedido_id}"):
        _limpar_cache_dados()
        st.rerun()
