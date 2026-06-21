import streamlit as st


def inject_desktop_visual():
    """
    Refinamento visual global para desktop.

    Mantém o mobile atual preservado e aplica melhorias somente em telas maiores.
    """
    st.markdown(
        """
        <style>
            :root {
                --g3d-primary: #100690;
                --g3d-deep-blue: #0A1A5C;
                --g3d-blue: #0C65AA;
                --g3d-sky: #58C3F0;
                --g3d-bg: #F4F8FB;
                --g3d-card: #FFFFFF;
                --g3d-border: #DEE9EF;
                --g3d-text: #1E3137;
                --g3d-muted: #5C6C74;
                --g3d-success: #1F8A4C;
                --g3d-orange: #B85C20;
                --g3d-danger: #D11A2A;
            }

            @media (min-width: 769px) {

                html, body, [class*="css"] {
                    font-family: 'Barlow', system-ui, sans-serif !important;
                }

                .stApp {
                    background: linear-gradient(180deg, #F7FBFE 0%, #F4F8FB 100%) !important;
                }

                .block-container {
                    padding-top: 2.0rem !important;
                    padding-left: 2.2rem !important;
                    padding-right: 2.2rem !important;
                    max-width: 1420px !important;
                }

                h1 {
                    color: var(--g3d-deep-blue) !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                    font-weight: 800 !important;
                    letter-spacing: -0.8px !important;
                    line-height: 1.08 !important;
                    margin-bottom: 0.25rem !important;
                }

                h2, h3 {
                    color: var(--g3d-deep-blue) !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                    font-weight: 800 !important;
                }

                [data-testid="stCaptionContainer"] {
                    color: var(--g3d-muted) !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                    font-weight: 500 !important;
                }

                /* Sidebar */
                section[data-testid="stSidebar"] {
                    background: #FFFFFF !important;
                    border-right: 1px solid rgba(222, 233, 239, 0.95) !important;
                    box-shadow: 6px 0 24px rgba(10, 26, 92, 0.035) !important;
                    overflow: hidden !important;
                }

                section[data-testid="stSidebar"] > div {
                    background: #FFFFFF !important;
                    padding-left: 1.0rem !important;
                    padding-right: 1.0rem !important;
                    overflow-y: auto !important;
                    overflow-x: hidden !important;
                }

                section[data-testid="stSidebar"] img {
                    filter: none !important;
                    box-shadow: none !important;
                }

                section[data-testid="stSidebar"] p,
                section[data-testid="stSidebar"] span,
                section[data-testid="stSidebar"] label {
                    font-family: 'Barlow', system-ui, sans-serif !important;
                }

                section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
                    color: #7A8992 !important;
                    font-size: 11px !important;
                    font-weight: 800 !important;
                    letter-spacing: 1.5px !important;
                    text-transform: uppercase !important;
                }

                section[data-testid="stSidebar"] a {
                    border-radius: 12px !important;
                    min-height: 38px !important;
                    color: var(--g3d-text) !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                    font-weight: 600 !important;
                    transition: background 0.15s ease, color 0.15s ease, transform 0.15s ease !important;
                }

                section[data-testid="stSidebar"] a:hover {
                    background: #EDF5FA !important;
                    color: var(--g3d-blue) !important;
                    transform: translateX(1px);
                }

                section[data-testid="stSidebar"] a[aria-current="page"] {
                    background: linear-gradient(90deg, #EDF5FA 0%, #F7FBFE 100%) !important;
                    color: var(--g3d-blue) !important;
                    border: 1px solid rgba(12, 101, 170, 0.12) !important;
                    font-weight: 800 !important;
                }

                section[data-testid="stSidebar"] hr {
                    border-color: rgba(222, 233, 239, 0.95) !important;
                }

                /* Cards / containers nativos */
                div[data-testid="stVerticalBlockBorderWrapper"] {
                    border-color: rgba(185, 205, 220, 0.70) !important;
                    border-radius: 18px !important;
                    box-shadow: 0 10px 24px rgba(10, 26, 92, 0.045) !important;
                    background: #FFFFFF !important;
                }

                div[data-testid="stExpander"] {
                    border-color: rgba(185, 205, 220, 0.85) !important;
                    border-radius: 15px !important;
                    overflow: hidden !important;
                    background: #FFFFFF !important;
                }

                div[data-testid="stExpander"] summary {
                    background: #FFFFFF !important;
                    border-radius: 15px !important;
                }

                div[data-testid="stExpander"] summary:hover {
                    background: #F7FBFE !important;
                }

                div[data-testid="stExpander"] summary p {
                    color: var(--g3d-deep-blue) !important;
                    font-weight: 700 !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                }

                /* Inputs */
                div[data-baseweb="base-input"],
                div[data-baseweb="base-input"] > div,
                div[data-baseweb="input"],
                div[data-baseweb="input"] > div,
                div[data-baseweb="textarea"],
                div[data-baseweb="textarea"] > div,
                div[data-baseweb="select"] > div {
                    border-radius: 12px !important;
                    overflow: hidden !important;
                    border-color: #D7E4EC !important;
                    background: #FFFFFF !important;
                }

                div[data-testid="stTextInput"] input,
                div[data-testid="stNumberInput"] input,
                div[data-testid="stDateInput"] input,
                div[data-testid="stTextArea"] textarea,
                div[data-baseweb="select"] > div {
                    border-radius: 12px !important;
                    border-color: #D7E4EC !important;
                    background: #FFFFFF !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                }

                div[data-testid="stTextInput"] input:focus,
                div[data-testid="stNumberInput"] input:focus,
                div[data-testid="stDateInput"] input:focus,
                div[data-testid="stTextArea"] textarea:focus {
                    border-color: var(--g3d-blue) !important;
                    box-shadow: 0 0 0 2px rgba(12, 101, 170, 0.10) !important;
                }

                label, div[data-testid="stMarkdownContainer"] p {
                    font-family: 'Barlow', system-ui, sans-serif !important;
                }

                /* Botões */
                .stButton > button {
                    border-radius: 13px !important;
                    min-height: 42px !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                    font-weight: 800 !important;
                    transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.12s ease !important;
                }

                .stButton > button:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 8px 18px rgba(10, 26, 92, 0.10) !important;
                }

                .stButton > button[kind="primary"],
                .stFormSubmitButton > button[kind="primary"] {
                    background: linear-gradient(135deg, #0A1A5C 0%, #0C65AA 100%) !important;
                    border-color: #0C65AA !important;
                    color: #FFFFFF !important;
                    box-shadow: 0 10px 24px rgba(12, 101, 170, 0.18) !important;
                }

                .stButton > button[kind="secondary"],
                .stFormSubmitButton > button[kind="secondary"] {
                    background: #FFFFFF !important;
                    border: 1px solid #B9CDDC !important;
                    color: var(--g3d-deep-blue) !important;
                }

                .stButton > button[kind="secondary"]:hover,
                .stFormSubmitButton > button[kind="secondary"]:hover {
                    background: #EDF5FA !important;
                    color: var(--g3d-blue) !important;
                    border-color: var(--g3d-blue) !important;
                }

                .stFormSubmitButton > button {
                    border-radius: 13px !important;
                    min-height: 44px !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                    font-weight: 800 !important;
                }

                /* Tabelas DataFrame */
                [data-testid="stDataFrame"] {
                    border-radius: 16px !important;
                    overflow: hidden !important;
                    border: 1px solid rgba(185, 205, 220, 0.65) !important;
                    box-shadow: 0 10px 24px rgba(10, 26, 92, 0.035) !important;
                }

                /* Métricas/alertas */
                div[data-testid="stAlert"] {
                    border-radius: 16px !important;
                    border-color: rgba(185, 205, 220, 0.8) !important;
                    font-family: 'Barlow', system-ui, sans-serif !important;
                }


                /* Hero desktop em degradê */
                .g3d-desktop-hero {
                    display: flex;
                    align-items: stretch;
                    justify-content: space-between;
                    gap: 22px;
                    width: 100%;
                    min-height: 154px;
                    margin: 4px 0 22px 0;
                    padding: 24px 28px;
                    border-radius: 26px;
                    background:
                        radial-gradient(circle at 90% -10%, rgba(88, 195, 240, 0.46) 0%, rgba(88, 195, 240, 0.00) 34%),
                        linear-gradient(135deg, #0A1A5C 0%, #0C65AA 62%, #58C3F0 100%);
                    color: #FFFFFF;
                    box-shadow: 0 18px 42px rgba(10, 26, 92, 0.20);
                    overflow: hidden;
                    position: relative;
                    font-family: 'Barlow', system-ui, sans-serif;
                }

                .g3d-desktop-hero:before {
                    content: "";
                    position: absolute;
                    right: -72px;
                    top: -92px;
                    width: 220px;
                    height: 220px;
                    border-radius: 999px;
                    background: rgba(255, 255, 255, 0.12);
                }

                .g3d-desktop-hero-main,
                .g3d-desktop-hero-chips {
                    position: relative;
                    z-index: 1;
                }

                .g3d-desktop-hero-label {
                    font-size: 11px;
                    font-weight: 800;
                    letter-spacing: 2.2px;
                    text-transform: uppercase;
                    opacity: 0.86;
                    margin-bottom: 10px;
                }

                .g3d-desktop-hero-value {
                    font-size: 44px;
                    font-weight: 800;
                    line-height: 1;
                    letter-spacing: -1px;
                    margin-bottom: 10px;
                }

                .g3d-desktop-hero-subtitle {
                    font-size: 15px;
                    font-weight: 500;
                    opacity: 0.92;
                }

                .g3d-desktop-hero-chips {
                    display: grid;
                    grid-template-columns: repeat(2, minmax(120px, 1fr));
                    gap: 12px;
                    min-width: 360px;
                    align-content: center;
                }

                .g3d-desktop-hero-chip {
                    background: rgba(255, 255, 255, 0.14);
                    border: 1px solid rgba(255, 255, 255, 0.22);
                    border-radius: 18px;
                    padding: 14px 15px;
                    backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px);
                }

                .g3d-desktop-hero-chip strong {
                    display: block;
                    font-size: 21px;
                    font-weight: 800;
                    color: #FFFFFF;
                    line-height: 1.05;
                    margin-bottom: 5px;
                }

                .g3d-desktop-hero-chip span {
                    display: block;
                    font-size: 10.5px;
                    font-weight: 800;
                    color: rgba(255,255,255,0.82);
                    text-transform: uppercase;
                    letter-spacing: 1.2px;
                }

                /* Tabelas customizadas da Dashboard */
                .g3d-table-wrap {
                    border: 1px solid rgba(185, 205, 220, 0.78) !important;
                    border-radius: 20px !important;
                    overflow: auto !important;
                    background: #FFFFFF !important;
                    box-shadow: 0 14px 32px rgba(10, 26, 92, 0.065) !important;
                }

                .g3d-table {
                    border-collapse: separate !important;
                    border-spacing: 0 !important;
                    min-width: 100% !important;
                    table-layout: fixed !important;
                }

                .g3d-table thead th {
                    background: linear-gradient(180deg, #F7FBFE 0%, #EDF5FA 100%) !important;
                    color: #0A1A5C !important;
                    font-weight: 800 !important;
                    border-bottom: 1px solid #D7E4EC !important;
                }

                .g3d-table tbody tr:hover {
                    background: #F7FBFE !important;
                }

                .g3d-status-text {
                    font-family: 'Barlow', system-ui, sans-serif !important;
                    font-size: 12px;
                    font-weight: 800;
                    white-space: nowrap;
                }


                /* Refinamento das listagens e cards de cadastro */
                @media (min-width: 769px) {
                    div[data-testid="stVerticalBlockBorderWrapper"] {
                        border-radius: 20px !important;
                        border-color: rgba(185, 205, 220, 0.78) !important;
                        box-shadow: 0 12px 28px rgba(10, 26, 92, 0.050) !important;
                    }

                    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
                        box-shadow: 0 16px 36px rgba(10, 26, 92, 0.070) !important;
                    }

                    div[data-testid="stExpander"] {
                        border-radius: 15px !important;
                        border-color: rgba(185, 205, 220, 0.82) !important;
                        background: #FFFFFF !important;
                    }

                    div[data-testid="stExpander"] summary {
                        min-height: 42px !important;
                    }

                    div[data-testid="stExpander"] summary p {
                        font-size: 13px !important;
                        font-weight: 800 !important;
                        color: #0A1A5C !important;
                        letter-spacing: 0.1px !important;
                    }
                }


                /* Refinamento de formulários desktop */
                @media (min-width: 769px) {
                    div[data-testid="stForm"] {
                        background: #FFFFFF !important;
                        border: 1px solid rgba(185, 205, 220, 0.82) !important;
                        border-radius: 20px !important;
                        padding: 18px 18px 16px 18px !important;
                        box-shadow: 0 12px 28px rgba(10, 26, 92, 0.050) !important;
                    }

                    div[data-testid="stForm"] div[data-testid="stVerticalBlock"] {
                        gap: 0.55rem !important;
                    }

                    div[data-testid="stTextInput"] label,
                    div[data-testid="stNumberInput"] label,
                    div[data-testid="stDateInput"] label,
                    div[data-testid="stTextArea"] label,
                    div[data-testid="stSelectbox"] label,
                    div[data-testid="stCheckbox"] label {
                        color: #1E3137 !important;
                        font-weight: 700 !important;
                        font-family: 'Barlow', system-ui, sans-serif !important;
                    }

                    div[data-baseweb="base-input"],
                    div[data-baseweb="base-input"] > div,
                    div[data-baseweb="input"],
                    div[data-baseweb="input"] > div,
                    div[data-baseweb="textarea"],
                    div[data-baseweb="textarea"] > div,
                    div[data-baseweb="select"] > div {
                        border-radius: 13px !important;
                        overflow: hidden !important;
                        border-color: #D7E4EC !important;
                    }

                    div[data-testid="stTextInput"] input,
                    div[data-testid="stNumberInput"] input,
                    div[data-testid="stDateInput"] input,
                    div[data-testid="stTextArea"] textarea,
                    div[data-baseweb="select"] > div {
                        min-height: 42px !important;
                        border-radius: 13px !important;
                        border-color: #D7E4EC !important;
                    }

                    div[data-testid="stTextArea"] textarea {
                        min-height: 90px !important;
                    }
                }

                /* Separação geral entre blocos */
                div[data-testid="stVerticalBlock"] {
                    gap: 0.9rem !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )
