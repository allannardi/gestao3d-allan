# Gestão 3D — v15.12 — Prontidão da Empresa

- APP_VERSION: `0.15.12`
- SCHEMA_VERSION: `v15_12_prontidao_empresa`

## Objetivo

Fechar pendências visíveis da fase de usuários/perfis/onboarding antes de avançar para o modelo de bancos separados por empresa.

## O que entrou

- A aba `SaaS futuro` foi removida da página `Administrador`.
- A página `Administrador` agora mantém apenas conteúdo útil para o Admin da Empresa.
- Nova aba `Prontidão` dentro de `Administrador`.
- Checklist de prontidão da empresa com itens obrigatórios e recomendações.
- Remoção de textos internos sobre Admin Geral Gestão 3D da interface administrativa da empresa.

## Checklist da aba Prontidão

Itens obrigatórios:

- Dados da Empresa preenchidos.
- Trilha inicial concluída.
- Pelo menos um Admin da Empresa ativo.
- Pelo menos um usuário ativo.

Itens recomendados:

- Pelo menos um Operador ativo.
- Ajustes antigos revisados.

## Decisão SaaS mantida

A decisão estratégica continua sendo: no futuro multiempresa, cada empresa/cliente deverá usar um banco separado.

Esta versão não cria banco central, não cria bancos automaticamente e não altera a estrutura operacional atual.

## O que validar

1. Entrar como Admin da Empresa.
2. Confirmar sidebar com `0.15.12`.
3. Abrir `Administrador`.
4. Confirmar que não existe mais a aba `SaaS futuro`.
5. Confirmar que existe a aba `Prontidão`.
6. Conferir se o checklist mostra os itens obrigatórios e recomendados.
7. Confirmar que Dados da Empresa, Implantação e Ajustes de Admin continuam funcionando.
8. Entrar como Operador e confirmar que ele continua vendo apenas `Configurações` em Sistema.
