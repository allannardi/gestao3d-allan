# Gestão 3D — v15.00 Usuários base

Checkpoint inicial da fase v15.

## Objetivo da versão

Iniciar a base técnica para usuários, perfis e liberação futura de acesso para um colega testar o sistema.

Esta versão ainda não cria a tela de gerenciamento de usuários. O foco foi preparar o login multiusuário com segurança e sem quebrar o acesso atual do Allan.

## O que entrou

- Nova tabela `usuarios` com migration segura.
- Criação automática de um usuário inicial `Admin` quando a tabela estiver vazia.
- Login passa a consultar primeiro a tabela `usuarios`.
- Compatibilidade preservada com o login antigo via `auth_config` ou `st.secrets`.
- Sessão agora guarda dados do usuário logado:
  - `usuario_id`
  - `usuario_nome`
  - `usuario_email`
  - `usuario_perfil`
  - `usuario_status`
  - `usuario_origem`
- Helpers criados em `components/auth.py`:
  - `get_usuario_atual()`
  - `is_admin()`
  - `is_operador()`
  - `require_admin()`
- Botão pequeno de **Sair** adicionado no rodapé da sidebar.
- Sidebar atualizada para `0.15.00`.
- `SCHEMA_VERSION` atualizado para `v15_00_usuarios_base`.

## O que não mudou

- Não foi criada tela de gerenciamento de usuários ainda.
- Nenhuma página foi bloqueada por perfil ainda.
- Nenhum dado existente de clientes, peças, pedidos, filamentos, acessórios ou impressoras é apagado/recriado.
- O modelo ainda é multiusuário simples dentro da mesma empresa/base.
- Ainda não é SaaS multiempresa.

## Cuidados técnicos

- Senha não é salva em texto puro.
- Senha de usuário novo usa hash PBKDF2.
- Caso o sistema já esteja usando senha personalizada em `auth_config`, o Admin inicial preserva essa senha por compatibilidade.
- O fallback do login antigo foi mantido para evitar travar o acesso do Allan.

## O que validar

1. Sidebar mostra `0.15.00`.
2. Login atual do Allan continua funcionando.
3. Dashboard abre.
4. Pedidos abre.
5. Configurações abre.
6. Botão **Sair** aparece pequeno no rodapé da sidebar.
7. Clicar em **Sair** volta para a tela de login.
8. Entrar novamente funciona.
9. Nenhum dado existente sumiu.

## Próximo passo recomendado

Depois da validação local da v15.00, seguir para:

`v15.01 — Tela de gerenciamento de usuários`

Funções previstas:

- listar usuários;
- criar usuário;
- editar nome/perfil/status;
- redefinir senha temporária;
- desativar usuário;
- liberar acesso somente para Admin.
