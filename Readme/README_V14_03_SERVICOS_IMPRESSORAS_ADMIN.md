# V14.03 — Separação de impressoras e ajustes de admin

## Objetivo
Continuar a fase V14 de simplificação interna, deixando a tela Configurações mais limpa por dentro.

## Alterações
- Criado `services/impressoras.py`.
- Criado `services/admin_ajustes.py`.
- Movidos para `services/impressoras.py`:
  - presets de impressoras;
  - cálculo de energia/hora;
  - garantia da tabela/coluna de impressoras;
  - carregamento de impressoras;
  - carregamento da impressora padrão;
  - geração de código de impressora;
  - sincronização da impressora padrão com Configurações.
- Movidos para `services/admin_ajustes.py`:
  - contagem de pedidos sem impressora;
  - aplicação da impressora padrão em pedidos antigos;
  - contagem de pedidos antigos com datas pendentes;
  - preenchimento pontual das datas antigas com Entrega Prevista.
- Sidebar renumerada para `0.14.03`.

## O que não mudou
- Visual da tela Configurações.
- Banco de dados.
- Regras de negócio.
- Cálculos.
- Comportamento dos botões.
- Ajustes continuam exigindo confirmação antes de executar.

## Próximo passo sugerido
Separar regras de pedidos em `services/pedidos.py`, sem alterar a tela.
