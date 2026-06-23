# Gestão 3D Allan v10.03 - Correção aviso da paginação

Correção:
- Removido aviso amarelo do Streamlit:
  `The widget with key "pecas_pagina" was created with a default value but also had its value set via the Session State API.`

Causa:
- O componente de paginação definia o valor da página no `st.session_state`
  e também passava `value=` no `st.number_input`.
- O Streamlit funciona, mas mostra esse aviso.

Correção aplicada:
- O `number_input` da página agora usa apenas `key=...`.
- O valor inicial continua controlado com segurança pelo `session_state`.
- Nenhuma regra de negócio foi alterada.

Preservado:
- Paginação.
- Itens por página.
- Busca.
- Visual.
- Mobile.
- Banco de dados.
- Cálculo de pós-processamento.
