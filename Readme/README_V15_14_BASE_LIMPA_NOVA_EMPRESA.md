# Gestão 3D — v15.14 — Base limpa para nova empresa

Esta versão continua a preparação para o modelo futuro escolhido: **uma empresa = um banco separado**.

## O que mudou

- Versão atualizada para `0.15.14`.
- `SCHEMA_VERSION` atualizado para `v15_14_base_limpa_nova_empresa`.
- O sistema deixou de criar automaticamente uma impressora padrão em bases novas.
- A primeira impressora agora deve ser cadastrada pelo Admin da Empresa durante a trilha inicial.
- Nova aba `Base limpa` na página `Administrador`.
- Novo service `services/base_limpa.py`.

## Por que isso é importante

Para liberar uma nova empresa no futuro, ela deverá começar em um banco separado e sem dados operacionais herdados ou fictícios.

Antes desta versão, uma base vazia poderia receber automaticamente uma impressora padrão `Bambu Lab A1 Mini`. Isso era útil no início do MVP, mas não é adequado para uma nova empresa real.

Agora, uma nova base pode começar limpa e a trilha inicial indicará que falta cadastrar a primeira impressora.

## Dados operacionais que devem começar zerados em uma nova base

- Impressoras
- Filamentos
- Peças
- Clientes
- Acessórios
- Pedidos

## Dados técnicos permitidos em uma nova base

- Configurações padrão
- Usuário Admin da Empresa inicial
- Categorias padrão de peças
- Tabela de compatibilidade do login antigo

## O que não mudou

- Não foi criado banco central.
- Não foi criado Admin Geral Gestão 3D.
- Não foi criada empresa automaticamente.
- Não houve alteração destrutiva no banco.
- Bases existentes não têm impressoras apagadas.
- Pedidos, Dashboard, Peças, Filamentos e Clientes não tiveram regra funcional alterada.

## Validação recomendada

1. Entrar como Admin da Empresa.
2. Confirmar sidebar com `0.15.14`.
3. Abrir `Administrador`.
4. Confirmar a nova aba `Base limpa`.
5. Conferir os contadores de dados operacionais.
6. Confirmar que a empresa atual pode aparecer com dados, pois já está em operação.
7. Confirmar que `Dados da Empresa`, `Base da Empresa`, `Implantação`, `Ajustes de Admin` e `Prontidão` continuam funcionando.
8. Entrar como Operador e confirmar que ele continua vendo apenas `Configurações` em Sistema.
