# V13.02 — Impressoras autocriar

## Correção
Corrige o erro:
`SQLite error: no such table: impressoras`

## Causa provável
A página Configurações já estava com o código novo, mas a migração do banco não havia criado a tabela `impressoras` antes da página tentar carregar os dados.

## O que foi feito
- A própria tela Configurações agora garante a criação da tabela `impressoras` antes de consultar.
- Se não houver nenhuma impressora, cria automaticamente:
  - `IMP-001 - Bambu Lab A1 Mini`
  - marcada como impressora padrão
  - usando energia/depreciação existentes como referência.
- A página Configurações chama `inicializar_banco(force=True)` para forçar a migração nesta tela.
- Sidebar reforçada para versão `0.13`.

## Segurança
- Não apaga dados.
- Não altera pedidos existentes.
- Não altera peças existentes.
- Apenas cria a tabela `impressoras` se ela ainda não existir.
