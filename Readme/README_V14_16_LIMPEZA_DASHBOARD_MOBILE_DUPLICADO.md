# V14.16 — Limpeza de bloco mobile duplicado na Dashboard

## Objetivo
Continuar a fase 2 do roadmap: simplificar e separar regras internas, reduzindo código duplicado.

## Alteração principal
A Dashboard tinha um bloco mobile duplicado com funções repetidas:
- `nome_curto`;
- `rotulo_mes_grafico`;
- `mobile_cor`;
- `mobile_kpi_html`;
- `mobile_section_header`;
- `mobile_status_chip`;
- `mobile_dashboard_css`;
- `render_mobile_dashboard`.

O primeiro bloco duplicado foi removido. A versão usada pela tela foi mantida.

## O que não mudou
- Visual.
- Banco de dados.
- Gráficos.
- Indicadores.
- Cálculos.
- Regras de negócio.
- Layout mobile e desktop.

## Observação
Esta é uma limpeza interna. O objetivo é reduzir o tamanho e a complexidade do arquivo `Dashboard.py`.
