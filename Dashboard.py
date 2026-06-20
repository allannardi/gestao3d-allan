import streamlit as st
from html import escape
from collections import defaultdict

from database import conectar, inicializar_banco
from components.sidebar import sidebar
from components.header import header
from components.kpi import kpi_card
from components.section import section_title
from components.auth import require_login


st.set_page_config(
    page_title="Gestão 3D",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)


with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()


def moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def garantir_tabelas_dashboard():
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


def carregar_acessorios_da_peca(conn, peca_id):
    return conn.execute("""
    SELECT
        a.custo_unitario,
        pa.quantidade
    FROM peca_acessorios pa
    LEFT JOIN acessorios a ON pa.acessorio_id = a.id
    WHERE pa.peca_id = ?
    """, (peca_id,)).fetchall()


def calcular_custo_unitario_peca(peca_id, energia_hora, depreciacao_hora):
    conn = conectar()

    peca = conn.execute("""
    SELECT
        p.peso_g,
        p.tempo_impressao_h,
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
            "custo_unitario": 0,
            "peso_unitario": 0,
            "tempo_unitario": 0,
        }

    acessorios = carregar_acessorios_da_peca(conn, peca_id)
    conn.close()

    peso_g = peca[0] if peca[0] else 0
    tempo_h = peca[1] if peca[1] else 0
    embalagem = peca[2] if peca[2] else 0
    quantidade_lote = peca[3] if peca[3] and peca[3] > 0 else 1
    custo_grama = peca[4] if peca[4] else 0

    custo_material = peso_g * custo_grama
    custo_energia = tempo_h * energia_hora
    custo_depreciacao = tempo_h * depreciacao_hora
    custo_acessorios = sum(
        (a[0] if a[0] else 0) * (a[1] if a[1] else 0)
        for a in acessorios
    )

    custo_lote = (
        custo_material
        + custo_energia
        + custo_depreciacao
        + embalagem
        + custo_acessorios
    )

    custo_unitario = custo_lote / quantidade_lote if quantidade_lote > 0 else custo_lote
    peso_unitario = peso_g / quantidade_lote if quantidade_lote > 0 else peso_g
    tempo_unitario = tempo_h / quantidade_lote if quantidade_lote > 0 else tempo_h

    return {
        "custo_unitario": custo_unitario,
        "peso_unitario": peso_unitario,
        "tempo_unitario": tempo_unitario,
    }


def calcular_pedido(peca_id, quantidade, valor_unitario, desconto, frete, energia_hora, depreciacao_hora):
    custo_peca = calcular_custo_unitario_peca(peca_id, energia_hora, depreciacao_hora)

    quantidade = quantidade if quantidade else 0
    valor_unitario = valor_unitario if valor_unitario else 0
    desconto = desconto if desconto else 0
    frete = frete if frete else 0

    subtotal = quantidade * valor_unitario
    total = subtotal - desconto + frete
    custo_total = quantidade * custo_peca["custo_unitario"]
    lucro = total - custo_total
    tempo_total = quantidade * custo_peca["tempo_unitario"]

    margem_venda = (lucro / total) * 100 if total > 0 else 0
    lucro_hora = lucro / tempo_total if tempo_total > 0 else 0

    return {
        "subtotal": subtotal,
        "total": total,
        "custo_total": custo_total,
        "lucro": lucro,
        "tempo_total": tempo_total,
        "margem_venda": margem_venda,
        "lucro_hora": lucro_hora,
    }


def largura_coluna(header):
    larguras = {
        "Pedido": "120px",
        "Cliente": "220px",
        "Peça": "340px",
        "Qtd.": "80px",
        "Status": "130px",
        "Total": "130px",
        "Faturamento": "150px",
        "Lucro": "130px",
        "Pedidos": "100px",
    }

    return larguras.get(str(header), "160px")


def coluna_numerica(header):
    return str(header) in [
        "Qtd.",
        "Pedidos",
        "Faturamento",
        "Lucro",
        "Total",
    ]


def tabela_html(headers, rows, empty_message):
    if not rows:
        return f"""
        <div style="
            border:1px solid #DEE9EF;
            background:#FFFFFF;
            border-radius:12px;
            padding:18px;
            font-family:'Barlow', system-ui, sans-serif;
            color:#5C6C74;
            font-size:13px;
        ">
            {escape(empty_message)}
        </div>
        """

    colgroup = "".join([
        f'<col style="width:{largura_coluna(header)};">'
        for header in headers
    ])

    thead = "".join([
        f"""
        <th style="
            text-align:center;
            padding:12px 14px;
            border-bottom:2px solid #DEE9EF;
            color:#5C6C74;
            font-weight:800;
            letter-spacing:1.5px;
            font-size:11px;
            text-transform:uppercase;
            white-space:nowrap;
            background:#F4F8FB;
            position:sticky;
            top:0;
            z-index:2;
        ">{escape(str(header))}</th>
        """
        for header in headers
    ])

    linhas = ""

    for row in rows:
        tds = ""

        for idx, value in enumerate(row):
            header = headers[idx]

            if coluna_numerica(header):
                align = "center"
                weight = "700"
            else:
                align = "left"
                weight = "800" if idx == 0 else "500"

            tds += f"""
            <td style="
                padding:11px 14px;
                border-bottom:1px solid #DEE9EF;
                color:#1E3137;
                font-weight:{weight};
                text-align:{align};
                white-space:nowrap;
                font-size:13px;
                vertical-align:middle;
            ">{escape(str(value))}</td>
            """

        linhas += f"<tr>{tds}</tr>"

    return f"""
    <style>
        .g3d-table-wrap {{
            border:1px solid #DEE9EF;
            border-radius:12px;
            overflow:auto;
            background:#FFFFFF;
            font-family:'Barlow', system-ui, sans-serif;
            width:100%;
            max-height:360px;
        }}

        .g3d-table {{
            border-collapse:collapse;
            min-width:100%;
            table-layout:fixed;
        }}

        .g3d-table tbody tr:hover {{
            background:#F4F8FB;
        }}
    </style>

    <div class="g3d-table-wrap">
        <table class="g3d-table">
            <colgroup>
                {colgroup}
            </colgroup>
            <thead>
                <tr>{thead}</tr>
            </thead>
            <tbody>
                {linhas}
            </tbody>
        </table>
    </div>
    """


def render_tabela(headers, rows, empty_message):
    html = tabela_html(headers, rows, empty_message)

    if not rows:
        altura = 90
    else:
        altura = min(430, 82 + (len(rows) * 44))

    st.components.v1.html(
        html,
        height=altura,
        scrolling=True
    )


inicializar_banco()
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

energia = config[0]
depreciacao = config[1]
margem = config[2]
meta_lucro = config[3]

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
    ped.data_entrega_prevista
FROM pedidos ped
LEFT JOIN clientes c ON ped.cliente_id = c.id
LEFT JOIN pecas pc ON ped.peca_id = pc.id
ORDER BY ped.id DESC
""").fetchall()

total_clientes = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
total_pecas = conn.execute("SELECT COUNT(*) FROM pecas").fetchone()[0]
total_filamentos = conn.execute("SELECT COUNT(*) FROM filamentos").fetchone()[0]

conn.close()


pedidos_abertos = 0
faturamento_total = 0
lucro_total = 0
horas_total = 0
quantidade_total = 0

status_resumo = defaultdict(lambda: {
    "pedidos": 0,
    "faturamento": 0,
    "lucro": 0,
})

pecas_resumo = defaultdict(lambda: {
    "quantidade": 0,
    "faturamento": 0,
    "lucro": 0,
})

clientes_resumo = defaultdict(lambda: {
    "pedidos": 0,
    "faturamento": 0,
    "lucro": 0,
})

pedidos_recentes = []

for pedido in pedidos:
    codigo = pedido[1]
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

    calc = calcular_pedido(
        peca_id,
        quantidade,
        valor_unitario,
        desconto,
        frete,
        energia,
        depreciacao,
    )

    if status not in ["Entregue", "Cancelado"]:
        pedidos_abertos += 1

    if status != "Cancelado":
        faturamento_total += calc["total"]
        lucro_total += calc["lucro"]
        horas_total += calc["tempo_total"]
        quantidade_total += quantidade

        pecas_key = f"{peca_codigo} - {peca_nome}"
        pecas_resumo[pecas_key]["quantidade"] += quantidade
        pecas_resumo[pecas_key]["faturamento"] += calc["total"]
        pecas_resumo[pecas_key]["lucro"] += calc["lucro"]

        clientes_key = f"{cliente_codigo} - {cliente_nome}"
        clientes_resumo[clientes_key]["pedidos"] += 1
        clientes_resumo[clientes_key]["faturamento"] += calc["total"]
        clientes_resumo[clientes_key]["lucro"] += calc["lucro"]

    status_resumo[status]["pedidos"] += 1
    status_resumo[status]["faturamento"] += calc["total"] if status != "Cancelado" else 0
    status_resumo[status]["lucro"] += calc["lucro"] if status != "Cancelado" else 0

    if len(pedidos_recentes) < 5:
        pedidos_recentes.append([
            codigo,
            cliente_nome,
            peca_nome,
            f"{quantidade:.0f}",
            status,
            moeda(calc["total"]),
        ])


lucro_hora = lucro_total / horas_total if horas_total > 0 else 0
margem_media = (lucro_total / faturamento_total) * 100 if faturamento_total > 0 else 0
ticket_medio = faturamento_total / len(pedidos) if len(pedidos) > 0 else 0


sidebar()

header(
    "Dashboard",
    "Visão geral da operação"
)


col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    kpi_card(
        "Pedidos em aberto",
        str(pedidos_abertos),
        "pedidos aguardando ação",
        "blue"
    )

with col2:
    kpi_card(
        "Faturamento",
        moeda(faturamento_total),
        "pedidos não cancelados",
        "green"
    )

with col3:
    kpi_card(
        "Lucro",
        moeda(lucro_total),
        f"margem {margem_media:.0f}%",
        "green" if lucro_total >= 0 else "red"
    )

with col4:
    kpi_card(
        "Horas impressas",
        f"{horas_total:.1f}h",
        "tempo estimado vendido",
        "orange"
    )

with col5:
    kpi_card(
        "Lucro/Hora",
        f"R$ {lucro_hora:.2f}".replace(".", ","),
        f"meta: {moeda(meta_lucro)}/h",
        "green" if lucro_hora >= meta_lucro else "gray"
    )


section_title(
    "Resumo da operação",
    "Indicadores comerciais calculados a partir dos pedidos cadastrados"
)


col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    kpi_card("Clientes", str(total_clientes), "clientes cadastrados", "blue")

with col_b:
    kpi_card("Peças", str(total_pecas), "modelos cadastrados", "orange")

with col_c:
    kpi_card("Filamentos", str(total_filamentos), "rolos cadastrados", "gray")

with col_d:
    kpi_card("Ticket médio", moeda(ticket_medio), "por pedido cadastrado", "green")


section_title(
    "Pedidos recentes",
    "Últimos pedidos registrados no sistema"
)

render_tabela(
    ["Pedido", "Cliente", "Peça", "Qtd.", "Status", "Total"],
    pedidos_recentes,
    "Nenhum pedido cadastrado ainda."
)


col_r1, col_r2 = st.columns(2)

with col_r1:
    section_title(
        "Peças mais vendidas",
        "Ranking por quantidade vendida"
    )

    pecas_ranking = sorted(
        pecas_resumo.items(),
        key=lambda item: item[1]["quantidade"],
        reverse=True
    )[:5]

    render_tabela(
        ["Peça", "Qtd.", "Faturamento", "Lucro"],
        [
            [
                nome,
                f"{dados['quantidade']:.0f}",
                moeda(dados["faturamento"]),
                moeda(dados["lucro"]),
            ]
            for nome, dados in pecas_ranking
        ],
        "Nenhuma peça vendida ainda."
    )

with col_r2:
    section_title(
        "Clientes com mais pedidos",
        "Ranking por número de pedidos"
    )

    clientes_ranking = sorted(
        clientes_resumo.items(),
        key=lambda item: item[1]["pedidos"],
        reverse=True
    )[:5]

    render_tabela(
        ["Cliente", "Pedidos", "Faturamento", "Lucro"],
        [
            [
                nome,
                f"{dados['pedidos']:.0f}",
                moeda(dados["faturamento"]),
                moeda(dados["lucro"]),
            ]
            for nome, dados in clientes_ranking
        ],
        "Nenhum cliente com pedido cadastrado ainda."
    )


section_title(
    "Pedidos por status",
    "Distribuição dos pedidos por etapa"
)


status_ordem = ["Orçamento", "Confirmado", "Em Produção", "Pronto", "Entregue", "Cancelado"]

status_linhas = []

for status in status_ordem:
    if status in status_resumo:
        dados = status_resumo[status]
        status_linhas.append([
            status,
            f"{dados['pedidos']:.0f}",
            moeda(dados["faturamento"]),
            moeda(dados["lucro"]),
        ])

for status, dados in status_resumo.items():
    if status not in status_ordem:
        status_linhas.append([
            status,
            f"{dados['pedidos']:.0f}",
            moeda(dados["faturamento"]),
            moeda(dados["lucro"]),
        ])

render_tabela(
    ["Status", "Pedidos", "Faturamento", "Lucro"],
    status_linhas,
    "Nenhum status encontrado."
)


st.write("")
st.write("")


st.markdown(
    f"""
    <div style="
        margin-top:36px;
        padding-top:14px;
        border-top:1px solid rgba(92,108,116,0.18);
        font-family:'Barlow', system-ui, sans-serif;
        font-size:12px;
        font-weight:500;
        color:#5C6C74;
        display:flex;
        gap:8px;
        flex-wrap:wrap;
        align-items:center;
    ">
        <span style="font-weight:700;">Parâmetros atuais:</span>
        <span>Energia {moeda(energia)}/h</span>
        <span>·</span>
        <span>Depreciação {moeda(depreciacao)}/h</span>
        <span>·</span>
        <span>Margem padrão {margem:.0f}%</span>
        <span>·</span>
        <span>Meta lucro/hora {moeda(meta_lucro)}</span>
    </div>
    """,
    unsafe_allow_html=True
)
