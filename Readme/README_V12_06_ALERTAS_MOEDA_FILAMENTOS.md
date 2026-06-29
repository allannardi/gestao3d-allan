# V12.06 — Correção de moeda nos alertas e Filamentos operator friendly

## Correção visual
- Corrigido o problema do `R$` nos alertas em Markdown.
- Agora os alertas exibem corretamente valores como `R$ 4,00`, sem perder o símbolo `$`.

## Continuação da fase operator friendly: Filamentos
Melhorias no cadastro de Filamentos para evitar erros de operador.

## Alterações em Filamentos
- Subtítulo do cadastro ajustado para reforçar que cada registro representa um rolo físico.
- Adicionado resumo do rolo antes de salvar:
  - peso original;
  - valor de compra;
  - custo por grama estimado.
- Adicionados alertas preventivos para:
  - nome vazio;
  - material não selecionado;
  - cor vazia;
  - peso original inválido;
  - valor da compra zerado.
- Ao salvar, o sistema bloqueia:
  - cor vazia;
  - peso original zerado;
  - valor de compra zerado.

## Mantido
- Dashboard validada.
- Ajuda em modal.
- Alertas de Pedidos e Peças.
- Banco de dados e cálculos existentes.
