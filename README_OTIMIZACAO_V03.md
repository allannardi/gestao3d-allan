# Gestão 3D Cloud Allan v03 - Conexão Turso otimizada

Alteração principal:

- No modo Turso/cloud, o app mantém uma conexão remota aberta por sessão do Streamlit.
- As chamadas `conn.close()` das páginas continuam existindo, mas são ignoradas no modo Turso.
- Isso evita abrir e fechar uma conexão remota em cada clique, troca de página ou salvamento.

O que testar:

1. `streamlit run Dashboard.py`
2. Fazer login
3. Trocar de páginas
4. Abrir novo pedido
5. Salvar cliente/pedido
6. Comparar a velocidade com a v02

Se ainda ficar lento, o próximo gargalo provável é volume de consultas e cálculos repetidos na página Pedidos e na Dashboard.
