import streamlit as st


def sidebar_section(titulo):
    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            gap:8px;
            margin-top:14px;
            margin-bottom:6px;
            font-family:'Barlow', system-ui, sans-serif;
        ">
            <span style="
                font-size:11px;
                font-weight:700;
                color:#8A8F98;
                text-transform:uppercase;
                letter-spacing:0.8px;
                white-space:nowrap;
            ">
                {titulo}
            </span>
            <span style="
                height:1px;
                background:#DEE9EF;
                flex:1;
            "></span>
        </div>
        """,
        unsafe_allow_html=True
    )


def sidebar():
    with st.sidebar:

        st.markdown(
            """
            <div style="
                display:flex;
                flex-direction:column;
                align-items:center;
                text-align:center;
                margin-top:-90px;
                margin-bottom:18px;
            ">
            """,
            unsafe_allow_html=True
        )

        st.image("assets/logo.png", width=105)

        st.markdown(
            """
            <div style="
                font-family:'Barlow', system-ui, sans-serif;
                font-size:22px;
                font-weight:800;
                color:#1E3137;
                margin-top:2px;
                line-height:1.1;
            ">
                Gestão 3D
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")
        st.write("")
        st.write("")
        st.write("")


        sidebar_section("Geral")
        st.page_link("Dashboard.py", label="Dashboard")
        st.page_link("pages/5_Pedidos.py", label="Pedidos")

        sidebar_section("Cadastros")
        st.page_link("pages/4_Clientes.py", label="Clientes")
        st.page_link("pages/3_Pecas.py", label="Peças")
        st.page_link("pages/2_Acessorios.py", label="Acessórios")
        st.page_link("pages/1_Filamentos.py", label="Filamentos")

        sidebar_section("Sistema")
        st.page_link("pages/Configuracoes.py", label="Configurações")

        st.markdown(
            """
            <div style="
                margin-top:22px;
                padding-top:10px;
                border-top:1px solid #DEE9EF;
                font-family:'Barlow', system-ui, sans-serif;
                font-size:11px;
                color:#8A8F98;
            ">
                Versão 0.8
            </div>
            """,
            unsafe_allow_html=True
        )