# V11.11 — Mobile forçado com nova key

## Correção
A Dashboard mobile foi renderizada em uma nova key:
`dashboard_mobile_v11`

Isso evita reaproveitamento visual/cache do container mobile antigo do Streamlit.

## Mantido
- Desktop preservado.
- Mobile com a ordem correta:
  1. Resumo do mês
  2. Pedidos por status
  3. Pedidos abertos por peça
  4. Vendas por mês
  5. Peças com maior faturamento
  6. Clientes com maior faturamento

## Observação
Depois de aplicar, parar e abrir o app novamente.
Se estiver no navegador, usar Ctrl+F5.
