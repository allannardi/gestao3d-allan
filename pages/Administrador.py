import streamlit as st

from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.desktop_visual import inject_desktop_visual
from components.help_ui import header_with_help
from components.kpi import kpi_card
from components.section import section_title, small_section
from components.auth import require_permissao, usuario_auth_atual
from database import inicializar_banco
from services.impressoras import carregar_impressora_padrao
from services.admin_ajustes import (
    aplicar_entrega_prevista_nas_datas_antigas,
    aplicar_impressora_padrao_pedidos_antigos,
    contar_pedidos_para_ajuste_datas_previstas,
    contar_pedidos_sem_impressora,
)
from services.empresa import obter_dados_empresa, salvar_dados_empresa, STATUS_IMPLANTACAO_OPCOES
from components.onboarding import render_trilha_inicial
from services.onboarding import obter_status_onboarding
from services.usuarios import resumo_usuarios
from services.base_empresa import (
    AMBIENTE_BASE_OPCOES,
    obter_diagnostico_base_empresa,
    salvar_base_empresa,
)
from services.base_limpa import obter_diagnostico_base_limpa
from services.integridade_base import obter_diagnostico_integridade_base


@st.cache_data(ttl=3600, show_spinner=False)
def carregar_css_base_cache():
    with open("assets/style.css", encoding="utf-8") as f:
        return f.read()


def moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def moeda_md(valor):
    return moeda(valor).replace("$", "\\$")


def render_resumo_admin(dados_empresa, status_atual, pedidos_sem_impressora, resumo_ajuste_datas):
    section_title(
        "Central administrativa",
        "Resumo da empresa, implantação e pendências técnicas"
    )

    with st.container(key="administrador_desktop_resumo"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            kpi_card("Empresa", dados_empresa.get("nome_empresa") or "Não definida", "nome no sidebar", "blue")

        with col2:
            kpi_card("Implantação", status_atual or "Em implantação", "status atual", "blue")

        with col3:
            kpi_card(
                "Sem impressora",
                str(pedidos_sem_impressora),
                "pedidos antigos",
                "orange" if pedidos_sem_impressora > 0 else "green"
            )

        with col4:
            kpi_card(
                "Ajuste datas",
                str(resumo_ajuste_datas["total"]),
                "pedidos elegíveis",
                "orange" if resumo_ajuste_datas["total"] > 0 else "green",
            )

    status_onboarding = obter_status_onboarding()
    st.info(
        f"Implantação inicial: {status_onboarding['concluidas']}/{status_onboarding['total']} etapas concluídas "
        f"({status_onboarding['percentual']}%)."
    )

    with st.container(border=True):
        small_section("Próximos atalhos")
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("**Dados da Empresa**")
            st.caption("Identificação do projeto e login Admin da Empresa.")

        with col_b:
            st.markdown("**Trilha inicial**")
            st.caption("Checklist para uma empresa começar do zero.")

        with col_c:
            st.markdown("**Ajustes de Admin**")
            st.caption("Correções pontuais e ações em lote protegidas.")


def render_dados_empresa(dados_empresa, status_atual):
    section_title(
        "Dados da Empresa",
        "Identificação administrativa do projeto e preparação para implantação futura"
    )

    with st.container(border=True):
        small_section("Identificação e implantação")
        st.caption(
            "Os campos marcados com * são obrigatórios. O nome da empresa/projeto aparece abaixo do logo na sidebar."
        )

        status_index = STATUS_IMPLANTACAO_OPCOES.index(status_atual) if status_atual in STATUS_IMPLANTACAO_OPCOES else 0

        with st.form("form_admin_dados_empresa"):
            col_emp1, col_emp2 = st.columns(2)

            with col_emp1:
                nome_empresa_novo = st.text_input(
                    "*Nome da empresa/projeto",
                    value=dados_empresa.get("nome_empresa", ""),
                    help="Obrigatório. Este nome aparece abaixo do logo Gestão 3D na sidebar."
                )

                login_admin_empresa_novo = st.text_input(
                    "*Login Admin da Empresa",
                    value=dados_empresa.get("login_admin_empresa", ""),
                    help="Obrigatório. Pode ser um login livre, como allan, admin ou um e-mail."
                )

                responsavel_empresa_novo = st.text_input(
                    "Responsável",
                    value=dados_empresa.get("responsavel_empresa", ""),
                    help="Pessoa principal responsável pelo projeto dentro da empresa."
                )

                telefone_empresa_novo = st.text_input(
                    "Telefone/WhatsApp",
                    value=dados_empresa.get("telefone_whatsapp_empresa", ""),
                    help="Contato principal da empresa ou responsável."
                )

            with col_emp2:
                cidade_uf_empresa_novo = st.text_input(
                    "Cidade/UF",
                    value=dados_empresa.get("cidade_uf_empresa", ""),
                    help="Ex.: São José dos Campos/SP."
                )

                status_implantacao_novo = st.selectbox(
                    "Status da implantação",
                    STATUS_IMPLANTACAO_OPCOES,
                    index=status_index,
                    help="Use para acompanhar se a empresa ainda está em implantação ou já está operando."
                )

                observacoes_empresa_novo = st.text_area(
                    "Observações internas",
                    value=dados_empresa.get("observacoes_internas_empresa", ""),
                    help="Anotações administrativas internas sobre a implantação, suporte ou contexto da empresa."
                )

            salvar_dados_empresa_btn = st.form_submit_button("Salvar Dados da Empresa")

        if salvar_dados_empresa_btn:
            ok, mensagem, _dados = salvar_dados_empresa(
                nome_empresa_novo,
                login_admin_empresa_novo,
                responsavel_empresa_novo,
                telefone_empresa_novo,
                cidade_uf_empresa_novo,
                observacoes_empresa_novo,
                status_implantacao_novo,
            )

            if not ok:
                st.warning(mensagem)
            else:
                try:
                    st.cache_data.clear()
                except Exception:
                    pass
                st.success(mensagem)
                st.rerun()


def render_implantacao():
    section_title(
        "Trilha inicial",
        "Checklist para começar um projeto do zero"
    )
    render_trilha_inicial(mostrar_quando_completo=True, prefixo_key="onboarding_admin")


def render_ajustes_admin(impressora_padrao, pedidos_sem_impressora, resumo_ajuste_datas):
    section_title(
        "Ajustes de Admin",
        "Ações pontuais e correções em lote para manutenção do sistema"
    )

    with st.container(border=True):
        small_section("Ajuste em lote")

        if impressora_padrao:
            impressora_padrao_label = f"{impressora_padrao[1]} - {impressora_padrao[2]} {impressora_padrao[3]}"

            col_lote1, col_lote2 = st.columns([2, 1])

            with col_lote1:
                st.markdown(
                    f"""
                    **Pedidos sem impressora:** {pedidos_sem_impressora}  
                    **Impressora padrão atual:** {impressora_padrao_label}
                    """
                )
                st.caption(
                    "Use esta opção para preencher automaticamente a impressora padrão nos pedidos antigos que ainda estão sem impressora."
                )

            with col_lote2:
                kpi_card(
                    "Pendentes",
                    str(pedidos_sem_impressora),
                    "sem impressora",
                    "orange" if pedidos_sem_impressora > 0 else "green"
                )

            if pedidos_sem_impressora > 0:
                confirmar_lote = st.checkbox(
                    "Confirmo que desejo aplicar a impressora padrão aos pedidos antigos sem impressora.",
                    key="admin_confirmar_lote_impressora_padrao"
                )

                if st.button(
                    "Aplicar impressora padrão aos pedidos antigos",
                    key="admin_aplicar_impressora_padrao_lote",
                    disabled=not confirmar_lote,
                    use_container_width=True
                ):
                    quantidade_atualizada = aplicar_impressora_padrao_pedidos_antigos(impressora_padrao[0])

                    try:
                        st.cache_data.clear()
                    except Exception:
                        pass

                    st.success(
                        f"Impressora padrão aplicada em {quantidade_atualizada} pedidos antigos."
                    )
                    st.rerun()
            else:
                st.success("Todos os pedidos já possuem impressora vinculada.")
        else:
            st.warning("Cadastre ou defina uma impressora padrão antes de aplicar em lote.")

    with st.container(border=True):
        small_section("Ajuste pontual de datas dos pedidos antigos")

        col_datas1, col_datas2, col_datas3 = st.columns(3)

        with col_datas1:
            kpi_card(
                "Pedidos elegíveis",
                str(resumo_ajuste_datas["total"]),
                "com entrega prevista",
                "orange" if resumo_ajuste_datas["total"] > 0 else "green"
            )

        with col_datas2:
            kpi_card(
                "Sem Data Final Produção",
                str(resumo_ajuste_datas["sem_data_final"]),
                "será preenchida",
                "orange" if resumo_ajuste_datas["sem_data_final"] > 0 else "green"
            )

        with col_datas3:
            kpi_card(
                "Sem Data da Entrega",
                str(resumo_ajuste_datas["sem_data_entrega"]),
                "será preenchida",
                "orange" if resumo_ajuste_datas["sem_data_entrega"] > 0 else "green"
            )

        st.caption(
            "Esta ação pontual preenche Data Final Produção e Data da Entrega usando a Entrega Prevista dos pedidos antigos. "
            "Datas que já foram preenchidas manualmente não são alteradas."
        )

        if resumo_ajuste_datas["total"] > 0:
            confirmar_datas_antigas = st.checkbox(
                "Confirmo que desejo preencher as datas vazias dos pedidos antigos com a Entrega Prevista.",
                key="admin_confirmar_ajuste_datas_pedidos_antigos"
            )

            if st.button(
                "Preencher datas dos pedidos antigos",
                key="admin_preencher_datas_pedidos_antigos",
                disabled=not confirmar_datas_antigas,
                use_container_width=True
            ):
                quantidade_atualizada = aplicar_entrega_prevista_nas_datas_antigas()

                try:
                    st.cache_data.clear()
                except Exception:
                    pass

                st.success(
                    f"Datas preenchidas em {quantidade_atualizada} pedidos antigos."
                )
                st.rerun()
        else:
            st.success("Não há pedidos antigos pendentes para este ajuste.")



def render_base_empresa(diagnostico_base):
    section_title(
        "Base da Empresa",
        "Identidade técnica da base atual para o modelo de um banco por empresa"
    )

    codigo_atual = diagnostico_base.get("codigo_empresa") or "empresa"
    ambiente_atual = diagnostico_base.get("ambiente_base") or AMBIENTE_BASE_OPCOES[0]
    ambiente_index = AMBIENTE_BASE_OPCOES.index(ambiente_atual) if ambiente_atual in AMBIENTE_BASE_OPCOES else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Modelo", "Banco único", "por empresa", "blue")
    with col2:
        kpi_card("Ambiente", ambiente_atual, "base atual", "blue")
    with col3:
        kpi_card("Conexão", diagnostico_base.get("modo") or "Não identificada", "banco atual", "blue")
    with col4:
        kpi_card("Schema", diagnostico_base.get("schema_version") or "-", "versão do banco", "blue")

    with st.container(border=True):
        small_section("Identidade da base")
        st.caption(
            "Estes dados identificam esta base como a base de uma única empresa. "
            "Cada empresa pode apontar para um arquivo SQLite local ou banco Turso diferente via configuração."
        )

        with st.form("form_base_empresa"):
            col_a, col_b = st.columns(2)

            with col_a:
                st.text_input(
                    "Identificador único da base",
                    value=diagnostico_base.get("base_empresa_id") or "",
                    disabled=True,
                    help="Gerado automaticamente para identificar esta base."
                )

                codigo_novo = st.text_input(
                    "Código interno da empresa/base",
                    value=codigo_atual,
                    help="Código curto usado para identificar esta base. Ex.: atelie-van-siqueira, empresa-teste-01."
                )

            with col_b:
                ambiente_novo = st.selectbox(
                    "Ambiente da base",
                    AMBIENTE_BASE_OPCOES,
                    index=ambiente_index,
                    help="Use Operação para a base oficial da empresa. Teste ou Homologação devem ser usados apenas em bases separadas."
                )

                st.text_input(
                    "Modelo de dados",
                    value=diagnostico_base.get("modelo_dados") or "Um banco por empresa",
                    disabled=True,
                )

            salvar_base = st.form_submit_button("Salvar identidade da base")

        if salvar_base:
            ok, mensagem, _dados = salvar_base_empresa(codigo_novo, ambiente_novo)
            if ok:
                try:
                    st.cache_data.clear()
                except Exception:
                    pass
                st.success(mensagem)
                st.rerun()
            else:
                st.warning(mensagem)

    with st.container(border=True):
        small_section("Conexão atual")
        st.caption(
            "Diagnóstico seguro da conexão em uso. O token de acesso nunca é exibido. "
            "Para empresas diferentes, use bancos/URLs separados."
        )

        col_c, col_d = st.columns(2)
        with col_c:
            st.text_input("Tipo de conexão", value=diagnostico_base.get("modo") or "", disabled=True)
            st.text_input("Origem", value=diagnostico_base.get("origem") or "", disabled=True)

        with col_d:
            st.text_input("Banco conectado", value=diagnostico_base.get("banco") or "", disabled=True)
            token_status = "Configurado" if diagnostico_base.get("tem_token") else "Não aplicável / não configurado"
            st.text_input("Token cloud", value=token_status, disabled=True)

    st.success(
        "Base configurável por empresa ativa. Para uma nova empresa, aponte o ambiente para outro arquivo SQLite local "
        "ou outra URL Turso/libSQL, mantendo os dados isolados desta base."
    )



def render_base_limpa(diagnostico_limpa):
    section_title(
        "Base limpa",
        "Validação para uma nova empresa começar em um banco separado sem dados automáticos"
    )

    total_operacional = int(diagnostico_limpa.get("total_operacional") or 0)
    base_limpa = bool(diagnostico_limpa.get("base_operacional_limpa"))
    usuarios = diagnostico_limpa.get("usuarios") or {}

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card(
            "Dados operacionais",
            str(total_operacional),
            "em tabelas principais",
            "green" if base_limpa else "blue",
        )
    with col2:
        kpi_card(
            "Usuários ativos",
            str(usuarios.get("ativos") or 0),
            "acessos da empresa",
            "green" if int(usuarios.get("ativos") or 0) > 0 else "orange",
        )
    with col3:
        kpi_card(
            "Admins da Empresa",
            str(usuarios.get("admins") or 0),
            "ativos",
            "green" if int(usuarios.get("admins") or 0) > 0 else "orange",
        )

    if base_limpa:
        st.success(
            "Esta base não possui dados operacionais cadastrados. Este é o comportamento esperado para uma nova empresa antes da trilha inicial."
        )
    else:
        st.info(
            "Esta base já possui dados operacionais. Isso é esperado para uma empresa em uso. "
            "Para uma nova empresa, o banco separado deve começar sem impressoras, filamentos, peças, clientes, acessórios ou pedidos cadastrados automaticamente."
        )

    with st.container(border=True):
        small_section("Regra técnica para nova base")
        st.caption(
            "A partir desta versão, a criação automática de dados operacionais fica removida do código. "
            "Uma base nova pode receber dados técnicos mínimos, mas impressoras, filamentos, peças, clientes, acessórios e pedidos devem começar vazios."
        )

        seed_operacional = bool(diagnostico_limpa.get("seed_operacional_automatico"))
        if seed_operacional:
            st.warning("Existe regra de seed operacional ativa. Revise antes de criar uma nova base de empresa.")
        else:
            st.success("Seed operacional automático removido. A nova empresa começa sem dados operacionais criados pelo sistema.")

        for regra in diagnostico_limpa.get("regras_base_nova") or []:
            st.markdown(
                f"**{regra.get('item')}** · {regra.get('regra')}  \n"
                f"{regra.get('descricao')}"
            )

    with st.container(border=True):
        small_section("Dados operacionais")
        st.caption(
            "Em uma base nova, estes itens devem começar zerados. O Admin da Empresa preenche tudo pela trilha inicial e pelo uso normal do sistema."
        )

        for item in diagnostico_limpa.get("operacionais") or []:
            total = int(item.get("total") or 0)
            status = "✅ zerado" if total == 0 else "ℹ️ possui dados"
            st.markdown(f"**{item.get('label')}**: {total} · {status}")

    with st.container(border=True):
        small_section("Dados técnicos permitidos")
        st.caption(
            "Esses registros podem existir em uma base nova, pois fazem parte da estrutura mínima do sistema."
        )

        for item in diagnostico_limpa.get("tecnicas") or []:
            st.markdown(f"**{item.get('label')}**: {int(item.get('total') or 0)}")

    st.warning(
        "A partir da v15.14, o sistema não cria mais uma impressora padrão automaticamente em bases novas. "
        "A primeira impressora deve ser cadastrada manualmente pela empresa durante a implantação."
    )


def render_integridade_base(diagnostico_integridade):
    section_title(
        "Integridade da Base",
        "Conferência técnica da estrutura necessária para esta empresa operar com segurança"
    )

    integridade_ok = bool(diagnostico_integridade.get("integridade_ok"))
    total_tabelas = int(diagnostico_integridade.get("total_tabelas") or 0)
    total_tabelas_ok = int(diagnostico_integridade.get("total_tabelas_ok") or 0)
    total_colunas_faltantes = int(diagnostico_integridade.get("total_colunas_faltantes") or 0)
    schema_version = diagnostico_integridade.get("schema_version") or "Não identificado"

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card(
            "Tabelas OK",
            f"{total_tabelas_ok}/{total_tabelas}",
            "estrutura esperada",
            "green" if total_tabelas_ok == total_tabelas else "orange",
        )
    with col2:
        kpi_card(
            "Colunas faltantes",
            str(total_colunas_faltantes),
            "migrações pendentes",
            "green" if total_colunas_faltantes == 0 else "orange",
        )
    with col3:
        kpi_card(
            "Schema",
            schema_version,
            "versão da base",
            "green" if integridade_ok else "blue",
        )

    if integridade_ok:
        st.success(
            "A estrutura técnica da base está íntegra para a versão atual do Gestão 3D."
        )
    else:
        st.warning(
            "Foram encontradas pendências de estrutura. Normalmente isso indica que alguma migration não rodou completamente."
        )

    st.info(
        "Esta checagem é somente diagnóstica. Ela não cria, altera ou apaga dados. "
        "As migrations continuam sendo executadas automaticamente pelo sistema ao inicializar a base."
    )

    grupos = {}
    for item in diagnostico_integridade.get("itens") or []:
        grupos.setdefault(item.get("grupo") or "Outros", []).append(item)

    for grupo, itens in grupos.items():
        with st.container(border=True):
            small_section(grupo)
            for item in itens:
                if item.get("ok"):
                    st.markdown(
                        f"✅ **{item.get('label')}** · `{item.get('tabela')}` · "
                        f"{int(item.get('colunas_presentes') or 0)}/{int(item.get('colunas_esperadas') or 0)} colunas"
                    )
                elif not item.get("existe"):
                    st.markdown(f"⚠️ **{item.get('label')}** · `{item.get('tabela')}` · tabela não encontrada")
                else:
                    faltantes = ", ".join(item.get("colunas_faltantes") or [])
                    st.markdown(
                        f"⚠️ **{item.get('label')}** · `{item.get('tabela')}` · "
                        f"faltando: {faltantes}"
                    )

    if integridade_ok:
        st.caption(
            "Com esta validação, a base atual fica mais bem preparada para o próximo bloco técnico: "
            "trabalhar com bancos separados por empresa."
        )

def _render_item_prontidao(titulo, ok, texto_ok, texto_pendente, obrigatorio=True):
    status = "✅ Concluído" if ok else ("⚠️ Pendente" if obrigatorio else "ℹ️ Recomendado")

    with st.container(border=True):
        st.markdown(f"**{titulo}**")
        st.caption(status)
        if ok:
            st.success(texto_ok)
        elif obrigatorio:
            st.warning(texto_pendente)
        else:
            st.info(texto_pendente)


def render_prontidao_empresa(dados_empresa, status_onboarding, resumo_usuarios_dados, pedidos_sem_impressora, resumo_ajuste_datas):
    section_title(
        "Prontidão da Empresa",
        "Checklist para fechar pendências antes de avançar para uma nova base de empresa"
    )

    dados_empresa_ok = bool(
        str(dados_empresa.get("nome_empresa") or "").strip()
        and str(dados_empresa.get("login_admin_empresa") or "").strip()
    )
    trilha_ok = bool(status_onboarding.get("completo"))
    admin_ok = int(resumo_usuarios_dados.get("admins") or 0) >= 1
    usuarios_ok = int(resumo_usuarios_dados.get("ativos") or 0) >= 1
    operador_ok = int(resumo_usuarios_dados.get("operadores") or 0) >= 1
    ajustes_ok = int(pedidos_sem_impressora or 0) == 0 and int(resumo_ajuste_datas.get("total") or 0) == 0

    checks_obrigatorios = [dados_empresa_ok, trilha_ok, admin_ok, usuarios_ok]
    total_obrigatorios = len(checks_obrigatorios)
    obrigatorios_ok = sum(1 for item in checks_obrigatorios if item)

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Obrigatórios", f"{obrigatorios_ok}/{total_obrigatorios}", "para empresa operar", "green" if obrigatorios_ok == total_obrigatorios else "orange")
    with col2:
        kpi_card("Operadores", str(resumo_usuarios_dados.get("operadores") or 0), "ativos", "green" if operador_ok else "orange")
    with col3:
        pendencias_tecnicas = int(pedidos_sem_impressora or 0) + int(resumo_ajuste_datas.get("total") or 0)
        kpi_card("Pendências técnicas", str(pendencias_tecnicas), "ajustes antigos", "green" if ajustes_ok else "orange")

    st.info(
        "A base atual deve representar uma única empresa. Quando uma nova empresa for liberada no futuro, "
        "ela deverá começar em uma base/banco separado, sem misturar dados com esta empresa."
    )

    small_section("Checklist obrigatório")
    col_a, col_b = st.columns(2)

    with col_a:
        _render_item_prontidao(
            "Dados da Empresa",
            dados_empresa_ok,
            "Nome da empresa/projeto e Login Admin da Empresa estão preenchidos.",
            "Preencha Nome da empresa/projeto e Login Admin da Empresa na aba Dados da Empresa.",
            obrigatorio=True,
        )
        _render_item_prontidao(
            "Admin da Empresa ativo",
            admin_ok,
            "Existe pelo menos um Admin da Empresa ativo.",
            "Mantenha pelo menos um Admin da Empresa ativo para não perder a gestão do sistema.",
            obrigatorio=True,
        )

    with col_b:
        _render_item_prontidao(
            "Trilha inicial concluída",
            trilha_ok,
            "Empresa, impressora, filamento e peça inicial estão cadastrados.",
            "Conclua a trilha inicial: Dados da Empresa, primeira impressora, primeiro filamento e primeira peça.",
            obrigatorio=True,
        )
        _render_item_prontidao(
            "Usuário ativo",
            usuarios_ok,
            "Existe pelo menos um usuário ativo para acessar o sistema.",
            "Crie ou reative um usuário para acessar o sistema.",
            obrigatorio=True,
        )

    small_section("Recomendações antes de liberar uso")
    col_c, col_d = st.columns(2)

    with col_c:
        _render_item_prontidao(
            "Operador ativo",
            operador_ok,
            "Existe pelo menos um Operador ativo para uso operacional.",
            "Recomendado criar um Operador ativo para testar o uso sem acesso administrativo.",
            obrigatorio=False,
        )

    with col_d:
        _render_item_prontidao(
            "Ajustes antigos revisados",
            ajustes_ok,
            "Não há pedidos antigos pendentes nos ajustes administrativos atuais.",
            "Revise a aba Ajustes de Admin se houver pedidos antigos sem impressora ou datas pendentes.",
            obrigatorio=False,
        )

    if obrigatorios_ok == total_obrigatorios:
        st.success("Prontidão obrigatória concluída. Esta empresa está apta para operar nesta base.")
    else:
        st.warning("Ainda há pendências obrigatórias antes de considerar esta empresa pronta para operação.")

st.markdown(f"<style>{carregar_css_base_cache()}</style>", unsafe_allow_html=True)

require_permissao("ver_ajustes_admin")

inicializar_banco()

sidebar()
mobile_bottom_nav("mais")
inject_desktop_visual()


@st.dialog("Ajuda - Administrador")
def ajuda_administrador():
    st.markdown(
        """
        Esta página concentra as configurações administrativas da empresa no Gestão 3D.

        **Use aqui para:**
        - editar os dados da empresa/projeto;
        - acompanhar a trilha inicial de implantação;
        - identificar a base atual da empresa;
        - executar ajustes administrativos pontuais ou em lote;
        - revisar a prontidão da empresa para operar com segurança;
        - validar se uma base nova começa sem dados operacionais automáticos;
        - conferir a integridade técnica das tabelas e colunas da base.

        Esta tela fica disponível apenas para usuários com perfil **Admin da Empresa**.
        """
    )


header_with_help(
    "Administrador",
    "Dados da empresa, base atual, implantação, ajustes administrativos e prontidão operacional",
    ajuda_administrador,
    key="ajuda_administrador_link",
)


dados_empresa = obter_dados_empresa(fallback_login_admin=usuario_auth_atual())
impressora_padrao = carregar_impressora_padrao()
pedidos_sem_impressora = contar_pedidos_sem_impressora()
resumo_ajuste_datas = contar_pedidos_para_ajuste_datas_previstas()
resumo_usuarios_dados = resumo_usuarios()
diagnostico_base = obter_diagnostico_base_empresa()
diagnostico_limpa = obter_diagnostico_base_limpa()
diagnostico_integridade = obter_diagnostico_integridade_base()
status_atual = dados_empresa.get("status_implantacao", STATUS_IMPLANTACAO_OPCOES[0])

aba_resumo, aba_empresa, aba_base, aba_base_limpa, aba_integridade, aba_implantacao, aba_ajustes, aba_prontidao = st.tabs([
    "Resumo",
    "Dados da Empresa",
    "Base da Empresa",
    "Base limpa",
    "Integridade",
    "Implantação",
    "Ajustes de Admin",
    "Prontidão",
])

with aba_resumo:
    render_resumo_admin(dados_empresa, status_atual, pedidos_sem_impressora, resumo_ajuste_datas)

with aba_empresa:
    render_dados_empresa(dados_empresa, status_atual)

with aba_base:
    render_base_empresa(diagnostico_base)

with aba_base_limpa:
    render_base_limpa(diagnostico_limpa)

with aba_integridade:
    render_integridade_base(diagnostico_integridade)

with aba_implantacao:
    render_implantacao()

with aba_ajustes:
    render_ajustes_admin(impressora_padrao, pedidos_sem_impressora, resumo_ajuste_datas)

with aba_prontidao:
    status_onboarding_prontidao = obter_status_onboarding()
    render_prontidao_empresa(
        dados_empresa,
        status_onboarding_prontidao,
        resumo_usuarios_dados,
        pedidos_sem_impressora,
        resumo_ajuste_datas,
    )
