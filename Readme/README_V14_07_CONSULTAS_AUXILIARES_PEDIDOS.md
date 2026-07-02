# V14.07 — Consultas auxiliares de pedidos no service

## Objetivo
Continuar a simplificação interna da tela Pedidos, movendo consultas e regras auxiliares para `services/pedidos.py`.

## Alterações
- Movidos para `services/pedidos.py`:
  - `carregar_impressoras_pedidos()`;
  - `selecionar_impressora_padrao()`;
  - `label_impressora()`;
  - `carregar_clientes()`;
  - `carregar_pecas()`;
  - `cor_status()`;
  - `cor_status_hex()`.
- A página `pages/5_Pedidos.py` passou a importar essas funções do service.
- Sidebar renumerada para `0.14.07`.

## O que não mudou
- Visual.
- Banco de dados.
- Campos.
- Filtros.
- Paginação.
- Cálculos.
- Fluxo de cadastro, edição, duplicação e status.

## Por que isso importa
Essas funções eram regras e consultas auxiliares que deixavam a página Pedidos maior. Agora ficam centralizadas no service, mantendo a tela mais limpa internamente.
