# Gestão 3D Allan v06 - Mobile v04 navegação por botões

Correção aplicada:

1. Removido `st.page_link(..., icon="...")`, pois alguns símbolos não são emojis válidos para o Streamlit.
2. Menu inferior agora usa `st.button` + `st.switch_page`.
3. Isso preserva a sessão e não deve pedir login a cada troca de aba.
4. Mantém os ícones no texto do botão.
5. Mantém a página "Mais" com Filamentos, Acessórios, Configurações e Sair.

Teste:
- Rodar `streamlit run Dashboard.py`
- Fazer login
- Testar Início, Pedidos, Peças, Clientes e Mais em tela estreita/celular.
