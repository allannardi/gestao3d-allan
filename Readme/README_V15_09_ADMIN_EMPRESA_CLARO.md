# Gestão 3D — v15.09 — Admin da Empresa claro

## Versão

- App: `0.15.09`
- SCHEMA_VERSION: `v15_09_admin_empresa_claro`

## Objetivo

Separar melhor na interface o conceito atual de **Admin da Empresa** do futuro **Admin Geral Gestão 3D**.

## O que entrou

- O perfil exibido na interface agora aparece como **Admin da Empresa**.
- O valor técnico interno continua sendo `Admin` para manter compatibilidade com os usuários já criados.
- A sidebar agora mostra **Admin da Empresa** no card do usuário logado.
- A tela **Usuários** agora mostra **Admin da Empresa** nos chips, seleção de perfil e métricas.
- A tela **Usuários** ganhou aviso explicando que o **Admin Geral Gestão 3D** será uma camada futura do SaaS.
- As mensagens de proteção foram ajustadas para usar **Admin da Empresa**.
- A aba **SaaS futuro** explica que o app atual salva internamente o Admin da Empresa como `Admin` por compatibilidade.

## O que não mudou

- Não foi criado o perfil real de Admin Geral.
- Não foi criado banco central.
- Não foi criado banco separado automaticamente.
- Não houve alteração destrutiva no banco.
- Usuários existentes com perfil `Admin` continuam funcionando normalmente.
- Operador continua vendo apenas **Configurações** dentro de Sistema.

## Validação sugerida

1. Entrar como Admin.
2. Confirmar sidebar com versão `0.15.09`.
3. Confirmar que o card do usuário na sidebar mostra **Admin da Empresa**.
4. Abrir **Usuários**.
5. Confirmar que os cards mostram **Admin da Empresa**, não apenas Admin.
6. Criar/editar um usuário e confirmar que o perfil aparece como **Admin da Empresa** ou **Operador**.
7. Entrar como Operador.
8. Confirmar que continua abrindo normalmente e com permissões iguais às da v15.08.
