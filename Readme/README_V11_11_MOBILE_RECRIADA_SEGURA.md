# V11.11 — Dashboard mobile recriada com segurança

## Base usada
Este checkpoint foi criado a partir da V11.07 aprovada.

## O que foi feito
A Dashboard mobile foi recriada do zero, sem alterar a Dashboard desktop.

## Segurança
- Não altera banco de dados.
- Não altera tabelas.
- Não altera pedidos, peças, clientes, filamentos ou configurações.
- Alteração principal concentrada no `Dashboard.py`.

## Ordem no mobile
- Resumo do mês / cards principais
- Pedidos por status
- Pedidos abertos por peça
- Vendas por mês
- Peças com maior faturamento
- Clientes com maior faturamento

## Observações
- A assinatura antiga da função `render_mobile_dashboard` foi preservada.
- Isso evita o erro `unexpected keyword argument`.
- O gráfico de vendas por mês é lido das variáveis já calculadas na Dashboard.
