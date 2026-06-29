# V13.07 — Dashboard por Impressora

## Objetivo
Continuar a integração da Gestão de Impressoras, agora na tela Início/Dashboard.

## Alterações
- Dashboard passa a ler a impressora vinculada ao pedido.
- Cálculos do Dashboard usam energia/hora e depreciação/hora da impressora do pedido.
- Pedidos antigos sem impressora continuam usando a configuração padrão.
- Adicionada seção:
  - Faturamento por impressora
- Ranking mostra faturamento, pedidos, lucro e margem por máquina.
- Rodapé de parâmetros mostra a impressora padrão atual.

## Segurança
- Não altera banco de dados.
- Não altera pedidos existentes.
- Não altera peças, clientes ou filamentos.
- Apenas ajusta cálculos e visualização da Dashboard.
