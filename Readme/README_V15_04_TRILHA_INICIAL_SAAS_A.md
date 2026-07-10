# Gestão 3D — v15.04

## Objetivo da versão

Esta versão inicia a trilha inicial de implantação para projetos novos e registra a decisão técnica futura do SaaS:

```text
Caminho A: um banco separado por empresa/cliente.
```

A versão atual ainda não transforma o sistema em SaaS multiempresa. O Gestão 3D continua usando a mesma base para os usuários cadastrados neste projeto. A decisão do banco por empresa fica como norte técnico para a migração futura.

## O que entrou

- Versão atualizada para `0.15.04`.
- `SCHEMA_VERSION` atualizado para `v15_04_trilha_inicial_saas_a`.
- Novo service:

```text
services/onboarding.py
```

- Novo componente:

```text
components/onboarding.py
```

- Trilha inicial para Admin com 4 etapas:

```text
1. Nome da empresa/projeto
2. Primeira impressora
3. Primeiro filamento
4. Primeira peça
```

- A trilha aparece no Início quando ainda houver etapa pendente.
- A trilha aparece em Configurações para Admin como checklist de implantação.
- Botões de atalho para ir direto ao cadastro/configuração pendente.

## O que não mudou

- Ainda não é SaaS multiempresa.
- Ainda não existe um banco separado por empresa dentro do app atual.
- Não foi adicionado `empresa_id` nas tabelas, porque o caminho futuro escolhido foi banco por empresa.
- Não houve alteração destrutiva no banco.
- Pedidos, Peças, Filamentos, Clientes e Dashboard seguem com as regras atuais.

## Roadmap SaaS registrado

Quando chegar a fase SaaS, o caminho escolhido será:

```text
empresa/cliente A -> banco A
empresa/cliente B -> banco B
empresa/cliente C -> banco C
```

Isso mantém os dados dos clientes isolados e combina melhor com a ideia futura de provisionar um ambiente próprio para cada negócio.

## O que validar

1. Entrar como Admin.
2. Confirmar que a sidebar mostra `0.15.04`.
3. Abrir `Início`.
4. Se houver etapa pendente, confirmar que aparece a trilha inicial.
5. Abrir `Configurações`.
6. Confirmar que aparece a área `Trilha inicial` para Admin.
7. Confirmar que a trilha mostra corretamente o status de:
   - empresa/projeto;
   - impressora;
   - filamento;
   - peça.
8. Entrar como Operador.
9. Confirmar que o Operador não vê a trilha administrativa em Configurações.

## Observação

Em bancos/projetos já preenchidos, a trilha pode aparecer como concluída ou nem aparecer no Início. Isso é esperado. Ela foi criada principalmente para orientar projetos iniciados do zero.
