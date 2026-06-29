# V12.05 — Peças com alertas operator friendly

## Ajuste em Pedidos
- Alterado o texto `+ Novo Pedido Guiado` para `+ Novo Pedido`.
- Alterado o título interno `Novo Pedido Guiado` para `Novo Pedido`.
- Mantidos os alertas preventivos da V12.04.

## Próxima fase iniciada: Peças
Melhorias no cadastro de Peças para evitar erros de operador.

## Alterações em Peças
- Adicionados alertas preventivos no resumo da nova peça.
- O sistema alerta quando:
  - nome da peça está vazio;
  - categoria está vazia;
  - quantidade do lote é inválida;
  - filamento de referência não foi informado;
  - peso total do lote está zerado;
  - tempo de impressão do lote está zerado;
  - custo unitário está zerado;
  - preço sugerido está zerado;
  - lucro/hora está abaixo da meta.
- Adicionados helps em:
  - Nome da Peça;
  - Categoria;
  - Link do STL / Arquivo;
  - Link do modelo na internet;
  - Pasta Google Drive;
  - Observações.
- Ao salvar, a peça agora bloqueia peso zerado e tempo de impressão zerado, evitando cadastro com cálculo incorreto.

## Segurança
- Não altera banco de dados.
- Não cria tabela.
- Não altera cálculo existente.
- Não altera peças já cadastradas.
- Atua apenas no fluxo de cadastro de nova peça e textos de orientação.
