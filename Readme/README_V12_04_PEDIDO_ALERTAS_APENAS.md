# V12.04 — Pedido com alertas apenas

## Objetivo
Ajustar a V12.03 conforme validação do usuário.

## Alteração realizada
- Removida a área `Conferência antes de salvar` do fluxo de novo pedido.
- Mantido apenas o espaço para exibição de alertas, quando existirem.
- Quando não houver alertas, nenhuma caixa extra é exibida no resumo lateral.

## Mantido
- Fluxo `Novo Pedido Guiado`.
- Helps nos campos.
- Regras de validação preventiva.
- Cálculos, banco e lógica existente.

## Segurança
- Não altera banco de dados.
- Não altera estrutura de tabelas.
- Não altera pedidos já cadastrados.
