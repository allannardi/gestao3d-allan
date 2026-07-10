# Gestão 3D — v15.17 — Base configurável por empresa

- App: `0.15.17`
- `SCHEMA_VERSION`: `v15_17_base_configuravel_por_empresa`

## Objetivo

Dar um passo real no caminho escolhido:

```text
Uma empresa = um banco separado
```

A partir desta versão, o app pode apontar para um banco local diferente por empresa usando configuração, sem alterar código.

## O que entrou

### 1. SQLite local configurável

O caminho do banco local agora pode ser definido por:

```toml
[database]
mode = "local"
local_path = "database/empresa_teste.db"
```

Se `local_path` não for informado, o padrão continua sendo:

```text
database/atelie.db
```

### 2. Variáveis de ambiente aceitas

Também é possível configurar por variável de ambiente:

```text
GESTAO3D_LOCAL_DB_PATH
DATABASE_PATH
SQLITE_DB_PATH
```

### 3. Turso/libSQL continua separado por URL

Para nuvem, o isolamento por empresa continua sendo feito com uma URL/token Turso diferente para cada empresa:

```toml
[database]
mode = "turso"
url = "libsql://BANCO-DA-EMPRESA.turso.io"
auth_token = "TOKEN-DA-EMPRESA"
```

### 4. Diagnóstico atualizado

A aba **Administrador > Base da Empresa** agora deixa claro que a base pode apontar para outro arquivo SQLite ou outro banco Turso.

## O que não mudou

- Não criou banco central.
- Não criou Admin Geral Gestão 3D.
- Não criou empresa automaticamente.
- Não apagou dados existentes.
- Não alterou Pedidos, Dashboard, Peças, Filamentos ou Clientes.
- Operador continua vendo apenas **Configurações** em Sistema.

## Como validar

1. Entrar como Admin da Empresa.
2. Confirmar sidebar com `0.15.17`.
3. Abrir **Administrador**.
4. Ir em **Base da Empresa**.
5. Confirmar que o banco atual continua apontando para `database/atelie.db` se nenhum `local_path` foi configurado.
6. Confirmar que as abas **Base limpa**, **Integridade**, **Implantação**, **Ajustes de Admin** e **Prontidão** continuam funcionando.
7. Entrar como Operador.
8. Confirmar que ele continua vendo apenas **Configurações** dentro de Sistema.

## Observação

Esta versão não mistura empresas no mesmo banco e não adiciona `empresa_id` nas tabelas. Ela prepara o app para apontar cada instalação/empresa para uma base própria.
