# Gestão 3D — v15.18 — Gerador de base local por empresa

- App: `0.15.18`
- `SCHEMA_VERSION`: `v15_18_gerador_base_local_empresa`

## Objetivo

Avançar no caminho definido para o futuro SaaS:

```text
Uma empresa = um banco separado
```

A v15.18 cria uma ferramenta técnica segura para gerar uma base SQLite local vazia para uma nova empresa, sem misturar dados com a base atual.

## O que entrou

Novo script:

```text
scripts/criar_base_empresa_local.py
```

Esse script cria um arquivo `.db` separado para uma empresa nova.

Exemplo:

```bat
python scripts\criar_base_empresa_local.py --codigo empresa-teste --nome "Empresa Teste" --admin-login admin --admin-senha 1234
```

No Windows, rodando dentro da pasta do projeto:

```bat
cd /d "C:\Users\USUARIO\Documents\4. Python\1_Gestao_3D"
python scripts\criar_base_empresa_local.py --codigo empresa-teste --nome "Empresa Teste" --admin-login admin --admin-senha 1234
```

## O que o script cria

- Arquivo SQLite separado em `database/<codigo>.db`.
- Estrutura técnica do banco.
- Configurações padrão.
- Categorias de apoio.
- Dados da Empresa iniciais.
- Um Admin da Empresa inicial.

## O que o script não cria

O script não cria dados operacionais automáticos:

```text
Impressoras
Filamentos
Peças
Clientes
Acessórios
Pedidos
```

Esses itens devem ser criados pela própria empresa, na trilha inicial.

## Segurança

O script não sobrescreve arquivo `.db` existente.

Se o arquivo já existir, ele cancela a operação para evitar perda de dados.

## Como abrir a base gerada localmente

Depois de gerar a base, configure `.streamlit/secrets.toml` com o caminho do novo banco:

```toml
[database]
mode = "local"
local_path = "database/empresa-teste.db"
```

Depois rode:

```bat
python -m streamlit run Dashboard.py
```

## O que não mudou

- Não foi criado banco central.
- Não foi criado Admin Geral Gestão 3D.
- Não foi criado SaaS ainda.
- Não foi adicionado `empresa_id` nas tabelas.
- Não houve alteração em Pedidos, Dashboard, Peças, Filamentos ou Clientes.

## Validação recomendada

1. Entrar normalmente na base atual.
2. Confirmar sidebar com `0.15.18`.
3. Confirmar que a base atual continua funcionando.
4. Rodar o script para criar uma base local teste.
5. Confirmar que o arquivo `database/empresa-teste.db` foi criado.
6. Apontar `local_path` para essa nova base.
7. Rodar o sistema.
8. Entrar com o Admin inicial criado no script.
9. Confirmar que a trilha inicial aparece pendente.
10. Confirmar que não há impressoras, filamentos, peças, clientes, acessórios ou pedidos criados automaticamente.

## Observação

Essa versão é um passo prático para o modelo de bancos separados. Ela ainda é local/SQLite, mas a mesma lógica será usada depois no Turso: cada empresa terá sua própria URL/banco.
