# V14.25 — Correção do helper de status no mobile da Dashboard

## Objetivo
Corrigir erro na tela inicial após a consolidação da Dashboard na v14.24.

## Correção
- Adicionado o import de `cor_status_hex` a partir de `components/dashboard_widgets.py`.
- A função `render_mobile_dashboard`, que ainda fica em `Dashboard.py`, usa esse helper para colorir os status no mobile.

## O que não mudou
- Banco de dados.
- Cálculos.
- Filtros.
- Gráficos.
- Regras de negócio.
- Services.
- Layout planejado.
