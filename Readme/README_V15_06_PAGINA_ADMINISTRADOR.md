# Gestão 3D — v15.06 — Página Administrador

## Objetivo

Separar melhor as áreas operacionais das áreas administrativas.

A partir desta versão, a tela `Configurações` fica mais limpa e os itens administrativos foram movidos para uma nova página chamada `Administrador`.

## Versão

- Sidebar: `0.15.06`
- `SCHEMA_VERSION`: `v15_06_pagina_administrador`

## O que entrou

### Nova página

Criada a nova página:

```text
pages/Administrador.py
```

Ela concentra:

```text
Dados da Empresa
Trilha inicial
Ajustes de Admin
```

### Menu Sistema

Para usuário Admin, a sidebar agora exibe:

```text
Sistema
- Configurações
- Administrador
- Usuários
```

Para usuário Operador, a sidebar exibe apenas:

```text
Sistema
- Configurações
```

### Configurações mais limpa

A página `Configurações` mantém os itens operacionais:

```text
Configurações gerais da empresa
Impressoras
Acesso e senha
```

Foram removidos dela:

```text
Dados da Empresa
Trilha inicial
Ajustes de Admin
```

### Mais / Mobile

Na tela `Mais`, o Admin também passa a ver o atalho `Administrador`.

O Operador não vê esse atalho.

## Permissões

A página `Administrador` exige permissão de Admin.

Se um Operador tentar acessar manualmente:

```text
/Administrador
```

O sistema bloqueia o acesso e redireciona para a página inicial.

## O que não mudou

- Não houve alteração destrutiva no banco.
- Não houve mudança nas regras de Pedidos.
- Não houve mudança nos cadastros de Clientes, Peças, Acessórios ou Filamentos.
- Não houve mudança na lógica de usuários já validada.
- O modelo futuro SaaS continua definido como banco separado por empresa/cliente.

## O que validar

### Como Admin

1. Entrar como Admin.
2. Confirmar sidebar com `0.15.06`.
3. Confirmar menu:

```text
Sistema
- Configurações
- Administrador
- Usuários
```

4. Abrir `Configurações`.
5. Confirmar que não aparecem mais:

```text
Dados da Empresa
Trilha inicial
Ajustes de Admin
```

6. Confirmar que `Configurações` ainda mostra:

```text
Configurações gerais da empresa
Impressoras
Acesso e senha
```

7. Abrir `Administrador`.
8. Confirmar que aparecem:

```text
Dados da Empresa
Trilha inicial
Ajustes de Admin
```

9. Editar/salvar Dados da Empresa.
10. Confirmar que o nome da empresa continua aparecendo abaixo do logo na sidebar.

### Como Operador

1. Entrar como Operador.
2. Confirmar que o menu Sistema mostra apenas:

```text
Configurações
```

3. Confirmar que `Administrador` e `Usuários` não aparecem.
4. Tentar acessar manualmente `/Administrador`.
5. Confirmar que o acesso é bloqueado.
