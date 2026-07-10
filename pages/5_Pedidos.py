import streamlit as st
from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.desktop_visual import inject_desktop_visual
from components.header import header
from components.help_ui import header_with_help
from components.kpi import kpi_card
from components.button import primary_button
from components.searchbar import searchbar
from components.pagination import paginar_itens
from components.section import section_title
from components.auth import require_login
from database import conectar, inicializar_banco
from services.pedido_dados import (
    carregar_configuracoes_pedidos,
    garantir_tabelas_pedidos,
    gerar_codigo_cliente,
)
from components.pedidos_widgets import (
    moeda,
    pedido_card,
    pedido_mobile_form_css,
    pedidos_mobile_css,
    pedidos_resumo_mobile_css,
    render_pedidos_mobile_resumo,
)
from components.pedido_novo_form import render_novo_pedido_form
from components.pedido_dialogs import duplicar_pedido_dialog, editar_pedido_dialog
from components.pedidos_listagem import render_listagem_pedidos
from services.pedidos import (
    STATUS_PEDIDOS,
    atualizar_status_pedido_db,
    carregar_clientes,
    carregar_impressoras_pedidos,
    carregar_pecas,
    carregar_pedidos_listagem_cache,
    selecionar_impressora_padrao,
)


from services.pedido_custos import carregar_pedidos_resumo_cache


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


def atualizar_status_pedido(pedido_id, novo_status, data_final_producao=None, data_entrega_real=None):
    atualizar_status_pedido_db(
        pedido_id,
        novo_status,
        data_final_producao=data_final_producao,
        data_entrega_real=data_entrega_real,
    )
    limpar_cache_dados()


@st.cache_data(ttl=3600, show_spinner=False)
def carregar_css_base_cache():
    with open("assets/style.css", encoding="utf-8") as f:
        return f.read()


st.markdown(f"<style>{carregar_css_base_cache()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()
garantir_tabelas_pedidos()
sidebar()
mobile_bottom_nav("pedidos")
inject_desktop_visual()
pedidos_mobile_css()
pedidos_resumo_mobile_css()
pedido_mobile_form_css()


@st.dialog("Ajuda - Pedidos")
def ajuda_pedidos():
    st.markdown(
        """
        Use esta tela para registrar e acompanhar as vendas.

        **Fluxo recomendado:**
        1. Clique em **+ Novo Pedido**.
        2. Escolha ou cadastre o cliente.
        3. Selecione a peça vendida e a quantidade.
        4. Escolha o **filamento/rolo usado neste pedido**.
        5. Confira preço, lucro e lucro por hora antes de salvar.

        **Legenda dos status:**
        - **Orçamento:** cliente ainda não confirmou.
        - **Encomendado:** cliente confirmou, mas a produção ainda não começou.
        - **Em Produção:** peça sendo impressa, montada ou finalizada.
        - **Pronto:** pedido finalizado, aguardando entrega.
        - **Entregue:** pedido concluído.
        - **Cancelado:** pedido não será produzido e não entra nos resultados.
        """
    )

header_with_help("Pedidos", "Cadastro e acompanhamento dos pedidos da Gestão 3D", ajuda_pedidos, key="ajuda_pedidos_link")


energia_hora, depreciacao_hora, margem_padrao, meta_lucro_hora, custo_pos_processamento_hora = carregar_configuracoes_pedidos()
clientes = carregar_clientes()
pecas = carregar_pecas()
impressoras_pedidos = carregar_impressoras_pedidos()
impressora_padrao_pedido = selecionar_impressora_padrao(impressoras_pedidos)


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
    "Fluxo guiado para registrar uma venda com menos risco de erro"
)


if "mostrar_form_pedido" not in st.session_state:
    st.session_state["mostrar_form_pedido"] = False


if primary_button("+ Novo Pedido", "btn_novo_pedido"):
    st.session_state["mostrar_form_pedido"] = not st.session_state["mostrar_form_pedido"]


if st.session_state["mostrar_form_pedido"]:
    render_novo_pedido_form(
        pecas=pecas,
        clientes=clientes,
        impressoras_pedidos=impressoras_pedidos,
        energia_hora=energia_hora,
        depreciacao_hora=depreciacao_hora,
        margem_padrao=margem_padrao,
        meta_lucro_hora=meta_lucro_hora,
        custo_pos_processamento_hora=custo_pos_processamento_hora,
        gerar_codigo_cliente_func=gerar_codigo_cliente,
        limpar_cache_dados_func=limpar_cache_dados,
    )


section_title(
    "Pedidos cadastrados",
    "Consulte, edite, duplique, exclua e acompanhe os pedidos"
)


busca = searchbar(
    placeholder="Pesquisar por pedido, cliente, peça, status ou canal...",
    key="buscar_pedido"
)

status_filtro = st.selectbox(
    "Filtrar por status",
    ["Todos"] + STATUS_PEDIDOS,
    key="filtro_status_pedidos"
)


pedidos_base, filamentos_pedidos = carregar_pedidos_listagem_cache()

termo_busca = (busca or "").strip().lower()

pedidos = pedidos_base

if status_filtro != "Todos":
    pedidos = [
        p for p in pedidos
        if (p[12] or "Orçamento") == status_filtro
    ]

if termo_busca:
    pedidos = [
        p for p in pedidos
        if termo_busca in str(p[1] or "").lower()
        or termo_busca in str(p[3] or "").lower()
        or termo_busca in str(p[4] or "").lower()
        or termo_busca in str(p[6] or "").lower()
        or termo_busca in str(p[7] or "").lower()
        or termo_busca in str(p[12] or "").lower()
        or termo_busca in str(p[13] or "").lower()
    ]

pedidos = paginar_itens(
    pedidos,
    "pedidos",
    opcoes=(10, 25, 50, 100),
    nome_item="pedidos"
)

render_listagem_pedidos(
    pedidos=pedidos,
    filamentos_pedidos=filamentos_pedidos,
    energia_hora=energia_hora,
    depreciacao_hora=depreciacao_hora,
    custo_pos_processamento_hora=custo_pos_processamento_hora,
    meta_lucro_hora=meta_lucro_hora,
    atualizar_status_pedido_func=atualizar_status_pedido,
    limpar_cache_dados_func=limpar_cache_dados,
    editar_pedido_dialog_func=editar_pedido_dialog,
    duplicar_pedido_dialog_func=duplicar_pedido_dialog,
)
