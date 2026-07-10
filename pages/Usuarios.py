import streamlit as st
from html import escape

from components.auth import get_usuario_atual, label_perfil, require_admin, require_login
from components.header import header
from components.mobile_nav import mobile_bottom_nav
from components.mobile_summary import mobile_summary_css
from components.section import section_title, small_section
from components.sidebar import sidebar
from components.desktop_visual import inject_desktop_visual
from database import inicializar_banco
from services.usuarios import (
    PERFIL_ADMIN,
    PERFIL_OPERADOR,
    PERFIS_USUARIO,
    STATUS_ATIVO,
    STATUS_INATIVO,
    STATUS_USUARIO,
    atualizar_usuario,
    criar_usuario,
    listar_usuarios,
    obter_usuario,
    redefinir_senha_usuario,
    resumo_usuarios,
)


@st.cache_data(ttl=3600, show_spinner=False)
def carregar_css_base_cache():
    with open("assets/style.css", encoding="utf-8") as f:
        return f.read()


def limpar_cache_dados():
    try:
        st.cache_data.clear()
    except Exception:
        pass


def data_br(valor):
    if not valor:
        return "Nunca"

    texto = str(valor)
    try:
        data, hora = texto.split(" ")
        ano, mes, dia = data.split("-")
        return f"{dia}/{mes}/{ano} {hora[:5]}"
    except Exception:
        return texto


def chip_html(texto, tipo="neutro"):
    cores = {
        "admin": ("#EAF5FC", "#0A1A5C", "#B9CDDC"),
        "operador": ("#F4F7F9", "#1E3137", "#DEE9EF"),
        "ativo": ("#EAF8EF", "#166534", "#B7E4C7"),
        "inativo": ("#FFF1F2", "#9F1239", "#FECDD3"),
        "neutro": ("#F8FBFD", "#5C6C74", "#DEE9EF"),
    }
    bg, cor, borda = cores.get(tipo, cores["neutro"])
    texto_seguro = escape(str(texto or ""))
    estilo = (
        "display:inline-flex;align-items:center;padding:4px 9px;"
        "border-radius:999px;line-height:1;margin-right:4px;"
        f"background:{bg};color:{cor};border:1px solid {borda};"
        "font-size:12px;font-weight:800;"
    )
    return f'<span style="{estilo}">{texto_seguro}</span>'


def usuario_card_html(usuario, tipo_perfil, tipo_status):
    nome = escape(str(usuario.get("nome") or "Usuário"))
    login = escape(str(usuario.get("email") or ""))
    perfil = chip_html(label_perfil(usuario.get("perfil") or PERFIL_OPERADOR), tipo_perfil)
    status = chip_html(usuario.get("status") or STATUS_ATIVO, tipo_status)
    data_criacao = data_br(usuario.get("data_criacao"))
    ultimo_login = data_br(usuario.get("ultimo_login"))

    return (
        '<div class="g3d-user-card">'
        f'<h4>{nome}</h4>'
        f'<p>{login}</p>'
        f'{perfil}{status}'
        '<div class="g3d-user-muted" style="margin-top:0.55rem;">'
        f'Criado em: {escape(str(data_criacao))}<br>'
        f'Último login: {escape(str(ultimo_login))}'
        '</div>'
        '</div>'
    )


def usuarios_css():
    st.markdown(
        """
        <style>
            .g3d-user-card {
                padding: 0.88rem 0.95rem;
                border-radius: 18px;
                border: 1px solid #DEE9EF;
                background: #FFFFFF;
                box-shadow: 0 8px 22px rgba(10, 26, 92, 0.04);
                margin-bottom: 0.75rem;
            }

            .g3d-user-card h4 {
                margin: 0 0 0.12rem 0;
                font-family: 'Barlow', system-ui, sans-serif;
                color: #0A1A5C;
                font-size: 17px;
                font-weight: 800;
            }

            .g3d-user-card p {
                margin: 0.12rem 0 0.45rem 0;
                color: #5C6C74;
                font-size: 13px;
            }

            .g3d-user-muted {
                color: #8A8F98;
                font-size: 12px;
                line-height: 1.35;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )



@st.dialog("Novo usuário")
def novo_usuario_dialog():
    st.caption("Crie o acesso para um colega testar o Gestão 3D.")

    with st.form("form_novo_usuario"):
        nome = st.text_input("Nome", placeholder="Ex.: João Silva")
        email = st.text_input("Usuário / login", placeholder="Ex.: vanessa, operador01 ou email@exemplo.com")
        senha_temporaria = st.text_input("Senha temporária", type="password")

        col1, col2 = st.columns(2)
        with col1:
            perfil = st.selectbox("Perfil", PERFIS_USUARIO, index=PERFIS_USUARIO.index(PERFIL_OPERADOR), format_func=label_perfil)
        with col2:
            status = st.selectbox("Status", STATUS_USUARIO, index=STATUS_USUARIO.index(STATUS_ATIVO))

        st.caption("Para o colega testar, use normalmente Perfil: Operador e Status: Ativo. O perfil Admin exibido aqui representa o Admin da Empresa.")

        confirmar = st.form_submit_button("Criar usuário", type="primary", use_container_width=True)

    if confirmar:
        ok, mensagem = criar_usuario(nome, email, senha_temporaria, perfil, status)
        if ok:
            st.success(mensagem)
            limpar_cache_dados()
            st.rerun()
        else:
            st.warning(mensagem)


@st.dialog("Editar usuário")
def editar_usuario_dialog(usuario_id):
    usuario = obter_usuario(usuario_id)
    usuario_atual = get_usuario_atual() or {}

    if not usuario:
        st.warning("Usuário não encontrado.")
        return

    st.caption("Atualize nome, usuário/login, perfil e status do usuário.")

    with st.form(f"form_editar_usuario_{usuario_id}"):
        nome = st.text_input("Nome", value=usuario.get("nome") or "")
        email = st.text_input("Usuário / login", value=usuario.get("email") or "")

        col1, col2 = st.columns(2)
        with col1:
            perfil_atual = usuario.get("perfil") or PERFIL_OPERADOR
            perfil_index = PERFIS_USUARIO.index(perfil_atual) if perfil_atual in PERFIS_USUARIO else 0
            perfil = st.selectbox("Perfil", PERFIS_USUARIO, index=perfil_index, format_func=label_perfil)
        with col2:
            status_atual = usuario.get("status") or STATUS_ATIVO
            status_index = STATUS_USUARIO.index(status_atual) if status_atual in STATUS_USUARIO else 0
            status = st.selectbox("Status", STATUS_USUARIO, index=status_index)

        confirmar = st.form_submit_button("Salvar alterações", type="primary", use_container_width=True)

    if confirmar:
        ok, mensagem = atualizar_usuario(
            usuario_id,
            nome,
            email,
            perfil,
            status,
            usuario_atual_id=usuario_atual.get("id"),
        )
        if ok:
            st.success(mensagem)
            limpar_cache_dados()
            st.rerun()
        else:
            st.warning(mensagem)

    st.divider()
    small_section("Redefinir senha")
    st.caption("Use para gerar uma senha temporária para o usuário.")

    with st.form(f"form_redefinir_senha_{usuario_id}"):
        nova_senha = st.text_input("Nova senha temporária", type="password")
        confirmar_senha = st.form_submit_button("Redefinir senha", use_container_width=True)

    if confirmar_senha:
        ok, mensagem = redefinir_senha_usuario(usuario_id, nova_senha)
        if ok:
            st.success(mensagem)
            limpar_cache_dados()
            st.rerun()
        else:
            st.warning(mensagem)


st.markdown(f"<style>{carregar_css_base_cache()}</style>", unsafe_allow_html=True)

require_login()
inicializar_banco()
require_admin()

sidebar()
mobile_bottom_nav("mais")
inject_desktop_visual()
mobile_summary_css("usuarios")
usuarios_css()

header("Usuários", "Crie e gerencie acessos da empresa")

section_title(
    "Gerenciamento de usuários",
    "Crie, edite, ative, inative e redefina senhas dos usuários desta empresa."
)

resumo = resumo_usuarios()
usuarios = listar_usuarios()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Usuários", resumo["total"])
col2.metric("Ativos", resumo["ativos"])
col3.metric("Admins da Empresa", resumo["admins"])
col4.metric("Operadores ativos", resumo["operadores"])

st.divider()

col_titulo, col_botao = st.columns([3, 1])
with col_titulo:
    small_section("Lista de usuários")
    st.caption("Crie usuários Operador ou Admin da Empresa para esta empresa.")
with col_botao:
    if st.button("+ Novo usuário", type="primary", use_container_width=True):
        novo_usuario_dialog()

if not usuarios:
    st.info("Nenhum usuário encontrado.")
else:
    for usuario in usuarios:
        tipo_perfil = "admin" if usuario.get("perfil") == PERFIL_ADMIN else "operador"
        tipo_status = "ativo" if usuario.get("status") == STATUS_ATIVO else "inativo"

        with st.container():
            col_info, col_acoes = st.columns([4, 1])

            with col_info:
                st.markdown(
                    usuario_card_html(usuario, tipo_perfil, tipo_status),
                    unsafe_allow_html=True,
                )

            with col_acoes:
                if st.button("Editar", key=f"editar_usuario_{usuario.get('id')}", use_container_width=True):
                    editar_usuario_dialog(usuario.get("id"))

                usuario_atual = get_usuario_atual() or {}
                if usuario.get("status") == STATUS_ATIVO:
                    novo_status = STATUS_INATIVO
                    label_status = "Inativar"
                else:
                    novo_status = STATUS_ATIVO
                    label_status = "Reativar"

                if st.button(label_status, key=f"status_usuario_{usuario.get('id')}", use_container_width=True):
                    ok, mensagem = atualizar_usuario(
                        usuario.get("id"),
                        usuario.get("nome"),
                        usuario.get("email"),
                        usuario.get("perfil"),
                        novo_status,
                        usuario_atual_id=usuario_atual.get("id"),
                    )
                    if ok:
                        st.success(mensagem)
                        limpar_cache_dados()
                        st.rerun()
                    else:
                        st.warning(mensagem)
