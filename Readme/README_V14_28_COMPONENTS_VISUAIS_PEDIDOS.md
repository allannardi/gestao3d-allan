# V14.28 — Componentes visuais da tela Pedidos

## Objetivo
Continuar a fase 2 do roadmap: simplificar e separar regras internas.

## Alteração principal
Foi criado o componente `components/pedidos_widgets.py` para concentrar funções visuais da tela Pedidos.

## O que foi movido
Saíram da `pages/5_Pedidos.py` e foram para `components/pedidos_widgets.py`:
- `moeda`;
- `moeda_md`;
- `pedidos_mobile_css`;
- `pedido_card`;
- `pedidos_resumo_mobile_css`;
- `pedidos_mobile_kpi_html`;
- `render_pedidos_mobile_resumo`;
- `pedido_mobile_form_css`;
- `pedido_mobile_step`;
- `render_novo_pedido_mobile_resumo`.

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
- Services.

## Validação recomendada
- Abrir a tela Pedidos.
- Conferir os cards de pedidos.
- Conferir o resumo superior desktop.
- Conferir o resumo superior mobile.
- Clicar em `+ Novo Pedido`.
- Conferir as etapas do formulário.
- Conferir o resumo do novo pedido.
- Abrir/editar/duplicar um pedido existente.
