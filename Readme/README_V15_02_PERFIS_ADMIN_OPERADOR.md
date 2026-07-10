# Gestão 3D — v15.02 — Perfis Admin / Operador

## Objetivo

Consolidar a lógica de perfis da v15, separando permissões de Admin e Operador de forma centralizada e segura.

## O que entrou

- Versão da sidebar: `0.15.02`
- `SCHEMA_VERSION`: `v15_02_perfis_admin_operador`
- Permissões centralizadas em `components/auth.py`.
- Perfil Admin com acesso completo.
- Perfil Operador com acesso operacional.
- Tela `Usuários` protegida por permissão de Admin.
- Se um Operador tentar acessar `Usuários` por URL direta, ele é redirecionado para `Início` com aviso.
- Menu lateral e tela `Mais` continuam ocultando `Usuários` para Operador.
- `Ajustes de Admin` em Configurações continuam visíveis apenas para Admin.

## O que não mudou

- Não houve alteração destrutiva no banco.
- Não houve mudança nas regras de Pedidos, Dashboard, Clientes, Peças, Acessórios ou Filamentos.
- Usuários continuam acessando a mesma empresa/base de dados.
- Não foi implementado modelo multiempresa/SaaS nesta versão.

## Validação recomendada

1. Entrar como Admin.
2. Confirmar sidebar com `0.15.02`.
3. Confirmar que `Usuários` aparece no menu Sistema.
4. Abrir `Usuários` normalmente.
5. Sair.
6. Entrar como Operador.
7. Confirmar que abre no `Início`.
8. Confirmar que `Usuários` não aparece na sidebar.
9. Confirmar que `Usuários` não aparece em `Mais`.
10. Tentar acessar `/Usuarios` manualmente e confirmar que volta para `Início` com aviso.
11. Ir em `Configurações` e confirmar que `Ajustes de Admin` não aparece para Operador.

## Observação

Esta versão fecha a base de perfis simples da v15 antes de criar um usuário real para teste externo ou avançar para proteções administrativas adicionais.
