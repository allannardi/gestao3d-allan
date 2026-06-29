# V13.04 — kWh global e cards azuis

## Ajustes realizados

1. Markup Padrão
- Removido do help o trecho: "Antes era chamado de margem padrão".
- Texto final: "Percentual usado para sugerir o preço de venda com base no custo calculado."

2. Valor do kWh
- Removido dos campos da impressora, tanto em nova impressora quanto em edição de impressora existente.
- O valor do kWh agora fica apenas em Parâmetros Gerais.
- A energia/hora da impressora usa:
  consumo da impressora × valor do kWh geral.

3. Cards superiores
- Todos os 5 cards superiores foram ajustados para azul:
  - Impressoras
  - Markup Padrão
  - Pós Processamento
  - Meta Lucro/hora
  - Valor do kWh

4. Presets
- Os presets de impressora não carregam mais valor do kWh próprio.
- O kWh vem sempre dos Parâmetros Gerais.

## Segurança
- Não apaga dados.
- Não altera pedidos existentes.
- Não altera peças existentes.
- Mantém a tabela de impressoras.
