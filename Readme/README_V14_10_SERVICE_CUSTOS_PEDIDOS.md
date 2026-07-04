# V14.10 — Service de custos internos de Pedidos

## Objetivo
Continuar a fase 2 do roadmap: simplificar e separar regras internas, sem mudar telas e sem mudar regras de negócio.

## Alterações
- Criado `services/pedido_custos.py`.
- Separadas para o novo service as regras de:
  - custo unitário da peça no contexto de pedidos;
  - custo de várias peças em lote;
  - cálculo financeiro do pedido;
  - resumo financeiro superior de Pedidos;
  - cache de custos usados na listagem de Pedidos.
- A tela `pages/5_Pedidos.py` agora delega essas regras para o service.
- Mantido fallback local de segurança caso algum arquivo fique desatualizado.
- Sidebar renumerada para `0.14.10`.

## O que não mudou
- Visual.
- Banco de dados.
- Campos.
- Status.
- Fluxo de cadastro, edição e duplicação.
- Cálculos.
- Filtros e paginação.

## Observação
Esta versão ainda não é uma otimização visual de carregamento. Ela prepara a base para a próxima etapa, onde poderemos otimizar a tela Pedidos com menos risco.
