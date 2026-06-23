# Gestão 3D Allan v09.06 - Paginação e listagens inteligentes

Objetivo:
Evitar que o Streamlit renderize todos os cards de uma vez quando a base crescer.

Contexto:
Mesmo com cache e consultas otimizadas, o Streamlit ainda precisa montar visualmente todos os cards exibidos na tela.
Se houver muitos pedidos, peças, clientes ou filamentos, renderizar tudo de uma vez deixa a página pesada.

Alterações aplicadas:

## Novo componente
Criado:
- `components/pagination.py`

Função:
- `paginar_itens(...)`

## Páginas com paginação
Paginação aplicada em:
- Pedidos;
- Peças;
- Clientes;
- Filamentos;
- Acessórios.

## Como funciona
Quando a lista tiver mais de 10 itens, aparece:
- Itens por página;
- Página;
- indicação de quantos itens estão sendo exibidos.

Opções:
- 10;
- 25;
- 50;
- 100.

## Benefício
A página passa a renderizar somente uma parte dos cards por vez.
Isso reduz o peso visual do rerun do Streamlit.

Preservado:
- Visual aprovado.
- Mobile aprovado.
- Busca.
- Detalhes.
- Edição.
- Duplicação.
- Exclusão.
- Cálculos.
- Banco de dados.

Teste:
1. Rodar `streamlit run Dashboard.py`.
2. Abrir:
   - Pedidos;
   - Peças;
   - Clientes;
   - Filamentos;
   - Acessórios.
3. Validar:
   - busca;
   - mudança de itens por página;
   - mudança de página;
   - abrir detalhes;
   - editar/duplicar/excluir se possível.
