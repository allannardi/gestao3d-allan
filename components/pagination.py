import streamlit as st


def paginar_itens(itens, chave, opcoes=(10, 25, 50, 100), nome_item="itens"):
    """
    Paginação simples para listas do Streamlit.

    O Streamlit reexecuta a página a cada clique, então limitar a quantidade
    de cards renderizados por vez ajuda bastante quando a base crescer.
    """
    total = len(itens)

    if total == 0:
        st.caption("Nenhum item encontrado.")
        return itens

    menor_opcao = min(opcoes)

    if total <= menor_opcao:
        st.caption(f"Exibindo {total} de {total} {nome_item}.")
        return itens

    por_pagina_key = f"{chave}_por_pagina"
    pagina_key = f"{chave}_pagina"

    col_pag1, col_pag2, col_pag3 = st.columns([1.1, 0.9, 2.4])

    with col_pag1:
        por_pagina = st.selectbox(
            "Itens por página",
            list(opcoes),
            index=0,
            key=por_pagina_key
        )

    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)

    if pagina_key not in st.session_state:
        st.session_state[pagina_key] = 1

    if st.session_state[pagina_key] > total_paginas:
        st.session_state[pagina_key] = total_paginas

    if st.session_state[pagina_key] < 1:
        st.session_state[pagina_key] = 1

    # Não passamos `value=` aqui porque o Streamlit mostra aviso quando
    # um widget tem `key` e também recebe valor padrão enquanto a chave
    # já existe no session_state.
    with col_pag2:
        pagina = st.number_input(
            "Página",
            min_value=1,
            max_value=total_paginas,
            step=1,
            key=pagina_key
        )

    inicio = (pagina - 1) * por_pagina
    fim = min(inicio + por_pagina, total)

    with col_pag3:
        st.caption(
            f"Exibindo {inicio + 1}–{fim} de {total} {nome_item} "
            f"· página {pagina} de {total_paginas}"
        )

    return itens[inicio:fim]
