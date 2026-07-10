# Gestão 3D — v15.10.1 — remove liberação de teste

## Versão

- APP_VERSION: `0.15.10.1`
- SCHEMA_VERSION: `v15_10_1_remove_liberacao_teste`

## Objetivo

Remover a área de mensagem para liberação de acesso, mantendo a tela **Usuários** focada apenas em gerenciamento real de usuários.

## O que mudou

- Removida a área **Liberar acesso para colega testar** da tela **Usuários**.
- Removida a mensagem explicativa sobre o futuro **Admin Geral Gestão 3D** da tela **Usuários**.
- O texto inicial da tela **Usuários** agora fica focado apenas na gestão de usuários da empresa.

## O que foi mantido

- Criar usuário.
- Editar usuário.
- Ativar/Inativar usuário.
- Redefinir senha temporária.
- Login livre continua funcionando.
- Operador continua sem acesso à tela **Usuários**.
- Operador continua vendo apenas **Configurações** dentro de **Sistema**.

## O que validar

1. Entrar como Admin da Empresa.
2. Confirmar sidebar com `0.15.10.1`.
3. Abrir **Usuários**.
4. Confirmar que não aparece mais **Liberar acesso para colega testar**.
5. Confirmar que não aparece mais a mensagem sobre **Admin Geral Gestão 3D**.
6. Criar/editar/inativar usuário normalmente.
7. Redefinir senha de um usuário teste.
8. Entrar como Operador e confirmar que ele continua sem acesso a **Usuários**.

## Validação técnica

- Sintaxe Python validada com `py_compile`.
- Nenhuma alteração destrutiva de banco.
