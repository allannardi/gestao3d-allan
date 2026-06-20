# Gestão 3D Allan v06 - Mobile v01

Esta versão adiciona a primeira camada de experiência mobile.

## O que foi incluído

1. Novo componente:
   - `components/mobile_nav.py`

2. Menu inferior fixo para celular:
   - Início
   - Pedidos
   - Peças
   - Clientes
   - Mais

3. No desktop:
   - Continua usando a sidebar lateral normalmente.

4. No celular:
   - A sidebar lateral é escondida.
   - O menu inferior aparece fixo no rodapé.
   - O conteúdo ganha padding inferior para o menu não cobrir os cards.
   - Campos, botões e colunas ficam mais confortáveis em telas pequenas.

## Como testar

1. Rode localmente:
   `streamlit run Dashboard.py`

2. Abra pelo celular usando o link do Streamlit Cloud depois do deploy, ou teste no navegador reduzindo a largura da janela.

3. Verifique:
   - Menu inferior aparece no celular.
   - Sidebar lateral continua no desktop.
   - Links Início / Pedidos / Peças / Clientes / Mais funcionam.

## Observação

Esta é a v01 mobile. Ela não reestrutura toda a Dashboard nem todas as listas ainda.
O próximo passo será adaptar Dashboard e Pedidos com cards específicos para celular.
