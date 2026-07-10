# Gestão 3D — v15.08

## Versão

- App: `0.15.08`
- SCHEMA_VERSION: `v15_08_hierarquia_saas`

## Objetivo da versão

Registrar com clareza a hierarquia futura de acesso do SaaS Gestão 3D, separando o conceito de **Admin Geral Gestão 3D** do **Admin da Empresa**.

Essa versão não muda as permissões reais do app atual. Ela documenta e organiza a preparação para a futura arquitetura SaaS.

## Hierarquia futura definida

### 1. Admin Geral Gestão 3D

- Acesso exclusivo do Allan.
- Gerencia o ecossistema inteiro do Gestão 3D.
- Vê empresas/clientes cadastrados.
- Acompanha status, implantação e ambiente de cada empresa.
- Futuramente poderá criar, pausar, ativar ou administrar empresas.

### 2. Admin da Empresa

- Admin responsável por uma empresa/cliente.
- Vê e gerencia somente a própria empresa.
- Gerencia usuários da própria empresa.
- Edita Dados da Empresa.
- Acompanha implantação da própria empresa.

### 3. Operador

- Usuário operacional da empresa.
- Usa Dashboard, Pedidos, Peças, Filamentos, Clientes e demais áreas operacionais permitidas.
- Não gerencia empresa, usuários ou ajustes administrativos.

## Modelo SaaS mantido

A decisão estratégica continua sendo:

```text
Empresa A -> banco A
Empresa B -> banco B
Empresa C -> banco C
```

Ou seja: **um banco separado por empresa/cliente**.

## Banco central futuro

Além dos bancos individuais das empresas, o SaaS futuro deverá ter um **banco central do Gestão 3D**, usado pelo Admin Geral para controlar:

- empresas/clientes cadastrados;
- status de cada empresa no ecossistema;
- plano/assinatura futura;
- vínculo com o banco individual de cada empresa;
- responsável/Admin da Empresa;
- informações administrativas globais.

Esse banco central não deve guardar os dados operacionais de cada empresa, como pedidos, peças, filamentos e clientes. Esses dados seguem isolados no banco individual de cada cliente.

## O que entrou

- Atualização da aba **SaaS futuro** na página Administrador.
- Nova seção **Hierarquia futura de acesso**.
- Nova seção **Banco central do ecossistema**.
- Ajuste de textos para diferenciar:
  - Admin Geral Gestão 3D;
  - Admin da Empresa;
  - Operador.
- README da versão atualizado com a decisão.

## O que não mudou

- Não foi criado o perfil real de Admin Geral ainda.
- Não foi criado banco central ainda.
- Não foi criado banco separado automaticamente.
- Não houve alteração destrutiva no banco.
- Não houve alteração nas regras de Pedidos, Peças, Filamentos, Clientes ou Dashboard.
- Operador continua vendo apenas **Configurações** dentro de Sistema.

## Como validar

1. Entrar como Admin.
2. Confirmar sidebar com versão `0.15.08`.
3. Abrir **Administrador**.
4. Abrir a aba **SaaS futuro**.
5. Confirmar que aparece a hierarquia:
   - Admin Geral Gestão 3D;
   - Admin da Empresa;
   - Operador.
6. Confirmar que aparece a explicação do banco central do ecossistema.
7. Entrar como Operador.
8. Confirmar que o Operador continua vendo apenas **Configurações** em Sistema.

## Validação técnica

- `py_compile` executado em todos os arquivos `.py`.
- Resultado: OK.
