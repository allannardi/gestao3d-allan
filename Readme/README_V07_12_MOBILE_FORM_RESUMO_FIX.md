# Gestão 3D Allan v07.12 - Correção resumo mobile do novo pedido

Correção aplicada:

- A função `pedido_mobile_form_css()` existia, mas não estava sendo chamada.
- Por isso o resumo do pedido aparecia sem o card em degradê e o resumo desktop continuava visível no celular.
- Agora o CSS do formulário mobile é carregado corretamente.

Resultado esperado no celular:

- O resumo do novo pedido aparece como card azul em degradê.
- O bloco desktop "Resumo" fica oculto no celular.
- Botão "Salvar Pedido" continua destacado.
- Nenhum cálculo foi alterado.
- Nenhuma regra de banco foi alterada.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir Pedidos no modo celular
3. Clicar em + Novo Pedido
4. Descer até o resumo
5. Confirmar se aparece como card azul em degradê
