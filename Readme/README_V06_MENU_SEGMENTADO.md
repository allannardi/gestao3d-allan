# Gestão 3D Allan v06 - Mobile v07 menu segmentado

Correção aplicada:

- As versões com st.columns estavam empilhando os botões no mobile.
- Esta versão usa st.segmented_control, um único widget horizontal.
- Ao escolher uma opção, usa st.switch_page para preservar a sessão do login.
- Os READMEs foram movidos para a pasta `Readme/` para não poluir a raiz.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Reduzir a largura do navegador ou abrir no celular
3. Confirmar se aparecem 5 opções no menu inferior
4. Testar Início, Pedidos, Peças, Clientes e Mais
5. Confirmar que não pede login a cada troca
