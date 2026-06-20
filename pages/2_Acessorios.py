import streamlit as st

from components.sidebar import sidebar
from components.header import header
from components.kpi import kpi_card
from components.card import item_card
from components.button import primary_button, secondary_button, danger_button
from components.searchbar import searchbar
from components.section import section_title, small_section
from components.auth import require_login
from database import conectar, inicializar_banco



def moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def gerar_codigo_acessorio(conn):
    ultimo = conn.execute("""
        SELECT MAX(id)
        FROM acessorios
    """).fetchone()[0]

    proximo = 1 if ultimo is None else ultimo + 1
    return f"ACE-{proximo:04d}"


def duplicar_acessorio(acessorio_id):
    conn = conectar()

    acessorio = conn.execute("""
    SELECT
        nome,
        categoria,
        custo_unitario,
        observacoes
    FROM acessorios
    WHERE id = ?
    """, (acessorio_id,)).fetchone()

    if acessorio is None:
        conn.close()
        return None

    codigo = gerar_codigo_acessorio(conn)

    cursor = conn.execute("""
    INSERT INTO acessorios
    (
        codigo,
        nome,
        categoria,
        custo_unitario,
        observacoes
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        codigo,
        acessorio[0],
        acessorio[1],
        acessorio[2],
        acessorio[3]
    ))

    novo_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    conn.commit()
    conn.close()

    return novo_id


@st.dialog("Editar Acessório")
def editar_acessorio_modal(acessorio_id):
    conn = conectar()

    acessorio = conn.execute("""
    SELECT
        id,
        nome,
        categoria,
        custo_unitario,
        observacoes
    FROM acessorios
    WHERE id = ?
    """, (acessorio_id,)).fetchone()

    conn.close()

    if acessorio is None:
        st.warning("Acessório não encontrado.")
        return

    small_section("Dados do acessório")

    with st.form("editar_acessorio_form_modal"):

        nome_edit = st.text_input("Nome", value=acessorio[1])

        categorias_lista = ["Chaveiro", "Imã", "Parafuso", "Embalagem", "Etiqueta", "Outro"]

        categoria_edit = st.selectbox(
            "Categoria",
            categorias_lista,
            index=categorias_lista.index(acessorio[2]) if acessorio[2] in categorias_lista else 5
        )

        custo_edit = st.number_input(
            "Custo Unitário (R$)",
            min_value=0.0,
            value=float(acessorio[3]),
            step=0.01
        )

        observacoes_edit = st.text_area(
            "Observações",
            value=acessorio[4] if acessorio[4] else ""
        )

        salvar_edicao = st.form_submit_button("Salvar Alterações")

    if salvar_edicao:

        if not nome_edit:
            st.warning("Informe o nome do acessório.")

        else:
            conn = conectar()

            conn.execute("""
            UPDATE acessorios
            SET
                nome = ?,
                categoria = ?,
                custo_unitario = ?,
                observacoes = ?
            WHERE id = ?
            """,
            (
                nome_edit,
                categoria_edit,
                custo_edit,
                observacoes_edit,
                acessorio_id
            ))

            conn.commit()
            conn.close()

            st.success("Acessório atualizado!")
            st.rerun()


with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()

sidebar()
header("Acessórios", "Cadastro e controle dos itens adicionais")


conn = conectar()

total_acessorios = conn.execute("SELECT COUNT(*) FROM acessorios").fetchone()[0]

categorias = conn.execute("""
SELECT COUNT(DISTINCT categoria)
FROM acessorios
""").fetchone()[0]

custo_medio = conn.execute("""
SELECT COALESCE(AVG(custo_unitario), 0)
FROM acessorios
""").fetchone()[0]

valor_total = conn.execute("""
SELECT COALESCE(SUM(custo_unitario), 0)
FROM acessorios
""").fetchone()[0]

conn.close()


col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card("Acessórios", str(total_acessorios), "itens cadastrados", "blue")

with col2:
    kpi_card("Categorias", str(categorias), "tipos diferentes", "green")

with col3:
    kpi_card("Custo médio", moeda(custo_medio), "média por unidade", "orange")

with col4:
    kpi_card("Valor base", moeda(valor_total), "soma dos custos unitários", "gray")


section_title(
    "Cadastro de Acessórios",
    "Adicione itens usados na composição das peças"
)


if "mostrar_form_acessorio" not in st.session_state:
    st.session_state["mostrar_form_acessorio"] = False


if primary_button("+ Novo Acessório", "btn_novo_acessorio"):
    st.session_state["mostrar_form_acessorio"] = not st.session_state["mostrar_form_acessorio"]


if st.session_state["mostrar_form_acessorio"]:

    small_section("Novo Acessório")

    with st.form("novo_acessorio"):

        nome = st.text_input("Nome do Acessório")

        categoria = st.selectbox(
            "Categoria",
            ["Chaveiro", "Imã", "Parafuso", "Embalagem", "Etiqueta", "Outro"]
        )

        custo_unitario = st.number_input(
            "Custo Unitário (R$)",
            min_value=0.0,
            value=0.0,
            step=0.01
        )

        observacoes = st.text_area("Observações")

        salvar = st.form_submit_button("Salvar Acessório")

    if salvar:

        if not nome:
            st.warning("Informe o nome do acessório.")

        else:
            conn = conectar()

            codigo = gerar_codigo_acessorio(conn)

            conn.execute("""
            INSERT INTO acessorios
            (
                codigo,
                nome,
                categoria,
                custo_unitario,
                observacoes
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                codigo,
                nome,
                categoria,
                custo_unitario,
                observacoes
            ))

            conn.commit()
            conn.close()

            st.success("Acessório cadastrado com sucesso!")
            st.session_state["mostrar_form_acessorio"] = False
            st.rerun()


section_title(
    "Acessórios cadastrados",
    "Consulte, edite, duplique ou exclua itens cadastrados"
)


busca = searchbar(
    placeholder="Pesquisar por código, nome ou categoria...",
    key="buscar_acessorio"
)


conn = conectar()

acessorios = conn.execute("""
SELECT
    id,
    codigo,
    nome,
    categoria,
    custo_unitario,
    observacoes
FROM acessorios
WHERE nome LIKE ?
   OR codigo LIKE ?
   OR categoria LIKE ?
ORDER BY id DESC
""", (
    f"%{busca}%",
    f"%{busca}%",
    f"%{busca}%"
)).fetchall()

conn.close()


for a in acessorios:

    acessorio_id = a[0]
    codigo = a[1]
    nome = a[2]
    categoria = a[3] if a[3] else "-"
    custo_unitario = a[4]
    observacoes = a[5] if a[5] else ""

    with st.container(border=True):

        item_card(
            codigo=codigo,
            titulo=nome,
            subtitulo=f"{categoria} • {moeda(custo_unitario)} por unidade",
            cor="blue"
        )

        with st.expander("Detalhes e ações"):

            col_d1, col_d2, col_d3 = st.columns(3)

            with col_d1:
                st.write(f"**Código:** {codigo}")

            with col_d2:
                st.write(f"**Categoria:** {categoria}")

            with col_d3:
                st.write(f"**Custo unitário:** {moeda(custo_unitario)}")

            if observacoes:
                st.write(f"**Observações:** {observacoes}")

            col_btn1, col_btn2, col_btn3 = st.columns(3)

            with col_btn1:
                if secondary_button("Editar", f"editar_acessorio_{acessorio_id}"):
                    editar_acessorio_modal(acessorio_id)

            with col_btn2:
                if secondary_button("Duplicar", f"duplicar_acessorio_{acessorio_id}"):
                    novo_id = duplicar_acessorio(acessorio_id)

                    if novo_id:
                        editar_acessorio_modal(novo_id)
                    else:
                        st.error("Não foi possível duplicar este acessório.")

            with col_btn3:
                if danger_button("Excluir", f"excluir_acessorio_{acessorio_id}"):
                    conn = conectar()
                    conn.execute(
                        "DELETE FROM acessorios WHERE id = ?",
                        (acessorio_id,)
                    )
                    conn.commit()
                    conn.close()
                    st.rerun()

    st.write("")
