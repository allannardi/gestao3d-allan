# V14.27 — Limpeza de fallbacks antigos da tela Pedidos

## Objetivo
Iniciar o novo ciclo de organização da tela Pedidos, depois do checkpoint seguro da v14.26.

## Alteração principal
Foram removidos da `pages/5_Pedidos.py` os fallbacks antigos que já estavam consolidados em services.

## O que foi consolidado
A tela Pedidos agora importa diretamente funções de:

- `services/pedidos.py`
- `services/pedido_filamentos.py`
- `services/pedido_custos.py`

## O que saiu da tela Pedidos
Foram removidas cópias locais antigas de:
- consultas auxiliares de clientes, peças e impressoras;
- consulta de listagem de pedidos;
- funções de filamentos do pedido;
- funções de cálculo de custo de pedidos.

## O que não mudou
- Visual.
- Banco de dados.
- Fluxo de novo pedido.
- Edição de pedido.
- Duplicação de pedido.
- Status.
- Filtros.
- Paginação.
- Regras de cálculo.

## Validação recomendada
- Abrir a tela Pedidos.
- Conferir resumo superior.
- Abrir um pedido existente.
- Editar um pedido.
- Duplicar um pedido.
- Alterar status.
- Criar um novo pedido.
- Conferir filamentos do pedido.
