# Gestão 3D Allan v06 - Mobile v06 menu horizontal forçado

Correção aplicada:

- O menu inferior ainda mostrava apenas o botão Início.
- O Streamlit empilhava as colunas no celular.
- Esta versão força o bloco do menu a ficar em linha horizontal:
  Início | Pedidos | Peças | Clientes | Mais

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Reduzir a tela ou abrir no celular
3. Confirmar se aparecem os 5 botões
4. Testar se a troca de aba não pede login novamente
