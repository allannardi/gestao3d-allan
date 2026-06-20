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


def garantir_colunas_pecas():
    conn = conectar()
    colunas = conn.execute("PRAGMA table_info(pecas)").fetchall()
    nomes_colunas = [coluna[1] for coluna in colunas]

    if "quantidade_lote" not in nomes_colunas:
        conn.execute("ALTER TABLE pecas ADD COLUMN quantidade_lote INTEGER DEFAULT 1")

    conn.commit()
    conn.close()


def gerar_codigo_peca(conn):
    ultimo = conn.execute("""
        SELECT MAX(id)
        FROM pecas
    """).fetchone()[0]

    proximo = 1 if ultimo is None else ultimo + 1
    return f"PEC-{proximo:04d}"


def carregar_acessorios_da_peca(conn, peca_id):
    return conn.execute("""
    SELECT
        a.id,
        a.nome,
        a.custo_unitario,
        pa.quantidade
    FROM peca_acessorios pa
    LEFT JOIN acessorios a ON pa.acessorio_id = a.id
    WHERE pa.peca_id = ?
    """, (peca_id,)).fetchall()


def calcular_custos(
    peso_g,
    tempo_impressao_h,
    embalagem_custo,
    custo_grama,
    acessorios_selecionados,
    energia_hora,
    depreciacao_hora,
    margem_padrao,
    meta_lucro_hora,
    quantidade_lote=1
):
    quantidade = int(quantidade_lote) if quantidade_lote else 1
    if quantidade <= 0:
        quantidade = 1

    custo_material = peso_g * custo_grama
    custo_energia = tempo_impressao_h * energia_hora
    custo_depreciacao = tempo_impressao_h * depreciacao_hora
    custo_acessorios = sum(valor * qtd for _, valor, qtd in acessorios_selecionados)

    custo_total_lote = (
        custo_material
        + custo_energia
        + custo_depreciacao
        + embalagem_custo
        + custo_acessorios
    )

    preco_sugerido_lote = custo_total_lote * (1 + margem_padrao / 100)
    lucro_lote = preco_sugerido_lote - custo_total_lote

    custo_unitario = custo_total_lote / quantidade
    preco_unitario = preco_sugerido_lote / quantidade
    lucro_unitario = lucro_lote / quantidade
    peso_unitario = peso_g / quantidade
    tempo_unitario = tempo_impressao_h / quantidade if quantidade > 0 else 0

    lucro_percentual = (lucro_lote / custo_total_lote) * 100 if custo_total_lote > 0 else 0
    lucro_hora = lucro_lote / tempo_impressao_h if tempo_impressao_h > 0 else 0

    if lucro_hora >= meta_lucro_hora:
        status = "Recomendado"
        cor = "green"
    elif lucro_hora >= meta_lucro_hora * 0.6:
        status = "Atenção"
        cor = "orange"
    else:
        status = "Baixa rentabilidade"
        cor = "red"

    return {
        "quantidade": quantidade,
        "material": custo_material,
        "energia": custo_energia,
        "depreciacao": custo_depreciacao,
        "acessorios": custo_acessorios,
        "embalagem": embalagem_custo,
        "total": custo_total_lote,
        "preco": preco_sugerido_lote,
        "lucro": lucro_lote,
        "lucro_percentual": lucro_percentual,
        "lucro_hora": lucro_hora,
        "custo_unitario": custo_unitario,
        "preco_unitario": preco_unitario,
        "lucro_unitario": lucro_unitario,
        "peso_unitario": peso_unitario,
        "tempo_unitario": tempo_unitario,
        "status": status,
        "cor": cor
    }


def duplicar_peca(peca_id):
    conn = conectar()

    peca = conn.execute("""
    SELECT
        nome,
        categoria,
        peso_g,
        tempo_impressao_h,
        tempo_pos_processamento_min,
        filamento_id,
        embalagem_custo,
        link_stl,
        link_modelo,
        pasta_google_drive,
        observacoes,
        COALESCE(quantidade_lote, 1)
    FROM pecas
    WHERE id = ?
    """, (peca_id,)).fetchone()

    if peca is None:
        conn.close()
        return None

    codigo = gerar_codigo_peca(conn)

    cursor = conn.execute("""
    INSERT INTO pecas
    (
        codigo,
        nome,
        categoria,
        peso_g,
        tempo_impressao_h,
        tempo_pos_processamento_min,
        filamento_id,
        embalagem_custo,
        link_stl,
        link_modelo,
        pasta_google_drive,
        observacoes,
        quantidade_lote
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        codigo,
        peca[0],
        peca[1],
        peca[2],
        peca[3],
        peca[4],
        peca[5],
        peca[6],
        peca[7],
        peca[8],
        peca[9],
        peca[10],
        peca[11]
    ))

    nova_peca_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    acessorios = conn.execute("""
    SELECT
        acessorio_id,
        quantidade
    FROM peca_acessorios
    WHERE peca_id = ?
    """, (peca_id,)).fetchall()

    for acessorio in acessorios:
        conn.execute("""
        INSERT INTO peca_acessorios
        (
            peca_id,
            acessorio_id,
            quantidade
        )
        VALUES (?, ?, ?)
        """, (
            nova_peca_id,
            acessorio[0],
            acessorio[1]
        ))

    conn.commit()
    conn.close()

    return nova_peca_id


def excluir_peca(peca_id):
    conn = conectar()

    conn.execute(
        "DELETE FROM peca_acessorios WHERE peca_id = ?",
        (peca_id,)
    )

    conn.execute(
        "DELETE FROM pecas WHERE id = ?",
        (peca_id,)
    )

    conn.commit()
    conn.close()


@st.dialog("Editar Peça")
def editar_peca_modal(peca_id_edit):
    conn = conectar()

    peca_edit = conn.execute("""
    SELECT
        id,
        nome,
        categoria,
        peso_g,
        tempo_impressao_h,
        tempo_pos_processamento_min,
        filamento_id,
        embalagem_custo,
        link_stl,
        link_modelo,
        pasta_google_drive,
        observacoes,
        COALESCE(quantidade_lote, 1)
    FROM pecas
    WHERE id = ?
    """, (peca_id_edit,)).fetchone()

    acessorios_edit = carregar_acessorios_da_peca(conn, peca_id_edit)
    conn.close()

    if peca_edit is None:
        st.warning("Peça não encontrada para edição.")
        return

    small_section("Dados da peça")

    acessorios_por_id = {
        a[0]: {
            "nome": a[1],
            "custo": a[2],
            "quantidade": a[3]
        }
        for a in acessorios_edit
    }

    col_edit, col_resumo_edit = st.columns([2, 1])

    with col_edit:

        nome_edit = st.text_input("Nome da Peça", value=peca_edit[1], key=f"modal_edit_nome_{peca_id_edit}")

        categorias_lista = [
            "Chaveiro",
            "Decoração",
            "Organizador",
            "Suporte",
            "Brinquedo",
            "Outro"
        ]

        categoria_edit = st.selectbox(
            "Categoria",
            categorias_lista,
            index=categorias_lista.index(peca_edit[2]) if peca_edit[2] in categorias_lista else 5,
            key=f"modal_edit_categoria_{peca_id_edit}"
        )

        filamento_opcoes_edit = {
            f"{f[1]} - {f[2]} ({f[3]} {f[4]})": f
            for f in filamentos_todos
        }

        filamento_keys_edit = list(filamento_opcoes_edit.keys())
        index_filamento_edit = 0

        for idx, item in enumerate(filamento_keys_edit):
            if filamento_opcoes_edit[item][0] == peca_edit[6]:
                index_filamento_edit = idx
                break

        filamento_selecionado_edit = st.selectbox(
            "Filamento padrão",
            filamento_keys_edit,
            index=index_filamento_edit,
            key=f"modal_edit_filamento_{peca_id_edit}"
        )

        filamento_dados_edit = filamento_opcoes_edit[filamento_selecionado_edit]

        quantidade_lote_edit = st.number_input(
            "Quantidade produzida no lote",
            min_value=1,
            value=int(peca_edit[12]) if peca_edit[12] else 1,
            step=1,
            key=f"modal_edit_quantidade_{peca_id_edit}"
        )

        peso_edit = st.number_input(
            "Peso total do lote (g)",
            min_value=0.0,
            value=float(peca_edit[3]) if peca_edit[3] else 0.0,
            step=1.0,
            key=f"modal_edit_peso_{peca_id_edit}"
        )

        tempo_edit = st.number_input(
            "Tempo total de impressão do lote (horas)",
            min_value=0.0,
            value=float(peca_edit[4]) if peca_edit[4] else 0.0,
            step=0.25,
            key=f"modal_edit_tempo_{peca_id_edit}"
        )

        tempo_pos_edit = st.number_input(
            "Tempo de pós-processamento do lote (minutos)",
            min_value=0.0,
            value=float(peca_edit[5]) if peca_edit[5] else 0.0,
            step=1.0,
            key=f"modal_edit_pos_{peca_id_edit}"
        )

        embalagem_edit = st.number_input(
            "Custo de embalagem do lote (R$)",
            min_value=0.0,
            value=float(peca_edit[7]) if peca_edit[7] else 0.0,
            step=0.01,
            key=f"modal_edit_embalagem_{peca_id_edit}"
        )

        small_section("Acessórios do lote")
        st.caption("Informe a quantidade total de acessórios usados no lote completo.")

        acessorios_selecionados_edit = []

        for a in acessorios:
            ja_usava = a[0] in acessorios_por_id

            usar_edit = st.checkbox(
                f"{a[1]} - {a[2]} | {moeda(a[3])}",
                value=ja_usava,
                key=f"modal_edit_usar_acessorio_{peca_id_edit}_{a[0]}"
            )

            if usar_edit:
                qtd_padrao = (
                    float(acessorios_por_id[a[0]]["quantidade"])
                    if ja_usava
                    else float(quantidade_lote_edit)
                )

                qtd_edit = st.number_input(
                    f"Quantidade total de {a[2]} no lote",
                    min_value=0.0,
                    value=qtd_padrao,
                    step=1.0,
                    key=f"modal_edit_qtd_acessorio_{peca_id_edit}_{a[0]}"
                )

                acessorios_selecionados_edit.append((a[0], a[3], qtd_edit))

        small_section("Arquivos e links")

        link_stl_edit = st.text_input(
            "Link do STL / Arquivo",
            value=peca_edit[8] if peca_edit[8] else "",
            key=f"modal_edit_link_stl_{peca_id_edit}"
        )

        link_modelo_edit = st.text_input(
            "Link do modelo na internet",
            value=peca_edit[9] if peca_edit[9] else "",
            key=f"modal_edit_link_modelo_{peca_id_edit}"
        )

        pasta_drive_edit = st.text_input(
            "Pasta Google Drive",
            value=peca_edit[10] if peca_edit[10] else "",
            key=f"modal_edit_drive_{peca_id_edit}"
        )

        observacoes_edit = st.text_area(
            "Observações",
            value=peca_edit[11] if peca_edit[11] else "",
            key=f"modal_edit_obs_{peca_id_edit}"
        )

    custos_edit = calcular_custos(
        peso_edit,
        tempo_edit,
        embalagem_edit,
        filamento_dados_edit[5],
        acessorios_selecionados_edit,
        energia_hora,
        depreciacao_hora,
        margem_padrao,
        meta_lucro_hora,
        quantidade_lote_edit
    )

    with col_resumo_edit:
        small_section("Resumo editado")

        kpi_card("Quantidade", str(custos_edit["quantidade"]), "unidades no lote", "blue")
        kpi_card("Custo unitário", moeda(custos_edit["custo_unitario"]), "por peça", "orange")
        kpi_card("Preço unitário", moeda(custos_edit["preco_unitario"]), "sugerido por peça", "green")
        kpi_card(
            "Lucro/Hora",
            f"R$ {custos_edit['lucro_hora']:.2f}/h".replace(".", ","),
            custos_edit["status"],
            custos_edit["cor"]
        )

    col_salvar, col_cancelar = st.columns(2)

    with col_salvar:
        salvar_edicao = primary_button("Salvar Alterações", f"modal_salvar_edicao_peca_{peca_id_edit}")

    with col_cancelar:
        cancelar_edicao = secondary_button("Cancelar", f"modal_cancelar_edicao_peca_{peca_id_edit}")

    if cancelar_edicao:
        st.rerun()

    if salvar_edicao:
        if not nome_edit:
            st.warning("Informe o nome da peça.")
        else:
            conn = conectar()

            conn.execute("""
            UPDATE pecas
            SET
                nome = ?,
                categoria = ?,
                peso_g = ?,
                tempo_impressao_h = ?,
                tempo_pos_processamento_min = ?,
                filamento_id = ?,
                embalagem_custo = ?,
                link_stl = ?,
                link_modelo = ?,
                pasta_google_drive = ?,
                observacoes = ?,
                quantidade_lote = ?
            WHERE id = ?
            """,
            (
                nome_edit,
                categoria_edit,
                peso_edit,
                tempo_edit,
                tempo_pos_edit,
                filamento_dados_edit[0],
                embalagem_edit,
                link_stl_edit,
                link_modelo_edit,
                pasta_drive_edit,
                observacoes_edit,
                quantidade_lote_edit,
                peca_id_edit
            ))

            conn.execute(
                "DELETE FROM peca_acessorios WHERE peca_id = ?",
                (peca_id_edit,)
            )

            for acessorio_id, _, quantidade in acessorios_selecionados_edit:
                conn.execute("""
                INSERT INTO peca_acessorios
                (
                    peca_id,
                    acessorio_id,
                    quantidade
                )
                VALUES (?, ?, ?)
                """,
                (
                    peca_id_edit,
                    acessorio_id,
                    quantidade
                ))

            conn.commit()
            conn.close()

            st.success("Peça atualizada com sucesso!")
            st.rerun()


with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()
sidebar()
header("Peças", "Biblioteca de modelos e cálculo de rentabilidade")


conn = conectar()

config = conn.execute("""
SELECT
    energia_hora,
    depreciacao_hora,
    margem_padrao,
    meta_lucro_hora
FROM configuracoes
LIMIT 1
""").fetchone()

energia_hora = config[0]
depreciacao_hora = config[1]
margem_padrao = config[2]
meta_lucro_hora = config[3]

filamentos = conn.execute("""
SELECT
    id,
    codigo,
    nome,
    material,
    cor,
    custo_grama
FROM filamentos
WHERE status IS NULL OR status = 'Ativo'
ORDER BY id DESC
""").fetchall()

filamentos_todos = conn.execute("""
SELECT
    id,
    codigo,
    nome,
    material,
    cor,
    custo_grama
FROM filamentos
ORDER BY id DESC
""").fetchall()

acessorios = conn.execute("""
SELECT
    id,
    codigo,
    nome,
    custo_unitario
FROM acessorios
ORDER BY nome ASC
""").fetchall()

pecas_base = conn.execute("""
SELECT
    p.id,
    p.codigo,
    p.nome,
    p.categoria,
    p.peso_g,
    p.tempo_impressao_h,
    p.embalagem_custo,
    COALESCE(p.quantidade_lote, 1),
    f.codigo,
    f.nome,
    f.custo_grama
FROM pecas p
LEFT JOIN filamentos f ON p.filamento_id = f.id
ORDER BY p.id DESC
""").fetchall()

conn.close()


total_pecas = len(pecas_base)
total_recomendadas = 0
soma_lucro_hora = 0
soma_custo_unitario = 0

for p in pecas_base:
    conn = conectar()
    acessorios_peca = carregar_acessorios_da_peca(conn, p[0])
    conn.close()

    acessorios_calc = [
        (a[0], a[2] if a[2] else 0, a[3] if a[3] else 0)
        for a in acessorios_peca
    ]

    custos = calcular_custos(
        p[4] if p[4] else 0,
        p[5] if p[5] else 0,
        p[6] if p[6] else 0,
        p[10] if p[10] else 0,
        acessorios_calc,
        energia_hora,
        depreciacao_hora,
        margem_padrao,
        meta_lucro_hora,
        p[7] if p[7] else 1
    )

    soma_lucro_hora += custos["lucro_hora"]
    soma_custo_unitario += custos["custo_unitario"]

    if custos["status"] == "Recomendado":
        total_recomendadas += 1

lucro_hora_medio = soma_lucro_hora / total_pecas if total_pecas > 0 else 0
custo_unitario_medio = soma_custo_unitario / total_pecas if total_pecas > 0 else 0


col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card("Peças", str(total_pecas), "modelos cadastrados", "blue")

with col2:
    kpi_card("Recomendadas", str(total_recomendadas), "acima da meta", "green")

with col3:
    kpi_card("Custo unit. médio", moeda(custo_unitario_medio), "média por unidade", "orange")

with col4:
    kpi_card(
        "Lucro/Hora médio",
        f"R$ {lucro_hora_medio:.2f}/h".replace(".", ","),
        f"meta: R$ {meta_lucro_hora:.2f}/h".replace(".", ","),
        "gray"
    )


section_title(
    "Cadastro de Peças",
    "Cadastre modelos, calcule custos por lote e acompanhe os valores unitários"
)


if "mostrar_form_peca" not in st.session_state:
    st.session_state["mostrar_form_peca"] = False


if primary_button("+ Nova Peça", "btn_nova_peca"):
    st.session_state["mostrar_form_peca"] = not st.session_state["mostrar_form_peca"]
    st.session_state.pop("editar_peca", None)


if st.session_state["mostrar_form_peca"]:

    if not filamentos:
        st.warning("Cadastre pelo menos um filamento ativo antes de criar uma peça.")

    else:

        small_section("Nova Peça")

        col_form, col_resumo = st.columns([2, 1])

        with col_form:

            nome = st.text_input("Nome da Peça", key="nova_peca_nome")

            categoria = st.selectbox(
                "Categoria",
                [
                    "Chaveiro",
                    "Decoração",
                    "Organizador",
                    "Suporte",
                    "Brinquedo",
                    "Outro"
                ],
                key="nova_peca_categoria"
            )

            filamento_opcoes = {
                f"{f[1]} - {f[2]} ({f[3]} {f[4]})": f
                for f in filamentos
            }

            filamento_selecionado = st.selectbox(
                "Filamento padrão",
                list(filamento_opcoes.keys()),
                key="nova_peca_filamento"
            )

            filamento_dados = filamento_opcoes[filamento_selecionado]

            quantidade_lote = st.number_input(
                "Quantidade produzida no lote",
                min_value=1,
                value=1,
                step=1,
                key="nova_peca_quantidade"
            )

            peso_g = st.number_input(
                "Peso total do lote (g)",
                min_value=0.0,
                value=0.0,
                step=1.0,
                key="nova_peca_peso"
            )

            tempo_impressao_h = st.number_input(
                "Tempo total de impressão do lote (horas)",
                min_value=0.0,
                value=0.0,
                step=0.25,
                key="nova_peca_tempo"
            )

            tempo_pos = st.number_input(
                "Tempo de pós-processamento do lote (minutos)",
                min_value=0.0,
                value=0.0,
                step=1.0,
                key="nova_peca_pos"
            )

            embalagem_custo = st.number_input(
                "Custo de embalagem do lote (R$)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                key="nova_peca_embalagem"
            )

            small_section("Acessórios do lote")
            st.caption("Informe a quantidade total de acessórios usados no lote completo.")

            acessorios_selecionados = []

            for a in acessorios:
                usar = st.checkbox(
                    f"{a[1]} - {a[2]} | {moeda(a[3])}",
                    key=f"nova_usar_acessorio_{a[0]}"
                )

                if usar:
                    qtd = st.number_input(
                        f"Quantidade total de {a[2]} no lote",
                        min_value=0.0,
                        value=float(quantidade_lote),
                        step=1.0,
                        key=f"nova_qtd_acessorio_{a[0]}"
                    )

                    acessorios_selecionados.append((a[0], a[3], qtd))

            small_section("Arquivos e links")

            link_stl = st.text_input("Link do STL / Arquivo", key="nova_peca_link_stl")
            link_modelo = st.text_input("Link do modelo na internet", key="nova_peca_link_modelo")
            pasta_drive = st.text_input("Pasta Google Drive", key="nova_peca_drive")
            observacoes = st.text_area("Observações", key="nova_peca_obs")

        custos = calcular_custos(
            peso_g,
            tempo_impressao_h,
            embalagem_custo,
            filamento_dados[5],
            acessorios_selecionados,
            energia_hora,
            depreciacao_hora,
            margem_padrao,
            meta_lucro_hora,
            quantidade_lote
        )

        with col_resumo:

            small_section("Resumo do lote")

            kpi_card("Quantidade", str(custos["quantidade"]), "unidades no lote", "blue")
            kpi_card("Custo lote", moeda(custos["total"]), "custo total", "orange")
            kpi_card("Preço lote", moeda(custos["preco"]), "sugerido total", "green")
            kpi_card(
                "Lucro/Hora",
                f"R$ {custos['lucro_hora']:.2f}/h".replace(".", ","),
                custos["status"],
                custos["cor"]
            )

            small_section("Resumo unitário")

            kpi_card("Peso unitário", f"{custos['peso_unitario']:.1f} g", "por peça", "gray")
            kpi_card("Custo unitário", moeda(custos["custo_unitario"]), "por peça", "orange")
            kpi_card("Preço unitário", moeda(custos["preco_unitario"]), "sugerido por peça", "green")
            kpi_card("Lucro unitário", moeda(custos["lucro_unitario"]), "por peça", custos["cor"])

        if primary_button("Salvar Peça", "salvar_nova_peca"):

            if not nome:
                st.warning("Informe o nome da peça.")

            else:
                conn = conectar()
                codigo = gerar_codigo_peca(conn)

                cursor = conn.cursor()

                cursor.execute("""
                INSERT INTO pecas
                (
                    codigo,
                    nome,
                    categoria,
                    peso_g,
                    tempo_impressao_h,
                    tempo_pos_processamento_min,
                    filamento_id,
                    embalagem_custo,
                    link_stl,
                    link_modelo,
                    pasta_google_drive,
                    observacoes,
                    quantidade_lote
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    codigo,
                    nome,
                    categoria,
                    peso_g,
                    tempo_impressao_h,
                    tempo_pos,
                    filamento_dados[0],
                    embalagem_custo,
                    link_stl,
                    link_modelo,
                    pasta_drive,
                    observacoes,
                    quantidade_lote
                ))

                peca_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

                for acessorio_id, _, quantidade in acessorios_selecionados:
                    cursor.execute("""
                    INSERT INTO peca_acessorios
                    (
                        peca_id,
                        acessorio_id,
                        quantidade
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        peca_id,
                        acessorio_id,
                        quantidade
                    ))

                conn.commit()
                conn.close()

                st.success("Peça cadastrada com sucesso!")
                st.session_state["mostrar_form_peca"] = False
                st.rerun()


section_title(
    "Peças cadastradas",
    "Consulte custos por lote, valores unitários, rentabilidade e acessórios usados"
)


busca = searchbar(
    placeholder="Pesquisar por código, nome, categoria ou filamento...",
    key="buscar_peca"
)


conn = conectar()

pecas = conn.execute("""
SELECT
    p.id,
    p.codigo,
    p.nome,
    p.categoria,
    p.peso_g,
    p.tempo_impressao_h,
    p.tempo_pos_processamento_min,
    p.embalagem_custo,
    p.link_stl,
    p.link_modelo,
    p.pasta_google_drive,
    p.observacoes,
    COALESCE(p.quantidade_lote, 1),
    f.codigo,
    f.nome,
    f.custo_grama
FROM pecas p
LEFT JOIN filamentos f ON p.filamento_id = f.id
WHERE p.nome LIKE ?
   OR p.codigo LIKE ?
   OR p.categoria LIKE ?
   OR f.nome LIKE ?
   OR f.codigo LIKE ?
ORDER BY p.id DESC
""", (
    f"%{busca}%",
    f"%{busca}%",
    f"%{busca}%",
    f"%{busca}%",
    f"%{busca}%"
)).fetchall()

conn.close()


for p in pecas:

    peca_id = p[0]
    codigo = p[1]
    nome = p[2]
    categoria = p[3] if p[3] else "-"
    peso = p[4] if p[4] else 0
    tempo_impressao = p[5] if p[5] else 0
    tempo_pos = p[6] if p[6] else 0
    embalagem = p[7] if p[7] else 0
    link_stl = p[8] if p[8] else ""
    link_modelo = p[9] if p[9] else ""
    pasta_drive = p[10] if p[10] else ""
    observacoes = p[11] if p[11] else ""
    quantidade_lote = p[12] if p[12] else 1
    filamento_codigo = p[13] if p[13] else "-"
    filamento_nome = p[14] if p[14] else "-"
    custo_grama = p[15] if p[15] else 0

    conn = conectar()
    acessorios_peca = carregar_acessorios_da_peca(conn, peca_id)
    conn.close()

    acessorios_calc = [
        (a[0], a[2] if a[2] else 0, a[3] if a[3] else 0)
        for a in acessorios_peca
    ]

    custos = calcular_custos(
        peso,
        tempo_impressao,
        embalagem,
        custo_grama,
        acessorios_calc,
        energia_hora,
        depreciacao_hora,
        margem_padrao,
        meta_lucro_hora,
        quantidade_lote
    )

    with st.container(border=True):

        item_card(
            codigo=codigo,
            titulo=nome,
            subtitulo=f"{categoria} • {quantidade_lote} un • {filamento_codigo} - {filamento_nome}",
            cor=custos["cor"]
        )

        with st.expander("Detalhes, custos e ações"):

            col_d1, col_d2, col_d3, col_d4 = st.columns(4)

            with col_d1:
                st.write(f"**Status:** {custos['status']}")
                st.write(f"**Categoria:** {categoria}")

            with col_d2:
                st.write(f"**Quantidade:** {quantidade_lote} un")
                st.write(f"**Peso lote:** {peso:.1f} g")

            with col_d3:
                st.write(f"**Tempo lote:** {tempo_impressao:.2f} h")
                st.write(f"**Filamento:** {filamento_codigo}")

            with col_d4:
                st.write(f"**Preço unit.:** {moeda(custos['preco_unitario'])}")
                st.write(f"**Lucro/Hora:** R$ {custos['lucro_hora']:.2f}/h".replace(".", ","))

            small_section("Resumo unitário")

            col_u1, col_u2, col_u3, col_u4, col_u5 = st.columns(5)

            with col_u1:
                st.write(f"**Peso:** {custos['peso_unitario']:.1f} g")

            with col_u2:
                st.write(f"**Tempo:** {custos['tempo_unitario']:.2f} h")

            with col_u3:
                st.write(f"**Custo:** {moeda(custos['custo_unitario'])}")

            with col_u4:
                st.write(f"**Preço:** {moeda(custos['preco_unitario'])}")

            with col_u5:
                st.write(f"**Lucro:** {moeda(custos['lucro_unitario'])}")

            small_section("Resumo do lote")

            col_l1, col_l2, col_l3, col_l4, col_l5 = st.columns(5)

            with col_l1:
                st.write(f"**Material:** {moeda(custos['material'])}")

            with col_l2:
                st.write(f"**Energia:** {moeda(custos['energia'])}")

            with col_l3:
                st.write(f"**Depreciação:** {moeda(custos['depreciacao'])}")

            with col_l4:
                st.write(f"**Acessórios:** {moeda(custos['acessorios'])}")

            with col_l5:
                st.write(f"**Total:** {moeda(custos['total'])}")

            col_lp1, col_lp2, col_lp3 = st.columns(3)

            with col_lp1:
                st.write(f"**Preço lote:** {moeda(custos['preco'])}")

            with col_lp2:
                st.write(f"**Lucro lote:** {moeda(custos['lucro'])}")

            with col_lp3:
                st.write(f"**Lucro %:** {custos['lucro_percentual']:.0f}%")

            if acessorios_peca:
                small_section("Acessórios usados no lote")

                for a in acessorios_peca:
                    st.write(
                        f"- **{a[1]}** | Quantidade total: {a[3]} | Unitário: {moeda(a[2])}"
                    )

            if link_stl or link_modelo or pasta_drive:
                small_section("Arquivos e links")

                if link_stl:
                    st.write(f"**STL / Arquivo:** {link_stl}")

                if link_modelo:
                    st.write(f"**Modelo:** {link_modelo}")

                if pasta_drive:
                    st.write(f"**Google Drive:** {pasta_drive}")

            if observacoes:
                st.write(f"**Observações:** {observacoes}")

            col_btn1, col_btn2, col_btn3 = st.columns(3)

            with col_btn1:
                if secondary_button("Editar", f"editar_peca_{peca_id}"):
                    editar_peca_modal(peca_id)

            with col_btn2:
                if secondary_button("Duplicar", f"duplicar_peca_{peca_id}"):
                    nova_peca_id = duplicar_peca(peca_id)

                    if nova_peca_id:
                        editar_peca_modal(nova_peca_id)
                    else:
                        st.error("Não foi possível duplicar esta peça.")

            with col_btn3:
                if danger_button("Excluir", f"excluir_peca_{peca_id}"):
                    excluir_peca(peca_id)
                    st.rerun()

    st.write("")
