import streamlit as st
from datetime import date

from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.desktop_visual import inject_desktop_visual
from components.mobile_summary import mobile_summary_css, render_mobile_summary
from components.header import header
from components.help_ui import header_with_help
from components.kpi import kpi_card
from components.section import section_title, small_section
from components.auth import require_login, alterar_senha_app, usuario_auth_atual, senha_personalizada_ativa, get_usuario_atual, label_perfil
from database import conectar, inicializar_banco
from services.impressoras import (
    PRESETS_IMPRESSORAS,
    calcular_energia_hora,
    carregar_impressora_padrao,
    carregar_impressoras,
    garantir_coluna_configuracoes_valor_kwh,
    garantir_impressoras_configuracoes,
    gerar_codigo_impressora,
    sincronizar_configuracao_com_impressora_padrao,
)



@st.cache_data(ttl=3600, show_spinner=False)
def carregar_css_base_cache():
    with open("assets/style.css", encoding="utf-8") as f:
        return f.read()


def moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")

def moeda_md(valor):
    return moeda(valor).replace("$", "\\$")




st.markdown(f"<style>{carregar_css_base_cache()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()

sidebar()
mobile_bottom_nav("mais")
inject_desktop_visual()
mobile_summary_css("configuracoes")


@st.dialog("Ajuda - Configurações")
def ajuda_configuracoes():
    st.markdown(
        """
        Esta tela define os valores usados nos cálculos do sistema.

        **Configurações gerais da empresa:**
        - **Markup padrão:** percentual usado para sugerir o preço de venda.
        - **Meta lucro/hora:** ganho mínimo desejado por hora.
        - **Pós-processamento:** custo por hora de acabamento, montagem, limpeza ou embalagem.

        **Impressoras:**
        - cada impressora tem consumo, valor do kWh, energia/hora e depreciação/hora próprios;
        - a energia/hora é calculada automaticamente pelo consumo da impressora e valor do kWh;
        - a primeira impressora cadastrada é usada como padrão.

        Se você não tiver certeza de algum valor, mantenha o valor atual e ajuste depois com base na prática.
        """
    )

header_with_help("Configurações", "Parâmetros principais do sistema", ajuda_configuracoes, key="ajuda_configuracoes_link")


garantir_coluna_configuracoes_valor_kwh()
garantir_impressoras_configuracoes()

conn = conectar()

config = conn.execute("""
SELECT
    energia_hora,
    depreciacao_hora,
    margem_padrao,
    meta_lucro_hora,
    COALESCE(custo_pos_processamento_hora, 0),
    COALESCE(valor_kwh, 0.65)
FROM configuracoes
LIMIT 1
""").fetchone()

conn.close()


energia = config[0]
depreciacao = config[1]
margem = config[2]
meta = config[3]
custo_pos = config[4] if len(config) > 4 else 0
valor_kwh_geral = config[5] if len(config) > 5 else 0.65

impressoras = carregar_impressoras()
impressora_padrao = carregar_impressora_padrao()
total_impressoras = len(impressoras)
impressoras_ativas = len([i for i in impressoras if (i[4] or "Ativa") == "Ativa"])

if impressora_padrao:
    energia = impressora_padrao[7] if impressora_padrao[7] is not None else energia
    depreciacao = impressora_padrao[8] if impressora_padrao[8] is not None else depreciacao


with st.container(key="configuracoes_mobile_resumo"):
    render_mobile_summary(
        hero_label="Parâmetros ativos",
        hero_value=f"{moeda(meta)}/h",
        hero_subtitle=f"meta de lucro/hora · markup padrão {margem:.0f}%",
        kpis=[
            {"titulo": "Impressoras", "valor": impressoras_ativas, "subtitulo": "ativas", "cor": "#0C65AA"},
            {"titulo": "Markup", "valor": f"{margem:.0f}%", "subtitulo": "preço sugerido", "cor": "#0C65AA"},
            {"titulo": "Pós-proc.", "valor": f"{moeda(custo_pos)}/h", "subtitulo": "mão de obra", "cor": "#0C65AA"},
            {"titulo": "Meta", "valor": moeda(meta), "subtitulo": "lucro/hora", "cor": "#0C65AA"},
            {"titulo": "kWh", "valor": moeda(valor_kwh_geral), "subtitulo": "energia", "cor": "#0C65AA"},
        ],
    )

with st.container(key="configuracoes_desktop_resumo"):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        kpi_card("Impressoras", str(total_impressoras), f"{impressoras_ativas} ativas", "blue")

    with col2:
        kpi_card("Markup padrão", f"{margem:.0f}%", "preço sugerido", "blue")

    with col3:
        kpi_card("Pós-processamento", f"{moeda(custo_pos)}/h", "custo por hora manual", "blue")

    with col4:
        kpi_card("Meta lucro/hora", moeda(meta), "referência mínima", "blue")

    with col5:
        kpi_card("Valor do kWh", moeda(valor_kwh_geral), "energia elétrica", "blue")


section_title(
    "Configurações gerais da empresa",
    "Ajuste valores que valem para toda a operação"
)


with st.container(border=True):

    small_section("Parâmetros gerais")

    with st.form("configuracoes"):

        col_form1, col_form2 = st.columns(2)

        with col_form1:

            margem_nova = st.number_input(
                "Markup Padrão (%)",
                min_value=0.0,
                value=float(margem),
                step=10.0,
                help="Percentual usado para sugerir o preço de venda com base no custo calculado."
            )

            custo_pos_novo = st.number_input(
                "Pós-processamento (R$/hora)",
                min_value=0.0,
                value=float(custo_pos),
                step=1.0,
                help="Custo por hora de trabalho manual depois da impressão: acabamento, montagem, limpeza ou embalagem."
            )

        with col_form2:

            meta_nova = st.number_input(
                "Meta lucro/hora (R$)",
                min_value=0.0,
                value=float(meta),
                step=1.0,
                help="Ganho mínimo desejado por hora. O sistema usa isso para indicar se a peça/pedido está dentro da meta."
            )

            valor_kwh_novo_geral = st.number_input(
                "Valor do kWh (R$)",
                min_value=0.0,
                value=float(valor_kwh_geral),
                step=0.01,
                help="Valor médio cobrado pela energia elétrica. Este valor será usado como referência para calcular energia/hora das impressoras."
            )

        salvar = st.form_submit_button("Salvar Configurações Gerais")

    if salvar:

        conn = conectar()

        conn.execute("""
        UPDATE configuracoes
        SET
            margem_padrao = ?,
            meta_lucro_hora = ?,
            custo_pos_processamento_hora = ?,
            valor_kwh = ?
        """,
        (
            margem_nova,
            meta_nova,
            custo_pos_novo,
            valor_kwh_novo_geral
        ))

        impressoras_para_recalcular = conn.execute("""
        SELECT id, COALESCE(consumo_w, 0)
        FROM impressoras
        """).fetchall()

        for impressora_id_recalc, consumo_recalc in impressoras_para_recalcular:
            energia_recalculada = calcular_energia_hora(consumo_recalc, valor_kwh_novo_geral)
            conn.execute("""
            UPDATE impressoras
            SET
                valor_kwh = ?,
                energia_hora = ?
            WHERE id = ?
            """,
            (
                valor_kwh_novo_geral,
                energia_recalculada,
                impressora_id_recalc
            ))

        conn.commit()
        conn.close()

        try:
            st.cache_data.clear()
        except Exception:
            pass

        st.success("Configurações gerais atualizadas com sucesso!")
        st.rerun()


section_title(
    "Impressoras",
    "Cadastre as máquinas e seus custos próprios de energia e depreciação"
)


with st.container(border=True):

    small_section("Impressoras cadastradas")

    if not impressoras:
        st.info("Nenhuma impressora cadastrada ainda.")

    for imp in impressoras:
        (
            impressora_id,
            codigo,
            marca,
            modelo,
            status,
            consumo_w,
            valor_kwh,
            energia_imp,
            depreciacao_imp,
            observacoes_imp,
            is_padrao,
            data_cadastro,
        ) = imp

        titulo_padrao = " · Padrão" if is_padrao else ""

        with st.expander(f"{codigo} - {marca} {modelo}{titulo_padrao}", expanded=bool(is_padrao)):

            col_card1, col_card2, col_card3, col_card4 = st.columns(4)

            with col_card1:
                kpi_card("Status", status or "Ativa", "situação atual", "green" if status == "Ativa" else "gray")

            with col_card2:
                kpi_card("Consumo", f"{consumo_w:.0f} W", "potência informada", "blue")

            with col_card3:
                kpi_card("Energia/hora", f"{moeda(energia_imp)}/h", "calculado", "orange")

            with col_card4:
                kpi_card("Depreciação", f"{moeda(depreciacao_imp)}/h", "por hora", "gray")

            with st.form(f"editar_impressora_{impressora_id}"):

                col_edit1, col_edit2 = st.columns(2)

                with col_edit1:
                    marca_edit = st.text_input("Marca", value=marca or "", key=f"marca_imp_{impressora_id}")
                    modelo_edit = st.text_input("Modelo", value=modelo or "", key=f"modelo_imp_{impressora_id}")
                    status_edit = st.selectbox(
                        "Status",
                        ["Ativa", "Inativa"],
                        index=0 if (status or "Ativa") == "Ativa" else 1,
                        key=f"status_imp_{impressora_id}"
                    )

                with col_edit2:
                    consumo_edit = st.number_input(
                        "Consumo da impressora (W)",
                        min_value=0.0,
                        value=float(consumo_w or 0),
                        step=10.0,
                        key=f"consumo_imp_{impressora_id}"
                    )

                    valor_kwh_edit = valor_kwh_geral
                    energia_edit = calcular_energia_hora(consumo_edit, valor_kwh_geral)

                    st.markdown(f"**Energia/hora calculada:** {moeda_md(energia_edit)}/h  \nValor do kWh usado: **{moeda_md(valor_kwh_geral)}**")

                    depreciacao_edit = st.number_input(
                        "Depreciação/hora (R$)",
                        min_value=0.0,
                        value=float(depreciacao_imp or 0),
                        step=0.01,
                        key=f"depreciacao_imp_{impressora_id}"
                    )

                observacoes_edit = st.text_area(
                    "Observações",
                    value=observacoes_imp or "",
                    key=f"obs_imp_{impressora_id}"
                )

                salvar_edicao_imp = st.form_submit_button("Salvar Alterações")

            if salvar_edicao_imp:

                if not marca_edit:
                    st.warning("Informe a marca da impressora.")

                elif not modelo_edit:
                    st.warning("Informe o modelo da impressora.")

                elif consumo_edit <= 0:
                    st.warning("Informe o consumo da impressora em W.")

                else:
                    conn = conectar()

                    conn.execute("""
                    UPDATE impressoras
                    SET
                        marca = ?,
                        modelo = ?,
                        status = ?,
                        consumo_w = ?,
                        valor_kwh = ?,
                        energia_hora = ?,
                        depreciacao_hora = ?,
                        observacoes = ?
                    WHERE id = ?
                    """,
                    (
                        marca_edit,
                        modelo_edit,
                        status_edit,
                        consumo_edit,
                        valor_kwh_edit,
                        energia_edit,
                        depreciacao_edit,
                        observacoes_edit,
                        impressora_id
                    ))

                    if is_padrao:
                        sincronizar_configuracao_com_impressora_padrao(conn, impressora_id)

                    conn.commit()
                    conn.close()

                    st.success("Impressora atualizada com sucesso!")
                    st.rerun()

            if not is_padrao and status == "Ativa":
                if st.button("Definir como impressora padrão", key=f"padrao_imp_{impressora_id}"):
                    conn = conectar()
                    conn.execute("UPDATE impressoras SET is_padrao = 0")
                    conn.execute("UPDATE impressoras SET is_padrao = 1 WHERE id = ?", (impressora_id,))
                    sincronizar_configuracao_com_impressora_padrao(conn, impressora_id)
                    conn.commit()
                    conn.close()
                    st.success(f"{codigo} definida como impressora padrão.")
                    st.rerun()



if "mostrar_form_impressora" not in st.session_state:
    st.session_state["mostrar_form_impressora"] = False


if st.button("+ Adicionar nova impressora", key="btn_adicionar_nova_impressora"):
    st.session_state["mostrar_form_impressora"] = not st.session_state["mostrar_form_impressora"]


if st.session_state["mostrar_form_impressora"]:

    with st.container(border=True):

        small_section("Nova impressora")

        preset_escolhido = st.selectbox(
            "Modelo pré-definido",
            list(PRESETS_IMPRESSORAS.keys()),
            key="preset_nova_impressora",
            help="Escolha um modelo para preencher valores iniciais. O valor do kWh vem dos Parâmetros Gerais."
        )

        preset = PRESETS_IMPRESSORAS[preset_escolhido]

        with st.form("nova_impressora"):

            col_imp1, col_imp2 = st.columns(2)

            with col_imp1:
                marca_nova = st.text_input(
                    "Marca",
                    value=preset["marca"],
                    help="Marca da impressora. Ex.: Bambu Lab, Creality, Anycubic."
                )

                modelo_novo = st.text_input(
                    "Modelo",
                    value=preset["modelo"],
                    help="Modelo da impressora. Ex.: A1 Mini, Ender-3 V3 SE."
                )

                status_novo = st.selectbox(
                    "Status",
                    ["Ativa", "Inativa"],
                    help="Use Inativa para máquinas paradas ou fora de uso."
                )

            with col_imp2:
                consumo_novo = st.number_input(
                    "Consumo da impressora (W)",
                    min_value=0.0,
                    value=float(preset["consumo_w"]),
                    step=10.0,
                    help="Potência média/estimada da impressora durante uso. Ex.: 200 W."
                )

                valor_kwh_novo = valor_kwh_geral
                energia_hora_nova = calcular_energia_hora(consumo_novo, valor_kwh_geral)

                st.markdown(
                    f"**Energia/hora calculada:** {moeda_md(energia_hora_nova)}/h  "
                    f"\nValor do kWh usado: **{moeda_md(valor_kwh_geral)}**"
                )

                depreciacao_nova_imp = st.number_input(
                    "Depreciação/hora (R$)",
                    min_value=0.0,
                    value=float(preset["depreciacao_hora"]),
                    step=0.01,
                    help="Custo estimado de desgaste, manutenção e uso da impressora por hora."
                )

            observacoes_nova = st.text_area(
                "Observações",
                help="Opcional. Registre bico instalado, local da máquina, material preferido ou cuidados especiais."
            )

            salvar_impressora = st.form_submit_button("Salvar Impressora")

        if salvar_impressora:

            if not marca_nova:
                st.warning("Informe a marca da impressora.")

            elif not modelo_novo:
                st.warning("Informe o modelo da impressora.")

            elif consumo_novo <= 0:
                st.warning("Informe o consumo da impressora em W.")

            else:
                conn = conectar()

                total_atual = conn.execute("SELECT COUNT(*) FROM impressoras").fetchone()[0]
                is_padrao = 1 if total_atual == 0 else 0
                codigo = gerar_codigo_impressora(conn)

                conn.execute("""
                INSERT INTO impressoras
                (
                    codigo,
                    marca,
                    modelo,
                    status,
                    consumo_w,
                    valor_kwh,
                    energia_hora,
                    depreciacao_hora,
                    observacoes,
                    is_padrao,
                    data_cadastro
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    codigo,
                    marca_nova,
                    modelo_novo,
                    status_novo,
                    consumo_novo,
                    valor_kwh_novo,
                    energia_hora_nova,
                    depreciacao_nova_imp,
                    observacoes_nova,
                    is_padrao,
                    str(date.today())
                ))

                if is_padrao:
                    nova_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                    sincronizar_configuracao_com_impressora_padrao(conn, nova_id)

                conn.commit()
                conn.close()

                st.success(f"Impressora {codigo} cadastrada com sucesso!")
                st.session_state["mostrar_form_impressora"] = False
                st.rerun()


section_title(
    "Acesso e senha",
    "Troque a senha usada para entrar no sistema"
)


with st.container(border=True):

    small_section("Trocar senha")

    usuario_login = usuario_auth_atual()
    usuario_atual = get_usuario_atual() or {}
    usuario_nome = usuario_atual.get("nome") or usuario_login
    usuario_perfil = label_perfil(usuario_atual.get("perfil") or "")

    if usuario_perfil:
        st.markdown(f"**Conta atual:** {usuario_nome}  \n**Login:** {usuario_login}  \n**Perfil:** {usuario_perfil}")
    else:
        st.markdown(f"**Conta atual:** {usuario_nome}  \n**Login:** {usuario_login}")

    if senha_personalizada_ativa():
        st.caption("A troca altera somente a senha do usuário logado na base atual do sistema.")
    else:
        st.caption("Ainda usando a senha inicial do sistema. Ao trocar, a nova senha ficará salva no banco atual.")

    with st.form("trocar_senha_acesso"):

        usuario_exibicao = st.text_input(
            "Usuário/Login",
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
