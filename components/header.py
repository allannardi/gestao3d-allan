import streamlit as st


def header(titulo, subtitulo=""):
    st.title(titulo)

    if subtitulo:
        st.caption(subtitulo)