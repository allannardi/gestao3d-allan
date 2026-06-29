# V13.05 — Correção de moeda em Impressoras

## Correção
Corrigido o problema visual no texto dentro da edição/cadastro de impressora:

- Energia/hora calculada
- Valor do kWh usado

O símbolo `R$` estava sendo interpretado pelo Markdown como fórmula matemática.
Agora o valor é exibido corretamente como `R$`.

## Segurança
- Não altera banco de dados.
- Não altera cálculos.
- Não altera impressoras cadastradas.
- Alteração apenas visual na página Configurações.
