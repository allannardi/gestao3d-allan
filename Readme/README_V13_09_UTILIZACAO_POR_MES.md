# V13.09 — Utilização por mês

## Ajuste
O gráfico de utilização das impressoras foi alterado para mostrar a utilização separada por mês.

## Como ficou
- Barras verticais.
- Eixo X por mês.
- Cada impressora aparece como uma série de barras.
- Mostra os últimos 12 meses.
- Tooltip mostra:
  - percentual de utilização;
  - horas usadas;
  - capacidade do mês;
  - quantidade de pedidos.

## Cálculo
Utilização % = horas usadas no mês / horas disponíveis no mês × 100

Horas disponíveis do mês = quantidade de dias do mês × 24.

## Segurança
- Não altera banco de dados.
- Não altera pedidos.
- Não altera cálculo de preço.
- Apenas altera a visualização da Dashboard.
