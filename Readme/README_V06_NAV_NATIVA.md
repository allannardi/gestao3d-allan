# Gestão 3D Allan v06 - Mobile v03 navegação nativa

Correções desta versão:

1. O menu inferior mobile agora usa `st.page_link`.
2. Isso evita recarregar a página como link HTML puro.
3. O login deixa de ser solicitado a cada troca de aba.
4. O botão "Mais" agora abre uma página própria: `pages/6_Mais.py`.
5. A página Mais contém:
   - Filamentos
   - Acessórios
   - Configurações
   - Sair

Teste recomendado:
1. Rodar `streamlit run Dashboard.py`
2. Entrar pelo login
3. Reduzir a janela ou testar no celular
4. Clicar em Início, Pedidos, Peças, Clientes e Mais
5. Confirmar que não pede login novamente a cada troca
