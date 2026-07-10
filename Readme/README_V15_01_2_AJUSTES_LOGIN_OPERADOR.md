# Gestão 3D — v15.01.2 — ajustes de login e Operador

Patch corretivo da v15.01.1.

## O que foi corrigido

- Após login bem-sucedido, o sistema força abertura da página inicial (`Dashboard.py`).
- Após clicar em **Sair**, o sistema volta para a tela inicial/login, evitando ficar preso na página anterior.
- A seção **Ajustes de Admin** da tela Configurações agora só aparece para usuários Admin.
- O cadastro de usuários não exige mais e-mail válido como login. O Admin pode escolher login livre, como `vanessa`, `operador01` ou um e-mail.
- A listagem de usuários foi ajustada para não exibir HTML literal dentro do card.

## O que não mudou

- Não houve alteração destrutiva no banco.
- Os usuários continuam compartilhando a mesma empresa/base de dados.
- Dashboard, Pedidos e Cadastros continuam acessíveis para Operador.
- A tela Usuários continua restrita a Admin.

## Validação sugerida

1. Confirmar sidebar com versão `0.15.01.2`.
2. Entrar como Admin.
3. Abrir Usuários e confirmar que os cards aparecem sem texto HTML estranho.
4. Criar um usuário com login livre, por exemplo `vanessa` ou `operador01`.
5. Clicar em Sair.
6. Entrar com o usuário Operador e confirmar que abre na página inicial.
7. Abrir Configurações como Operador e confirmar que **Ajustes de Admin** não aparece.
8. Voltar como Admin e confirmar que **Ajustes de Admin** aparece normalmente.
