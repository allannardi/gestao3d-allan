# V14.24 — Consolidação final da Dashboard

## Objetivo
Consolidar as etapas v14.21 a v14.24 em um único patch, encerrando o ciclo principal de organização interna da Dashboard.

## O que foi feito
- Criado `components/dashboard_widgets.py`.
- Movidas para esse componente funções visuais da Dashboard:
  - formatação visual;
  - rankings;
  - tabelas;
  - gráficos;
  - card de distribuição do faturamento;
  - helpers visuais do mobile.
- Removidas da `Dashboard.py` funções antigas/fallbacks locais de:
  - custo;
  - consulta SQL;
  - montagem alternativa de dados.
- A `Dashboard.py` ficou mais focada em:
  - carregar dados pelos services;
  - aplicar filtro de período;
  - chamar services de resumo;
  - renderizar a página com componentes.

## Estrutura consolidada
- `Dashboard.py`: orquestra a página.
- `services/dashboard_dados.py`: consultas de banco.
- `services/dashboard_custos.py`: custos e pré-cálculos.
- `services/dashboard_resumos.py`: montagem dos indicadores.
- `components/dashboard_widgets.py`: renderizações visuais.

## O que não mudou
- Banco de dados.
- Cálculos.
- Regras de negócio.
- Filtro por mês/ano.
- Gráfico de distribuição do faturamento.
- Layout geral desktop/mobile.

## Validação recomendada
- Abrir a Dashboard.
- Testar filtro `Todos`.
- Testar filtro com um mês.
- Testar filtro com vários meses.
- Conferir cards principais.
- Conferir gráfico de rosca.
- Conferir Faturamento por Impressora.
- Conferir Utilização das Impressoras por mês.
- Conferir visual mobile se possível.
