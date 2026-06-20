# Gestão 3D Cloud Allan v02 - Otimização de velocidade

Alterações desta versão:

1. `database.inicializar_banco()` agora roda criação/migração de tabelas apenas uma vez por sessão.
2. Foram removidas chamadas redundantes de migração nas páginas:
   - Dashboard
   - Filamentos
   - Peças
   - Clientes
   - Pedidos
3. Isso reduz chamadas remotas ao Turso em cada clique, troca de página e salvamento.

Teste recomendado:

1. Rodar `streamlit run Dashboard.py`
2. Entrar com login
3. Trocar entre páginas
4. Abrir `+ Novo Pedido`
5. Salvar um cliente/pedido
6. Comparar o tempo com a versão anterior

Se ainda ficar lento, o próximo passo será otimizar as consultas e cálculos da página Pedidos e Dashboard.
