import streamlit as st


def action_button(label, key, variant="secondary"):
    tipo = "primary" if variant == "primary" else "secondary"

    return st.button(
        label,
        key=key,
        type=tipo,
        use_container_width=True
    )


def primary_button(label, key):
    return action_button(label, key, "primary")


def secondary_button(label, key):
    return action_button(label, key, "secondary")


def danger_button(label, key):
    return action_button(label, key, "secondary")