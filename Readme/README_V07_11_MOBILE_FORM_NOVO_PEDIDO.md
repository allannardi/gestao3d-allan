# Gestão 3D Allan v07.11 - Mobile formulário de novo pedido

Alterações:

- Formulário de novo pedido ficou mais guiado no celular.
- Foram criadas etapas visuais:
  1. Cliente
  2. Peça e preço
  3. Valores
  4. Acompanhamento
- Resumo do pedido no celular virou um card em degradê, no padrão da Dashboard.
- Resumo desktop foi preservado com KPIs laterais.
- Botão Salvar Pedido ganhou mais destaque no celular.
- Nenhuma regra de cálculo foi alterada.
- Nenhuma estrutura de banco foi alterada.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir Pedidos no celular/tela estreita
3. Clicar em + Novo Pedido
4. Validar etapas, campos, resumo e botão salvar
5. Testar criar um pedido novo
6. Confirmar que o desktop segue preservado
