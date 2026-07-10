# Gestão 3D — v15.13 — Identidade da Base da Empresa

- APP_VERSION: `0.15.13`
- SCHEMA_VERSION: `v15_13_identidade_base_empresa`

## Objetivo

Começar a preparação técnica para o modelo escolhido de futuro multiempresa: **um banco separado por empresa/cliente**.

Esta versão não cria uma ponte improvisada e não mistura empresas. Ela apenas identifica melhor a base atual como a base de uma única empresa.

## O que entrou

- Nova aba `Base da Empresa` dentro da página `Administrador`.
- Novo service `services/base_empresa.py`.
- Novos campos seguros na tabela `configuracoes`:
  - `base_empresa_id`
  - `codigo_empresa`
  - `ambiente_base`
- Geração automática de um identificador único da base.
- Código interno da empresa/base editável pelo Admin da Empresa.
- Ambiente da base:
  - `Operação`
  - `Teste`
  - `Homologação`
- Diagnóstico seguro da conexão atual:
  - tipo de conexão;
  - origem;
  - banco conectado;
  - schema atual;
  - status do token cloud sem exibir o token.

## Decisão mantida

O caminho futuro continua sendo:

```text
Empresa A -> banco A
Empresa B -> banco B
Empresa C -> banco C
```

A base atual deve representar uma única empresa.

## O que não mudou

- Não foi criado banco central.
- Não foi criado banco separado automaticamente.
- Não foi criado painel de Admin Geral.
- Não houve alteração nas regras de Pedidos, Dashboard, Peças, Filamentos ou Clientes.
- Operador continua sem acesso à página Administrador.

## O que validar

1. Entrar como Admin da Empresa.
2. Confirmar sidebar com `0.15.13`.
3. Abrir `Administrador`.
4. Confirmar que existe a aba `Base da Empresa`.
5. Conferir se aparece um identificador único da base.
6. Conferir o código interno da empresa/base.
7. Alterar o código interno e salvar.
8. Confirmar que o diagnóstico de conexão aparece sem exibir token.
9. Confirmar que Dados da Empresa, Implantação, Ajustes de Admin e Prontidão continuam funcionando.
10. Entrar como Operador e confirmar que ele continua vendo apenas `Configurações` em Sistema.
