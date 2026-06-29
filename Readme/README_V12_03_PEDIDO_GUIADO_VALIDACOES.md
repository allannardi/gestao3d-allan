# V12.03 — Pedido Guiado com Conferência

## Objetivo
Início da próxima fase operator friendly: deixar o fluxo de novo pedido mais guiado e seguro para operadores com qualquer nível técnico.

## Alterações
- Botão alterado para `+ Novo Pedido Guiado`.
- Subtítulo do cadastro de pedido ajustado para fluxo guiado.
- Adicionada orientação curta antes do formulário.
- Adicionados helps em campos importantes:
  - Cliente
  - Peça
  - Status
  - Canal
  - Observações
- Adicionada área `Conferência antes de salvar` no resumo do pedido.
- Adicionados alertas preventivos antes de salvar:
  - novo cliente sem nome;
  - filamento não selecionado;
  - quantidade ou valor zerado;
  - peça sem custo calculado;
  - peça sem tempo calculado;
  - pedido com prejuízo;
  - lucro/hora abaixo da meta;
  - preço mínimo estimado para atingir a meta de lucro/hora.

## Segurança
- Não altera banco de dados.
- Não cria tabela.
- Não altera lógica de cálculo existente.
- Não altera pedidos já cadastrados.
- Apenas adiciona orientação, conferência e alertas no fluxo de criação de pedido.
