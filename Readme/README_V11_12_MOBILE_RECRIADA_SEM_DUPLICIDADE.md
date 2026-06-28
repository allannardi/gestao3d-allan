# V11.12 — Dashboard mobile recriada sem duplicidade

## Correção importante
O Dashboard.py tinha duas funções com o mesmo nome:
`render_mobile_dashboard`.

A função antiga aparecia depois da nova e acabava sobrescrevendo a versão recriada.
Por isso o mobile continuava exibindo:
- Pedidos abertos
- Peças mais vendidas
- Ranking por quantidade

## O que foi feito
- Removida a função mobile antiga duplicada.
- Mantida apenas a nova Dashboard mobile recriada.
- Mantida a Dashboard desktop aprovada da V11.07.
- Mantida a assinatura antiga da função para evitar erro de keyword argument.

## Ordem esperada no mobile
- Resumo do mês / cards principais
- Pedidos por status
- Pedidos abertos por peça
- Vendas por mês
- Peças com maior faturamento
- Clientes com maior faturamento

## Segurança
- Não altera banco de dados.
- Não altera tabelas.
- Não altera pedidos, peças, clientes, filamentos ou configurações.
- Alteração concentrada no Dashboard.py.
