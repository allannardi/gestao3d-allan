from database import conectar, SCHEMA_VERSION


SCHEMA_ESPERADO = {
    "configuracoes": {
        "label": "Configurações",
        "grupo": "Base técnica",
        "colunas": [
            "id",
            "energia_hora",
            "depreciacao_hora",
            "margem_padrao",
            "meta_lucro_hora",
            "custo_pos_processamento_hora",
            "valor_kwh",
            "nome_empresa",
            "login_admin_empresa",
            "responsavel_empresa",
            "telefone_whatsapp_empresa",
            "cidade_uf_empresa",
            "observacoes_internas_empresa",
            "status_implantacao",
            "base_empresa_id",
            "codigo_empresa",
            "ambiente_base",
        ],
    },
    "usuarios": {
        "label": "Usuários",
        "grupo": "Base técnica",
        "colunas": [
            "id",
            "nome",
            "email",
            "senha_hash",
            "perfil",
            "status",
            "data_criacao",
            "ultimo_login",
        ],
    },
    "auth_config": {
        "label": "Login antigo",
        "grupo": "Base técnica",
        "colunas": [
            "id",
            "username",
            "password_hash",
            "password_salt",
            "updated_at",
        ],
    },
    "categorias_pecas": {
        "label": "Categorias de peças",
        "grupo": "Apoio",
        "colunas": [
            "id",
            "nome",
        ],
    },
    "impressoras": {
        "label": "Impressoras",
        "grupo": "Operacional",
        "colunas": [
            "id",
            "codigo",
            "marca",
            "modelo",
            "status",
            "consumo_w",
            "valor_kwh",
            "energia_hora",
            "depreciacao_hora",
            "observacoes",
            "is_padrao",
            "data_cadastro",
        ],
    },
    "filamentos": {
        "label": "Filamentos",
        "grupo": "Operacional",
        "colunas": [
            "id",
            "codigo",
            "nome",
            "material",
            "marca",
            "cor",
            "peso_original",
            "valor_compra",
            "fornecedor",
            "data_compra",
            "observacoes",
            "custo_grama",
            "status",
            "data_finalizacao",
        ],
    },
    "acessorios": {
        "label": "Acessórios",
        "grupo": "Operacional",
        "colunas": [
            "id",
            "codigo",
            "nome",
            "categoria",
            "custo_unitario",
            "observacoes",
        ],
    },
    "pecas": {
        "label": "Peças",
        "grupo": "Operacional",
        "colunas": [
            "id",
            "codigo",
            "nome",
            "categoria",
            "peso_g",
            "tempo_impressao_h",
            "tempo_pos_processamento_min",
            "filamento_id",
            "embalagem_custo",
            "link_stl",
            "link_modelo",
            "pasta_google_drive",
            "observacoes",
            "quantidade_lote",
        ],
    },
    "peca_acessorios": {
        "label": "Acessórios por peça",
        "grupo": "Relacionamentos",
        "colunas": [
            "id",
            "peca_id",
            "acessorio_id",
            "quantidade",
        ],
    },
    "peca_filamentos": {
        "label": "Filamentos por peça",
        "grupo": "Relacionamentos",
        "colunas": [
            "id",
            "peca_id",
            "filamento_id",
            "peso_g",
            "observacao",
        ],
    },
    "clientes": {
        "label": "Clientes",
        "grupo": "Operacional",
        "colunas": [
            "id",
            "codigo",
            "nome",
            "tipo",
            "documento",
            "telefone",
            "email",
            "cidade",
            "estado",
            "instagram",
            "origem",
            "observacoes",
            "status",
            "data_cadastro",
        ],
    },
    "pedidos": {
        "label": "Pedidos",
        "grupo": "Operacional",
        "colunas": [
            "id",
            "codigo",
            "cliente_id",
            "peca_id",
            "quantidade",
            "valor_unitario",
            "desconto",
            "frete",
            "status",
            "canal",
            "data_pedido",
            "data_entrega_prevista",
            "data_final_producao",
            "data_entrega_real",
            "observacoes",
            "impressora_id",
        ],
    },
    "pedido_filamentos": {
        "label": "Filamentos por pedido",
        "grupo": "Relacionamentos",
        "colunas": [
            "id",
            "pedido_id",
            "filamento_id",
            "peso_g",
            "observacao",
        ],
    },
}


def _listar_tabelas(conn):
    rows = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """).fetchall()
    return {str(row[0]) for row in rows}


def _listar_colunas(conn, tabela):
    try:
        rows = conn.execute(f"PRAGMA table_info({tabela})").fetchall()
        return {str(row[1]) for row in rows}
    except Exception:
        return set()


def obter_diagnostico_integridade_base():
    """Valida se a base atual possui a estrutura esperada do Gestão 3D.

    Esta checagem é somente diagnóstica. Ela não cria, altera ou remove dados.
    A criação/migração real continua centralizada em `database.py`.
    """
    conn = conectar()
    tabelas_existentes = _listar_tabelas(conn)

    itens = []
    total_colunas_esperadas = 0
    total_colunas_presentes = 0
    total_tabelas_ok = 0

    for tabela, especificacao in SCHEMA_ESPERADO.items():
        existe = tabela in tabelas_existentes
        colunas_esperadas = list(especificacao.get("colunas") or [])
        colunas_existentes = _listar_colunas(conn, tabela) if existe else set()
        colunas_faltantes = [col for col in colunas_esperadas if col not in colunas_existentes]
        colunas_presentes = [col for col in colunas_esperadas if col in colunas_existentes]

        total_colunas_esperadas += len(colunas_esperadas)
        total_colunas_presentes += len(colunas_presentes)
        if existe and not colunas_faltantes:
            total_tabelas_ok += 1

        itens.append({
            "tabela": tabela,
            "label": especificacao.get("label") or tabela,
            "grupo": especificacao.get("grupo") or "Outros",
            "existe": existe,
            "colunas_esperadas": len(colunas_esperadas),
            "colunas_presentes": len(colunas_presentes),
            "colunas_faltantes": colunas_faltantes,
            "ok": bool(existe and not colunas_faltantes),
        })

    conn.close()

    total_tabelas = len(SCHEMA_ESPERADO)
    total_colunas_faltantes = total_colunas_esperadas - total_colunas_presentes
    tabelas_faltantes = [item for item in itens if not item["existe"]]
    tabelas_com_pendencia = [item for item in itens if item["existe"] and item["colunas_faltantes"]]

    return {
        "schema_version": SCHEMA_VERSION,
        "itens": itens,
        "total_tabelas": total_tabelas,
        "total_tabelas_ok": total_tabelas_ok,
        "total_colunas_esperadas": total_colunas_esperadas,
        "total_colunas_presentes": total_colunas_presentes,
        "total_colunas_faltantes": total_colunas_faltantes,
        "tabelas_faltantes": tabelas_faltantes,
        "tabelas_com_pendencia": tabelas_com_pendencia,
        "integridade_ok": bool(total_tabelas_ok == total_tabelas and total_colunas_faltantes == 0),
    }
