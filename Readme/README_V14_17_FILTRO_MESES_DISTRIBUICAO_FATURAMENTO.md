# V14.17 — Filtro mensal e distribuição do faturamento

## Objetivo
Adicionar análise por período na Dashboard e um gráfico de rosca para entender a composição do faturamento.

## Alterações principais
- Adicionado filtro por mês/ano na Dashboard.
- O filtro permite:
  - Todos;
  - um mês específico;
  - vários meses selecionados.
- O filtro afeta a Dashboard inteira:
  - cards principais;
  - pedidos por status;
  - pedidos abertos por peça;
  - vendas por mês;
  - faturamento por impressora;
  - utilização das impressoras;
  - rankings;
  - novo gráfico de distribuição do faturamento.
- Adicionado gráfico de rosca `Distribuição do faturamento`, ao lado de `Faturamento por impressora`.

## Itens da distribuição
O gráfico de rosca divide o faturamento selecionado em:
- Filamento;
- Energia;
- Depreciação;
- Pós-processamento;
- Acessórios;
- Embalagem;
- Lucro.

## Regra do filtro
O filtro mensal usa a Data do Pedido.

## O que não mudou
- Banco de dados.
- Cadastro de pedidos.
- Cadastro de peças.
- Cadastro de impressoras.
- Regras de preço.
- Regras de custo.
- Layout geral da Dashboard.

## Observação
Esta versão continua a fase 2 do roadmap: simplificar e separar regras internas, usando os services para preparar uma futura migração para backend/API.
