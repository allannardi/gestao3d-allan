# Gestão 3D — v15.07

## Versão

- App: `0.15.07`
- SCHEMA_VERSION: `v15_07_admin_central_saas`

## Objetivo da versão

Organizar a página **Administrador** como uma central administrativa mais clara, preparando o Gestão 3D para uso por outras empresas no futuro e mantendo a configuração operacional separada das ações de Admin.

## O que entrou

### 1. Página Administrador organizada por abas

A página **Administrador** agora possui abas:

- **Resumo**
- **Dados da Empresa**
- **Implantação**
- **Ajustes de Admin**
- **SaaS futuro**

### 2. Aba Resumo

Inclui uma visão geral com:

- nome da empresa/projeto;
- status da implantação;
- pedidos antigos sem impressora;
- pedidos elegíveis para ajuste de datas;
- progresso da trilha inicial.

### 3. Aba Dados da Empresa

Mantém os campos administrativos:

- Nome da empresa/projeto;
- Login Admin da Empresa;
- Responsável;
- Telefone/WhatsApp;
- Cidade/UF;
- Observações internas;
- Status da implantação.

Os campos obrigatórios continuam sendo:

- Nome da empresa/projeto;
- Login Admin da Empresa.

### 4. Aba Implantação

Mantém a trilha inicial:

- Dados da Empresa;
- Primeira impressora;
- Primeiro filamento;
- Primeira peça.

Também foi corrigido o atalho da etapa **Dados da Empresa**, que agora aponta para a página **Administrador**, não mais para Configurações.

### 5. Aba Ajustes de Admin

Concentra ações administrativas protegidas:

- aplicar impressora padrão em pedidos antigos sem impressora;
- preencher datas antigas com base na entrega prevista.

### 6. Aba SaaS futuro

Registra a decisão estratégica:

- futuro SaaS seguirá o modelo **um banco separado por empresa/cliente**;
- não será usado `empresa_id` nas tabelas atuais do app Streamlit;
- o app atual continua como MVP operacional e base de validação.

## O que não mudou

- Não houve alteração destrutiva no banco.
- Não foi criado SaaS multiempresa ainda.
- Não foi criado banco separado automaticamente.
- Não houve alteração nas regras de Pedidos, Peças, Filamentos, Clientes ou Dashboard.
- Operador continua vendo apenas Configurações dentro de Sistema.

## Como validar

1. Entrar como Admin.
2. Confirmar sidebar com versão `0.15.07`.
3. Abrir **Administrador**.
4. Confirmar que a página possui abas:
   - Resumo;
   - Dados da Empresa;
   - Implantação;
   - Ajustes de Admin;
   - SaaS futuro.
5. Conferir se **Dados da Empresa** continua salvando normalmente.
6. Conferir se **Implantação** mostra a trilha inicial.
7. Conferir se **SaaS futuro** mostra o modelo de banco por empresa.
8. Entrar como Operador.
9. Confirmar que o Operador continua vendo apenas **Configurações** em Sistema.

## Validação técnica

- `py_compile` executado em todos os arquivos `.py`.
- Resultado: OK.
