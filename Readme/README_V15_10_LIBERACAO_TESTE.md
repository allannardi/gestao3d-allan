# Gestão 3D — v15.10

## Versão

- APP_VERSION: `0.15.10`
- SCHEMA_VERSION: `v15_10_liberacao_teste`

## Objetivo

Melhorar a liberação de acesso para um colega testar o Gestão 3D, mantendo a separação entre Admin da Empresa e Operador.

## O que entrou

- Nova área na tela **Usuários**: **Liberar acesso para colega testar**.
- A área permite escolher um Operador ativo e montar uma mensagem com:
  - link do app;
  - login do usuário;
  - senha temporária informada pelo Admin;
  - orientação para trocar a senha no primeiro acesso.
- Correção técnica na redefinição de senha dos usuários.

## O que não mudou

- Não foi criado o perfil real de Admin Geral Gestão 3D.
- Não foi criado banco central.
- Não foi criado banco separado automaticamente.
- Não foram alteradas regras de Pedidos, Peças, Filamentos, Clientes ou Dashboard.

## Validação sugerida

1. Entrar como Admin da Empresa.
2. Abrir **Usuários**.
3. Confirmar sidebar com `0.15.10`.
4. Abrir a área **Liberar acesso para colega testar**.
5. Selecionar um Operador ativo.
6. Digitar a senha temporária criada para ele.
7. Conferir a mensagem sugerida.
8. Testar redefinir a senha de um usuário teste.
9. Sair e entrar com o usuário teste.
10. Confirmar que o Operador continua sem ver Administrador/Usuários.

## Observação

A senha digitada na área de liberação não é salva. Ela serve apenas para montar a mensagem de envio ao colega.
