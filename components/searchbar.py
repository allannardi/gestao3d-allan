import streamlit as st


def searchbar(placeholder="Pesquisar...", key="searchbar"):
    termo = st.text_input(
        label="Buscar",
        placeholder=placeholder,
        key=key,
        label_visibility="collapsed"
    )

    return termo