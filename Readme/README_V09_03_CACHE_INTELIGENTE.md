# Gestão 3D Allan v09.03 - Cache inteligente

Objetivo:
Reduzir o peso dos reruns do Streamlit sem deixar dados recém-salvos escondidos.

Contexto:
No Streamlit, cada clique/interação reexecuta a página.
O cache não impede o rerun, mas evita que dados fixos sejam buscados de novo no banco a cada interação.

Alterações aplicadas:

## Pedidos
Dados com cache curto de 30 segundos:
- configurações;
- clientes ativos;
- peças;
- filamentos ativos.

Ao salvar/editar/duplicar/excluir, o cache é limpo antes do rerun.

## Peças
Criado carregamento em cache da base da página:
- configurações;
- filamentos ativos;
- todos os filamentos;
- acessórios;
- categorias;
- lista base de peças.

Ao salvar/editar/duplicar/excluir, o cache é limpo antes do rerun.

## CSS base
O arquivo `assets/style.css` passa a ser carregado com cache de 1 hora nas páginas que usam esse arquivo.
Isso reduz pequenas leituras repetidas a cada rerun.

Preservado:
- Visual aprovado.
- Mobile aprovado.
- Desktop aprovado.
- Regras de negócio.
- Cálculos.
- Banco de dados.

Impacto esperado:
- Menos consultas repetidas ao banco em cliques simples.
- Pedidos e Peças devem ficar mais leves em interações.
- Melhor efeito no ambiente online com Turso/Streamlit Cloud.

Teste:
1. Rodar `streamlit run Dashboard.py`.
2. Validar:
   - Pedidos;
   - Novo Pedido;
   - Peças;
   - Nova Peça;
   - edição/duplicação se possível.
3. Criar um item de teste e confirmar que aparece após salvar.
4. Se algo parecer desatualizado, recarregar a página. O cache também expira em 30 segundos.
