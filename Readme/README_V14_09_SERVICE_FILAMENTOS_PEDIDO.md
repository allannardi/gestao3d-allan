# V14.09 — Service de filamentos do pedido

## Objetivo
Continuar a simplificação interna da tela Pedidos, separando consultas e gravações relacionadas aos filamentos reais usados em cada pedido.

## Alterações
- Criado `services/pedido_filamentos.py`.
- Movidas para o novo service:
  - `carregar_filamentos_ativos()`;
  - `carregar_consumo_filamentos()`;
  - `carregar_disponibilidade_filamentos()`;
  - `carregar_requisitos_filamentos_peca()`;
  - `carregar_filamentos_pedido_registros()`;
  - `salvar_filamentos_pedido()`;
  - `carregar_filamentos_pedido()`.
- A interface de escolha dos filamentos continua na tela Pedidos.
- Adicionado fallback de segurança na página Pedidos.
- Sidebar renumerada para `0.14.09`.

## O que não mudou
- Visual.
- Banco de dados.
- Fluxo de pedidos.
- Cálculos.
- Filtros.
- Paginação.
- Escolha de filamentos do pedido.

## Por que isso importa
O controle de consumo de filamento é uma regra importante e agora fica em um service próprio, deixando a tela Pedidos mais organizada internamente.
