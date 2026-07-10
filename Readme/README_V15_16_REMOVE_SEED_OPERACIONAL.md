# Gestão 3D — v15.16 — Remove seed operacional

- App: `0.15.16`
- `SCHEMA_VERSION`: `v15_16_remove_seed_operacional`

## Objetivo

Fechar uma pendência técnica antes de avançar para o modelo de bancos separados por empresa.

A partir desta versão, o código legado que poderia criar uma impressora operacional automaticamente em bases novas foi removido.

## O que entrou

- Remoção da função legada de criação automática de impressora padrão.
- Reforço da regra: uma base nova pode nascer com dados técnicos mínimos, mas não com dados operacionais.
- Aba **Base limpa** atualizada com a seção **Regra técnica para nova base**.
- Diagnóstico indicando que o seed operacional automático está removido.

## Regras para uma base nova

Permitido:

- configurações técnicas mínimas;
- usuário Admin da Empresa inicial;
- categorias de apoio.

Manual pela empresa:

- primeira impressora;
- primeiro filamento;
- primeira peça;
- clientes;
- acessórios;
- pedidos.

## O que não mudou

- Não cria banco central.
- Não cria banco separado automaticamente.
- Não cria Admin Geral Gestão 3D.
- Não altera dados existentes.
- Não apaga impressoras já cadastradas.

## Validação sugerida

1. Confirmar sidebar com `0.15.16`.
2. Abrir **Administrador**.
3. Ir para **Base limpa**.
4. Confirmar a seção **Regra técnica para nova base**.
5. Confirmar a mensagem de que o seed operacional automático foi removido.
6. Confirmar que os contadores da base atual continuam aparecendo normalmente.
7. Confirmar que as demais abas de Administrador continuam funcionando.
8. Entrar como Operador e confirmar que ele continua vendo apenas **Configurações** em Sistema.

## Validação técnica

- `py_compile`: OK.
