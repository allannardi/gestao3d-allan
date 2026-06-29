import streamlit as st

from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.desktop_visual import inject_desktop_visual
from components.mobile_summary import mobile_summary_css, render_mobile_summary
from components.header import header
from components.help_ui import header_with_help
from components.kpi import kpi_card
from components.card import item_card
from components.button import primary_button, secondary_button, danger_button
from components.searchbar import searchbar
from components.pagination import paginar_itens
from components.section import section_title, small_section
from components.auth import require_login
from database import conectar, inicializar_banco




@st.cache_data(ttl=3600, show_spinner=False)
def carregar_css_base_cache():
    with open("assets/style.css", encoding="utf-8") as f:
        return f.read()


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

        nome_edit = st.text_input(
            "Nome",
            value=acessorio[1],
            help="Use um nome fácil de reconhecer no cadastro de peças."
        )

        categorias_lista = ["Chaveiro", "Imã", "Parafuso", "Embalagem", "Etiqueta", "Outro"]

        categoria_edit = st.selectbox(
            "Categoria",
            categorias_lista,
            index=categorias_lista.index(acessorio[2]) if acessorio[2] in categorias_lista else 5,
            help="Escolha o tipo de acessório para facilitar busca e organização."
        )

        custo_edit = st.number_input(
            "Custo Unitário (R$)",
            min_value=0.0,
            value=float(acessorio[3]),
            step=0.01,
            help="Informe o custo de 1 unidade. Esse valor entra no cálculo de custo das peças."
        )

        observacoes_edit = st.text_area(
            "Observações",
            value=acessorio[4] if acessorio[4] else "",
            help="Opcional. Registre fornecedor, tamanho, cor, lote ou observações de uso."
        )

        salvar_edicao = st.form_submit_button("Salvar Alterações")

    if salvar_edicao:

        if not nome_edit:
            st.warning("Informe o nome do acessório.")

        elif custo_edit <= 0:
            st.warning("Informe o custo unitário do acessório.")

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


st.markdown(f"<style>{carregar_css_base_cache()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()

sidebar()
mobile_bottom_nav("mais")
inject_desktop_visual()
mobile_summary_css("acessorios")


@st.dialog("Ajuda - Acessórios")
def ajuda_acessorios():
    st.markdown(
        """
        Use esta tela para cadastrar itens extras usados nas peças ou pedidos.

        Exemplos:
        - argolas de chaveiro;
        - ímãs;
        - embalagens especiais;
        - partes metálicas;
        - etiquetas ou acessórios decorativos.

        Depois de cadastrados, esses itens podem entrar no custo da peça para deixar o cálculo de lucro mais realista.
        """
    )

header_with_help("Acessórios", "Cadastro e controle dos itens adicionais", ajuda_acessorios, key="ajuda_acessorios_link")


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


with st.container(key="acessorios_mobile_resumo"):
    render_mobile_summary(
        hero_label="Itens complementares",
        hero_value=f"{total_acessorios} acessórios",
        hero_subtitle=f"{categorias} categorias · custo médio {moeda(custo_medio)}",
        kpis=[
            {"titulo": "Categorias", "valor": categorias, "subtitulo": "tipos diferentes", "cor": "#1F8A4C"},
            {"titulo": "Custo médio", "valor": moeda(custo_medio), "subtitulo": "por unidade", "cor": "#B85C20"},
            {"titulo": "Valor base", "valor": moeda(valor_total), "subtitulo": "custos somados", "cor": "#8A8F98"},
            {"titulo": "Total", "valor": total_acessorios, "subtitulo": "itens", "cor": "#0C65AA"},
        ],
        note="<strong>Atalho:</strong> use o botão <strong>+ Novo Acessório</strong> abaixo para cadastrar um novo item.",
    )

with st.container(key="acessorios_desktop_resumo"):
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

st.caption("Dica: cadastre o custo de uma unidade do acessório. O sistema multiplica pela quantidade usada no lote da peça.")


if "mostrar_form_acessorio" not in st.session_state:
    st.session_state["mostrar_form_acessorio"] = False


if primary_button("+ Novo Acessório", "btn_novo_acessorio"):
    st.session_state["mostrar_form_acessorio"] = not st.session_state["mostrar_form_acessorio"]


if st.session_state["mostrar_form_acessorio"]:

    small_section("Novo Acessório")

    with st.form("novo_acessorio"):

        nome = st.text_input(
            "Nome do Acessório",
            help="Use um nome fácil de reconhecer. Ex.: Argola de chaveiro, imã 10 mm, embalagem kraft."
        )

        categoria = st.selectbox(
            "Categoria",
            ["Chaveiro", "Imã", "Parafuso", "Embalagem", "Etiqueta", "Outro"],
            help="Escolha o tipo de acessório. Isso ajuda a organizar e encontrar o item depois."
        )

        custo_unitario = st.number_input(
            "Custo Unitário (R$)",
            min_value=0.0,
            value=0.0,
            step=0.01,
            help="Informe quanto custa 1 unidade deste acessório. Ex.: se 100 argolas custam R$ 20,00, o custo unitário é R$ 0,20."
        )

        observacoes = st.text_area(
            "Observações",
            help="Opcional. Use para registrar fornecedor, tamanho, cor, lote ou observações de uso."
        )

        salvar = st.form_submit_button("Salvar Acessório")

    if salvar:

        if not nome:
            st.warning("Informe o nome do acessório.")

        elif custo_unitario <= 0:
            st.warning("Informe o custo unitário do acessório. Esse valor é usado no cálculo de lucro da peça.")

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

            st.success(f"Acessório {codigo} cadastrado com sucesso! Ele já pode ser usado no cadastro de peças.")
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

acessorios = paginar_itens(
    acessorios,
    "acessorios",
    opcoes=(10, 25, 50, 100),
    nome_item="acessórios"
)


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
