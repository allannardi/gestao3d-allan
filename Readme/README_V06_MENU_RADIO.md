# Gestão 3D Allan v06 - Mobile v10 menu radio

Alterações:

- Substituído `st.segmented_control` por `st.radio(horizontal=True)`.
- Objetivo: remover o visual de tabela/bordas internas do segmented control.
- Mantém `st.switch_page`, preservando sessão do login.
- Menu continua com:
  Início | Pedidos | Peças | Clientes | Mais
- Novos READMEs continuam dentro da pasta `Readme/`.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Reduzir a largura do navegador ou abrir no celular
3. Verificar visual do menu inferior
4. Testar troca de páginas sem pedir login
