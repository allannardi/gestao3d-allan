# Gestão 3D — v15.11 — Troca de senha multiusuário

## Versão

- APP_VERSION: `0.15.11`
- SCHEMA_VERSION: `v15_11_troca_senha_multiusuario`

## Objetivo

Revisar a troca de senha já existente em **Configurações** para garantir compatibilidade total com a estrutura multiusuário da v15.

## O que entrou

- Mantida a área existente de **Acesso e senha** em Configurações.
- A troca de senha agora altera somente o usuário logado.
- Admin da Empresa pode trocar a própria senha.
- Operador pode trocar a própria senha.
- A senha continua salva com hash seguro na tabela `usuarios`.
- A função de troca de senha não recria mais a sessão usando `verificar_login()`.
- Mantido fallback legado para compatibilidade com versões antigas.
- A tela agora mostra a conta atual, login e perfil antes da troca de senha.

## O que não mudou

- Não foi criada nova tela.
- Não foi duplicada a função de troca de senha.
- Admin da Empresa continua redefinindo senha de outros usuários pela tela **Usuários**.
- Operador continua sem acesso à tela **Usuários**.
- Não houve alteração destrutiva no banco.

## O que validar

1. Entrar como Admin da Empresa.
2. Confirmar sidebar com `0.15.11`.
3. Abrir **Configurações**.
4. Ir em **Acesso e senha**.
5. Trocar a própria senha.
6. Clicar em **Sair**.
7. Entrar novamente com a nova senha.
8. Repetir o teste com um usuário Operador.
9. Confirmar que o Operador continua vendo apenas **Configurações** em Sistema.

## Observação

A senha nunca é salva em texto puro. O sistema grava apenas o hash da senha.
