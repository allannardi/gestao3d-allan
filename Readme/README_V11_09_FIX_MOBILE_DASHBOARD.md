# V11.09 — Correção erro Dashboard mobile

## Correção
Corrigido erro:
`TypeError: render_mobile_dashboard() got an unexpected keyword argument 'vendas_mes_grafico'`

## O que foi reforçado
- A função mobile agora aceita `vendas_mes_grafico` e `clientes_resumo`.
- Foram adicionados valores padrão para evitar falha caso o Streamlit reaproveite algum estado antigo.
- A Dashboard mobile continua com:
  - Pedidos por status
  - Pedidos abertos por peça
  - Gráfico Vendas por mês
  - Peças com maior faturamento
  - Clientes com maior faturamento

## Observação
Substituir o arquivo Dashboard.py inteiro é importante.
