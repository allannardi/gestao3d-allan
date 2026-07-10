# Gestão 3D — v15.01.3 — Correção dos cards de usuários

Patch de correção visual da tela **Usuários**.

## O que foi corrigido

- Corrigido HTML que aparecia dentro dos cards da tela Usuários.
- Mantidas as correções da v15.01.2:
  - login após autenticação vai para a página inicial;
  - logout volta ao login/início;
  - Operador não vê Ajustes de Admin em Configurações;
  - cadastro de usuário permite login livre, sem exigir e-mail.

## Versão

- Sidebar: `0.15.01.3`
- SCHEMA_VERSION: `v15_01_3_corrige_cards_usuarios`

## Validação recomendada

1. Entrar como Admin.
2. Abrir Usuários.
3. Confirmar que os cards mostram apenas dados limpos, sem HTML aparente.
4. Sair.
5. Entrar como Operador.
6. Confirmar que abre no Início.
7. Confirmar que Ajustes de Admin não aparece em Configurações para Operador.
