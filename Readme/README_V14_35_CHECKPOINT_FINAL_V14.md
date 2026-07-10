# V14.35 — Checkpoint final da fase v14

## Objetivo
Encerrar a fase v14 como uma base segura antes de iniciar a etapa v15 de usuários.

## Natureza deste patch
Esta versão é um checkpoint de fechamento.

Não foram alteradas regras de negócio, banco de dados funcional, cálculos, telas ou fluxos operacionais.

## Base usada
- Base anterior: v14.34 — Listagem de Pedidos em componente.
- Nova versão: v14.35 — Checkpoint final v14.

## Principais entregas consolidadas na v14

### Dashboard
A Dashboard foi reorganizada e consolidada:
- `Dashboard.py` ficou focada em orquestrar a página.
- `services/dashboard_dados.py` concentra consultas.
- `services/dashboard_custos.py` concentra custos e pré-cálculos.
- `services/dashboard_resumos.py` concentra indicadores e resumos.
- `components/dashboard_widgets.py` concentra gráficos, rankings e renderizações visuais.
- Dashboard mobile passou a exibir também:
  - Faturamento por impressora;
  - Distribuição do faturamento;
  - Utilização das impressoras por mês.

### Pedidos
A tela Pedidos foi reorganizada e consolidada:
- `pages/5_Pedidos.py` ficou focada em orquestrar a tela.
- `components/pedido_novo_form.py` concentra o formulário de novo pedido.
- `components/pedido_dialogs.py` concentra edição e duplicação.
- `components/pedidos_listagem.py` concentra listagem, status rápido e ações.
- `components/pedidos_widgets.py` concentra visual, cards e CSS.
- `components/pedidos_filamentos_ui.py` concentra seleção de filamento/rolo.
- `services/pedido_dados.py` concentra dados auxiliares.
- `services/pedido_validacoes.py` concentra alertas e validações.
- `services/pedido_custos.py` concentra cálculos.
- `services/pedido_filamentos.py` concentra filamentos.

## Tamanho aproximado dos arquivos principais
- `Dashboard.py`: 21032 caracteres.
- `pages/5_Pedidos.py`: 7401 caracteres.

## O que não mudou nesta versão
- Banco de dados funcional.
- Regras de cálculo.
- Fluxo de novo pedido.
- Edição de pedido.
- Duplicação de pedido.
- Status.
- Filtros.
- Paginação.
- Dashboard.
- Mobile.
- Visual.

## Validação recomendada
Antes de subir como checkpoint seguro:
1. Abrir Dashboard.
2. Conferir filtro por mês/ano.
3. Conferir gráficos da Dashboard desktop.
4. Conferir Dashboard mobile.
5. Abrir Pedidos.
6. Conferir busca e filtro de status.
7. Clicar em `+ Novo Pedido`.
8. Abrir/editar/duplicar um pedido existente.
9. Alterar status rápido.
10. Abrir Configurações.

## Próxima fase
Após este checkpoint, a próxima fase será a v15:

- v15.00 — Estrutura de usuários.
- v15.01 — Tela de gerenciamento de usuários.
- v15.02 — Perfis Admin / Operador.
- v15.03 — Proteger Ajustes de Admin.
- v15.04 — Criar usuário para colega testar.
