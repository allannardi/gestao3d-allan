# V14.05 — Consulta da listagem de pedidos no service

## Objetivo
Continuar a fase V14 de simplificação interna, retirando da tela Pedidos a consulta principal da listagem.

## Alterações
- `carregar_pedidos_listagem_cache()` saiu de `pages/5_Pedidos.py`.
- A função agora fica em `services/pedidos.py`.
- A tela Pedidos continua usando a mesma função, com o mesmo nome e mesmo retorno.
- A consulta continua trazendo pedidos e filamentos por pedido em lote.
- Sidebar renumerada para `0.14.05`.

## O que não mudou
- Visual.
- Banco de dados.
- Filtros.
- Paginação.
- Cards de pedidos.
- Regras de status.
- Cálculos.
- Fluxo de cadastro, edição e duplicação.

## Por que isso importa
A tela Pedidos é uma das maiores do sistema. Esta versão remove mais uma parte de consulta SQL da tela, deixando o caminho preparado para otimizações futuras.
