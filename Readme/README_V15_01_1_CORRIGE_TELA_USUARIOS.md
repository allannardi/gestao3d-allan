# Gestão 3D — v15.01.1 — Correção da tela Usuários

## Objetivo

Corrigir erro visual/funcional da tela **Usuários** identificado na v15.01.

## Correção aplicada

- Corrigidas chamadas do componente `small_section()` em `pages/Usuarios.py`.
- O componente aceita apenas um argumento nesta base do projeto.
- As descrições extras foram movidas para `st.caption()`.

## Mantido da v15.01

- Tela **Usuários** no menu Sistema.
- Listagem de usuários.
- Criação de usuário.
- Edição de usuário.
- Redefinição de senha temporária.
- Inativação/Reativação.
- Proteção para não inativar o próprio usuário.
- Proteção para não remover/inativar o último Admin ativo.

## O que validar

1. Confirmar sidebar com versão `0.15.01.1`.
2. Abrir **Usuários** sem erro.
3. Criar um usuário Operador teste.
4. Clicar em **Sair**.
5. Entrar com o usuário Operador.
6. Sair e voltar com o Admin.
7. Editar, redefinir senha ou inativar o usuário teste.

## Observação

Não houve alteração destrutiva no banco de dados.
