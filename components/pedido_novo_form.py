"""
Formulário de Novo Pedido.

Este componente concentra o fluxo guiado de cadastro de pedido.
A página `pages/5_Pedidos.py` fica responsável por orquestrar a tela,
e este arquivo cuida do formulário quando o usuário clica em `+ Novo Pedido`.
"""

from datetime import date

import streamlit as st

from components.button import primary_button
from components.kpi import kpi_card
from components.section import small_section
from components.pedidos_widgets import (
    moeda,
    pedido_mobile_step,
    render_conferencia_pedido_operador,
    render_novo_pedido_mobile_resumo,
)
from components.pedidos_filamentos_ui import montar_filamentos_pedido
from database import conectar
from services.pedido_custos import (
    calcular_pedido,
    carregar_custos_pedidos_cache,
)
from services.pedido_filamentos import salvar_filamentos_pedido
from services.pedido_validacoes import montar_alertas_pedido_operador
from services.pedidos import (
    STATUS_PEDIDOS,
    gerar_codigo_pedido,
    label_impressora,
)


def render_novo_pedido_form(
    *,
    pecas,
    clientes,
    impressoras_pedidos,
    energia_hora,
    depreciacao_hora,
    margem_padrao,
    meta_lucro_hora,
    custo_pos_processamento_hora,
    gerar_codigo_cliente_func,
    limpar_cache_dados_func,
):

    if not pecas:
        st.warning("Cadastre pelo menos uma peça antes de criar um pedido.")

    else:

        small_section("Novo Pedido")
        st.caption("Preencha as etapas em sequência. O sistema mostra alertas se encontrar algum ponto de atenção.")

        col_form, col_resumo = st.columns([2, 1])

        with col_form:

            pedido_mobile_step("1. Cliente", "Selecione um cliente existente ou cadastre rapidamente um novo.")

            clientes_opcoes = {f"{c[1]} - {c[2]}": c for c in clientes}
            opcao_novo_cliente = "+ Cadastrar novo cliente"
            cliente_labels = [opcao_novo_cliente] + list(clientes_opcoes.keys())

            cliente_selecionado = st.selectbox(
                "Cliente",
                cliente_labels,
                key="novo_pedido_cliente",
                help="Escolha um cliente já cadastrado ou use a primeira opção para cadastrar rapidamente um novo cliente."
            )

            cliente_dados = None
            novo_cliente_nome = ""
            novo_cliente_tipo = "Pessoa Física"
            novo_cliente_telefone = ""
            novo_cliente_email = ""
            novo_cliente_cidade = ""
            novo_cliente_estado = ""
            novo_cliente_origem = "WhatsApp"

            if cliente_selecionado == opcao_novo_cliente:
                with st.container(border=True):
                    small_section("Novo cliente rápido")

                    novo_cliente_nome = st.text_input(
                        "Nome do cliente",
                        key="pedido_novo_cliente_nome"
                    )

                    novo_cliente_tipo = st.selectbox(
                        "Tipo de cliente",
                        ["Pessoa Física", "Pessoa Jurídica"],
                        key="pedido_novo_cliente_tipo"
                    )

                    col_nc1, col_nc2 = st.columns(2)

                    with col_nc1:
                        novo_cliente_telefone = st.text_input(
                            "Telefone / WhatsApp",
                            key="pedido_novo_cliente_telefone"
                        )

                        novo_cliente_cidade = st.text_input(
                            "Cidade",
                            key="pedido_novo_cliente_cidade"
                        )

                    with col_nc2:
                        novo_cliente_email = st.text_input(
                            "E-mail",
                            key="pedido_novo_cliente_email"
                        )

                        novo_cliente_estado = st.text_input(
                            "Estado",
                            key="pedido_novo_cliente_estado"
                        )

                    novo_cliente_origem = st.selectbox(
                        "Origem do cliente",
                        [
                            "Indicação",
                            "Instagram",
                            "WhatsApp",
                            "Marketplace",
                            "Feira / Evento",
                            "Cliente recorrente",
                            "Outro"
                        ],
                        index=2,
                        key="pedido_novo_cliente_origem"
                    )
            else:
                cliente_dados = clientes_opcoes[cliente_selecionado]

            pedido_mobile_step("2. Filamento deste pedido", "Escolha a peça, informe a quantidade e confirme qual rolo/cor será usado.")

            pecas_opcoes = {f"{p[1]} - {p[2]}": p for p in pecas}
            peca_selecionada = st.selectbox(
                "Peça",
                list(pecas_opcoes.keys()),
                key="novo_pedido_peca",
                help="Escolha o produto vendido. O sistema usa o cadastro da peça para buscar custo, tempo, peso e preço sugerido."
            )
            peca_dados = pecas_opcoes[peca_selecionada]

            if impressoras_pedidos:
                impressora_labels = [label_impressora(i) for i in impressoras_pedidos]
                impressora_padrao_index = 0

                for idx_imp, impressora_item in enumerate(impressoras_pedidos):
                    if impressora_item[7]:
                        impressora_padrao_index = idx_imp
                        break

                impressora_selecionada_label = st.selectbox(
                    "Impressora",
                    impressora_labels,
                    index=impressora_padrao_index,
                    key="novo_pedido_impressora",
                    help="Escolha em qual impressora este pedido será produzido. O custo usa energia/hora e depreciação/hora desta impressora."
                )

                impressora_dados_pedido = impressoras_pedidos[impressora_labels.index(impressora_selecionada_label)]
                impressora_id_pedido = impressora_dados_pedido[0]
                energia_hora_pedido = impressora_dados_pedido[5] if impressora_dados_pedido[5] else energia_hora
                depreciacao_hora_pedido = impressora_dados_pedido[6] if impressora_dados_pedido[6] else depreciacao_hora
            else:
                impressora_dados_pedido = None
                impressora_id_pedido = None
                energia_hora_pedido = energia_hora
                depreciacao_hora_pedido = depreciacao_hora
                st.info("Nenhuma impressora ativa encontrada. O pedido usará a configuração padrão atual.")

            custo_ref = carregar_custos_pedidos_cache(
                tuple([peca_dados[0]]),
                energia_hora_pedido,
                depreciacao_hora_pedido,
                custo_pos_processamento_hora
            ).get(peca_dados[0], {
                "custo_unitario": 0,
                "peso_unitario": 0,
                "tempo_unitario": 0,
            })
            preco_sugerido = custo_ref["custo_unitario"] * (1 + margem_padrao / 100)

            if st.session_state.get("novo_pedido_peca_anterior") != peca_dados[0]:
                st.session_state["novo_pedido_valor_unitario"] = float(preco_sugerido)
                st.session_state["novo_pedido_peca_anterior"] = peca_dados[0]

            st.markdown(
                f"""
                <div style="
                    font-family:'Barlow', system-ui, sans-serif;
                    font-size:13px;
                    font-weight:500;
                    color:#5C6C74;
                    margin-top:4px;
                    margin-bottom:18px;
                ">
                    Valor sugerido para esta peça:
                    <strong>{moeda(preco_sugerido)}</strong> por unidade
                    <span style="color:#8A8F98;">
                        (custo unitário: {moeda(custo_ref['custo_unitario'])})
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

            quantidade = st.number_input(
                "Quantidade vendida",
                min_value=1.0,
                value=1.0,
                step=1.0,
                key="novo_pedido_quantidade",
                help="Informe quantas unidades o cliente comprou. O sistema usa esse número para calcular custo, lucro e consumo de filamento."
            )

            filamentos_pedido = montar_filamentos_pedido(
                peca_dados[0],
                quantidade,
                "novo_pedido"
            )

            pedido_mobile_step("3. Valores", "Ajuste venda, desconto e frete.")

            valor_unitario = st.number_input(
                "Valor unitário de venda (R$)",
                min_value=0.0,
                step=1.0,
                key="novo_pedido_valor_unitario",
                help="Preço cobrado por unidade. O sistema sugere um valor com base no custo e na margem configurada."
            )

            col_v1, col_v2 = st.columns(2)

            with col_v1:
                desconto = st.number_input(
                    "Desconto total (R$)",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    key="novo_pedido_desconto",
                    help="Informe o desconto total do pedido, não o desconto por unidade."
                )

            with col_v2:
                frete = st.number_input(
                    "Frete cobrado (R$)",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    key="novo_pedido_frete",
                    help="Valor de frete cobrado do cliente. Se não houver frete, deixe zero."
                )

            pedido_mobile_step("4. Acompanhamento", "Defina status, canal, datas e observações.")

            col_s1, col_s2 = st.columns(2)

            with col_s1:
                status = st.selectbox(
                    "Status do pedido",
                    STATUS_PEDIDOS,
                    key="novo_pedido_status",
                    help="Use Encomendado quando o cliente confirmou, Em Produção quando já começou, Pronto quando terminou e Entregue quando foi concluído."
                )

                canal = st.selectbox(
                    "Canal",
                    ["WhatsApp", "Instagram", "Marketplace", "Indicação", "Feira / Evento", "Outro"],
                    key="novo_pedido_canal",
                    help="Informe por onde este pedido chegou. Isso ajuda a entender quais canais geram mais vendas."
                )

            with col_s2:
                data_pedido = st.date_input("Data do pedido", value=date.today(), format="DD/MM/YYYY", key="novo_pedido_data")
                data_entrega = st.date_input("Entrega prevista", value=date.today(), format="DD/MM/YYYY", key="novo_pedido_entrega")

            observacoes = st.text_area(
                "Observações",
                key="novo_pedido_observacoes",
                help="Use este campo para registrar combinados, preferências do cliente, cor especial, prazo ou detalhes da entrega."
            )

        calc = calcular_pedido(peca_dados[0], quantidade, valor_unitario, desconto, frete, energia_hora_pedido, depreciacao_hora_pedido, custo_ref)
        tempo_total_estimado_novo = calc["tempo_unitario"] * quantidade
        lucro_hora_novo = calc["lucro"] / tempo_total_estimado_novo if tempo_total_estimado_novo > 0 else 0

        cliente_nome_conferencia = novo_cliente_nome if cliente_selecionado == opcao_novo_cliente else cliente_dados[2]
        if not cliente_nome_conferencia:
            cliente_nome_conferencia = "Novo cliente ainda sem nome"

        alertas_pedido_operador = montar_alertas_pedido_operador(
            cliente_selecionado=cliente_selecionado,
            opcao_novo_cliente=opcao_novo_cliente,
            novo_cliente_nome=novo_cliente_nome,
            filamentos_pedido=filamentos_pedido,
            calc=calc,
            valor_unitario=valor_unitario,
            quantidade=quantidade,
            lucro_hora=lucro_hora_novo,
            meta_lucro_hora=meta_lucro_hora,
            tempo_total_estimado=tempo_total_estimado_novo,
            desconto=desconto,
            frete=frete,
        )

        if lucro_hora_novo >= meta_lucro_hora:
            cor_lucro_hora_novo = "green"
            status_lucro_hora_novo = "acima da meta"
        elif lucro_hora_novo >= meta_lucro_hora * 0.6:
            cor_lucro_hora_novo = "orange"
            status_lucro_hora_novo = "atenção"
        else:
            cor_lucro_hora_novo = "red"
            status_lucro_hora_novo = "abaixo da meta"

        with col_resumo:

            with st.container(key="novo_pedido_resumo_mobile"):
                render_novo_pedido_mobile_resumo(calc, preco_sugerido, margem_padrao)

            with st.container(key="novo_pedido_resumo_desktop"):
                small_section("Resumo")

                kpi_card("Custo unitário", moeda(calc["custo_unitario"]), "referência da peça", "orange")
                kpi_card("Venda sugerida", moeda(preco_sugerido), f"margem {margem_padrao:.0f}%", "green")
                kpi_card("Subtotal", moeda(calc["subtotal"]), "quantidade x valor", "blue")
                kpi_card("Total pedido", moeda(calc["total"]), "com desconto e frete", "green")
                kpi_card("Lucro", moeda(calc["lucro"]), "estimado no pedido", "green")
                kpi_card("Lucro unitário", moeda(calc["lucro_unitario"]), f"{calc['lucro_percentual']:.0f}% sobre custo", "gray")
                if impressora_dados_pedido:
                    kpi_card("Impressora", impressora_dados_pedido[1], f"{impressora_dados_pedido[2]} {impressora_dados_pedido[3]}", "blue")
                kpi_card(
                    "Lucro por hora",
                    f"R$ {lucro_hora_novo:.2f}/h".replace(".", ","),
                    status_lucro_hora_novo,
                    cor_lucro_hora_novo
                )

                render_conferencia_pedido_operador(
                    cliente_nome=cliente_nome_conferencia,
                    peca_nome=peca_selecionada,
                    quantidade=quantidade,
                    status=status,
                    canal=canal,
                    data_entrega=data_entrega,
                    filamentos_pedido=filamentos_pedido,
                    calc=calc,
                    lucro_hora=lucro_hora_novo,
                    alertas=alertas_pedido_operador,
                )

        if primary_button("Salvar Pedido", "salvar_novo_pedido"):

            if cliente_selecionado == opcao_novo_cliente and not novo_cliente_nome:
                st.warning("Informe o nome do novo cliente.")

            elif not filamentos_pedido:
                st.warning("Selecione o filamento deste pedido.")

            else:
                conn = conectar()

                if cliente_selecionado == opcao_novo_cliente:
                    codigo_cliente = gerar_codigo_cliente_func(conn)

                    cursor_cliente = conn.execute("""
                    INSERT INTO clientes
                    (
                        codigo,
                        nome,
                        tipo,
                        telefone,
                        email,
                        cidade,
                        estado,
                        origem,
                        status,
                        data_cadastro
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        codigo_cliente,
                        novo_cliente_nome,
                        novo_cliente_tipo,
                        novo_cliente_telefone,
                        novo_cliente_email,
                        novo_cliente_cidade,
                        novo_cliente_estado,
                        novo_cliente_origem,
                        "Ativo",
                        str(date.today())
                    ))

                    cliente_id_para_salvar = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                else:
                    cliente_id_para_salvar = cliente_dados[0]

                codigo = gerar_codigo_pedido(conn)

                conn.execute("""
                INSERT INTO pedidos
                (
                    codigo,
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
                    observacoes,
                    impressora_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    codigo,
                    cliente_id_para_salvar,
                    peca_dados[0],
                    quantidade,
                    valor_unitario,
                    desconto,
                    frete,
                    status,
                    canal,
                    str(data_pedido),
                    str(data_entrega),
                    observacoes,
                    impressora_id_pedido,
                ))

                pedido_id_salvo = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                salvar_filamentos_pedido(conn, pedido_id_salvo, filamentos_pedido)

                conn.commit()
                conn.close()

                st.success(f"Pedido {codigo} cadastrado com sucesso! Próximo passo: acompanhar o status na lista de pedidos.")
                st.session_state["mostrar_form_pedido"] = False
                limpar_cache_dados_func()
                st.rerun()
