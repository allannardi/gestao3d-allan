# Gestão 3D Allan v11.02 - Cards de lucro no pedido

Objetivo:
Levar os indicadores de lucro para o card principal do pedido, antes de abrir os detalhes.

Alterações:

## Cards da listagem de pedidos
A sequência dos mini-cards passou a ser:
1. Data;
2. Qtd.;
3. Total;
4. Lucro, com margem pequena;
5. Lucro/hora.

## Detalhes do pedido
- Removidos os cards grandes de lucro, margem e lucro/hora de dentro dos detalhes.
- O resumo financeiro detalhado continua mostrando subtotal, desconto, frete, custo e total.

## Novo Pedido
- Incluído o card lateral "Lucro por hora" no resumo da criação do pedido.
- O card mostra também o status em relação à meta:
  - acima da meta;
  - atenção;
  - abaixo da meta.

Preservado:
- Fluxo de filamento real no pedido.
- Pós-processamento no cálculo.
- Datas em DD/MM/AAAA.
- Paginação.
- Dados e banco preservados.
