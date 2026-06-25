import streamlit as st
from html import escape

from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.desktop_visual import inject_desktop_visual
from components.mobile_summary import mobile_summary_css, render_mobile_summary
from components.header import header
from components.kpi import kpi_card
from components.card import item_card
from components.button import primary_button, secondary_button, danger_button
from components.searchbar import searchbar
from components.pagination import paginar_itens
from components.section import section_title, small_section
from components.auth import require_login
from database import conectar, inicializar_banco
from components.formatters import data_br



def limpar_cache_dados():
    """
    Limpa cache de dados após gravações.

    Mantém o app rápido nos reruns, mas evita que cadastros recém-salvos
    fiquem temporariamente escondidos por causa do cache.
    """
    try:
        st.cache_data.clear()
    except Exception:
        pass


@st.cache_data(ttl=3600, show_spinner=False)
def carregar_css_base_cache():
    with open("assets/style.css", encoding="utf-8") as f:
        return f.read()


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


def carregar_filamentos_da_peca(conn, peca_id):
    return conn.execute("""
    SELECT
        pf.id,
        f.id,
        f.codigo,
        f.nome,
        f.material,
        f.cor,
        f.custo_grama,
        pf.peso_g,
        pf.observacao
    FROM peca_filamentos pf
    LEFT JOIN filamentos f ON pf.filamento_id = f.id
    WHERE pf.peca_id = ?
    ORDER BY pf.id ASC
    """, (peca_id,)).fetchall()


def salvar_filamentos_da_peca(conn, peca_id, filamentos_selecionados):
    conn.execute("DELETE FROM peca_filamentos WHERE peca_id = ?", (peca_id,))

    for filamento_id, custo_grama, peso_g, observacao in filamentos_selecionados:
        if filamento_id and peso_g and peso_g > 0:
            conn.execute("""
            INSERT INTO peca_filamentos
            (
                peca_id,
                filamento_id,
                peso_g,
                observacao
            )
            VALUES (?, ?, ?, ?)
            """, (
                peca_id,
                filamento_id,
                peso_g,
                observacao
            ))


def montar_filamentos_lote(prefixo, filamentos_disponiveis, registros_existentes=None):
    registros_existentes = registros_existentes or []

    if not filamentos_disponiveis:
        return []

    if f"{prefixo}_qtd_filamentos" not in st.session_state:
        st.session_state[f"{prefixo}_qtd_filamentos"] = max(1, len(registros_existentes))

    filamento_opcoes = {
        f"{f[1]} - {f[2]} ({f[3]} {f[4]})": f
        for f in filamentos_disponiveis
    }

    labels = list(filamento_opcoes.keys())
    filamentos_lote = []

    for idx in range(st.session_state[f"{prefixo}_qtd_filamentos"]):
        existente = registros_existentes[idx] if idx < len(registros_existentes) else None

        index_padrao = 0
        peso_padrao = 0.0
        observacao_padrao = "Principal" if idx == 0 else "Adicional"

        if existente:
            existente_filamento_id = existente[1]
            peso_padrao = float(existente[7] if existente[7] else 0)
            observacao_padrao = existente[8] if existente[8] else observacao_padrao

            for label_idx, label in enumerate(labels):
                if filamento_opcoes[label][0] == existente_filamento_id:
                    index_padrao = label_idx
                    break

        col_f1, col_f2, col_f3 = st.columns([2.2, 1, 1])

        with col_f1:
            filamento_label = st.selectbox(
                f"Filamento {idx + 1}",
                labels,
                index=index_padrao,
                key=f"{prefixo}_filamento_{idx}"
            )

        with col_f2:
            peso_filamento = st.number_input(
                "Peso no lote (g)",
                min_value=0.0,
                value=peso_padrao,
                step=1.0,
                key=f"{prefixo}_peso_filamento_{idx}"
            )

        with col_f3:
            observacao_filamento = st.text_input(
                "Uso / cor",
                value=observacao_padrao,
                placeholder="Ex.: base, detalhe azul",
                key=f"{prefixo}_obs_filamento_{idx}"
            )

        filamento = filamento_opcoes[filamento_label]
        filamentos_lote.append((
            filamento[0],
            filamento[5] if filamento[5] else 0,
            peso_filamento,
            observacao_filamento
        ))

    if secondary_button("+ Adicionar mais um filamento", f"{prefixo}_add_filamento"):
        st.session_state[f"{prefixo}_qtd_filamentos"] += 1
        limpar_cache_dados()
        st.rerun()

    return filamentos_lote


def montar_registros_filamentos_existentes(filamentos_registrados, filamento_id_padrao, peso_total_padrao, filamentos_disponiveis):
    if filamentos_registrados:
        return filamentos_registrados

    for f in filamentos_disponiveis:
        if f[0] == filamento_id_padrao:
            return [
                (
                    None,
                    f[0],
                    f[1],
                    f[2],
                    f[3],
                    f[4],
                    f[5] if len(f) > 5 else 0,
                    peso_total_padrao,
                    "Principal"
                )
            ]

    return []


def resumo_filamentos_lote(filamentos_lote):
    total_peso = sum(f[2] if f[2] else 0 for f in filamentos_lote)
    total_custo = sum((f[1] if f[1] else 0) * (f[2] if f[2] else 0) for f in filamentos_lote)
    return total_peso, total_custo


def carregar_categorias_pecas(conn):
    categorias = conn.execute("""
    SELECT nome
    FROM categorias_pecas
    ORDER BY nome ASC
    """).fetchall()

    return [c[0] for c in categorias]


def salvar_categoria_se_nova(conn, categoria):
    categoria = (categoria or "").strip()

    if categoria:
        conn.execute(
            "INSERT OR IGNORE INTO categorias_pecas (nome) VALUES (?)",
            (categoria,)
        )

    return categoria


@st.cache_data(ttl=30, show_spinner=False)
def carregar_base_pecas_cache():
    """
    Carrega dados da página de Peças em lote.

    Reduz o problema do Streamlit de reexecutar a página a cada clique:
    em vez de consultar acessórios/filamentos item por item, carregamos tudo
    de uma vez e usamos dicionários em memória.
    """
    conn = conectar()

    config = conn.execute("""
    SELECT
        energia_hora,
        depreciacao_hora,
        margem_padrao,
        meta_lucro_hora,
        COALESCE(custo_pos_processamento_hora, 0)
    FROM configuracoes
    LIMIT 1
    """).fetchone()

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

    categorias = carregar_categorias_pecas(conn)

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
        f.custo_grama,
        p.tempo_pos_processamento_min
    FROM pecas p
    LEFT JOIN filamentos f ON p.filamento_id = f.id
    ORDER BY p.id DESC
    """).fetchall()

    pecas_completas = conn.execute("""
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
    ORDER BY p.id DESC
    """).fetchall()

    peca_ids = [p[0] for p in pecas_base]

    acessorios_por_peca = {}
    filamentos_por_peca = {}

    if peca_ids:
        placeholders = ",".join(["?"] * len(peca_ids))

        acessorios_rows = conn.execute(f"""
        SELECT
            pa.peca_id,
            a.id,
            a.nome,
            a.custo_unitario,
            pa.quantidade
        FROM peca_acessorios pa
        LEFT JOIN acessorios a ON pa.acessorio_id = a.id
        WHERE pa.peca_id IN ({placeholders})
        """, peca_ids).fetchall()

        for row in acessorios_rows:
            peca_id = row[0]
            acessorios_por_peca.setdefault(peca_id, []).append(tuple(row[1:]))

        filamentos_rows = conn.execute(f"""
        SELECT
            pf.peca_id,
            pf.id,
            f.id,
            f.codigo,
            f.nome,
            f.material,
            f.cor,
            f.custo_grama,
            pf.peso_g,
            pf.observacao
        FROM peca_filamentos pf
        LEFT JOIN filamentos f ON pf.filamento_id = f.id
        WHERE pf.peca_id IN ({placeholders})
        ORDER BY pf.id ASC
        """, peca_ids).fetchall()

        for row in filamentos_rows:
            peca_id = row[0]
            filamentos_por_peca.setdefault(peca_id, []).append(tuple(row[1:]))

    conn.close()

    return {
        "config": tuple(config) if config else (0.15, 0.75, 150, 5, 0),
        "filamentos": [tuple(f) for f in filamentos],
        "filamentos_todos": [tuple(f) for f in filamentos_todos],
        "acessorios": [tuple(a) for a in acessorios],
        "categorias_pecas": list(categorias),
        "pecas_base": [tuple(p) for p in pecas_base],
        "pecas_completas": [tuple(p) for p in pecas_completas],
        "acessorios_por_peca": acessorios_por_peca,
        "filamentos_por_peca": filamentos_por_peca,
    }



def carregar_pedidos_da_peca(peca_id):
    conn = conectar()

    pedidos = conn.execute("""
    SELECT
        ped.codigo,
        c.nome,
        ped.quantidade,
        ped.valor_unitario,
        ped.desconto,
        ped.frete,
        ped.status,
        ped.data_pedido
    FROM pedidos ped
    LEFT JOIN clientes c ON ped.cliente_id = c.id
    WHERE ped.peca_id = ?
    ORDER BY ped.id DESC
    """, (peca_id,)).fetchall()

    conn.close()
    return pedidos


def calcular_custos(
    peso_g,
    tempo_impressao_h,
    tempo_pos_processamento_min,
    embalagem_custo,
    custo_grama,
    acessorios_selecionados,
    energia_hora,
    depreciacao_hora,
    custo_pos_processamento_hora,
    margem_padrao,
    meta_lucro_hora,
    quantidade_lote=1,
    filamentos_lote=None
):
    quantidade = int(quantidade_lote) if quantidade_lote else 1
    if quantidade <= 0:
        quantidade = 1

    tempo_pos_h = (tempo_pos_processamento_min if tempo_pos_processamento_min else 0) / 60
    tempo_total_h = (tempo_impressao_h if tempo_impressao_h else 0) + tempo_pos_h

    if filamentos_lote:
        peso_g = sum(f[2] if f[2] else 0 for f in filamentos_lote)
        custo_material = sum((f[1] if f[1] else 0) * (f[2] if f[2] else 0) for f in filamentos_lote)
    else:
        custo_material = peso_g * custo_grama

    custo_energia = tempo_impressao_h * energia_hora
    custo_depreciacao = tempo_impressao_h * depreciacao_hora
    custo_pos_processamento = tempo_pos_h * custo_pos_processamento_hora
    custo_acessorios = sum(valor * qtd for _, valor, qtd in acessorios_selecionados)

    custo_total_lote = (
        custo_material
        + custo_energia
        + custo_depreciacao
        + custo_pos_processamento
        + embalagem_custo
        + custo_acessorios
    )

    preco_sugerido_lote = custo_total_lote * (1 + margem_padrao / 100)
    lucro_lote = preco_sugerido_lote - custo_total_lote

    custo_unitario = custo_total_lote / quantidade
    preco_unitario = preco_sugerido_lote / quantidade
    lucro_unitario = lucro_lote / quantidade
    peso_unitario = peso_g / quantidade
    tempo_unitario = tempo_total_h / quantidade if quantidade > 0 else 0

    lucro_percentual = (lucro_lote / custo_total_lote) * 100 if custo_total_lote > 0 else 0
    lucro_hora = lucro_lote / tempo_total_h if tempo_total_h > 0 else 0

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
        "pos_processamento": custo_pos_processamento,
        "tempo_pos_h": tempo_pos_h,
        "tempo_total_h": tempo_total_h,
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

    filamentos_peca = conn.execute("""
    SELECT
        filamento_id,
        peso_g,
        observacao
    FROM peca_filamentos
    WHERE peca_id = ?
    """, (peca_id,)).fetchall()

    for filamento in filamentos_peca:
        conn.execute("""
        INSERT INTO peca_filamentos
        (
            peca_id,
            filamento_id,
            peso_g,
            observacao
        )
        VALUES (?, ?, ?, ?)
        """, (
            nova_peca_id,
            filamento[0],
            filamento[1],
            filamento[2]
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
        "DELETE FROM peca_filamentos WHERE peca_id = ?",
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
    filamentos_edit = carregar_filamentos_da_peca(conn, peca_id_edit)
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

        categorias_lista = categorias_pecas if categorias_pecas else ["Outro"]

        if peca_edit[2] and peca_edit[2] not in categorias_lista:
            categorias_lista = categorias_lista + [peca_edit[2]]

        opcoes_categoria_edit = categorias_lista + ["+ Adicionar nova categoria"]

        categoria_opcao_edit = st.selectbox(
            "Categoria",
            opcoes_categoria_edit,
            index=opcoes_categoria_edit.index(peca_edit[2]) if peca_edit[2] in opcoes_categoria_edit else 0,
            key=f"modal_edit_categoria_{peca_id_edit}"
        )

        if categoria_opcao_edit == "+ Adicionar nova categoria":
            categoria_edit = st.text_input(
                "Nova categoria",
                value="",
                placeholder="Ex.: Religião",
                key=f"modal_edit_nova_categoria_{peca_id_edit}"
            ).strip()
        else:
            categoria_edit = categoria_opcao_edit

        quantidade_lote_edit = st.number_input(
            "Quantidade produzida no lote",
            min_value=1,
            value=int(peca_edit[12]) if peca_edit[12] else 1,
            step=1,
            key=f"modal_edit_quantidade_{peca_id_edit}"
        )

        small_section("Filamentos de referência para cálculo")
        st.caption("Informe o peso total de referência usado no lote completo.")

        registros_filamentos_edit = montar_registros_filamentos_existentes(
            filamentos_edit,
            peca_edit[6],
            float(peca_edit[3]) if peca_edit[3] else 0.0,
            filamentos_todos
        )

        filamentos_lote_edit = montar_filamentos_lote(
            f"modal_edit_peca_{peca_id_edit}",
            filamentos_todos,
            registros_filamentos_edit
        )

        peso_edit, custo_material_edit = resumo_filamentos_lote(filamentos_lote_edit)

        st.info(
            f"Peso total calculado do lote: {peso_edit:.1f} g | "
            f"Custo de material: {moeda(custo_material_edit)}"
        )

        filamento_principal_id_edit = (
            filamentos_lote_edit[0][0]
            if filamentos_lote_edit
            else peca_edit[6]
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
        tempo_pos_edit,
        embalagem_edit,
        0,
        acessorios_selecionados_edit,
        energia_hora,
        depreciacao_hora,
        custo_pos_processamento_hora,
        margem_padrao,
        meta_lucro_hora,
        quantidade_lote_edit,
        filamentos_lote_edit
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
        limpar_cache_dados()
        st.rerun()

    if salvar_edicao:
        if not nome_edit:
            st.warning("Informe o nome da peça.")
        else:
            conn = conectar()
            categoria_edit = salvar_categoria_se_nova(conn, categoria_edit)

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
                filamento_principal_id_edit,
                embalagem_edit,
                link_stl_edit,
                link_modelo_edit,
                pasta_drive_edit,
                observacoes_edit,
                quantidade_lote_edit,
                peca_id_edit
            ))

            salvar_filamentos_da_peca(
                conn,
                peca_id_edit,
                filamentos_lote_edit
            )

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
            limpar_cache_dados()
            st.rerun()


def peca_mobile_form_css():
    st.markdown(
        """
        <style>
            .g3d-mobile-form-step,
            .st-key-nova_peca_resumo_mobile {
                display: none;
            }

            @media (min-width: 769px) {
                .st-key-nova_peca_resumo_mobile {
                    display: none !important;
                }

                .st-key-nova_peca_resumo_desktop {
                    display: block !important;
                }


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

                .st-key-salvar_nova_peca button {
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

            @media (max-width: 768px) {
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

                .st-key-nova_peca_resumo_desktop {
                    display: none !important;
                }

                .st-key-nova_peca_resumo_mobile {
                    display: block !important;
                }

                .g3d-nova-peca-resumo {
                    background: linear-gradient(135deg, #0A1A5C 0%, #0C65AA 58%, #58C3F0 100%);
                    border-radius: 22px;
                    padding: 16px 16px;
                    color: #FFFFFF;
                    box-shadow: 0 14px 34px rgba(10, 26, 92, 0.18);
                    margin: 14px 0 16px 0;
                    overflow: hidden;
                    position: relative;
                    font-family: 'Barlow', system-ui, sans-serif;
                }

                .g3d-nova-peca-resumo:after {
                    content: "";
                    width: 118px;
                    height: 118px;
                    border-radius: 50%;
                    background: rgba(255,255,255,0.12);
                    position: absolute;
                    right: -40px;
                    top: -52px;
                }

                .g3d-nova-peca-label {
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    opacity: 0.86;
                    margin-bottom: 8px;
                }

                .g3d-nova-peca-total {
                    font-size: 31px;
                    font-weight: 800;
                    line-height: 1;
                    margin-bottom: 8px;
                }

                .g3d-nova-peca-sub {
                    font-size: 13px;
                    font-weight: 500;
                    opacity: 0.92;
                    line-height: 1.25;
                }

                .g3d-nova-peca-mini-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin-top: 12px;
                }

                .g3d-nova-peca-mini {
                    background: rgba(255,255,255,0.14);
                    border: 1px solid rgba(255,255,255,0.20);
                    border-radius: 15px;
                    padding: 10px 10px;
                }

                .g3d-nova-peca-mini strong {
                    display: block;
                    font-size: 15px;
                    font-weight: 800;
                    line-height: 1.05;
                    color: #FFFFFF;
                    margin-bottom: 5px;
                }

                .g3d-nova-peca-mini span {
                    display: block;
                    font-size: 10px;
                    font-weight: 700;
                    opacity: 0.88;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }

                div[data-testid="stSelectbox"],
                div[data-testid="stNumberInput"],
                div[data-testid="stTextInput"],
                div[data-testid="stTextArea"],
                div[data-testid="stCheckbox"] {
                    margin-bottom: 0.45rem !important;
                }

                div[data-testid="stSelectbox"] label,
                div[data-testid="stNumberInput"] label,
                div[data-testid="stTextInput"] label,
                div[data-testid="stTextArea"] label,
                div[data-testid="stCheckbox"] label {
                    color: #1E3137 !important;
                    font-weight: 700 !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                }

                .st-key-salvar_nova_peca button {
                    background: #0C65AA !important;
                    color: #FFFFFF !important;
                    border-color: #0C65AA !important;
                    min-height: 52px !important;
                    border-radius: 16px !important;
                    font-size: 15px !important;
                    font-weight: 800 !important;
                    box-shadow: 0 10px 26px rgba(12, 101, 170, 0.22) !important;
                    margin-top: 8px !important;
                }

                .st-key-salvar_nova_peca button:before {
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


def render_nova_peca_mobile_resumo(custos):
    html = f"""
    <div class="g3d-nova-peca-resumo">
        <div class="g3d-nova-peca-label">Resumo da peça</div>
        <div class="g3d-nova-peca-total">{escape(moeda(custos["preco_unitario"]))}</div>
        <div class="g3d-nova-peca-sub">
            preço unitário sugerido · lucro/hora {escape(f"R$ {custos['lucro_hora']:.2f}/h".replace(".", ","))}
        </div>

        <div class="g3d-nova-peca-mini-grid">
            <div class="g3d-nova-peca-mini">
                <strong>{escape(moeda(custos["custo_unitario"]))}</strong>
                <span>Custo unit.</span>
            </div>
            <div class="g3d-nova-peca-mini">
                <strong>{escape(moeda(custos["preco"]))}</strong>
                <span>Preço lote</span>
            </div>
            <div class="g3d-nova-peca-mini">
                <strong>{escape(f"{custos['peso_unitario']:.1f} g")}</strong>
                <span>Peso unit.</span>
            </div>
            <div class="g3d-nova-peca-mini">
                <strong>{escape(moeda(custos["lucro_unitario"]))}</strong>
                <span>Lucro unit.</span>
            </div>
        </div>
    </div>
    """

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)


st.markdown(f"<style>{carregar_css_base_cache()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()
sidebar()
mobile_bottom_nav("pecas")
inject_desktop_visual()
peca_mobile_form_css()
mobile_summary_css("pecas")
header("Peças", "Biblioteca de modelos e cálculo de rentabilidade")


base_pecas = carregar_base_pecas_cache()

config = base_pecas["config"]
energia_hora = config[0]
depreciacao_hora = config[1]
margem_padrao = config[2]
meta_lucro_hora = config[3]
custo_pos_processamento_hora = config[4] if len(config) > 4 else 0

filamentos = base_pecas["filamentos"]
filamentos_todos = base_pecas["filamentos_todos"]
acessorios = base_pecas["acessorios"]
categorias_pecas = base_pecas["categorias_pecas"]
pecas_base = base_pecas["pecas_base"]
pecas_completas = base_pecas["pecas_completas"]
acessorios_por_peca = base_pecas["acessorios_por_peca"]
filamentos_por_peca = base_pecas["filamentos_por_peca"]


total_pecas = len(pecas_base)
total_recomendadas = 0
soma_lucro_hora = 0
soma_custo_unitario = 0

for p in pecas_base:
    acessorios_peca = acessorios_por_peca.get(p[0], [])
    filamentos_peca = filamentos_por_peca.get(p[0], [])

    acessorios_calc = [
        (a[0], a[2] if a[2] else 0, a[3] if a[3] else 0)
        for a in acessorios_peca
    ]

    filamentos_calc = [
        (f[1], f[6] if f[6] else 0, f[7] if f[7] else 0, f[8] if f[8] else "")
        for f in filamentos_peca
    ]

    custos = calcular_custos(
        p[4] if p[4] else 0,
        p[5] if p[5] else 0,
        p[11] if len(p) > 11 and p[11] else 0,
        p[6] if p[6] else 0,
        p[10] if p[10] else 0,
        acessorios_calc,
        energia_hora,
        depreciacao_hora,
        custo_pos_processamento_hora,
        margem_padrao,
        meta_lucro_hora,
        p[7] if p[7] else 1,
        filamentos_calc
    )

    soma_lucro_hora += custos["lucro_hora"]
    soma_custo_unitario += custos["custo_unitario"]

    if custos["status"] == "Recomendado":
        total_recomendadas += 1

lucro_hora_medio = soma_lucro_hora / total_pecas if total_pecas > 0 else 0
custo_unitario_medio = soma_custo_unitario / total_pecas if total_pecas > 0 else 0


with st.container(key="pecas_mobile_resumo"):
    render_mobile_summary(
        hero_label="Biblioteca de peças",
        hero_value=f"{total_pecas} peças",
        hero_subtitle=f"{total_recomendadas} acima da meta · lucro/hora médio R$ {lucro_hora_medio:.2f}/h".replace(".", ","),
        kpis=[
            {"titulo": "Recomendadas", "valor": total_recomendadas, "subtitulo": "acima da meta", "cor": "#1F8A4C"},
            {"titulo": "Custo médio", "valor": moeda(custo_unitario_medio), "subtitulo": "por unidade", "cor": "#B85C20"},
            {"titulo": "Lucro/Hora", "valor": f"R$ {lucro_hora_medio:.2f}/h".replace(".", ","), "subtitulo": "média das peças", "cor": "#0C65AA"},
            {"titulo": "Meta", "valor": f"R$ {meta_lucro_hora:.2f}/h".replace(".", ","), "subtitulo": "referência mínima", "cor": "#100690"},
        ],
        note="<strong>Atalho:</strong> use o botão <strong>+ Nova Peça</strong> abaixo para cadastrar um novo modelo.",
    )

with st.container(key="pecas_desktop_resumo"):
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

            mobile_form_step("1. Identificação", "Informe nome, categoria e quantidade produzida no lote.")

            nome = st.text_input("Nome da Peça", key="nova_peca_nome")

            opcoes_categoria = (categorias_pecas if categorias_pecas else ["Outro"]) + ["+ Adicionar nova categoria"]

            categoria_opcao = st.selectbox(
                "Categoria",
                opcoes_categoria,
                key="nova_peca_categoria"
            )

            if categoria_opcao == "+ Adicionar nova categoria":
                categoria = st.text_input(
                    "Nova categoria",
                    placeholder="Ex.: Religião",
                    key="nova_peca_categoria_nova"
                ).strip()
            else:
                categoria = categoria_opcao

            quantidade_lote = st.number_input(
                "Quantidade produzida no lote",
                min_value=1,
                value=1,
                step=1,
                key="nova_peca_quantidade"
            )

            mobile_form_step("2. Filamentos e cores", "Cadastre a referência de material para cálculo previsto. A cor real será confirmada no pedido.")

            small_section("Filamentos de referência para cálculo")
            st.caption("Informe o peso total de referência usado no lote completo.")

            filamentos_lote = montar_filamentos_lote(
                "nova_peca",
                filamentos
            )

            peso_g, custo_material_lote = resumo_filamentos_lote(filamentos_lote)

            st.info(
                f"Peso total calculado do lote: {peso_g:.1f} g | "
                f"Custo de material: {moeda(custo_material_lote)}"
            )

            filamento_principal_id = (
                filamentos_lote[0][0]
                if filamentos_lote
                else filamentos[0][0]
            )

            mobile_form_step("3. Produção e embalagem", "Informe tempo total de impressão, pós-processamento e embalagem.")

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

            mobile_form_step("4. Acessórios", "Inclua argolas, embalagens, imãs ou outros itens usados no lote.")

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

            mobile_form_step("5. Arquivos e observações", "Salve links, arquivos e informações úteis para produção.")

            small_section("Arquivos e links")

            link_stl = st.text_input("Link do STL / Arquivo", key="nova_peca_link_stl")
            link_modelo = st.text_input("Link do modelo na internet", key="nova_peca_link_modelo")
            pasta_drive = st.text_input("Pasta Google Drive", key="nova_peca_drive")
            observacoes = st.text_area("Observações", key="nova_peca_obs")

        custos = calcular_custos(
            peso_g,
            tempo_impressao_h,
            tempo_pos,
            embalagem_custo,
            0,
            acessorios_selecionados,
            energia_hora,
            depreciacao_hora,
            custo_pos_processamento_hora,
            margem_padrao,
            meta_lucro_hora,
            quantidade_lote,
            filamentos_lote
        )

        with col_resumo:

            with st.container(key="nova_peca_resumo_mobile"):
                render_nova_peca_mobile_resumo(custos)

            with st.container(key="nova_peca_resumo_desktop"):
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
                categoria = salvar_categoria_se_nova(conn, categoria)
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
                    filamento_principal_id,
                    embalagem_custo,
                    link_stl,
                    link_modelo,
                    pasta_drive,
                    observacoes,
                    quantidade_lote
                ))

                peca_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

                salvar_filamentos_da_peca(
                    conn,
                    peca_id,
                    filamentos_lote
                )

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
                st.session_state.pop("nova_peca_qtd_filamentos", None)
                limpar_cache_dados()
                st.rerun()


section_title(
    "Peças cadastradas",
    "Consulte custos por lote, valores unitários, rentabilidade e acessórios usados"
)


busca = searchbar(
    placeholder="Pesquisar por código, nome, categoria ou filamento...",
    key="buscar_peca"
)


termo_busca = (busca or "").strip().lower()

if termo_busca:
    pecas = [
        p for p in pecas_completas
        if termo_busca in str(p[1] or "").lower()
        or termo_busca in str(p[2] or "").lower()
        or termo_busca in str(p[3] or "").lower()
        or termo_busca in str(p[13] or "").lower()
        or termo_busca in str(p[14] or "").lower()
    ]
else:
    pecas = pecas_completas

pecas = paginar_itens(
    pecas,
    "pecas",
    opcoes=(10, 25, 50, 100),
    nome_item="peças"
)


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

    acessorios_peca = acessorios_por_peca.get(peca_id, [])
    filamentos_peca = filamentos_por_peca.get(peca_id, [])

    acessorios_calc = [
        (a[0], a[2] if a[2] else 0, a[3] if a[3] else 0)
        for a in acessorios_peca
    ]

    filamentos_calc = [
        (f[1], f[6] if f[6] else 0, f[7] if f[7] else 0, f[8] if f[8] else "")
        for f in filamentos_peca
    ]

    custos = calcular_custos(
        peso,
        tempo_impressao,
        tempo_pos,
        embalagem,
        custo_grama,
        acessorios_calc,
        energia_hora,
        depreciacao_hora,
        custo_pos_processamento_hora,
        margem_padrao,
        meta_lucro_hora,
        quantidade_lote,
        filamentos_calc
    )

    with st.container(border=True):

        if filamentos_peca:
            filamento_resumo = (
                f"{len(filamentos_peca)} referências de cálculo"
                if len(filamentos_peca) > 1
                else f"{filamentos_peca[0][2]} - {filamentos_peca[0][3]}"
            )
        else:
            filamento_resumo = f"{filamento_codigo} - {filamento_nome}"

        item_card(
            codigo=codigo,
            titulo=nome,
            subtitulo=f"{categoria} • {quantidade_lote} un • {filamento_resumo}",
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
                st.write(f"**Filamentos:** {filamento_resumo}")

            with col_d4:
                st.write(f"**Preço unit.:** {moeda(custos['preco_unitario'])}")
                st.write(f"**Lucro/Hora:** R$ {custos['lucro_hora']:.2f}/h".replace(".", ","))

            small_section("Resumo unitário")

            col_u1, col_u2, col_u3, col_u4, col_u5 = st.columns(5)

            with col_u1:
                st.write(f"**Peso:** {custos['peso_unitario']:.1f} g")

            with col_u2:
                st.write(f"**Tempo total:** {custos['tempo_unitario']:.2f} h")

            with col_u3:
                st.write(f"**Custo:** {moeda(custos['custo_unitario'])}")

            with col_u4:
                st.write(f"**Preço:** {moeda(custos['preco_unitario'])}")

            with col_u5:
                st.write(f"**Lucro:** {moeda(custos['lucro_unitario'])}")

            small_section("Resumo do lote")

            col_l1, col_l2, col_l3, col_l4, col_l5, col_l6 = st.columns(6)

            with col_l1:
                st.write(f"**Material:** {moeda(custos['material'])}")

            with col_l2:
                st.write(f"**Energia:** {moeda(custos['energia'])}")

            with col_l3:
                st.write(f"**Depreciação:** {moeda(custos['depreciacao'])}")

            with col_l4:
                st.write(f"**Pós-proc.:** {moeda(custos['pos_processamento'])}")

            with col_l5:
                st.write(f"**Acessórios:** {moeda(custos['acessorios'])}")

            with col_l6:
                st.write(f"**Total:** {moeda(custos['total'])}")

            col_lp1, col_lp2, col_lp3 = st.columns(3)

            with col_lp1:
                st.write(f"**Preço lote:** {moeda(custos['preco'])}")

            with col_lp2:
                st.write(f"**Lucro lote:** {moeda(custos['lucro'])}")

            with col_lp3:
                st.write(f"**Lucro %:** {custos['lucro_percentual']:.0f}%")

            if filamentos_peca:
                small_section("Filamentos de referência para cálculo")

                for f in filamentos_peca:
                    peso_filamento = f[7] if f[7] else 0
                    custo_grama_filamento = f[6] if f[6] else 0
                    custo_filamento = peso_filamento * custo_grama_filamento
                    observacao_filamento = f[8] if f[8] else "-"

                    st.write(
                        f"- **{f[2]} - {f[3]}** | {f[4]} {f[5]} | "
                        f"{peso_filamento:.1f} g | {observacao_filamento} | "
                        f"Custo: {moeda(custo_filamento)}"
                    )

            mostrar_pedidos_key = f"mostrar_pedidos_peca_{peca_id}"

            if secondary_button("Carregar pedidos desta peça", f"carregar_pedidos_peca_{peca_id}"):
                st.session_state[mostrar_pedidos_key] = True

            if st.session_state.get(mostrar_pedidos_key, False):
                pedidos_peca = carregar_pedidos_da_peca(peca_id)

                small_section("Pedidos desta peça")

                if pedidos_peca:
                    qtd_vendida = 0
                    faturamento_peca = 0
                    lucro_peca = 0

                    for pedido_peca in pedidos_peca:
                        qtd_pedido = pedido_peca[2] if pedido_peca[2] else 0
                        valor_unitario_pedido = pedido_peca[3] if pedido_peca[3] else 0
                        desconto_pedido = pedido_peca[4] if pedido_peca[4] else 0
                        frete_pedido = pedido_peca[5] if pedido_peca[5] else 0
                        status_pedido = pedido_peca[6] if pedido_peca[6] else "Orçamento"
                        total_pedido_peca = qtd_pedido * valor_unitario_pedido - desconto_pedido + frete_pedido
                        lucro_pedido_peca = total_pedido_peca - (qtd_pedido * custos["custo_unitario"])

                        if status_pedido != "Cancelado":
                            qtd_vendida += qtd_pedido
                            faturamento_peca += total_pedido_peca
                            lucro_peca += lucro_pedido_peca

                    col_ped1, col_ped2, col_ped3, col_ped4 = st.columns(4)

                    with col_ped1:
                        st.write(f"**Pedidos:** {len(pedidos_peca)}")

                    with col_ped2:
                        st.write(f"**Qtd. vendida:** {qtd_vendida:.0f}")

                    with col_ped3:
                        st.write(f"**Faturamento:** {moeda(faturamento_peca)}")

                    with col_ped4:
                        st.write(f"**Lucro:** {moeda(lucro_peca)}")

                    for pedido_peca in pedidos_peca[:5]:
                        qtd_pedido = pedido_peca[2] if pedido_peca[2] else 0
                        valor_unitario_pedido = pedido_peca[3] if pedido_peca[3] else 0
                        desconto_pedido = pedido_peca[4] if pedido_peca[4] else 0
                        frete_pedido = pedido_peca[5] if pedido_peca[5] else 0
                        total_pedido_peca = qtd_pedido * valor_unitario_pedido - desconto_pedido + frete_pedido

                        st.write(
                            f"- **{pedido_peca[0]}** | {pedido_peca[1] or '-'} | "
                            f"{qtd_pedido:.0f} un | {pedido_peca[6]} | {data_br(pedido_peca[7])} | {moeda(total_pedido_peca)}"
                        )
                else:
                    st.caption("Ainda não existem pedidos para esta peça.")
            else:
                st.caption("Os pedidos desta peça serão carregados somente quando você clicar no botão acima.")

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
                    limpar_cache_dados()
                    st.rerun()

    st.write("")
