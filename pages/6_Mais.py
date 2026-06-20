import streamlit as st

from database import inicializar_banco
from components.sidebar import sidebar
from components.mobile_nav import mobile_bottom_nav
from components.header import header
from components.section import section_title
from components.auth import require_login, logout_button


with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_login()

inicializar_banco()

sidebar()
mobile_bottom_nav("mais")

header("Mais", "Acessos complementares do Gestão 3D")


section_title(
    "Cadastros e sistema",
    "Acesse as páginas que ficam fora do menu principal mobile"
)


col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.page_link("pages/1_Filamentos.py", label="Filamentos", icon="🧵")
        st.caption("Rolos, materiais, cores e custos por grama.")

    with st.container(border=True):
        st.page_link("pages/2_Acessorios.py", label="Acessórios", icon="🔩")
        st.caption("Argolas, embalagens, imãs e outros itens.")

with col2:
    with st.container(border=True):
        st.page_link("pages/Configuracoes.py", label="Configurações", icon="⚙️")
        st.caption("Energia, depreciação, margem e meta de lucro/hora.")

    with st.container(border=True):
        st.markdown("**Sair**")
        st.caption("Encerrar o acesso neste dispositivo.")
        logout_button()
