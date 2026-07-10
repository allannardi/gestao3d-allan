from services.empresa import dados_empresa_obrigatorios_configurados
from database import conectar


ETAPAS_ONBOARDING = [
    {
        "chave": "empresa",
        "titulo": "Dados da Empresa",
        "descricao": "Nome da empresa/projeto e login Admin da Empresa preenchidos.",
        "destino": "pages/Administrador.py",
        "botao": "Editar dados da empresa",
    },
    {
        "chave": "impressora",
        "titulo": "Primeira impressora",
        "descricao": "Máquina usada para calcular energia, depreciação e produção.",
        "destino": "pages/Configuracoes.py",
        "botao": "Cadastrar impressora",
    },
    {
        "chave": "filamento",
        "titulo": "Primeiro filamento",
        "descricao": "Rolo/material usado para formar o custo por grama.",
        "destino": "pages/1_Filamentos.py",
        "botao": "Cadastrar filamento",
    },
    {
        "chave": "peca",
        "titulo": "Primeira peça",
        "descricao": "Produto/modelo que poderá ser usado nos pedidos.",
        "destino": "pages/3_Pecas.py",
        "botao": "Cadastrar peça",
    },
]


def _contar_tabela(conn, tabela):
    try:
        return int(conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0] or 0)
    except Exception:
        return 0


def dados_empresa_configurados():
    return dados_empresa_obrigatorios_configurados()


def obter_status_onboarding():
    """Retorna o progresso da implantação inicial do projeto.

    Esta checagem é calculada a partir dos dados já existentes. Não cria bloqueio
    obrigatório no app, apenas orienta o Admin da Empresa no começo de um projeto novo.
    """
    conn = conectar()

    try:
        total_impressoras = _contar_tabela(conn, "impressoras")
        total_filamentos = _contar_tabela(conn, "filamentos")
        total_pecas = _contar_tabela(conn, "pecas")
    finally:
        try:
            conn.close()
        except Exception:
            pass

    status = {
        "empresa": dados_empresa_configurados(),
        "impressora": total_impressoras > 0,
        "filamento": total_filamentos > 0,
        "peca": total_pecas > 0,
    }

    etapas = []
    for etapa in ETAPAS_ONBOARDING:
        item = dict(etapa)
        item["concluida"] = bool(status.get(item["chave"]))
        etapas.append(item)

    concluidas = sum(1 for etapa in etapas if etapa["concluida"])
    total = len(etapas)
    completo = concluidas == total
    percentual = int((concluidas / total) * 100) if total else 0

    return {
        "etapas": etapas,
        "concluidas": concluidas,
        "total": total,
        "percentual": percentual,
        "completo": completo,
        "total_impressoras": total_impressoras,
        "total_filamentos": total_filamentos,
        "total_pecas": total_pecas,
    }
