# Gestão 3D Allan v06.11 - Menu mobile absoluto

Alterações:

- Substituído o menu em radio/segmented control por 5 botões Streamlit normais.
- Os botões são posicionados horizontalmente via CSS absoluto.
- Objetivo:
  - manter `st.switch_page`, preservando sessão do login;
  - evitar empilhamento de colunas no mobile;
  - evitar visual de tabela;
  - manter visual mais próximo de app.
- Arquivo README nomeado com versão completa conforme padrão solicitado.
- Novos READMEs ficam dentro da pasta `Readme/`.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Reduzir a largura do navegador ou abrir no celular
3. Confirmar se aparecem:
   Início | Pedidos | Peças | Clientes | Mais
4. Confirmar que o item ativo fica destacado
5. Confirmar que a troca de abas não pede login novamente
