# V14.13 — Otimização de custos da Dashboard

## Objetivo
Continuar a fase 2 do roadmap: simplificar e separar regras internas, começando a melhorar a performance real da Dashboard.

## Alteração principal
A Dashboard passou a pré-calcular custos em lote por grupo de energia/depreciação da impressora.

Antes:
- a Dashboard percorria os pedidos;
- para cada combinação de peça/impressora, chamava o cálculo de custo separadamente.

Agora:
- a Dashboard agrupa pedidos por energia/depreciação;
- calcula várias peças de uma vez por grupo;
- reaproveita o resultado durante a montagem dos indicadores.

## Arquivos alterados
- `Dashboard.py`
- `services/dashboard_custos.py`
- `components/sidebar.py`
- `database.py`

## O que não mudou
- Visual.
- Banco de dados.
- Gráficos.
- Indicadores.
- Regras de cálculo.
- Regras de negócio.

## Observação
Esta versão deve reduzir consultas e recálculos internos na Dashboard, principalmente quando houver muitos pedidos e peças repetidas.
