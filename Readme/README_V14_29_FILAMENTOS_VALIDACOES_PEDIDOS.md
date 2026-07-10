# V14.29 — Filamentos e validações da tela Pedidos

## Objetivo
Continuar a organização interna da tela Pedidos, separando interface, validações e página principal.

## O que foi criado
- `components/pedidos_filamentos_ui.py`
- `services/pedido_validacoes.py`

## O que foi movido
Saiu de `pages/5_Pedidos.py`:

### Para `components/pedidos_filamentos_ui.py`
- `montar_filamentos_pedido`

### Para `services/pedido_validacoes.py`
- `montar_alertas_pedido_operador`

### Para `components/pedidos_widgets.py`
- `render_conferencia_pedido_operador`

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
- Clicar em `+ Novo Pedido`.
- Selecionar uma peça.
- Conferir seleção de filamento/rolo.
- Conferir alertas antes de salvar.
- Salvar um novo pedido.
- Editar um pedido existente e conferir filamentos.
- Duplicar um pedido.
