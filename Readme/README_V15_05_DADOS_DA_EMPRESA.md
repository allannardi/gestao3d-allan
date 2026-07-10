# Gestão 3D — v15.05 — Dados da Empresa

## Objetivo da versão

Esta versão evolui a área administrativa da empresa/projeto para preparar melhor o Gestão 3D para implantação por outras empresas e para a futura arquitetura SaaS.

A decisão de SaaS permanece como Caminho A:

```text
um banco separado por empresa/cliente
```

Nesta versão ainda não há multiempresa real. Os dados continuam na mesma base atual.

---

## Alterações principais

- Versão atualizada para `0.15.05`.
- `SCHEMA_VERSION` atualizado para `v15_05_dados_da_empresa`.
- A antiga área `Empresa / Projeto` foi substituída por `Dados da Empresa`.
- A área `Dados da Empresa` fica visível apenas para Admin.
- O nome da empresa/projeto continua aparecendo abaixo do logo na sidebar.
- A trilha inicial agora considera os dados obrigatórios da empresa.

---

## Campos adicionados em Dados da Empresa

Campos obrigatórios:

```text
*Nome da empresa/projeto
*Login Admin da Empresa
```

Campos opcionais:

```text
Responsável
Telefone/WhatsApp
Cidade/UF
Observações internas
Status da implantação
```

Status disponíveis:

```text
Em implantação
Em operação
Em revisão
Pausado
```

---

## Banco de dados

Foram adicionadas colunas seguras na tabela `configuracoes`:

```text
nome_empresa
login_admin_empresa
responsavel_empresa
telefone_whatsapp_empresa
cidade_uf_empresa
observacoes_internas_empresa
status_implantacao
```

As migrations são seguras:

```text
CREATE TABLE IF NOT EXISTS
ALTER TABLE ADD COLUMN com checagem
Sem DROP TABLE
Sem recriar banco
```

---

## Arquivos alterados

```text
database.py
components/sidebar.py
pages/Configuracoes.py
services/empresa.py
services/onboarding.py
components/onboarding.py
Readme/README_V15_05_DADOS_DA_EMPRESA.md
```

---

## O que validar

1. Entrar como Admin.
2. Confirmar sidebar com `0.15.05`.
3. Abrir `Configurações`.
4. Confirmar a área `Dados da Empresa`.
5. Confirmar os campos:
   - `*Nome da empresa/projeto`
   - `*Login Admin da Empresa`
   - `Responsável`
   - `Telefone/WhatsApp`
   - `Cidade/UF`
   - `Observações internas`
   - `Status da implantação`
6. Tentar salvar sem um dos campos obrigatórios e confirmar o aviso.
7. Preencher os campos obrigatórios e salvar.
8. Confirmar que o nome da empresa/projeto aparece abaixo do logo na sidebar.
9. Confirmar que a trilha inicial continua concluída quando dados da empresa, impressora, filamento e peça estiverem preenchidos.
10. Entrar como Operador.
11. Confirmar que o Operador não vê `Dados da Empresa` nem `Trilha inicial` em Configurações.

---

## Observação importante

O campo `Login Admin da Empresa` é livre. Pode ser um e-mail ou um login simples, como:

```text
allan
admin
atelievan
operador01
```

Ele prepara o conceito de implantação por empresa, mas ainda não altera o login real nem cria banco separado automaticamente.
