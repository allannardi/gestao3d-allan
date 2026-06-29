# V13.10 — Correção do gráfico de utilização por mês

## Correção
Corrigido o erro:

`TypeError: keys must be str, int, float, bool or None, not tuple`

## Causa
O gráfico usava chaves internas em formato de tupla para montar os tooltips.
O JSON do Python não aceita tuplas como chave.

## Ajuste
- Chaves internas convertidas para texto.
- Mantido o gráfico em barras verticais.
- Mantida a separação por mês.
- Mantidos os últimos 12 meses.
- Mantido o tooltip com:
  - percentual de utilização;
  - horas usadas;
  - capacidade do mês;
  - pedidos.

## Segurança
- Não altera banco.
- Não altera pedidos.
- Não altera cálculo de preço.
- Ajuste apenas no gráfico da Dashboard.
