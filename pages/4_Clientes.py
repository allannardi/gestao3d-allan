import streamlit as st
from html import escape
from datetime import date

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
from components.item_results import carregar_resultados_cliente
from components.auth import require_login
from database import conectar, inicializar_banco
from components.formatters import data_br



@st.cache_data(ttl=3600, show_spinner=False)
def carregar_css_base_cache():
    with open("assets/style.css", encoding="utf-8") as f:
        return f.read()


def moeda(valor):
    valor = valor if valor is not None else 0
    return f"R$ {valor:.2f}".replace(".", ",")


def moeda_md(valor):
    return moeda(valor).replace("$", "\\$")


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

        nome_edit = st.text_input(
            "Nome",
            value=cliente[1],
            help="Campo obrigatório. Use o nome pelo qual você identifica o cliente."
        )

        tipos_lista = ["Pessoa Física", "Pessoa Jurídica"]

        tipo_edit = st.selectbox(
            "Tipo",
            tipos_lista,
            index=tipos_lista.index(cliente[2]) if cliente[2] in tipos_lista else 0,
            help="Escolha Pessoa Física para clientes comuns e Pessoa Jurídica para empresas."
        )

        documento_edit = st.text_input(
            "CPF / CNPJ",
            value=cliente[3] if cliente[3] else "",
            help="Opcional. Preencha apenas se você quiser manter esse dado no cadastro."
        )

        telefone_edit = st.text_input(
            "Telefone / WhatsApp",
            value=cliente[4] if cliente[4] else "",
            help="Opcional, mas recomendado para contato e entrega."
        )

        email_edit = st.text_input(
            "E-mail",
            value=cliente[5] if cliente[5] else "",
            help="Opcional. Útil para clientes empresariais, orçamentos ou comprovantes."
        )

        mobile_form_step("2. Contato e localização", "Preencha WhatsApp, e-mail, cidade, estado e origem.")

        col_form1, col_form2 = st.columns(2)

        with col_form1:
            cidade_edit = st.text_input(
                "Cidade",
                value=cliente[6] if cliente[6] else "",
                help="Opcional. Ajuda a organizar entregas e entender a localização dos clientes."
            )

            instagram_edit = st.text_input(
                "Instagram",
                value=cliente[8] if cliente[8] else "",
                help="Opcional. Use para registrar o @ do cliente."
            )

        with col_form2:
            estado_edit = st.text_input(
                "Estado",
                value=cliente[7] if cliente[7] else "",
                help="Opcional. Ex.: SP, RJ, MG."
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
                index=origem_lista.index(cliente[9]) if cliente[9] in origem_lista else 0,
                help="Informe como o cliente chegou até você."
            )

        status_lista = ["Ativo", "Inativo"]

        status_edit = st.selectbox(
            "Status",
            status_lista,
            index=status_lista.index(cliente[11]) if cliente[11] in status_lista else 0
        )

        observacoes_edit = st.text_area(
            "Observações",
            value=cliente[10] if cliente[10] else "",
            help="Opcional. Registre preferências, endereço combinado, histórico ou detalhes importantes."
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


def cliente_mobile_form_css():
    st.markdown(
        """
        <style>
            .g3d-mobile-form-step {
                display: none;
            }

            @media (max-width: 768px) {

            @media (min-width: 769px) {
                .g3d-mobile-form-step {
                    display: block !important;
                    background: linear-gradient(180deg, #FFFFFF 0%, #FBFDFE 100%);
                    border: 1px solid rgba(185, 205, 220, 0.82);
                    border-left: 4px solid #0C65AA;
                    border-radius: 17px;
                    padding: 13px 15px;
                    margin: 18px 0 12px 0;
                    box-shadow: 0 10px 24px rgba(10, 26, 92, 0.045);
                    font-family: 'Barlow', system-ui, sans-serif;
                }

                .g3d-mobile-form-step strong {
                    display: block;
                    font-size: 11px;
                    font-weight: 800;
                    color: #100690;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    margin-bottom: 5px;
                    line-height: 1.1;
                }

                .g3d-mobile-form-step span {
                    display: block;
                    font-size: 12px;
                    font-weight: 600;
                    color: #5C6C74;
                    line-height: 1.28;
                }

                .stFormSubmitButton button {
                    background: linear-gradient(135deg, #0A1A5C 0%, #0C65AA 100%) !important;
                    color: #FFFFFF !important;
                    border-color: #0C65AA !important;
                    min-height: 48px !important;
                    border-radius: 15px !important;
                    font-size: 15px !important;
                    font-weight: 800 !important;
                    box-shadow: 0 10px 26px rgba(12, 101, 170, 0.18) !important;
                    margin-top: 8px !important;
                }
            }

                .g3d-mobile-form-step {
                    display: block !important;
                    background: #FFFFFF;
                    border: 1px solid #DEE9EF;
                    border-left: 4px solid #0C65AA;
                    border-radius: 16px;
                    padding: 12px 13px;
                    margin: 16px 0 10px 0;
                    box-shadow: 0 8px 20px rgba(10, 26, 92, 0.04);
                    font-family: 'Barlow', system-ui, sans-serif;
                }

                .g3d-mobile-form-step strong {
                    display: block;
                    font-size: 11px;
                    font-weight: 800;
                    color: #100690;
                    text-transform: uppercase;
                    letter-spacing: 1.8px;
                    margin-bottom: 5px;
                    line-height: 1.1;
                }

                .g3d-mobile-form-step span {
                    display: block;
                    font-size: 12px;
                    font-weight: 500;
                    color: #5C6C74;
                    line-height: 1.28;
                }

                div[data-testid="stTextInput"],
                div[data-testid="stSelectbox"],
                div[data-testid="stTextArea"] {
                    margin-bottom: 0.45rem !important;
                }

                div[data-testid="stTextInput"] label,
                div[data-testid="stSelectbox"] label,
                div[data-testid="stTextArea"] label {
                    color: #1E3137 !important;
                    font-weight: 700 !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                }

                .stFormSubmitButton button {
                    background: #0C65AA !important;
                    color: #FFFFFF !important;
                    border-color: #0C65AA !important;
                    min-height: 52px !important;
                    border-radius: 16px !important;
                    font-size: 15px !important;
                    font-weight: 800 !important;
                    box-shadow: 0 10px 26px rgba(12, 101, 170, 0.22) !important;
                    margin-top: 8px !important;
                    width: 100% !important;
                }

                .stFormSubmitButton button:before {
                    content: "✓ ";
                    font-weight: 800;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def mobile_form_step(titulo, subtitulo):
    html = f"""
    <div class="g3d-mobile-form-step">
        <strong>{escape(str(titulo))}</strong>
        <span>{escape(str(subtitulo))}</span>
    </div>
    """

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)


def exibir_resultados_cliente(cliente_id):
    resultados = carregar_resultados_cliente(cliente_id)

    small_section("Resultados do cliente")

    col_r1, col_r2, col_r3, col_r4 = st.columns(4)

    with col_r1:
        kpi_card("Pedidos", str(resultados["pedidos_total"]), "pedidos vinculados", "blue")

    with col_r2:
        kpi_card("Em aberto", str(resultados["pedidos_abertos"]), "aguardando ação", "orange")

    with col_r3:
        kpi_card("Faturamento", moeda(resultados["faturamento"]), "pedidos não cancelados", "green")

    with col_r4:
        kpi_card("Lucro", moeda(resultados["lucro"]), "estimado", "green" if resultados["lucro"] >= 0 else "red")

    col_r5, col_r6 = st.columns(2)

    with col_r5:
        st.write(f"**Quantidade total vendida:** {resultados['quantidade_total']:.0f} un.")

    with col_r6:
        st.write(f"**Ticket médio:** {moeda(resultados['ticket_medio'])}")

    small_section("Pedidos deste cliente")

    if resultados["pedidos"]:
        for pedido in resultados["pedidos"][:8]:
            total_fmt = moeda_md(pedido["total"])
            lucro_fmt = moeda_md(pedido["lucro"])

            st.write(
                f"- **{pedido['codigo']}** | "
                f"{pedido['peca_codigo']} - {pedido['peca_nome']} | "
                f"{pedido['quantidade']:.0f} un | "
                f"{pedido['status']} | "
                f"{total_fmt} | "
                f"Lucro: {lucro_fmt}"
            )

        if len(resultados["pedidos"]) > 8:
            st.caption(f"Mostrando os 8 pedidos mais recentes de {len(resultados['pedidos'])} pedidos vinculados.")
    else:
        st.caption("Este cliente ainda não possui pedidos vinculados.")


st.markdown(f"<style>{carregar_css_base_cache()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()
sidebar()
mobile_bottom_nav("clientes")
inject_desktop_visual()
mobile_summary_css("clientes")


@st.dialog("Ajuda - Clientes")
def ajuda_clientes():
    st.markdown(
        """
        Use esta tela para organizar os clientes e facilitar a criação de pedidos.

        **Campo obrigatório:** apenas o nome do cliente é essencial.

        Os demais dados são opcionais, mas ajudam na operação:
        - telefone ou Instagram para contato;
        - cidade/estado para entrega;
        - origem para saber de onde veio o cliente;
        - observações para preferências, recorrência ou combinados.
        """
    )

header_with_help("Clientes", "Cadastro e gestão dos clientes da Gestão 3D", ajuda_clientes, key="ajuda_clientes_link")


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


with st.container(key="clientes_mobile_resumo"):
    render_mobile_summary(
        hero_label="Base de clientes",
        hero_value=f"{total_clientes} clientes",
        hero_subtitle=f"{clientes_ativos} ativos · {clientes_pf} PF · {clientes_pj} PJ",
        kpis=[
            {"titulo": "Ativos", "valor": clientes_ativos, "subtitulo": "disponíveis", "cor": "#1F8A4C"},
            {"titulo": "Pessoa Física", "valor": clientes_pf, "subtitulo": "clientes individuais", "cor": "#B85C20"},
            {"titulo": "Pessoa Jurídica", "valor": clientes_pj, "subtitulo": "empresas", "cor": "#0C65AA"},
            {"titulo": "Total", "valor": total_clientes, "subtitulo": "cadastros", "cor": "#100690"},
        ],
        note="<strong>Atalho:</strong> use o botão <strong>+ Novo Cliente</strong> abaixo para registrar um novo contato.",
    )

with st.container(key="clientes_desktop_resumo"):
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
    "Adicione clientes para vincular pedidos, produção e faturamento"
)

st.caption("Dica: apenas o nome é obrigatório. WhatsApp, Instagram e cidade ajudam na operação, mas podem ser preenchidos depois.")


if "mostrar_form_cliente" not in st.session_state:
    st.session_state["mostrar_form_cliente"] = False


if primary_button("+ Novo Cliente", "btn_novo_cliente"):
    st.session_state["mostrar_form_cliente"] = not st.session_state["mostrar_form_cliente"]


if st.session_state["mostrar_form_cliente"]:

    small_section("Novo Cliente")

    with st.form("novo_cliente"):

        mobile_form_step("1. Dados principais", "Informe nome, tipo e documento do cliente.")

        nome = st.text_input(
            "Nome do Cliente",
            help="Campo obrigatório. Use o nome pelo qual você identifica o cliente no atendimento."
        )

        tipo = st.selectbox(
            "Tipo",
            ["Pessoa Física", "Pessoa Jurídica"],
            help="Escolha Pessoa Física para clientes comuns e Pessoa Jurídica para empresas."
        )

        documento = st.text_input(
            "CPF / CNPJ",
            help="Opcional. Preencha apenas se você quiser manter esse dado no cadastro."
        )

        mobile_form_step("2. Contato e localização", "Preencha WhatsApp, e-mail, cidade, estado e origem.")

        col_form1, col_form2 = st.columns(2)

        with col_form1:
            telefone = st.text_input(
                "Telefone / WhatsApp",
                help="Opcional, mas recomendado. Facilita contato para entrega, confirmação ou recompra."
            )
            cidade = st.text_input(
                "Cidade",
                help="Opcional. Ajuda a organizar entregas e entender a localização dos clientes."
            )
            instagram = st.text_input(
                "Instagram",
                help="Opcional. Use para registrar o @ do cliente quando o atendimento vier pelo Instagram."
            )

        with col_form2:
            email = st.text_input(
                "E-mail",
                help="Opcional. Útil para clientes empresariais, orçamentos ou comprovantes."
            )
            estado = st.text_input(
                "Estado",
                help="Opcional. Ex.: SP, RJ, MG."
            )
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
                ],
                help="Informe como o cliente chegou até você. Isso ajuda a entender os canais que mais geram venda."
            )

        mobile_form_step("3. Observações", "Registre informações importantes para atendimento futuro.")

        observacoes = st.text_area(
            "Observações",
            help="Opcional. Registre preferências, endereço combinado, histórico de atendimento ou detalhes importantes."
        )

        salvar = st.form_submit_button("Salvar Cliente")

    if salvar:

        if not nome:
            st.warning("Informe o nome do cliente.")

        else:
            if not telefone and not email and not instagram:
                st.info("Dica: o cliente será salvo, mas depois vale cadastrar algum contato como WhatsApp, e-mail ou Instagram.")

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

            st.success(f"Cliente {codigo} cadastrado com sucesso! Ele já pode ser usado em novos pedidos.")
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

clientes = paginar_itens(
    clientes,
    "clientes",
    opcoes=(10, 25, 50, 100),
    nome_item="clientes"
)


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
    data_cadastro = data_br(c[13])

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

            mostrar_resultados_key = f"mostrar_resultados_cliente_{cliente_id}"

            if secondary_button("Carregar resultados do cliente", f"carregar_resultados_cliente_{cliente_id}"):
                st.session_state[mostrar_resultados_key] = True

            if st.session_state.get(mostrar_resultados_key, False):
                exibir_resultados_cliente(cliente_id)
            else:
                st.caption("Os resultados deste cliente serão carregados somente quando você clicar no botão acima.")

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
