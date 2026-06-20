# Gestão 3D Allan v06 - Mobile v05 menu corrigido

Correção aplicada:

- O menu inferior estava mostrando apenas o botão Início.
- A causa era uma regra de CSS que forçava todas as colunas do app a 100% no celular.
- Essa regra fazia os 5 botões do menu ficarem empilhados verticalmente, e só o primeiro aparecia dentro da barra.
- Removi essa regra global e deixei a largura de 20% apenas dentro do menu inferior.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Reduzir a largura da tela ou abrir no celular
3. Confirmar que aparecem:
   Início | Pedidos | Peças | Clientes | Mais
4. Confirmar que a troca de aba não pede login novamente.
