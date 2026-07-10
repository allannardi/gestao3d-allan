# Gestão 3D — v15.15 — Integridade da Base

## Versão

- App: `0.15.15`
- `SCHEMA_VERSION`: `v15_15_integridade_base`

## Objetivo

Adicionar uma conferência técnica da estrutura da base atual antes de avançar para o próximo bloco do caminho escolhido: uma empresa por banco separado.

Esta versão não cria banco central, não cria banco separado automaticamente e não altera dados operacionais.

## O que entrou

- Nova aba em `Administrador`:

```text
Integridade
```

- Novo service:

```text
services/integridade_base.py
```

- A aba valida se a base atual possui as tabelas e colunas esperadas para a versão atual do Gestão 3D.

## O que a aba Integridade mostra

- Total de tabelas esperadas.
- Quantas tabelas estão OK.
- Quantas colunas obrigatórias estão presentes.
- Quantas colunas estão faltando.
- `SCHEMA_VERSION` atual.
- Detalhamento por grupos:
  - Base técnica;
  - Apoio;
  - Operacional;
  - Relacionamentos.

## Importante

A aba `Integridade` é somente diagnóstica.

Ela não cria, altera nem apaga dados. As migrations continuam centralizadas em `database.py` e rodam durante a inicialização normal do sistema.

## O que não mudou

- Não criou banco central.
- Não criou Admin Geral Gestão 3D.
- Não criou nova empresa automaticamente.
- Não mexeu em Pedidos, Dashboard, Peças, Filamentos ou Clientes.
- Não alterou permissões do Operador.

## O que validar

1. Entrar como Admin da Empresa.
2. Confirmar sidebar com `0.15.15`.
3. Abrir `Administrador`.
4. Confirmar a nova aba `Integridade`.
5. Verificar se os KPIs de tabelas e colunas aparecem.
6. Confirmar se o status aparece como íntegro.
7. Confirmar que `Base da Empresa`, `Base limpa`, `Implantação`, `Ajustes de Admin` e `Prontidão` continuam funcionando.
8. Entrar como Operador e confirmar que ele continua vendo apenas `Configurações` em Sistema.

## Validação técnica

- Sintaxe Python validada com `py_compile`.
- Arquivos `__pycache__` e `.pyc` removidos antes do empacotamento.
