# V14.12 — Service de custos da Dashboard

## Objetivo
Continuar a fase 2 do roadmap: simplificar e separar regras internas.

## Alterações
- Criado `services/dashboard_custos.py`.
- A Dashboard passou a delegar para esse service:
  - cálculo de custo unitário de peça;
  - cálculo de custos de peças em lote;
  - cálculo financeiro de pedido.
- Mantido fallback local de segurança na Dashboard.
- Sidebar renumerada para `0.14.12`.

## O que não mudou
- Visual.
- Banco de dados.
- Gráficos.
- Cálculos.
- Indicadores.
- Regras de negócio.

## Observação
Esta versão ainda é uma separação interna. A próxima etapa pode focar na otimização real da Dashboard.
