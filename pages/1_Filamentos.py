import streamlit as st
from datetime import date

from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.mobile_summary import mobile_summary_css, render_mobile_summary
from components.header import header
from components.kpi import kpi_card
from components.card import item_card
from components.button import primary_button, secondary_button, danger_button
from components.searchbar import searchbar
from components.section import section_title, small_section
from components.item_results import carregar_resultados_filamento
from components.auth import require_login
from database import conectar, inicializar_banco



def moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def moeda_md(valor):
    return moeda(valor).replace("$", "\\$")


def garantir_colunas_filamentos():
    conn = conectar()
    colunas = conn.execute("PRAGMA table_info(filamentos)").fetchall()
    nomes_colunas = [coluna[1] for coluna in colunas]

    if "status" not in nomes_colunas:
        conn.execute("ALTER TABLE filamentos ADD COLUMN status TEXT DEFAULT 'Ativo'")

    if "data_finalizacao" not in nomes_colunas:
        conn.execute("ALTER TABLE filamentos ADD COLUMN data_finalizacao TEXT")

    conn.commit()
    conn.close()


def gerar_codigo_filamento(conn):
    ultimo = conn.execute("""
        SELECT MAX(id)
        FROM filamentos
    """).fetchone()[0]

    proximo = 1 if ultimo is None else ultimo + 1
    return f"FIL-{proximo:04d}"


def duplicar_filamento(filamento_id):
    conn = conectar()

    filamento = conn.execute("""
    SELECT
        nome,
        material,
        marca,
        cor,
        peso_original,
        valor_compra,
        fornecedor,
        observacoes
    FROM filamentos
    WHERE id = ?
    """, (filamento_id,)).fetchone()

    if filamento is None:
        conn.close()
        return None

    codigo = gerar_codigo_filamento(conn)
    custo_grama = filamento[5] / filamento[4] if filamento[4] else 0

    cursor = conn.execute("""
    INSERT INTO filamentos
    (
        codigo,
        nome,
        material,
        marca,
        cor,
        peso_original,
        valor_compra,
        fornecedor,
        data_compra,
        observacoes,
        custo_grama,
        status,
        data_finalizacao
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        codigo,
        filamento[0],
        filamento[1],
        filamento[2],
        filamento[3],
        filamento[4],
        filamento[5],
        filamento[6],
        str(date.today()),
        filamento[7],
        custo_grama,
        "Ativo",
        ""
    ))

    novo_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    conn.commit()
    conn.close()

    return novo_id


@st.dialog("Editar Filamento")
def editar_filamento_modal(filamento_id):
    conn = conectar()

    filamento = conn.execute("""
    SELECT
        id,
        nome,
        material,
        marca,
        cor,
        peso_original,
        valor_compra,
        fornecedor,
        data_compra,
        observacoes,
        status,
        data_finalizacao
    FROM filamentos
    WHERE id = ?
    """, (filamento_id,)).fetchone()

    conn.close()

    if filamento is None:
        st.warning("Filamento não encontrado.")
        return

    small_section("Dados do filamento")

    with st.form("editar_filamento_form_modal"):

        nome_edit = st.text_input("Nome", value=filamento[1])

        material_edit = st.selectbox(
            "Material",
            ["PLA", "PETG"],
            index=0 if filamento[2] == "PLA" else 1
        )

        marca_edit = st.text_input(
            "Marca",
            value=filamento[3] if filamento[3] else ""
        )

        cor_edit = st.text_input(
            "Cor",
            value=filamento[4] if filamento[4] else ""
        )

        col_peso_valor_1, col_peso_valor_2 = st.columns(2)

        with col_peso_valor_1:
            peso_edit = st.number_input(
                "Peso (g)",
                min_value=1.0,
                value=float(filamento[5]) if filamento[5] else 1000.0
            )

        with col_peso_valor_2:
            valor_edit = st.number_input(
                "Valor Compra",
                min_value=0.0,
                value=float(filamento[6]) if filamento[6] else 0.0
            )

        fornecedor_edit = st.text_input(
            "Fornecedor",
            value=filamento[7] if filamento[7] else ""
        )

        data_edit = st.text_input(
            "Data da compra",
            value=filamento[8] if filamento[8] else ""
        )

        observacoes_edit = st.text_area(
            "Observações",
            value=filamento[9] if filamento[9] else ""
        )

        col_status_1, col_status_2 = st.columns(2)

        with col_status_1:
            status_edit = st.selectbox(
                "Status",
                ["Ativo", "Consumido"],
                index=0 if (filamento[10] if filamento[10] else "Ativo") == "Ativo" else 1
            )

        with col_status_2:
            data_finalizacao_edit = st.text_input(
                "Data de finalização",
                value=filamento[11] if filamento[11] else ""
            )

        salvar_edicao = st.form_submit_button("Salvar Alterações")

    if salvar_edicao:

        if not nome_edit:
            st.warning("Informe o nome do filamento.")

        else:
            custo_grama = valor_edit / peso_edit if peso_edit else 0

            conn = conectar()

            conn.execute("""
            UPDATE filamentos
            SET
                nome = ?,
                material = ?,
                marca = ?,
                cor = ?,
                peso_original = ?,
                valor_compra = ?,
                fornecedor = ?,
                data_compra = ?,
                observacoes = ?,
                custo_grama = ?,
                status = ?,
                data_finalizacao = ?
            WHERE id = ?
            """,
            (
                nome_edit,
                material_edit,
                marca_edit,
                cor_edit,
                peso_edit,
                valor_edit,
                fornecedor_edit,
                data_edit,
                observacoes_edit,
                custo_grama,
                status_edit,
                data_finalizacao_edit,
                filamento_id
            ))

            conn.commit()
            conn.close()

            st.success("Filamento atualizado!")
            st.rerun()


def exibir_resultados_filamento(filamento_id):
    resultados = carregar_resultados_filamento(filamento_id)

    small_section("Resultados do filamento")

    col_r1, col_r2, col_r3, col_r4 = st.columns(4)

    with col_r1:
        kpi_card("Pedidos", str(resultados["pedidos_total"]), "pedidos vinculados", "blue")

    with col_r2:
        kpi_card("Peças", str(resultados["pecas_vinculadas"]), "peças vinculadas", "orange")

    with col_r3:
        kpi_card("Faturamento", moeda(resultados["faturamento"]), "pedidos vinculados", "green")

    with col_r4:
        kpi_card("Lucro", moeda(resultados["lucro"]), "estimado", "green" if resultados["lucro"] >= 0 else "red")

    col_r5, col_r6 = st.columns(2)

    with col_r5:
        st.write(f"**Quantidade vendida:** {resultados['quantidade_total']:.0f} un.")

    with col_r6:
        st.write(f"**Filamento estimado consumido:** {resultados['peso_consumido_g']:.1f} g")

    small_section("Pedidos vinculados ao filamento")

    if resultados["pedidos"]:
        for pedido in resultados["pedidos"][:8]:
            total_fmt = moeda_md(pedido["total"])

            st.write(
                f"- **{pedido['codigo']}** | "
                f"{pedido['cliente_nome']} | "
                f"{pedido['peca_codigo']} - {pedido['peca_nome']} | "
                f"{pedido['quantidade']:.0f} un | "
                f"{pedido['status']} | "
                f"{total_fmt} | "
                f"{pedido['peso_consumido_g']:.1f} g"
            )

        if len(resultados["pedidos"]) > 8:
            st.caption(f"Mostrando os 8 pedidos mais recentes de {len(resultados['pedidos'])} pedidos vinculados.")
    else:
        st.caption("Este filamento ainda não possui pedidos vinculados.")


with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()
sidebar()
mobile_bottom_nav("mais")
mobile_summary_css("filamentos")
header("Filamentos", "Cadastro e controle dos rolos utilizados")


conn = conectar()

total_filamentos = conn.execute("SELECT COUNT(*) FROM filamentos").fetchone()[0]

filamentos_ativos = conn.execute("""
SELECT COUNT(*)
FROM filamentos
WHERE status IS NULL OR status = 'Ativo'
""").fetchone()[0]

filamentos_consumidos = conn.execute("""
SELECT COUNT(*)
FROM filamentos
WHERE status = 'Consumido'
""").fetchone()[0]

valor_total = conn.execute("""
SELECT COALESCE(SUM(valor_compra), 0)
FROM filamentos
""").fetchone()[0]

conn.close()


with st.container(key="filamentos_mobile_resumo"):
    render_mobile_summary(
        hero_label="Estoque de filamentos",
        hero_value=f"{filamentos_ativos} ativos",
        hero_subtitle=f"{total_filamentos} rolos cadastrados · {moeda(valor_total)} investidos",
        kpis=[
            {"titulo": "Total", "valor": total_filamentos, "subtitulo": "rolos cadastrados", "cor": "#0C65AA"},
            {"titulo": "Ativos", "valor": filamentos_ativos, "subtitulo": "disponíveis", "cor": "#1F8A4C"},
            {"titulo": "Consumidos", "valor": filamentos_consumidos, "subtitulo": "finalizados", "cor": "#8A8F98"},
            {"titulo": "Investido", "valor": moeda(valor_total), "subtitulo": "em filamentos", "cor": "#B85C20"},
        ],
        note="<strong>Atalho:</strong> use o botão <strong>+ Novo Filamento</strong> abaixo para cadastrar um novo rolo.",
    )

with st.container(key="filamentos_desktop_resumo"):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_card("Filamentos", str(total_filamentos), "rolos cadastrados", "blue")

    with col2:
        kpi_card("Ativos", str(filamentos_ativos), "em uso disponível", "green")

    with col3:
        kpi_card("Consumidos", str(filamentos_consumidos), "rolos finalizados", "gray")

    with col4:
        kpi_card("Valor investido", moeda(valor_total), "total em filamentos", "orange")


section_title(
    "Cadastro de Filamentos",
    "Adicione novos rolos ou consulte filamentos já cadastrados"
)


if "mostrar_form_filamento" not in st.session_state:
    st.session_state["mostrar_form_filamento"] = False


if primary_button("+ Novo Filamento", "btn_novo_filamento"):
    st.session_state["mostrar_form_filamento"] = not st.session_state["mostrar_form_filamento"]


if st.session_state["mostrar_form_filamento"]:

    small_section("Novo Filamento")

    with st.form("novo_filamento"):

        nome = st.text_input("Nome do Filamento")

        material = st.selectbox("Material", ["PLA", "PETG"])

        marca = st.text_input("Marca")

        cor = st.text_input("Cor")

        peso_original = st.number_input(
            "Peso Original (g)",
            min_value=1.0,
            value=1000.0
        )

        valor_compra = st.number_input(
            "Valor da Compra (R$)",
            min_value=0.0,
            value=0.0
        )

        fornecedor = st.text_input("Fornecedor")

        data_compra = st.date_input("Data da Compra")

        observacoes = st.text_area("Observações")

        salvar = st.form_submit_button("Salvar Filamento")

    if salvar:

        if not nome:
            st.warning("Informe o nome do filamento.")

        else:
            conn = conectar()

            codigo = gerar_codigo_filamento(conn)
            custo_grama = valor_compra / peso_original

            conn.execute("""
            INSERT INTO filamentos
            (
                codigo,
                nome,
                material,
                marca,
                cor,
                peso_original,
                valor_compra,
                fornecedor,
                data_compra,
                observacoes,
                custo_grama,
                status,
                data_finalizacao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                codigo,
                nome,
                material,
                marca,
                cor,
                peso_original,
                valor_compra,
                fornecedor,
                str(data_compra),
                observacoes,
                custo_grama,
                "Ativo",
                ""
            ))

            conn.commit()
            conn.close()

            st.success("Filamento cadastrado com sucesso!")
            st.session_state["mostrar_form_filamento"] = False
            st.rerun()


section_title(
    "Filamentos cadastrados",
    "Consulte, edite, duplique ou finalize rolos cadastrados"
)

busca = searchbar(
    placeholder="Pesquisar por código, nome, marca, cor ou status...",
    key="buscar_filamento"
)

conn = conectar()

filamentos = conn.execute("""
SELECT
    id,
    codigo,
    nome,
    material,
    marca,
    cor,
    peso_original,
    valor_compra,
    fornecedor,
    data_compra,
    observacoes,
    custo_grama,
    status,
    data_finalizacao
FROM filamentos
WHERE nome LIKE ?
   OR codigo LIKE ?
   OR marca LIKE ?
   OR cor LIKE ?
   OR status LIKE ?
ORDER BY id DESC
""", (
    f"%{busca}%",
    f"%{busca}%",
    f"%{busca}%",
    f"%{busca}%",
    f"%{busca}%"
)).fetchall()

conn.close()

for f in filamentos:

    filamento_id = f[0]
    codigo = f[1]
    nome = f[2]
    material = f[3]
    marca = f[4] if f[4] else "-"
    cor = f[5] if f[5] else "-"
    peso = f[6]
    valor = f[7]
    fornecedor = f[8] if f[8] else "-"
    data = f[9] if f[9] else "-"
    observacoes = f[10] if f[10] else ""
    custo_g = f[11]
    status = f[12] if f[12] else "Ativo"
    data_finalizacao = f[13] if f[13] else "-"

    cor_card = "blue" if status == "Ativo" else "gray"

    with st.container(border=True):

        item_card(
            codigo=codigo,
            titulo=nome,
            subtitulo=f"{material} • {marca} • {cor}",
            cor=cor_card
        )

        conn = conectar()

        pecas_do_filamento = conn.execute("""
        SELECT
            codigo,
            nome,
            categoria,
            peso_g,
            tempo_impressao_h
        FROM pecas
        WHERE filamento_id = ?
        ORDER BY id DESC
        """, (filamento_id,)).fetchall()

        conn.close()

        with st.expander("Detalhes, peças vinculadas e ações"):

            col_d1, col_d2, col_d3, col_d4 = st.columns(4)

            with col_d1:
                st.write(f"**Status:** {status}")
                st.write(f"**Material:** {material}")

            with col_d2:
                st.write(f"**Marca:** {marca}")
                st.write(f"**Cor:** {cor}")

            with col_d3:
                st.write(f"**Peso:** {peso:.0f} g")
                st.write(f"**Valor:** {moeda(valor)}")

            with col_d4:
                st.write(f"**Custo/g:** {moeda(custo_g)}")
                st.write(f"**Fornecedor:** {fornecedor}")

            st.write(f"**Data da compra:** {data}")

            if status == "Consumido":
                st.write(f"**Data de finalização:** {data_finalizacao}")

            if observacoes:
                st.write(f"**Observações:** {observacoes}")

            st.markdown("#### Peças cadastradas com este filamento")

            if pecas_do_filamento:
                for peca in pecas_do_filamento:
                    st.write(
                        f"- **{peca[0]} - {peca[1]}** | "
                        f"Categoria: {peca[2]} | "
                        f"Peso: {peca[3]:.1f}g | "
                        f"Tempo: {peca[4]:.2f}h"
                    )
            else:
                st.caption("Nenhuma peça cadastrada com este filamento.")

            exibir_resultados_filamento(filamento_id)

            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

            with col_btn1:
                if secondary_button("Editar", f"editar_{filamento_id}"):
                    editar_filamento_modal(filamento_id)

            with col_btn2:
                if secondary_button("Duplicar", f"duplicar_{filamento_id}"):
                    novo_id = duplicar_filamento(filamento_id)

                    if novo_id:
                        editar_filamento_modal(novo_id)
                    else:
                        st.error("Não foi possível duplicar este filamento.")

            with col_btn3:
                if status == "Ativo":
                    if primary_button("Finalizado", f"finalizar_{filamento_id}"):
                        conn = conectar()
                        conn.execute("""
                        UPDATE filamentos
                        SET
                            status = ?,
                            data_finalizacao = ?
                        WHERE id = ?
                        """, (
                            "Consumido",
                            str(date.today()),
                            filamento_id
                        ))
                        conn.commit()
                        conn.close()
                        st.rerun()
                else:
                    if secondary_button("Reativar", f"reativar_{filamento_id}"):
                        conn = conectar()
                        conn.execute("""
                        UPDATE filamentos
                        SET
                            status = ?,
                            data_finalizacao = ?
                        WHERE id = ?
                        """, (
                            "Ativo",
                            "",
                            filamento_id
                        ))
                        conn.commit()
                        conn.close()
                        st.rerun()

            with col_btn4:
                if danger_button("Excluir", f"excluir_{filamento_id}"):
                    conn = conectar()
                    conn.execute(
                        "DELETE FROM filamentos WHERE id = ?",
                        (filamento_id,)
                    )
                    conn.commit()
                    conn.close()
                    st.rerun()

    st.write("")
