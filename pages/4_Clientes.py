import streamlit as st
from datetime import date

from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.header import header
from components.kpi import kpi_card
from components.card import item_card
from components.button import primary_button, secondary_button, danger_button
from components.searchbar import searchbar
from components.section import section_title, small_section
from components.auth import require_login
from database import conectar, inicializar_banco


def garantir_tabela_clientes():
    conn = conectar()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nome TEXT NOT NULL,
        tipo TEXT,
        documento TEXT,
        telefone TEXT,
        email TEXT,
        cidade TEXT,
        estado TEXT,
        instagram TEXT,
        origem TEXT,
        observacoes TEXT,
        status TEXT DEFAULT 'Ativo',
        data_cadastro TEXT
    )
    """)

    conn.commit()
    conn.close()


def gerar_codigo_cliente(conn):
    ultimo = conn.execute("""
        SELECT MAX(id)
        FROM clientes
    """).fetchone()[0]

    proximo = 1 if ultimo is None else ultimo + 1
    return f"CLI-{proximo:04d}"


def duplicar_cliente(cliente_id):
    conn = conectar()

    cliente = conn.execute("""
    SELECT
        nome,
        tipo,
        documento,
        telefone,
        email,
        cidade,
        estado,
        instagram,
        origem,
        observacoes
    FROM clientes
    WHERE id = ?
    """, (cliente_id,)).fetchone()

    if cliente is None:
        conn.close()
        return None

    codigo = gerar_codigo_cliente(conn)

    cursor = conn.execute("""
    INSERT INTO clientes
    (
        codigo,
        nome,
        tipo,
        documento,
        telefone,
        email,
        cidade,
        estado,
        instagram,
        origem,
        observacoes,
        status,
        data_cadastro
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        codigo,
        cliente[0],
        cliente[1],
        cliente[2],
        cliente[3],
        cliente[4],
        cliente[5],
        cliente[6],
        cliente[7],
        cliente[8],
        cliente[9],
        "Ativo",
        str(date.today())
    ))

    novo_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    conn.commit()
    conn.close()

    return novo_id


@st.dialog("Editar Cliente")
def editar_cliente_modal(cliente_id):
    conn = conectar()

    cliente = conn.execute("""
    SELECT
        id,
        nome,
        tipo,
        documento,
        telefone,
        email,
        cidade,
        estado,
        instagram,
        origem,
        observacoes,
        status
    FROM clientes
    WHERE id = ?
    """, (cliente_id,)).fetchone()

    conn.close()

    if cliente is None:
        st.warning("Cliente não encontrado.")
        return

    small_section("Dados do cliente")

    with st.form("editar_cliente_form_modal"):

        nome_edit = st.text_input("Nome", value=cliente[1])

        tipos_lista = ["Pessoa Física", "Pessoa Jurídica"]

        tipo_edit = st.selectbox(
            "Tipo",
            tipos_lista,
            index=tipos_lista.index(cliente[2]) if cliente[2] in tipos_lista else 0
        )

        documento_edit = st.text_input(
            "CPF / CNPJ",
            value=cliente[3] if cliente[3] else ""
        )

        telefone_edit = st.text_input(
            "Telefone / WhatsApp",
            value=cliente[4] if cliente[4] else ""
        )

        email_edit = st.text_input(
            "E-mail",
            value=cliente[5] if cliente[5] else ""
        )

        col_form1, col_form2 = st.columns(2)

        with col_form1:
            cidade_edit = st.text_input(
                "Cidade",
                value=cliente[6] if cliente[6] else ""
            )

            instagram_edit = st.text_input(
                "Instagram",
                value=cliente[8] if cliente[8] else ""
            )

        with col_form2:
            estado_edit = st.text_input(
                "Estado",
                value=cliente[7] if cliente[7] else ""
            )

            origem_lista = [
                "Indicação",
                "Instagram",
                "WhatsApp",
                "Marketplace",
                "Feira / Evento",
                "Cliente recorrente",
                "Outro"
            ]

            origem_edit = st.selectbox(
                "Origem do Cliente",
                origem_lista,
                index=origem_lista.index(cliente[9]) if cliente[9] in origem_lista else 0
            )

        status_lista = ["Ativo", "Inativo"]

        status_edit = st.selectbox(
            "Status",
            status_lista,
            index=status_lista.index(cliente[11]) if cliente[11] in status_lista else 0
        )

        observacoes_edit = st.text_area(
            "Observações",
            value=cliente[10] if cliente[10] else ""
        )

        salvar_edicao = st.form_submit_button("Salvar Alterações")

    if salvar_edicao:

        if not nome_edit:
            st.warning("Informe o nome do cliente.")

        else:
            conn = conectar()

            conn.execute("""
            UPDATE clientes
            SET
                nome = ?,
                tipo = ?,
                documento = ?,
                telefone = ?,
                email = ?,
                cidade = ?,
                estado = ?,
                instagram = ?,
                origem = ?,
                observacoes = ?,
                status = ?
            WHERE id = ?
            """,
            (
                nome_edit,
                tipo_edit,
                documento_edit,
                telefone_edit,
                email_edit,
                cidade_edit,
                estado_edit,
                instagram_edit,
                origem_edit,
                observacoes_edit,
                status_edit,
                cliente_id
            ))

            conn.commit()
            conn.close()

            st.success("Cliente atualizado!")
            st.rerun()


with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()
sidebar()
mobile_bottom_nav("clientes")
header("Clientes", "Cadastro e gestão dos clientes do Ateliê")


conn = conectar()

total_clientes = conn.execute("""
SELECT COUNT(*)
FROM clientes
""").fetchone()[0]

clientes_ativos = conn.execute("""
SELECT COUNT(*)
FROM clientes
WHERE status IS NULL OR status = 'Ativo'
""").fetchone()[0]

clientes_pf = conn.execute("""
SELECT COUNT(*)
FROM clientes
WHERE tipo = 'Pessoa Física'
""").fetchone()[0]

clientes_pj = conn.execute("""
SELECT COUNT(*)
FROM clientes
WHERE tipo = 'Pessoa Jurídica'
""").fetchone()[0]

conn.close()


col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card("Clientes", str(total_clientes), "clientes cadastrados", "blue")

with col2:
    kpi_card("Ativos", str(clientes_ativos), "clientes disponíveis", "green")

with col3:
    kpi_card("Pessoa Física", str(clientes_pf), "clientes individuais", "orange")

with col4:
    kpi_card("Pessoa Jurídica", str(clientes_pj), "empresas cadastradas", "gray")


section_title(
    "Cadastro de Clientes",
    "Adicione clientes para futuramente vincular pedidos, produção e faturamento"
)


if "mostrar_form_cliente" not in st.session_state:
    st.session_state["mostrar_form_cliente"] = False


if primary_button("+ Novo Cliente", "btn_novo_cliente"):
    st.session_state["mostrar_form_cliente"] = not st.session_state["mostrar_form_cliente"]


if st.session_state["mostrar_form_cliente"]:

    small_section("Novo Cliente")

    with st.form("novo_cliente"):

        nome = st.text_input("Nome do Cliente")

        tipo = st.selectbox(
            "Tipo",
            ["Pessoa Física", "Pessoa Jurídica"]
        )

        documento = st.text_input("CPF / CNPJ")

        col_form1, col_form2 = st.columns(2)

        with col_form1:
            telefone = st.text_input("Telefone / WhatsApp")
            cidade = st.text_input("Cidade")
            instagram = st.text_input("Instagram")

        with col_form2:
            email = st.text_input("E-mail")
            estado = st.text_input("Estado")
            origem = st.selectbox(
                "Origem do Cliente",
                [
                    "Indicação",
                    "Instagram",
                    "WhatsApp",
                    "Marketplace",
                    "Feira / Evento",
                    "Cliente recorrente",
                    "Outro"
                ]
            )

        observacoes = st.text_area("Observações")

        salvar = st.form_submit_button("Salvar Cliente")

    if salvar:

        if not nome:
            st.warning("Informe o nome do cliente.")

        else:
            conn = conectar()

            codigo = gerar_codigo_cliente(conn)

            conn.execute("""
            INSERT INTO clientes
            (
                codigo,
                nome,
                tipo,
                documento,
                telefone,
                email,
                cidade,
                estado,
                instagram,
                origem,
                observacoes,
                status,
                data_cadastro
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                codigo,
                nome,
                tipo,
                documento,
                telefone,
                email,
                cidade,
                estado,
                instagram,
                origem,
                observacoes,
                "Ativo",
                str(date.today())
            ))

            conn.commit()
            conn.close()

            st.success("Cliente cadastrado com sucesso!")
            st.session_state["mostrar_form_cliente"] = False
            st.rerun()


section_title(
    "Clientes cadastrados",
    "Consulte, edite, duplique ou exclua clientes cadastrados"
)


busca = searchbar(
    placeholder="Pesquisar por código, nome, telefone, cidade, estado ou origem...",
    key="buscar_cliente"
)


conn = conectar()

clientes = conn.execute("""
SELECT
    id,
    codigo,
    nome,
    tipo,
    documento,
    telefone,
    email,
    cidade,
    estado,
    instagram,
    origem,
    observacoes,
    status,
    data_cadastro
FROM clientes
WHERE nome LIKE ?
   OR codigo LIKE ?
   OR telefone LIKE ?
   OR email LIKE ?
   OR cidade LIKE ?
   OR estado LIKE ?
   OR origem LIKE ?
ORDER BY id DESC
""", (
    f"%{busca}%",
    f"%{busca}%",
    f"%{busca}%",
    f"%{busca}%",
    f"%{busca}%",
    f"%{busca}%",
    f"%{busca}%"
)).fetchall()

conn.close()


for c in clientes:

    cliente_id = c[0]
    codigo = c[1]
    nome = c[2]
    tipo = c[3] if c[3] else "-"
    documento = c[4] if c[4] else "-"
    telefone = c[5] if c[5] else "-"
    email = c[6] if c[6] else "-"
    cidade = c[7] if c[7] else "-"
    estado = c[8] if c[8] else "-"
    instagram = c[9] if c[9] else "-"
    origem = c[10] if c[10] else "-"
    observacoes = c[11] if c[11] else ""
    status = c[12] if c[12] else "Ativo"
    data_cadastro = c[13] if c[13] else "-"

    cor_card = "blue" if status == "Ativo" else "gray"

    with st.container(border=True):

        item_card(
            codigo=codigo,
            titulo=nome,
            subtitulo=f"{tipo} • {cidade}/{estado} • {origem}",
            cor=cor_card
        )

        with st.expander("Detalhes e ações"):

            col_d1, col_d2, col_d3, col_d4 = st.columns(4)

            with col_d1:
                st.write(f"**Status:** {status}")
                st.write(f"**Tipo:** {tipo}")

            with col_d2:
                st.write(f"**Telefone:** {telefone}")
                st.write(f"**E-mail:** {email}")

            with col_d3:
                st.write(f"**Cidade:** {cidade}")
                st.write(f"**Estado:** {estado}")

            with col_d4:
                st.write(f"**Origem:** {origem}")
                st.write(f"**Cadastro:** {data_cadastro}")

            st.write(f"**Documento:** {documento}")
            st.write(f"**Instagram:** {instagram}")

            if observacoes:
                st.write(f"**Observações:** {observacoes}")

            st.caption(
                "Quando o módulo de Pedidos estiver pronto, esta área mostrará "
                "histórico de compras, faturamento e peças compradas por este cliente."
            )

            col_btn1, col_btn2, col_btn3 = st.columns(3)

            with col_btn1:
                if secondary_button("Editar", f"editar_cliente_{cliente_id}"):
                    editar_cliente_modal(cliente_id)

            with col_btn2:
                if secondary_button("Duplicar", f"duplicar_cliente_{cliente_id}"):
                    novo_id = duplicar_cliente(cliente_id)

                    if novo_id:
                        editar_cliente_modal(novo_id)
                    else:
                        st.error("Não foi possível duplicar este cliente.")

            with col_btn3:
                if danger_button("Excluir", f"excluir_cliente_{cliente_id}"):
                    conn = conectar()
                    conn.execute(
                        "DELETE FROM clientes WHERE id = ?",
                        (cliente_id,)
                    )
                    conn.commit()
                    conn.close()
                    st.rerun()

    st.write("")
