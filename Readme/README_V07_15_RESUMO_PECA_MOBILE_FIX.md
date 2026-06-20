# Gestão 3D Allan v07.15 - Correção resumo mobile de Peças

Correção aplicada:

- A função `peca_mobile_form_css()` existia, mas não estava sendo chamada na página Peças.
- Por isso o "Resumo da peça" aparecia como texto simples no celular.
- Agora o CSS do formulário mobile de Peças é carregado corretamente.
- O resumo da peça deve aparecer como card azul em degradê.
- O resumo desktop "Resumo do lote" fica oculto no celular.

Nenhuma regra de cálculo foi alterada.
Nenhuma estrutura de banco foi alterada.
Arquivos Python validados por compilação antes de gerar o ZIP.

Teste:
1. Rodar `streamlit run Dashboard.py`
2. Abrir a aba Peças no celular/tela estreita
3. Clicar em + Nova Peça
4. Descer até o Resumo da peça
5. Confirmar se aparece como card azul em degradê
