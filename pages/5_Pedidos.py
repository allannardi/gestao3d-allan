import streamlit as st
from html import escape
from datetime import date

from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.desktop_visual import inject_desktop_visual
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


def garantir_tabelas():
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

    conn.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        cliente_id INTEGER,
        peca_id INTEGER,
        quantidade REAL DEFAULT 1,
        valor_unitario REAL DEFAULT 0,
        desconto REAL DEFAULT 0,
        frete REAL DEFAULT 0,
        status TEXT DEFAULT 'Orçamento',
        canal TEXT,
        data_pedido TEXT,
        data_entrega_prevista TEXT,
        observacoes TEXT
    )
    """)

    colunas_pecas = conn.execute("PRAGMA table_info(pecas)").fetchall()
    nomes_colunas_pecas = [coluna[1] for coluna in colunas_pecas]

    if "quantidade_lote" not in nomes_colunas_pecas:
        conn.execute("ALTER TABLE pecas ADD COLUMN quantidade_lote REAL DEFAULT 1")

    conn.commit()
    conn.close()


def gerar_codigo_cliente(conn):
    ultimo = conn.execute("""
        SELECT MAX(id)
        FROM clientes
    """).fetchone()[0]

    proximo = 1 if ultimo is None else ultimo + 1
    return f"CLI-{proximo:04d}"


def gerar_codigo_pedido(conn):
    ultimo = conn.execute("""
        SELECT MAX(id)
        FROM pedidos
    """).fetchone()[0]

    proximo = 1 if ultimo is None else ultimo + 1
    return f"PED-{proximo:04d}"


@st.cache_data(ttl=30, show_spinner=False)
def carregar_configuracoes():
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

    conn.close()

    return tuple(config) if config else None


@st.cache_data(ttl=30, show_spinner=False)
def carregar_clientes():
    conn = conectar()

    clientes = conn.execute("""
    SELECT
        id,
        codigo,
        nome,
        telefone,
        cidade,
        estado
    FROM clientes
    WHERE status IS NULL OR status = 'Ativo'
    ORDER BY nome ASC
    """).fetchall()

    conn.close()

    return [tuple(c) for c in clientes]


@st.cache_data(ttl=30, show_spinner=False)
def carregar_pecas():
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
        COALESCE(p.quantidade_lote, 1),
        f.codigo,
        f.nome,
        f.custo_grama
    FROM pecas p
    LEFT JOIN filamentos f ON p.filamento_id = f.id
    ORDER BY p.nome ASC
    """).fetchall()

    conn.close()

    return [tuple(p) for p in pecas]


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


def calcular_custo_unitario_peca(peca_id, energia_hora, depreciacao_hora, custo_pos_processamento_hora=0):
    conn = conectar()

    peca = conn.execute("""
    SELECT
        p.peso_g,
        p.tempo_impressao_h,
        p.tempo_pos_processamento_min,
        p.embalagem_custo,
        COALESCE(p.quantidade_lote, 1),
        f.custo_grama
    FROM pecas p
    LEFT JOIN filamentos f ON p.filamento_id = f.id
    WHERE p.id = ?
    """, (peca_id,)).fetchone()

    if peca is None:
        conn.close()
        return {
            "quantidade_lote": 1,
            "peso_unitario": 0,
            "tempo_unitario": 0,
            "custo_lote": 0,
            "custo_unitario": 0,
        }

    acessorios = carregar_acessorios_da_peca(conn, peca_id)
    filamentos_peca = carregar_filamentos_da_peca(conn, peca_id)
    conn.close()

    peso_g = peca[0] if peca[0] else 0
    tempo_h = peca[1] if peca[1] else 0
    tempo_pos_h = (peca[2] if peca[2] else 0) / 60
    embalagem = peca[3] if peca[3] else 0
    quantidade_lote = peca[4] if peca[4] and peca[4] > 0 else 1
    custo_grama = peca[5] if peca[5] else 0

    if filamentos_peca:
        peso_g = sum((f[5] if f[5] else 0) for f in filamentos_peca)
        custo_material = sum((f[4] if f[4] else 0) * (f[5] if f[5] else 0) for f in filamentos_peca)
    else:
        custo_material = peso_g * custo_grama

    custo_energia = tempo_h * energia_hora
    custo_depreciacao = tempo_h * depreciacao_hora
    custo_pos_processamento = tempo_pos_h * custo_pos_processamento_hora
    custo_acessorios = sum((a[2] if a[2] else 0) * (a[3] if a[3] else 0) for a in acessorios)

    custo_lote = custo_material + custo_energia + custo_depreciacao + custo_pos_processamento + embalagem + custo_acessorios
    custo_unitario = custo_lote / quantidade_lote if quantidade_lote > 0 else custo_lote
    peso_unitario = peso_g / quantidade_lote if quantidade_lote > 0 else peso_g
    tempo_total_h = tempo_h + tempo_pos_h
    tempo_unitario = tempo_total_h / quantidade_lote if quantidade_lote > 0 else tempo_total_h

    return {
        "quantidade_lote": quantidade_lote,
        "peso_unitario": peso_unitario,
        "tempo_unitario": tempo_unitario,
        "custo_lote": custo_lote,
        "custo_unitario": custo_unitario,
    }

def calcular_custos_pecas_lote(conn, peca_ids, energia_hora, depreciacao_hora, custo_pos_processamento_hora=0):
    """
    Calcula custos de várias peças em lote.

    Evita consultar filamentos/acessórios repetidamente para cada pedido.
    """
    peca_ids = sorted({int(pid) for pid in peca_ids if pid})

    if not peca_ids:
        return {}

    placeholders = ",".join(["?"] * len(peca_ids))

    pecas = conn.execute(f"""
    SELECT
        p.id,
        p.peso_g,
        p.tempo_impressao_h,
        p.tempo_pos_processamento_min,
        p.embalagem_custo,
        COALESCE(p.quantidade_lote, 1),
        f.custo_grama
    FROM pecas p
    LEFT JOIN filamentos f ON p.filamento_id = f.id
    WHERE p.id IN ({placeholders})
    """, peca_ids).fetchall()

    acessorios_rows = conn.execute(f"""
    SELECT
        pa.peca_id,
        a.custo_unitario,
        pa.quantidade
    FROM peca_acessorios pa
    LEFT JOIN acessorios a ON pa.acessorio_id = a.id
    WHERE pa.peca_id IN ({placeholders})
    """, peca_ids).fetchall()

    filamentos_rows = conn.execute(f"""
    SELECT
        pf.peca_id,
        f.custo_grama,
        pf.peso_g
    FROM peca_filamentos pf
    LEFT JOIN filamentos f ON pf.filamento_id = f.id
    WHERE pf.peca_id IN ({placeholders})
    ORDER BY pf.id ASC
    """, peca_ids).fetchall()

    acessorios_por_peca = {}
    for peca_id, custo_unitario, quantidade in acessorios_rows:
        acessorios_por_peca.setdefault(peca_id, []).append((
            custo_unitario if custo_unitario else 0,
            quantidade if quantidade else 0,
        ))

    filamentos_por_peca = {}
    for peca_id, custo_grama, peso_g in filamentos_rows:
        filamentos_por_peca.setdefault(peca_id, []).append((
            custo_grama if custo_grama else 0,
            peso_g if peso_g else 0,
        ))

    custos = {}

    for peca in pecas:
        peca_id = peca[0]
        peso_g = peca[1] if peca[1] else 0
        tempo_h = peca[2] if peca[2] else 0
        tempo_pos_h = (peca[3] if peca[3] else 0) / 60
        embalagem = peca[4] if peca[4] else 0
        quantidade_lote = peca[5] if peca[5] and peca[5] > 0 else 1
        custo_grama = peca[6] if peca[6] else 0

        filamentos_peca = filamentos_por_peca.get(peca_id, [])
        acessorios_peca = acessorios_por_peca.get(peca_id, [])

        if filamentos_peca:
            peso_g = sum(peso for _, peso in filamentos_peca)
            custo_material = sum(custo * peso for custo, peso in filamentos_peca)
        else:
            custo_material = peso_g * custo_grama

        custo_energia = tempo_h * energia_hora
        custo_depreciacao = tempo_h * depreciacao_hora
        custo_pos_processamento = tempo_pos_h * custo_pos_processamento_hora
        custo_acessorios = sum(custo * quantidade for custo, quantidade in acessorios_peca)

        custo_lote = (
            custo_material
            + custo_energia
            + custo_depreciacao
            + custo_pos_processamento
            + embalagem
            + custo_acessorios
        )

        custos[peca_id] = {
            "quantidade_lote": quantidade_lote,
            "peso_unitario": peso_g / quantidade_lote if quantidade_lote > 0 else peso_g,
            "tempo_unitario": (tempo_h + tempo_pos_h) / quantidade_lote if quantidade_lote > 0 else (tempo_h + tempo_pos_h),
            "custo_lote": custo_lote,
            "custo_unitario": custo_lote / quantidade_lote if quantidade_lote > 0 else custo_lote,
        }

    return custos


def calcular_pedido(peca_id, quantidade, valor_unitario, desconto, frete, energia_hora, depreciacao_hora, custo_peca=None, custo_pos_processamento_hora=0):
    if custo_peca is None:
        custo_peca = calcular_custo_unitario_peca(peca_id, energia_hora, depreciacao_hora, custo_pos_processamento_hora)

    quantidade = quantidade if quantidade else 0
    valor_unitario = valor_unitario if valor_unitario else 0
    desconto = desconto if desconto else 0
    frete = frete if frete else 0

    subtotal = quantidade * valor_unitario
    total = subtotal - desconto + frete
    custo_total = quantidade * custo_peca["custo_unitario"]
    lucro = total - custo_total
    lucro_percentual = (lucro / custo_total) * 100 if custo_total > 0 else 0
    lucro_unitario = lucro / quantidade if quantidade > 0 else 0

    return {
        "custo_unitario": custo_peca["custo_unitario"],
        "peso_unitario": custo_peca["peso_unitario"],
        "tempo_unitario": custo_peca["tempo_unitario"],
        "subtotal": subtotal,
        "total": total,
        "custo_total": custo_total,
        "lucro": lucro,
        "lucro_percentual": lucro_percentual,
        "lucro_unitario": lucro_unitario,
    }


@st.cache_data(ttl=30, show_spinner=False)
def carregar_pedidos_resumo_cache(energia_hora, depreciacao_hora, custo_pos_processamento_hora):
    """
    Carrega e calcula o resumo de pedidos com cache curto.

    Evita recalcular o topo da página a cada clique simples.
    """
    conn = conectar()

    resumo = conn.execute("""
    SELECT
        id,
        peca_id,
        quantidade,
        valor_unitario,
        desconto,
        frete,
        status
    FROM pedidos
    """).fetchall()

    peca_ids_resumo = sorted({item[1] for item in resumo if item[1]})
    custos_pecas_resumo = calcular_custos_pecas_lote(
        conn,
        peca_ids_resumo,
        energia_hora,
        depreciacao_hora,
        custo_pos_processamento_hora
    )

    conn.close()

    total_pedidos = len(resumo)
    pedidos_abertos = 0
    faturamento_total = 0
    lucro_total = 0

    for r in resumo:
        peca_id = r[1]
        quantidade = r[2] if r[2] else 0
        valor_unitario = r[3] if r[3] else 0
        desconto = r[4] if r[4] else 0
        frete = r[5] if r[5] else 0
        status = r[6] if r[6] else "Orçamento"

        calc = calcular_pedido(
            peca_id,
            quantidade,
            valor_unitario,
            desconto,
            frete,
            energia_hora,
            depreciacao_hora,
            custos_pecas_resumo.get(peca_id),
        )

        if status not in ["Entregue", "Cancelado"]:
            pedidos_abertos += 1

        if status != "Cancelado":
            faturamento_total += calc["total"]
            lucro_total += calc["lucro"]

    ticket_medio = faturamento_total / total_pedidos if total_pedidos > 0 else 0

    return {
        "total_pedidos": total_pedidos,
        "pedidos_abertos": pedidos_abertos,
        "faturamento_total": faturamento_total,
        "lucro_total": lucro_total,
        "ticket_medio": ticket_medio,
    }


@st.cache_data(ttl=30, show_spinner=False)
def carregar_pedidos_listagem_cache():
    """
    Carrega pedidos e filamentos das peças em lote.

    Evita nova consulta SQL a cada busca e evita consulta por item dentro da lista.
    """
    conn = conectar()

    pedidos = conn.execute("""
    SELECT
        ped.id,
        ped.codigo,
        ped.cliente_id,
        c.codigo,
        c.nome,
        ped.peca_id,
        pc.codigo,
        pc.nome,
        ped.quantidade,
        ped.valor_unitario,
        ped.desconto,
        ped.frete,
        ped.status,
        ped.canal,
        ped.data_pedido,
        ped.data_entrega_prevista,
        ped.observacoes
    FROM pedidos ped
    LEFT JOIN clientes c ON ped.cliente_id = c.id
    LEFT JOIN pecas pc ON ped.peca_id = pc.id
    ORDER BY ped.id DESC
    """).fetchall()

    peca_ids = sorted({pedido[5] for pedido in pedidos if pedido[5]})
    filamentos_por_peca = {}

    if peca_ids:
        placeholders = ",".join(["?"] * len(peca_ids))

        filamentos_rows = conn.execute(f"""
        SELECT
            pf.peca_id,
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

    return [tuple(p) for p in pedidos], filamentos_por_peca


@st.cache_data(ttl=30, show_spinner=False)
def carregar_custos_pedidos_cache(peca_ids, energia_hora, depreciacao_hora, custo_pos_processamento_hora):
    """
    Calcula custos das peças usadas nos pedidos com cache curto.
    """
    conn = conectar()
    custos = calcular_custos_pecas_lote(
        conn,
        list(peca_ids),
        energia_hora,
        depreciacao_hora,
        custo_pos_processamento_hora
    )
    conn.close()
    return custos



def cor_status(status):
    if status in ["Entregue", "Pronto"]:
        return "green"
    if status in ["Confirmado", "Em Produção"]:
        return "blue"
    if status == "Orçamento":
        return "orange"
    if status == "Cancelado":
        return "red"
    return "gray"


def cor_status_hex(status):
    mapa = {
        "Orçamento": "#B85C20",
        "Confirmado": "#0C65AA",
        "Em Produção": "#100690",
        "Pronto": "#1F8A4C",
        "Entregue": "#1F8A4C",
        "Cancelado": "#D11A2A",
    }
    return mapa.get(status, "#8A8F98")


def pedidos_mobile_css():
    st.markdown(
        """
        <style>
            @media (max-width: 768px) {
                .g3d-pedido-card {
                    border-radius: 18px !important;
                    padding: 15px 15px 14px 15px !important;
                    margin-bottom: 8px !important;
                    box-shadow: 0 8px 22px rgba(10, 26, 92, 0.06) !important;
                }

                .g3d-pedido-top {
                    display: flex !important;
                    align-items: center !important;
                    justify-content: space-between !important;
                    gap: 10px !important;
                    margin-bottom: 10px !important;
                }

                .g3d-pedido-code {
                    font-size: 25px !important;
                    color: #0C65AA !important;
                }

                .g3d-pedido-status {
                    font-size: 10.5px !important;
                    padding: 5px 8px !important;
                    white-space: nowrap !important;
                }

                .g3d-pedido-main {
                    display: block !important;
                }

                .g3d-pedido-piece {
                    font-size: 15.5px !important;
                    line-height: 1.18 !important;
                    margin-bottom: 6px !important;
                }

                .g3d-pedido-client {
                    font-size: 11.5px !important;
                    margin-bottom: 11px !important;
                }

                .g3d-pedido-bottom {
                    display: grid !important;
                    grid-template-columns: 1fr 1fr 1fr !important;
                    gap: 8px !important;
                    margin-top: 10px !important;
                }

                .g3d-pedido-mini {
                    background: #F4F8FB !important;
                    border: 1px solid #DEE9EF !important;
                    border-radius: 13px !important;
                    padding: 9px 8px !important;
                    text-align: center !important;
                }

                .g3d-pedido-mini strong {
                    display: block !important;
                    font-size: 16px !important;
                    font-weight: 800 !important;
                    color: #1E3137 !important;
                    line-height: 1 !important;
                    margin-bottom: 4px !important;
                }

                .g3d-pedido-mini span {
                    display: block !important;
                    font-size: 9.5px !important;
                    font-weight: 800 !important;
                    color: #5C6C74 !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.9px !important;
                    line-height: 1 !important;
                }

                div[data-testid="stExpander"] {
                    border-radius: 16px !important;
                    overflow: hidden !important;
                    margin-bottom: 14px !important;
                }

                div[data-testid="stExpander"] summary p {
                    font-size: 12px !important;
                    font-weight: 800 !important;
                    color: #0C65AA !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def pedido_card(codigo, cliente_nome, peca_codigo, peca_nome, quantidade, status, total, data_pedido="-"):
    cor = cor_status_hex(status)

    codigo = escape(str(codigo))
    cliente_nome = escape(str(cliente_nome))
    peca_codigo = escape(str(peca_codigo))
    peca_nome = escape(str(peca_nome))
    status = escape(str(status))
    data_pedido = escape(data_br(data_pedido))
    total_fmt = escape(moeda(total))

    html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800&display=swap');

    @media (min-width: 769px) {{
        .g3d-pedido-card {{
            position: relative;
            border: 1px solid rgba(185,205,220,0.82) !important;
            border-top: 4px solid {cor} !important;
            border-radius: 20px !important;
            background: linear-gradient(180deg, #FFFFFF 0%, #FBFDFE 100%) !important;
            padding: 16px 17px 15px 17px !important;
            margin-bottom: 6px !important;
            font-family: 'Barlow', system-ui, sans-serif !important;
            box-shadow: 0 12px 28px rgba(10, 26, 92, 0.055);
            overflow: hidden;
        }}

        .g3d-pedido-card:after {{
            content: "";
            position: absolute;
            right: -44px;
            top: -54px;
            width: 118px;
            height: 118px;
            border-radius: 999px;
            background: {cor}10;
        }}

        .g3d-pedido-top {{
            position: relative;
            z-index: 1;
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 12px;
        }}

        .g3d-pedido-code {{
            font-size: 30px !important;
            font-weight: 800 !important;
            color: #0A1A5C !important;
            line-height: 1 !important;
            letter-spacing: -0.6px;
        }}

        .g3d-pedido-status {{
            display: inline-flex !important;
            align-items: center !important;
            gap: 7px !important;
            padding: 6px 10px !important;
            border-radius: 999px !important;
            background: transparent !important;
            border: 1px solid {cor}35 !important;
            color: {cor} !important;
            font-size: 12px !important;
            font-weight: 800 !important;
            white-space: nowrap !important;
        }}

        .g3d-pedido-status span {{
            width: 8px !important;
            height: 8px !important;
            border-radius: 50% !important;
            background: {cor} !important;
            display: inline-block !important;
        }}

        .g3d-pedido-main {{
            position: relative;
            z-index: 1;
        }}

        .g3d-pedido-piece {{
            font-size: 18px !important;
            font-weight: 800 !important;
            color: #0A1A5C !important;
            line-height: 1.18 !important;
            max-width: 100%;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .g3d-pedido-client {{
            margin-top: 5px !important;
            font-size: 12px !important;
            color: #5C6C74 !important;
            font-weight: 600 !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .g3d-pedido-bottom {{
            position: relative;
            z-index: 1;
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            gap: 9px !important;
            margin-top: 14px !important;
        }}

        .g3d-pedido-mini {{
            background: #F4F8FB !important;
            border: 1px solid #DEE9EF !important;
            border-radius: 14px !important;
            padding: 9px 8px !important;
            text-align: center !important;
        }}

        .g3d-pedido-mini strong {{
            display: block !important;
            font-size: 16px !important;
            font-weight: 800 !important;
            color: #0A1A5C !important;
            line-height: 1 !important;
            margin-bottom: 4px !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .g3d-pedido-mini span {{
            display: block !important;
            font-size: 9.5px !important;
            font-weight: 800 !important;
            color: #5C6C74 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.9px !important;
            line-height: 1 !important;
        }}

        .g3d-pedido-peca-codigo {{
            position: relative;
            z-index: 1;
            margin-top: 10px;
            font-size: 11px;
            color: #8A8F98;
            font-weight: 700;
            letter-spacing: 0.8px;
        }}
    }}
</style>

<div class="g3d-pedido-card" style="border:1px solid #DEE9EF;border-top:4px solid {cor};border-radius:14px;background:#FFFFFF;padding:14px 16px;margin-bottom:4px;font-family:'Barlow', system-ui, sans-serif;">
    <div class="g3d-pedido-top">
        <div class="g3d-pedido-code">{codigo}</div>
        <div class="g3d-pedido-status">
            <span></span>{status}
        </div>
    </div>

    <div class="g3d-pedido-main">
        <div class="g3d-pedido-piece">{peca_nome}</div>
        <div class="g3d-pedido-client">{cliente_nome}</div>
    </div>

    <div class="g3d-pedido-bottom">
        <div class="g3d-pedido-mini">
            <strong>{quantidade:.0f}x</strong>
            <span>Qtd.</span>
        </div>
        <div class="g3d-pedido-mini">
            <strong>{total_fmt}</strong>
            <span>Total</span>
        </div>
        <div class="g3d-pedido-mini">
            <strong>{data_pedido}</strong>
            <span>Data</span>
        </div>
    </div>

    <div class="g3d-pedido-peca-codigo">{peca_codigo}</div>
</div>
"""

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)


@st.cache_data(ttl=30, show_spinner=False)
def carregar_filamentos_ativos():
    conn = conectar()
    filamentos = conn.execute("""
    SELECT id, codigo, nome, material, cor
    FROM filamentos
    WHERE status IS NULL OR status = 'Ativo'
    ORDER BY nome ASC
    """).fetchall()
    conn.close()
    return [tuple(f) for f in filamentos]


def salvar_filamentos_pedido(conn, pedido_id, filamentos_pedido):
    conn.execute("DELETE FROM pedido_filamentos WHERE pedido_id = ?", (pedido_id,))
    for filamento_id, observacao in filamentos_pedido:
        if filamento_id:
            conn.execute("""
            INSERT INTO pedido_filamentos (pedido_id, filamento_id, observacao)
            VALUES (?, ?, ?)
            """, (pedido_id, filamento_id, observacao))


def carregar_filamentos_pedido(pedido_id):
    conn = conectar()
    filamentos = conn.execute("""
    SELECT f.codigo, f.nome, f.material, f.cor, pf.observacao
    FROM pedido_filamentos pf
    LEFT JOIN filamentos f ON pf.filamento_id = f.id
    WHERE pf.pedido_id = ?
    ORDER BY pf.id ASC
    """, (pedido_id,)).fetchall()
    conn.close()
    return filamentos


def duplicar_pedido(pedido_id):
    conn = conectar()

    pedido = conn.execute("""
    SELECT
        cliente_id,
        peca_id,
        quantidade,
        valor_unitario,
        desconto,
        frete,
        canal,
        data_entrega_prevista,
        observacoes
    FROM pedidos
    WHERE id = ?
    """, (pedido_id,)).fetchone()

    if pedido is None:
        conn.close()
        return None

    codigo = gerar_codigo_pedido(conn)

    cursor = conn.execute("""
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
        observacoes
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        codigo,
        pedido[0],
        pedido[1],
        pedido[2],
        pedido[3],
        pedido[4],
        pedido[5],
        "Orçamento",
        pedido[6],
        str(date.today()),
        pedido[7],
        pedido[8],
    ))

    novo_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    conn.commit()
    conn.close()

    return novo_id


@st.dialog("Duplicar Pedido", width="large")
def duplicar_pedido_dialog(pedido_id):
    conn = conectar()
    pedido = conn.execute("""
    SELECT cliente_id, peca_id, quantidade, valor_unitario, desconto, frete, canal, data_entrega_prevista, observacoes
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
        limpar_cache_dados()
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
        INSERT INTO pedidos (codigo, cliente_id, peca_id, quantidade, valor_unitario, desconto, frete, status, canal, data_pedido, data_entrega_prevista, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (codigo, cliente_id_para_salvar, pedido[1], pedido[2], pedido[3], pedido[4], pedido[5], "Orçamento", pedido[6], str(date.today()), pedido[7], pedido[8]))
        novo_pedido_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        conn.close()
        st.success("Pedido duplicado com sucesso!")
        limpar_cache_dados()
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
        observacoes
    FROM pedidos
    WHERE id = ?
    """, (pedido_id,)).fetchone()

    conn.close()

    if pedido is None:
        st.warning("Pedido não encontrado.")
        if st.button("Fechar", key=f"fechar_modal_pedido_{pedido_id}"):
            limpar_cache_dados()
            st.rerun()
        return

    clientes_atualizados = carregar_clientes()
    pecas_atualizadas = carregar_pecas()

    if not clientes_atualizados:
        st.warning("Cadastre pelo menos um cliente ativo antes de editar o pedido.")
        if st.button("Fechar", key=f"fechar_modal_sem_cliente_{pedido_id}"):
            limpar_cache_dados()
            st.rerun()
        return

    if not pecas_atualizadas:
        st.warning("Cadastre pelo menos uma peça antes de editar o pedido.")
        if st.button("Fechar", key=f"fechar_modal_sem_peca_{pedido_id}"):
            limpar_cache_dados()
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

            status_lista = ["Orçamento", "Confirmado", "Em Produção", "Pronto", "Entregue", "Cancelado"]

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

        observacoes_edit = st.text_area(
            "Observações",
            value=pedido[11] if pedido[11] else "",
            key=f"modal_observacoes_{pedido_id}"
        )

        salvar_edicao = st.form_submit_button("Salvar Alterações")

    if salvar_edicao:

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
            observacoes = ?
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
            observacoes_edit,
            pedido_id,
        ))

        conn.commit()
        conn.close()

        st.success("Pedido atualizado!")
        limpar_cache_dados()
        st.rerun()

    if st.button("Cancelar", key=f"cancelar_modal_pedido_{pedido_id}"):
        limpar_cache_dados()
        st.rerun()


def pedidos_resumo_mobile_css():
    st.markdown(
        """
        <style>
            .st-key-pedidos_mobile_resumo {
                display: none;
            }

            @media (min-width: 769px) {
                .st-key-pedidos_desktop_resumo {
                    display: block !important;
                }

                .st-key-pedidos_mobile_resumo {
                    display: none !important;
                }
            }

            @media (max-width: 768px) {
                .st-key-pedidos_desktop_resumo {
                    display: none !important;
                }

                .st-key-pedidos_mobile_resumo {
                    display: block !important;
                }

                .g3d-pedidos-mobile {
                    font-family: 'Barlow', system-ui, sans-serif;
                    margin-top: 8px;
                    margin-bottom: 18px;
                }

                .g3d-pedidos-hero {
                    background: linear-gradient(135deg, #0A1A5C 0%, #0C65AA 58%, #58C3F0 100%);
                    border-radius: 22px;
                    padding: 18px 18px;
                    color: #FFFFFF;
                    box-shadow: 0 14px 34px rgba(10, 26, 92, 0.18);
                    margin: 8px 0 14px 0;
                    overflow: hidden;
                    position: relative;
                }

                .g3d-pedidos-hero:after {
                    content: "";
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    background: rgba(255,255,255,0.12);
                    position: absolute;
                    right: -38px;
                    top: -48px;
                }

                .g3d-pedidos-hero-label {
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    opacity: 0.86;
                    margin-bottom: 8px;
                }

                .g3d-pedidos-hero-value {
                    font-size: 32px;
                    font-weight: 800;
                    line-height: 1;
                    margin-bottom: 6px;
                }

                .g3d-pedidos-hero-sub {
                    font-size: 13px;
                    font-weight: 500;
                    opacity: 0.92;
                }

                .g3d-pedidos-mobile-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 12px;
                }

                .g3d-pedidos-mobile-kpi {
                    background: #FFFFFF;
                    border: 1px solid #DEE9EF;
                    border-top: 4px solid #0C65AA;
                    border-radius: 18px;
                    padding: 14px 14px 13px 14px;
                    box-shadow: 0 9px 24px rgba(10, 26, 92, 0.06);
                    min-height: 108px;
                }

                .g3d-pedidos-mobile-kpi-title {
                    font-size: 9.5px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    color: #5C6C74;
                    margin-bottom: 8px;
                }

                .g3d-pedidos-mobile-kpi-value {
                    font-size: 25px;
                    font-weight: 800;
                    line-height: 1.05;
                    margin-bottom: 7px;
                }

                .g3d-pedidos-mobile-kpi-subtitle {
                    font-size: 11.5px;
                    font-weight: 500;
                    color: #5C6C74;
                    line-height: 1.22;
                }

                .g3d-pedidos-mobile-actions {
                    margin-top: 12px;
                    background: #FFFFFF;
                    border: 1px solid #DEE9EF;
                    border-radius: 18px;
                    padding: 12px 14px;
                    box-shadow: 0 9px 24px rgba(10, 26, 92, 0.05);
                    color: #5C6C74;
                    font-size: 12px;
                    font-weight: 600;
                    line-height: 1.35;
                }

                .g3d-pedidos-mobile-actions strong {
                    color: #1E3137;
                    font-weight: 800;
                }

                .st-key-btn_novo_pedido button {
                    background: #0C65AA !important;
                    color: #FFFFFF !important;
                    border-color: #0C65AA !important;
                    min-height: 48px !important;
                    font-weight: 800 !important;
                    border-radius: 15px !important;
                    box-shadow: 0 8px 20px rgba(12, 101, 170, 0.18) !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def pedidos_mobile_kpi_html(titulo, valor, subtitulo, cor="#0C65AA"):
    return f"""
    <div class="g3d-pedidos-mobile-kpi" style="border-top-color:{cor};">
        <div class="g3d-pedidos-mobile-kpi-title">{escape(str(titulo))}</div>
        <div class="g3d-pedidos-mobile-kpi-value" style="color:{cor};">{escape(str(valor))}</div>
        <div class="g3d-pedidos-mobile-kpi-subtitle">{escape(str(subtitulo))}</div>
    </div>
    """


def render_pedidos_mobile_resumo(total_pedidos, pedidos_abertos, faturamento_total, lucro_total, ticket_medio):
    html = f"""
    <div class="g3d-pedidos-mobile">
        <div class="g3d-pedidos-hero">
            <div class="g3d-pedidos-hero-label">Resumo dos pedidos</div>
            <div class="g3d-pedidos-hero-value">{escape(moeda(faturamento_total))}</div>
            <div class="g3d-pedidos-hero-sub">{total_pedidos:.0f} pedidos cadastrados · {pedidos_abertos:.0f} em aberto</div>
        </div>

        <div class="g3d-pedidos-mobile-grid">
            {pedidos_mobile_kpi_html("Em aberto", pedidos_abertos, "aguardando conclusão", "#B85C20")}
            {pedidos_mobile_kpi_html("Lucro", moeda(lucro_total), "resultado estimado", "#1F8A4C" if lucro_total >= 0 else "#D11A2A")}
            {pedidos_mobile_kpi_html("Ticket médio", moeda(ticket_medio), "por pedido", "#0C65AA")}
            {pedidos_mobile_kpi_html("Total", total_pedidos, "pedidos cadastrados", "#100690")}
        </div>

        <div class="g3d-pedidos-mobile-actions">
            <strong>Atalho:</strong> use o botão <strong>+ Novo Pedido</strong> abaixo para registrar uma nova venda.
        </div>
    </div>
    """

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)


def pedido_mobile_form_css():
    st.markdown(
        """
        <style>
            .g3d-pedido-mobile-step,
            .st-key-novo_pedido_resumo_mobile {
                display: none;
            }

            @media (min-width: 769px) {
                .st-key-novo_pedido_resumo_mobile {
                    display: none !important;
                }

                .st-key-novo_pedido_resumo_desktop {
                    display: block !important;
                }


                .g3d-pedido-mobile-step {
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

                .g3d-pedido-mobile-step strong {
                    display: block;
                    font-size: 11px;
                    font-weight: 800;
                    color: #100690;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    margin-bottom: 5px;
                    line-height: 1.1;
                }

                .g3d-pedido-mobile-step span {
                    display: block;
                    font-size: 12px;
                    font-weight: 600;
                    color: #5C6C74;
                    line-height: 1.28;
                }

                .st-key-salvar_novo_pedido button {
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
                .g3d-pedido-mobile-step {
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

                .g3d-pedido-mobile-step strong {
                    display: block;
                    font-size: 11px;
                    font-weight: 800;
                    color: #100690;
                    text-transform: uppercase;
                    letter-spacing: 1.8px;
                    margin-bottom: 5px;
                    line-height: 1.1;
                }

                .g3d-pedido-mobile-step span {
                    display: block;
                    font-size: 12px;
                    font-weight: 500;
                    color: #5C6C74;
                    line-height: 1.28;
                }

                .st-key-novo_pedido_resumo_desktop {
                    display: none !important;
                }

                .st-key-novo_pedido_resumo_mobile {
                    display: block !important;
                }

                .g3d-novo-pedido-resumo {
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

                .g3d-novo-pedido-resumo:after {
                    content: "";
                    width: 118px;
                    height: 118px;
                    border-radius: 50%;
                    background: rgba(255,255,255,0.12);
                    position: absolute;
                    right: -40px;
                    top: -52px;
                }

                .g3d-novo-pedido-resumo-label {
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    opacity: 0.86;
                    margin-bottom: 8px;
                }

                .g3d-novo-pedido-resumo-total {
                    font-size: 31px;
                    font-weight: 800;
                    line-height: 1;
                    margin-bottom: 8px;
                }

                .g3d-novo-pedido-resumo-sub {
                    font-size: 13px;
                    font-weight: 500;
                    opacity: 0.92;
                    line-height: 1.25;
                }

                .g3d-novo-pedido-mini-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin-top: 12px;
                }

                .g3d-novo-pedido-mini {
                    background: rgba(255,255,255,0.14);
                    border: 1px solid rgba(255,255,255,0.20);
                    border-radius: 15px;
                    padding: 10px 10px;
                }

                .g3d-novo-pedido-mini strong {
                    display: block;
                    font-size: 15px;
                    font-weight: 800;
                    line-height: 1.05;
                    color: #FFFFFF;
                    margin-bottom: 5px;
                }

                .g3d-novo-pedido-mini span {
                    display: block;
                    font-size: 10px;
                    font-weight: 700;
                    opacity: 0.88;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }

                div[data-testid="stSelectbox"],
                div[data-testid="stNumberInput"],
                div[data-testid="stDateInput"],
                div[data-testid="stTextInput"],
                div[data-testid="stTextArea"] {
                    margin-bottom: 0.45rem !important;
                }

                div[data-testid="stSelectbox"] label,
                div[data-testid="stNumberInput"] label,
                div[data-testid="stDateInput"] label,
                div[data-testid="stTextInput"] label,
                div[data-testid="stTextArea"] label {
                    color: #1E3137 !important;
                    font-weight: 700 !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                }

                .st-key-salvar_novo_pedido button {
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

                .st-key-salvar_novo_pedido button:before {
                    content: "✓ ";
                    font-weight: 800;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def pedido_mobile_step(titulo, subtitulo):
    html = f"""
    <div class="g3d-pedido-mobile-step">
        <strong>{escape(str(titulo))}</strong>
        <span>{escape(str(subtitulo))}</span>
    </div>
    """

    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)


def render_novo_pedido_mobile_resumo(calc, preco_sugerido, margem_padrao):
    html = f"""
    <div class="g3d-novo-pedido-resumo">
        <div class="g3d-novo-pedido-resumo-label">Resumo do pedido</div>
        <div class="g3d-novo-pedido-resumo-total">{escape(moeda(calc["total"]))}</div>
        <div class="g3d-novo-pedido-resumo-sub">
            lucro estimado {escape(moeda(calc["lucro"]))} · venda sugerida {escape(moeda(preco_sugerido))}
        </div>

        <div class="g3d-novo-pedido-mini-grid">
            <div class="g3d-novo-pedido-mini">
                <strong>{escape(moeda(calc["custo_unitario"]))}</strong>
                <span>Custo unit.</span>
            </div>
            <div class="g3d-novo-pedido-mini">
                <strong>{escape(moeda(calc["subtotal"]))}</strong>
                <span>Subtotal</span>
            </div>
            <div class="g3d-novo-pedido-mini">
                <strong>{escape(moeda(calc["lucro_unitario"]))}</strong>
                <span>Lucro unit.</span>
            </div>
            <div class="g3d-novo-pedido-mini">
                <strong>{calc["lucro_percentual"]:.0f}%</strong>
                <span>Margem custo</span>
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
mobile_bottom_nav("pedidos")
inject_desktop_visual()
pedidos_mobile_css()
pedidos_resumo_mobile_css()
pedido_mobile_form_css()
header("Pedidos", "Cadastro e acompanhamento dos pedidos da Gestão 3D")


energia_hora, depreciacao_hora, margem_padrao, meta_lucro_hora, custo_pos_processamento_hora = carregar_configuracoes()
clientes = carregar_clientes()
pecas = carregar_pecas()


resumo_pedidos = carregar_pedidos_resumo_cache(
    energia_hora,
    depreciacao_hora,
    custo_pos_processamento_hora
)

total_pedidos = resumo_pedidos["total_pedidos"]
pedidos_abertos = resumo_pedidos["pedidos_abertos"]
faturamento_total = resumo_pedidos["faturamento_total"]
lucro_total = resumo_pedidos["lucro_total"]
ticket_medio = resumo_pedidos["ticket_medio"]


with st.container(key="pedidos_mobile_resumo"):
    render_pedidos_mobile_resumo(
        total_pedidos=total_pedidos,
        pedidos_abertos=pedidos_abertos,
        faturamento_total=faturamento_total,
        lucro_total=lucro_total,
        ticket_medio=ticket_medio,
    )

with st.container(key="pedidos_desktop_resumo"):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_card("Pedidos", str(total_pedidos), "pedidos cadastrados", "blue")

    with col2:
        kpi_card("Em aberto", str(pedidos_abertos), "aguardando conclusão", "orange")

    with col3:
        kpi_card("Faturamento", moeda(faturamento_total), "pedidos não cancelados", "green")

    with col4:
        kpi_card("Lucro estimado", moeda(lucro_total), "margem prevista", "green")


section_title(
    "Cadastro de Pedido",
    "Vincule cliente, peça, quantidade vendida e valor de venda"
)


if "mostrar_form_pedido" not in st.session_state:
    st.session_state["mostrar_form_pedido"] = False


if primary_button("+ Novo Pedido", "btn_novo_pedido"):
    st.session_state["mostrar_form_pedido"] = not st.session_state["mostrar_form_pedido"]


if st.session_state["mostrar_form_pedido"]:

    if not pecas:
        st.warning("Cadastre pelo menos uma peça antes de criar um pedido.")

    else:

        small_section("Novo Pedido")

        col_form, col_resumo = st.columns([2, 1])

        with col_form:

            pedido_mobile_step("1. Cliente", "Selecione um cliente existente ou cadastre rapidamente um novo.")

            clientes_opcoes = {f"{c[1]} - {c[2]}": c for c in clientes}
            opcao_novo_cliente = "+ Cadastrar novo cliente"
            cliente_labels = [opcao_novo_cliente] + list(clientes_opcoes.keys())

            cliente_selecionado = st.selectbox(
                "Cliente",
                cliente_labels,
                key="novo_pedido_cliente"
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

            pedido_mobile_step("2. Peça e preço", "Escolha a peça, revise o valor sugerido e informe a quantidade.")

            pecas_opcoes = {f"{p[1]} - {p[2]}": p for p in pecas}
            peca_selecionada = st.selectbox("Peça", list(pecas_opcoes.keys()), key="novo_pedido_peca")
            peca_dados = pecas_opcoes[peca_selecionada]

            custo_ref = carregar_custos_pedidos_cache(
                tuple([peca_dados[0]]),
                energia_hora,
                depreciacao_hora,
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

            pedido_mobile_step("3. Valores", "Ajuste quantidade, venda, desconto e frete.")

            quantidade = st.number_input("Quantidade vendida", min_value=1.0, value=1.0, step=1.0, key="novo_pedido_quantidade")
            valor_unitario = st.number_input("Valor unitário de venda (R$)", min_value=0.0, step=1.0, key="novo_pedido_valor_unitario")

            col_v1, col_v2 = st.columns(2)

            with col_v1:
                desconto = st.number_input("Desconto total (R$)", min_value=0.0, value=0.0, step=1.0, key="novo_pedido_desconto")

            with col_v2:
                frete = st.number_input("Frete cobrado (R$)", min_value=0.0, value=0.0, step=1.0, key="novo_pedido_frete")

            pedido_mobile_step("4. Acompanhamento", "Defina status, canal, datas e observações.")

            col_s1, col_s2 = st.columns(2)

            with col_s1:
                status = st.selectbox(
                    "Status do pedido",
                    ["Orçamento", "Confirmado", "Em Produção", "Pronto", "Entregue", "Cancelado"],
                    key="novo_pedido_status",
                )

                canal = st.selectbox(
                    "Canal",
                    ["WhatsApp", "Instagram", "Marketplace", "Indicação", "Feira / Evento", "Outro"],
                    key="novo_pedido_canal",
                )

            with col_s2:
                data_pedido = st.date_input("Data do pedido", value=date.today(), format="DD/MM/YYYY", key="novo_pedido_data")
                data_entrega = st.date_input("Entrega prevista", value=date.today(), format="DD/MM/YYYY", key="novo_pedido_entrega")

            observacoes = st.text_area("Observações", key="novo_pedido_observacoes")

        calc = calcular_pedido(peca_dados[0], quantidade, valor_unitario, desconto, frete, energia_hora, depreciacao_hora, custo_ref)

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

        if primary_button("Salvar Pedido", "salvar_novo_pedido"):

            if cliente_selecionado == opcao_novo_cliente and not novo_cliente_nome:
                st.warning("Informe o nome do novo cliente.")

            else:
                conn = conectar()

                if cliente_selecionado == opcao_novo_cliente:
                    codigo_cliente = gerar_codigo_cliente(conn)

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
                    observacoes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                ))

                conn.commit()
                conn.close()

                st.success("Pedido cadastrado com sucesso!")
                st.session_state["mostrar_form_pedido"] = False
                limpar_cache_dados()
                st.rerun()


section_title(
    "Pedidos cadastrados",
    "Consulte, edite, duplique, exclua e acompanhe os pedidos"
)


busca = searchbar(
    placeholder="Pesquisar por pedido, cliente, peça, status ou canal...",
    key="buscar_pedido"
)


pedidos_base, filamentos_pecas_pedidos = carregar_pedidos_listagem_cache()

termo_busca = (busca or "").strip().lower()

if termo_busca:
    pedidos = [
        p for p in pedidos_base
        if termo_busca in str(p[1] or "").lower()
        or termo_busca in str(p[3] or "").lower()
        or termo_busca in str(p[4] or "").lower()
        or termo_busca in str(p[6] or "").lower()
        or termo_busca in str(p[7] or "").lower()
        or termo_busca in str(p[12] or "").lower()
        or termo_busca in str(p[13] or "").lower()
    ]
else:
    pedidos = pedidos_base

peca_ids_pedidos = tuple(sorted({pedido[5] for pedido in pedidos if pedido[5]}))
custos_pecas_pedidos = carregar_custos_pedidos_cache(
    peca_ids_pedidos,
    energia_hora,
    depreciacao_hora,
    custo_pos_processamento_hora
)

pedidos = paginar_itens(
    pedidos,
    "pedidos",
    opcoes=(10, 25, 50, 100),
    nome_item="pedidos"
)


for pedido in pedidos:

    pedido_id = pedido[0]
    codigo = pedido[1]
    cliente_id = pedido[2]
    cliente_codigo = pedido[3] if pedido[3] else "-"
    cliente_nome = pedido[4] if pedido[4] else "-"
    peca_id = pedido[5]
    peca_codigo = pedido[6] if pedido[6] else "-"
    peca_nome = pedido[7] if pedido[7] else "-"
    quantidade = pedido[8] if pedido[8] else 0
    valor_unitario = pedido[9] if pedido[9] else 0
    desconto = pedido[10] if pedido[10] else 0
    frete = pedido[11] if pedido[11] else 0
    status = pedido[12] if pedido[12] else "Orçamento"
    canal = pedido[13] if pedido[13] else "-"
    data_pedido = data_br(pedido[14])
    data_entrega = data_br(pedido[15])
    observacoes = pedido[16] if pedido[16] else ""

    calc = calcular_pedido(peca_id, quantidade, valor_unitario, desconto, frete, energia_hora, depreciacao_hora, custos_pecas_pedidos.get(peca_id))

    with st.container(border=True):

        pedido_card(
            codigo=codigo,
            cliente_nome=cliente_nome,
            peca_codigo=peca_codigo,
            peca_nome=peca_nome,
            quantidade=quantidade,
            status=status,
            total=calc["total"],
            data_pedido=data_pedido,
        )

        with st.expander("Detalhes, valores e ações"):

            col_d1, col_d2, col_d3, col_d4 = st.columns(4)

            with col_d1:
                st.write(f"**Status:** {status}")
                st.write(f"**Canal:** {canal}")

            with col_d2:
                st.write(f"**Cliente:** {cliente_codigo}")
                st.write(f"**Peça:** {peca_codigo}")

            with col_d3:
                st.write(f"**Quantidade:** {quantidade:.0f}")
                st.write(f"**Valor unitário:** {moeda(valor_unitario)}")

            with col_d4:
                st.write(f"**Data pedido:** {data_pedido}")
                st.write(f"**Entrega:** {data_entrega}")

            filamentos_peca_detalhe = filamentos_pecas_pedidos.get(peca_id, [])

            if filamentos_peca_detalhe:
                small_section("Filamentos / cores da peça")

                for filamento in filamentos_peca_detalhe:
                    peso_filamento = filamento[5] if filamento[5] else 0
                    observacao_filamento = filamento[6] if filamento[6] else "-"
                    st.write(
                        f"- **{filamento[0]} - {filamento[1]}** | "
                        f"{filamento[2]} {filamento[3]} | "
                        f"{peso_filamento:.1f} g | {observacao_filamento}"
                    )

            small_section("Dados unitários da peça")

            col_u1, col_u2, col_u3, col_u4 = st.columns(4)

            with col_u1:
                st.write(f"**Peso unitário estimado:** {calc['peso_unitario']:.1f} g")

            with col_u2:
                st.write(f"**Tempo total unitário estimado:** {calc['tempo_unitario']:.2f} h")

            with col_u3:
                st.write(f"**Custo unitário:** {moeda(calc['custo_unitario'])}")

            with col_u4:
                st.write(f"**Lucro unitário:** {moeda(calc['lucro_unitario'])}")

            small_section("Resumo financeiro")

            margem_lucro = (calc["lucro"] / calc["total"]) * 100 if calc["total"] > 0 else 0
            tempo_total_estimado = calc["tempo_unitario"] * quantidade
            lucro_hora = calc["lucro"] / tempo_total_estimado if tempo_total_estimado > 0 else 0

            if lucro_hora >= meta_lucro_hora:
                cor_lucro_hora = "green"
                status_lucro_hora = "acima da meta"
            elif lucro_hora >= meta_lucro_hora * 0.6:
                cor_lucro_hora = "orange"
                status_lucro_hora = "atenção"
            else:
                cor_lucro_hora = "red"
                status_lucro_hora = "abaixo da meta"

            if margem_lucro >= 40:
                cor_margem = "green"
            elif margem_lucro >= 20:
                cor_margem = "orange"
            else:
                cor_margem = "red"

            col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)

            with col_f1:
                st.write(f"**Subtotal:** {moeda(calc['subtotal'])}")

            with col_f2:
                st.write(f"**Desconto:** {moeda(desconto)}")

            with col_f3:
                st.write(f"**Frete:** {moeda(frete)}")

            with col_f4:
                st.write(f"**Custo:** {moeda(calc['custo_total'])}")

            with col_f5:
                st.write(f"**Total:** {moeda(calc['total'])}")

            col_r1, col_r2, col_r3 = st.columns(3)

            with col_r1:
                kpi_card(
                    "Lucro",
                    moeda(calc["lucro"]),
                    "resultado do pedido",
                    "green" if calc["lucro"] > 0 else "red"
                )

            with col_r2:
                kpi_card(
                    "Margem de lucro",
                    f"{margem_lucro:.0f}%",
                    "lucro sobre venda",
                    cor_margem
                )

            with col_r3:
                kpi_card(
                    "Lucro por hora",
                    f"R$ {lucro_hora:.2f}/h".replace(".", ","),
                    status_lucro_hora,
                    cor_lucro_hora
                )

            if observacoes:
                st.write(f"**Observações:** {observacoes}")

            col_btn1, col_btn2, col_btn3 = st.columns(3)

            with col_btn1:
                if secondary_button("Editar", f"editar_pedido_{pedido_id}"):
                    editar_pedido_dialog(pedido_id)

            with col_btn2:
                if secondary_button("Duplicar", f"duplicar_pedido_{pedido_id}"):
                    duplicar_pedido_dialog(pedido_id)

            with col_btn3:
                if danger_button("Excluir", f"excluir_pedido_{pedido_id}"):
                    conn = conectar()
                    conn.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
                    conn.commit()
                    conn.close()
                    limpar_cache_dados()
                    st.rerun()

    st.write("")

