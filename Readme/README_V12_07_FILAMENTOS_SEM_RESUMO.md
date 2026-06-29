# V12.07 — Filamentos sem resumo e correção de moeda

## Correção
- Corrigido o problema do `R$` nos alertas em Markdown de Pedidos e Peças.

## Ajuste em Filamentos
- Removida a ideia de resumo do rolo na tela de Filamentos.
- Mantidas apenas orientações discretas nos campos.
- Mantida validação no clique de salvar:
  - nome obrigatório;
  - cor obrigatória;
  - peso original obrigatório;
  - valor de compra obrigatório.
- Corrigido o erro `Missing Submit Button`.
- Corrigido o erro `NameError: montar_alertas_filamento_operador`.

## Segurança
- Não altera banco de dados.
- Não cria tabela.
- Não altera cálculo existente.
- Não altera filamentos já cadastrados.
