import streamlit as st


def header_with_help(titulo, subtitulo, ajuda_callback, key):
    """
    Renderiza o título da página com um link discreto de Ajuda à direita.
    Mantém o visual limpo e evita um botão grande ocupando espaço.
    """
    st.markdown(
        """
        <style>
            .g3d-help-link-container button {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: #0C65AA !important;
                font-weight: 700 !important;
                padding: 0 !important;
                min-height: auto !important;
                height: auto !important;
                text-decoration: none !important;
            }

            .g3d-help-link-container button:hover {
                color: #0A1A5C !important;
                text-decoration: underline !important;
                background: transparent !important;
                border: none !important;
            }

            .g3d-help-title-row {
                margin-bottom: -0.35rem;
            }

            @media (max-width: 768px) {
                .g3d-help-title-row {
                    margin-bottom: -0.10rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_titulo, col_ajuda = st.columns([0.86, 0.14], vertical_alignment="top")

    with col_titulo:
        st.markdown(
            f"""
            <div class="g3d-help-title-row">
                <h1 style="
                    margin: 0;
                    color: #0A1A5C;
                    font-family: 'Barlow', system-ui, sans-serif;
                    font-size: clamp(2.25rem, 4vw, 3.15rem);
                    line-height: 1.05;
                    letter-spacing: -1.8px;
                    font-weight: 900;
                ">{titulo}</h1>
                <p style="
                    margin: 1.35rem 0 0 0;
                    color: #9AA6AF;
                    font-family: 'Barlow', system-ui, sans-serif;
                    font-size: 0.96rem;
                    line-height: 1.35;
                ">{subtitulo}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_ajuda:
        st.markdown('<div class="g3d-help-link-container" style="text-align:right;margin-top:0.55rem;">', unsafe_allow_html=True)
        if st.button("Ajuda", key=key, help="Clique para ver orientações rápidas sobre esta tela."):
            ajuda_callback()
        st.markdown("</div>", unsafe_allow_html=True)
