# V11.13 — Mobile corrigido preservando funções

## Causa do erro anterior
Na versão que removia duplicidade, acabou sendo removido junto um bloco de funções importantes da Dashboard, incluindo:
`calcular_custos_pecas_lote`.

## Correção
Esta versão parte novamente da V11.07 aprovada e substitui apenas a segunda função `render_mobile_dashboard`, que é a função efetivamente usada pelo app.

## Preservado
- `calcular_custos_pecas_lote`
- `calcular_pedido`
- lógica da Dashboard desktop
- banco de dados
- pedidos, peças, clientes, filamentos e configurações

## Mobile esperado
- Resumo do mês / cards principais
- Pedidos por status
- Pedidos abertos por peça
- Vendas por mês
- Peças com maior faturamento
- Clientes com maior faturamento
