# Gestão 3D — v15.01 — Tela de usuários

Esta versão continua a fase v15, iniciada para liberar o sistema para um colega testar com login próprio.

## O que entrou

- Nova tela `Usuários`.
- Link `Usuários` no menu Sistema da sidebar para usuários Admin.
- Atalho para `Usuários` na página `Mais`, também apenas para Admin.
- Listagem de usuários cadastrados.
- Criação de novo usuário com:
  - nome;
  - e-mail/login;
  - senha temporária;
  - perfil;
  - status.
- Edição de usuário com:
  - nome;
  - e-mail/login;
  - perfil;
  - status.
- Redefinição de senha temporária.
- Botões de inativar/reativar usuário.
- Proteção para evitar inativar o próprio usuário logado.
- Proteção para evitar remover ou inativar o último Admin ativo.

## O que não mudou

- Ainda não foi implementado SaaS multiempresa.
- Todos os usuários continuam acessando a mesma empresa/base de dados.
- Ainda não foram bloqueadas as demais telas por perfil Operador.
- Dashboard, Pedidos, Peças, Clientes, Filamentos, Acessórios e Configurações não tiveram alteração funcional.

## Validação recomendada

1. Confirmar sidebar com versão `0.15.01`.
2. Entrar com o login atual do Allan.
3. Verificar se aparece o menu `Usuários` dentro de Sistema.
4. Abrir a tela `Usuários`.
5. Criar um usuário teste com Perfil `Operador` e Status `Ativo`.
6. Sair pelo botão pequeno da sidebar.
7. Entrar com o usuário teste.
8. Confirmar que o usuário teste acessa o sistema.
9. Sair e voltar com o usuário Admin.
10. Inativar ou editar o usuário teste.

## Observação importante

A tela `Usuários` é protegida para Admin.
Nesta versão, o Operador ainda acessa as demais áreas operacionais.
As restrições finas de perfil ficam para a próxima etapa da v15.
