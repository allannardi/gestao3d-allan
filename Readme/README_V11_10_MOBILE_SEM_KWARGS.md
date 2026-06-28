# V11.10 — Correção definitiva do erro mobile

## Correção
Removida a passagem de novos parâmetros na chamada da função `render_mobile_dashboard`.

## Por que
No teste local apareceu:
`TypeError: render_mobile_dashboard() got an unexpected keyword argument 'vendas_mes_grafico'`

Para evitar esse erro, a função mobile voltou a usar a assinatura antiga e agora lê:
- `vendas_mes_grafico`
- `clientes_resumo`

diretamente das variáveis globais já calculadas na Dashboard.

## Resultado esperado
- Sem erro ao abrir a página Início.
- Gráfico Vendas por mês aparece no mobile.
- Ordem mobile acompanha a ordem aprovada:
  - Pedidos por status
  - Pedidos abertos por peça
  - Vendas por mês
  - Peças com maior faturamento
  - Clientes com maior faturamento
