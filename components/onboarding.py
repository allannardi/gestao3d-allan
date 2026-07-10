from html import escape

import streamlit as st

from components.auth import tem_permissao
from services.onboarding import obter_status_onboarding


def onboarding_css():
    st.markdown(
        """
        <style>
            .g3d-onboarding-wrap {
                margin: 0.35rem 0 1.35rem 0;
                padding: 1.05rem 1.10rem;
                border-radius: 18px;
                background: linear-gradient(135deg, #FFFFFF 0%, #F2F8FC 100%);
                border: 1px solid rgba(185, 205, 220, 0.85);
                box-shadow: 0 12px 32px rgba(10, 26, 92, 0.06);
                font-family: 'Barlow', system-ui, sans-serif;
            }

            .g3d-onboarding-head {
                display: flex;
                justify-content: space-between;
                gap: 1rem;
                align-items: flex-start;
                margin-bottom: 0.92rem;
            }

            .g3d-onboarding-title {
                font-size: 18px;
                font-weight: 900;
                color: #0A1A5C;
                line-height: 1.15;
                margin-bottom: 0.22rem;
            }

            .g3d-onboarding-subtitle {
                font-size: 12px;
                font-weight: 500;
                color: #5C6C74;
                line-height: 1.35;
            }

            .g3d-onboarding-badge {
                min-width: 78px;
                text-align: center;
                border-radius: 999px;
                padding: 0.42rem 0.68rem;
                background: #EAF5FC;
                color: #0C65AA;
                font-size: 12px;
                font-weight: 900;
                border: 1px solid rgba(12, 101, 170, 0.14);
                white-space: nowrap;
            }

            .g3d-onboarding-progress {
                height: 9px;
                width: 100%;
                border-radius: 999px;
                background: #E6EEF4;
                overflow: hidden;
                margin: 0.45rem 0 0.90rem 0;
            }

            .g3d-onboarding-progress span {
                display: block;
                height: 100%;
                border-radius: 999px;
                background: linear-gradient(90deg, #0C65AA 0%, #18A058 100%);
            }

            .g3d-onboarding-step {
                min-height: 104px;
                padding: 0.92rem 0.96rem;
                border-radius: 16px;
                border: 1px solid rgba(222, 233, 239, 0.95);
                background: #FFFFFF;
                box-shadow: 0 8px 20px rgba(10, 26, 92, 0.035);
                font-family: 'Barlow', system-ui, sans-serif;
                margin-bottom: 0.70rem;
            }

            .g3d-onboarding-step-title {
                display: flex;
                align-items: center;
                gap: 0.45rem;
                font-size: 14px;
                font-weight: 900;
                color: #0A1A5C;
                margin-bottom: 0.30rem;
            }

            .g3d-onboarding-step-desc {
                font-size: 12px;
                color: #5C6C74;
                line-height: 1.35;
                min-height: 34px;
            }

            .g3d-onboarding-ok,
            .g3d-onboarding-pending {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-width: 22px;
                height: 22px;
                border-radius: 999px;
                font-size: 12px;
                font-weight: 900;
            }

            .g3d-onboarding-ok {
                color: #0E7A3C;
                background: #E6F7EE;
                border: 1px solid rgba(14, 122, 60, 0.16);
            }

            .g3d-onboarding-pending {
                color: #B96B00;
                background: #FFF4E0;
                border: 1px solid rgba(185, 107, 0, 0.16);
            }

            .g3d-onboarding-complete {
                margin: 0.15rem 0 1.10rem 0;
                padding: 0.82rem 0.95rem;
                border-radius: 16px;
                background: #E6F7EE;
                border: 1px solid rgba(14, 122, 60, 0.16);
                color: #0E7A3C;
                font-family: 'Barlow', system-ui, sans-serif;
                font-size: 13px;
                font-weight: 800;
            }

            .st-key-onboarding_btn_empresa button,
            .st-key-onboarding_btn_impressora button,
            .st-key-onboarding_btn_filamento button,
            .st-key-onboarding_btn_peca button,
            .st-key-onboarding_cfg_btn_empresa button,
            .st-key-onboarding_cfg_btn_impressora button,
            .st-key-onboarding_cfg_btn_filamento button,
            .st-key-onboarding_cfg_btn_peca button,
            .st-key-onboarding_admin_btn_empresa button,
            .st-key-onboarding_admin_btn_impressora button,
            .st-key-onboarding_admin_btn_filamento button,
            .st-key-onboarding_admin_btn_peca button {
                background: #FFFFFF !important;
                color: #0C65AA !important;
                border: 1px solid #B9CDDC !important;
                border-radius: 12px !important;
                font-weight: 900 !important;
                min-height: 38px !important;
            }

            .st-key-onboarding_btn_empresa button:hover,
            .st-key-onboarding_btn_impressora button:hover,
            .st-key-onboarding_btn_filamento button:hover,
            .st-key-onboarding_btn_peca button:hover,
            .st-key-onboarding_cfg_btn_empresa button:hover,
            .st-key-onboarding_cfg_btn_impressora button:hover,
            .st-key-onboarding_cfg_btn_filamento button:hover,
            .st-key-onboarding_cfg_btn_peca button:hover,
            .st-key-onboarding_admin_btn_empresa button:hover,
            .st-key-onboarding_admin_btn_impressora button:hover,
            .st-key-onboarding_admin_btn_filamento button:hover,
            .st-key-onboarding_admin_btn_peca button:hover {
                background: #EDF5FA !important;
                color: #0A1A5C !important;
                border-color: #0C65AA !important;
            }

            @media (max-width: 768px) {
                .g3d-onboarding-head {
                    flex-direction: column;
                    gap: 0.55rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _html_card(etapa):
    concluida = bool(etapa.get("concluida"))
    icone = "✓" if concluida else "!"
    classe = "g3d-onboarding-ok" if concluida else "g3d-onboarding-pending"
    status = "Concluído" if concluida else "Pendente"

    return f"""
    <div class="g3d-onboarding-step">
        <div class="g3d-onboarding-step-title">
            <span class="{classe}">{icone}</span>
            <span>{escape(str(etapa.get('titulo') or 'Etapa'))}</span>
        </div>
        <div class="g3d-onboarding-step-desc">{escape(str(etapa.get('descricao') or ''))}</div>
        <div style="font-size:11px;font-weight:900;color:{'#0E7A3C' if concluida else '#B96B00'};margin-top:0.35rem;">{status}</div>
    </div>
    """


def render_trilha_inicial(mostrar_quando_completo=True, prefixo_key="onboarding"):
    """Renderiza a trilha inicial para Admin da Empresa.

    Retorna True quando renderizou algo na tela.
    """
    if not tem_permissao("ver_ajustes_admin"):
        return False

    status = obter_status_onboarding()

    if status["completo"] and not mostrar_quando_completo:
        return False

    onboarding_css()

    if status["completo"]:
        st.markdown(
            """
            <div class="g3d-onboarding-complete">
                Trilha inicial concluída: dados da empresa, impressora, filamento e peça já foram cadastrados.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return True

    st.markdown(
        f"""
        <div class="g3d-onboarding-wrap">
            <div class="g3d-onboarding-head">
                <div>
                    <div class="g3d-onboarding-title">Trilha inicial do projeto</div>
                    <div class="g3d-onboarding-subtitle">
                        Para um projeto novo, configure primeiro os dados obrigatórios da empresa e depois cadastre a primeira impressora, o primeiro filamento e a primeira peça.
                    </div>
                </div>
                <div class="g3d-onboarding-badge">{status['concluidas']}/{status['total']} etapas</div>
            </div>
            <div class="g3d-onboarding-progress"><span style="width:{status['percentual']}%;"></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    for idx, etapa in enumerate(status["etapas"]):
        with cols[idx % 4]:
            st.markdown(_html_card(etapa), unsafe_allow_html=True)
            if not etapa["concluida"]:
                key = f"{prefixo_key}_btn_{etapa['chave']}"
                if st.button(etapa["botao"], key=key, use_container_width=True):
                    st.switch_page(etapa["destino"])

    st.write("")
    return True
