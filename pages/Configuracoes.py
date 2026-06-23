import streamlit as st

from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.desktop_visual import inject_desktop_visual
from components.mobile_summary import mobile_summary_css, render_mobile_summary
from components.header import header
from components.kpi import kpi_card
from components.section import section_title, small_section
from components.auth import require_login, alterar_senha_app, usuario_auth_atual, senha_personalizada_ativa
from database import conectar, inicializar_banco



@st.cache_data(ttl=3600, show_spinner=False)
def carregar_css_base_cache():
    with open("assets/style.css", encoding="utf-8") as f:
        return f.read()


def moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


st.markdown(f"<style>{carregar_css_base_cache()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()

sidebar()
mobile_bottom_nav("mais")
inject_desktop_visual()
mobile_summary_css("configuracoes")
header("Configurações", "Parâmetros principais do sistema")


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


energia = config[0]
depreciacao = config[1]
margem = config[2]
meta = config[3]
custo_pos = config[4] if len(config) > 4 else 0


with st.container(key="configuracoes_mobile_resumo"):
    render_mobile_summary(
        hero_label="Parâmetros ativos",
        hero_value=f"{moeda(meta)}/h",
        hero_subtitle=f"meta de lucro/hora · margem padrão {margem:.0f}%",
        kpis=[
            {"titulo": "Energia", "valor": f"{moeda(energia)}/h", "subtitulo": "custo por hora", "cor": "#0C65AA"},
            {"titulo": "Depreciação", "valor": f"{moeda(depreciacao)}/h", "subtitulo": "desgaste", "cor": "#B85C20"},
            {"titulo": "Pós-proc.", "valor": f"{moeda(custo_pos)}/h", "subtitulo": "mão de obra", "cor": "#B85C20"},
            {"titulo": "Margem", "valor": f"{margem:.0f}%", "subtitulo": "lucro sugerido", "cor": "#1F8A4C"},
            {"titulo": "Meta", "valor": moeda(meta), "subtitulo": "referência mínima", "cor": "#100690"},
        ],
    )

with st.container(key="configuracoes_desktop_resumo"):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        kpi_card("Energia", f"{moeda(energia)}/h", "custo estimado por hora", "blue")

    with col2:
        kpi_card("Depreciação", f"{moeda(depreciacao)}/h", "desgaste da impressora", "orange")

    with col3:
        kpi_card("Pós-processamento", f"{moeda(custo_pos)}/h", "custo por hora manual", "orange")

    with col4:
        kpi_card("Margem padrão", f"{margem:.0f}%", "lucro sugerido", "green")

    with col5:
        kpi_card("Meta lucro/hora", moeda(meta), "referência mínima", "gray")


section_title(
    "Parâmetros de cálculo",
    "Ajuste os valores usados nos cálculos de custo, preço sugerido e rentabilidade"
)


with st.container(border=True):

    small_section("Custos operacionais")

    with st.form("configuracoes"):

        col_form1, col_form2 = st.columns(2)

        with col_form1:

            energia_nova = st.number_input(
                "Energia (R$/hora)",
                min_value=0.0,
                value=float(energia),
                step=0.01
            )

            custo_pos_novo = st.number_input(
                "Pós-processamento (R$/hora)",
                min_value=0.0,
                value=float(custo_pos),
                step=1.0
            )

        with col_form2:

            depreciacao_nova = st.number_input(
                "Depreciação (R$/hora)",
                min_value=0.0,
                value=float(depreciacao),
                step=0.01
            )

            margem_nova = st.number_input(
                "Margem padrão (%)",
                min_value=0.0,
                value=float(margem),
                step=10.0
            )

            meta_nova = st.number_input(
                "Meta lucro/hora (R$)",
                min_value=0.0,
                value=float(meta),
                step=1.0
            )

        salvar = st.form_submit_button("Salvar Configurações")

    if salvar:

        conn = conectar()

        conn.execute("""
        UPDATE configuracoes
        SET
            energia_hora = ?,
            depreciacao_hora = ?,
            margem_padrao = ?,
            meta_lucro_hora = ?,
            custo_pos_processamento_hora = ?
        """,
        (
            energia_nova,
            depreciacao_nova,
            margem_nova,
            meta_nova,
            custo_pos_novo
        ))

        conn.commit()
        conn.close()

        try:
            st.cache_data.clear()
        except Exception:
            pass

        st.success("Configurações atualizadas com sucesso!")
        st.rerun()


section_title(
    "Acesso e senha",
    "Troque a senha usada para entrar no sistema"
)


with st.container(border=True):

    small_section("Trocar senha")

    usuario_login = usuario_auth_atual()

    if senha_personalizada_ativa():
        st.caption("Senha personalizada ativa. A troca fica salva no banco atual do sistema.")
    else:
        st.caption("Ainda usando a senha inicial do secrets. Ao trocar, a nova senha ficará salva no banco atual.")

    with st.form("trocar_senha_acesso"):

        usuario_exibicao = st.text_input(
            "Usuário",
            value=usuario_login,
            disabled=True
        )

        senha_atual = st.text_input(
            "Senha atual",
            type="password"
        )

        nova_senha = st.text_input(
            "Nova senha",
            type="password"
        )

        confirmar_senha = st.text_input(
            "Confirmar nova senha",
            type="password"
        )

        salvar_senha = st.form_submit_button("Salvar Nova Senha")

    if salvar_senha:

        if not senha_atual or not nova_senha or not confirmar_senha:
            st.warning("Preencha a senha atual, a nova senha e a confirmação.")

        elif nova_senha != confirmar_senha:
            st.warning("A confirmação da senha não confere.")

        else:
            sucesso, mensagem = alterar_senha_app(usuario_login, senha_atual, nova_senha)

            if sucesso:
                st.success("Senha alterada com sucesso. No próximo login, use a nova senha.")
            else:
                st.error(mensagem)


section_title(
    "Como esses parâmetros são usados",
    "Referência rápida para manter os cálculos consistentes"
)


with st.container(border=True):

    col_info1, col_info2 = st.columns(2)

    with col_info1:
        st.markdown("**Energia**")
        st.write("Valor aplicado por hora de impressão.")

        st.markdown("**Depreciação**")
        st.write("Valor aplicado por hora para representar desgaste da impressora.")

        st.markdown("**Pós-processamento**")
        st.write("Valor aplicado por hora de trabalho manual após a impressão. O tempo é o campo de pós-processamento cadastrado em cada peça.")

    with col_info2:
        st.markdown("**Margem padrão**")
        st.write("Percentual usado para calcular o preço sugerido das peças.")

        st.markdown("**Meta lucro/hora**")
        st.write("Referência usada para indicar se uma peça está recomendada ou abaixo da meta.")