# Gestão 3D Allan v08.09 - Cards e listagens desktop

Objetivo:
Melhorar visualmente os cards e listagens do desktop, mantendo o mobile aprovado.

Alterações aplicadas:

## Cards gerais
- Criado/atualizado `components/card.py`.
- Cards de Clientes, Peças, Filamentos e Acessórios agora seguem padrão mais premium:
  - título em azul escuro;
  - código menor e discreto;
  - linha superior colorida;
  - subtítulo em cinza;
  - bordas arredondadas;
  - fundo branco com leve acabamento.

## Cards de Pedidos
- Card de pedido redesenhado no desktop:
  - número do pedido maior;
  - peça com destaque;
  - cliente mais discreto;
  - status com borda/colorido, sem fundo carregado;
  - resumo de quantidade, total e data em mini-cards;
  - acabamento com sombra suave.

## Listagens
- Containers e expanders de listagens receberam acabamento mais refinado no desktop.
- Mobile preservado por media query.

Preservado:
- Mobile aprovado.
- Cálculos.
- Banco de dados.
- Regras de negócio.
- Dashboard e sidebar aprovados.

Teste:
1. Rodar `streamlit run Dashboard.py`.
2. Validar desktop:
   - Pedidos;
   - Peças;
   - Clientes;
   - Filamentos;
   - Acessórios.
3. Abrir alguns expanders e confirmar que os detalhes continuam funcionando.
4. Fazer teste rápido no mobile.
