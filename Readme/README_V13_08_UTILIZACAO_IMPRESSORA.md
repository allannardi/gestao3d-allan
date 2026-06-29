# V13.08 — Utilização da Impressora

## Objetivo
Adicionar indicador visual para entender se cada impressora está subutilizada ou sobrecarregada.

## Cálculo
A utilização mensal é calculada assim:

Horas usadas no mês ÷ horas disponíveis no mês × 100

Exemplo:
- 150 horas usadas
- 720 horas disponíveis
- utilização = 20,8%

## Implementação
- Dashboard calcula horas usadas por impressora no mês atual.
- Horas usadas vêm do tempo total estimado dos pedidos não cancelados.
- Capacidade do mês = dias do mês atual × 24 horas.
- Pedidos antigos sem impressora usam a impressora padrão.
- Adicionado gráfico:
  - Utilização das impressoras no mês

## Segurança
- Não altera banco de dados.
- Não altera pedidos existentes.
- Não altera cálculos de preço.
- Apenas adiciona visualização na Dashboard.
