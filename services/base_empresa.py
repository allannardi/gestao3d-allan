import re
from uuid import uuid4

from database import conectar, garantir_coluna, obter_info_banco_atual
from services.empresa import obter_dados_empresa


AMBIENTE_BASE_OPCOES = [
    "Operação",
    "Teste",
    "Homologação",
]


CAMPOS_BASE_EMPRESA = {
    "base_empresa_id": "TEXT DEFAULT ''",
    "codigo_empresa": "TEXT DEFAULT ''",
    "ambiente_base": "TEXT DEFAULT 'Operação'",
}


def _texto(valor):
    return str(valor or "").strip()


def garantir_colunas_base_empresa():
    for coluna, definicao in CAMPOS_BASE_EMPRESA.items():
        try:
            garantir_coluna("configuracoes", coluna, definicao)
        except Exception:
            pass


def normalizar_ambiente_base(ambiente):
    ambiente = _texto(ambiente)
    return ambiente if ambiente in AMBIENTE_BASE_OPCOES else AMBIENTE_BASE_OPCOES[0]


def normalizar_codigo_empresa(valor):
    texto = _texto(valor).lower()
    mapa = str.maketrans({
        "á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a",
        "é": "e", "ê": "e", "è": "e", "ë": "e",
        "í": "i", "ì": "i", "î": "i", "ï": "i",
        "ó": "o", "ò": "o", "ô": "o", "õ": "o", "ö": "o",
        "ú": "u", "ù": "u", "û": "u", "ü": "u",
        "ç": "c",
    })
    texto = texto.translate(mapa)
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    texto = re.sub(r"-+", "-", texto).strip("-")
    return texto[:40] or "empresa"


def sugerir_codigo_empresa(nome_empresa=None):
    nome_empresa = nome_empresa or obter_dados_empresa().get("nome_empresa")
    return normalizar_codigo_empresa(nome_empresa)


def _gerar_base_empresa_id():
    return f"g3d-{uuid4().hex[:12]}"


def obter_base_empresa(criar_se_vazio=True):
    """Retorna a identidade da base atual.

    No modelo escolhido para o futuro, cada banco representa uma empresa.
    Estes metadados identificam a base atual sem misturar empresas no mesmo banco.
    """
    garantir_colunas_base_empresa()

    dados_empresa = obter_dados_empresa()
    base = {
        "base_empresa_id": "",
        "codigo_empresa": sugerir_codigo_empresa(dados_empresa.get("nome_empresa")),
        "ambiente_base": AMBIENTE_BASE_OPCOES[0],
    }

    conn = conectar()
    row = conn.execute("""
        SELECT
            COALESCE(base_empresa_id, ''),
            COALESCE(codigo_empresa, ''),
            COALESCE(ambiente_base, 'Operação')
        FROM configuracoes
        LIMIT 1
    """).fetchone()

    if row:
        base.update({
            "base_empresa_id": _texto(row[0]),
            "codigo_empresa": normalizar_codigo_empresa(row[1]) if _texto(row[1]) else base["codigo_empresa"],
            "ambiente_base": normalizar_ambiente_base(row[2]),
        })

    alterou = False
    if criar_se_vazio and not base["base_empresa_id"]:
        base["base_empresa_id"] = _gerar_base_empresa_id()
        alterou = True

    if criar_se_vazio and not _texto(row[1] if row else ""):
        base["codigo_empresa"] = sugerir_codigo_empresa(dados_empresa.get("nome_empresa"))
        alterou = True

    if alterou:
        total = conn.execute("SELECT COUNT(*) FROM configuracoes").fetchone()[0]
        if int(total or 0) == 0:
            conn.execute("""
                INSERT INTO configuracoes
                (
                    energia_hora,
                    depreciacao_hora,
                    margem_padrao,
                    meta_lucro_hora,
                    custo_pos_processamento_hora,
                    valor_kwh,
                    nome_empresa,
                    login_admin_empresa,
                    responsavel_empresa,
                    telefone_whatsapp_empresa,
                    cidade_uf_empresa,
                    observacoes_internas_empresa,
                    status_implantacao,
                    base_empresa_id,
                    codigo_empresa,
                    ambiente_base
                )
                VALUES (0.15, 0.75, 150, 5, 0, 0.65, 'Minha empresa', 'admin', '', '', '', '', 'Em implantação', ?, ?, ?)
            """, (base["base_empresa_id"], base["codigo_empresa"], base["ambiente_base"]))
        else:
            conn.execute("""
                UPDATE configuracoes
                SET
                    base_empresa_id = ?,
                    codigo_empresa = ?,
                    ambiente_base = ?
            """, (base["base_empresa_id"], base["codigo_empresa"], base["ambiente_base"]))
        conn.commit()

    conn.close()
    return base


def salvar_base_empresa(codigo_empresa, ambiente_base):
    codigo_empresa = normalizar_codigo_empresa(codigo_empresa)
    ambiente_base = normalizar_ambiente_base(ambiente_base)

    if not codigo_empresa:
        return False, "Informe o código interno da empresa/base.", None

    base_atual = obter_base_empresa(criar_se_vazio=True)
    base_empresa_id = base_atual.get("base_empresa_id") or _gerar_base_empresa_id()

    conn = conectar()
    conn.execute("""
        UPDATE configuracoes
        SET
            base_empresa_id = ?,
            codigo_empresa = ?,
            ambiente_base = ?
    """, (base_empresa_id, codigo_empresa, ambiente_base))
    conn.commit()
    conn.close()

    return True, "Identidade da base atualizada com sucesso.", obter_base_empresa(criar_se_vazio=True)


def obter_diagnostico_base_empresa():
    base = obter_base_empresa(criar_se_vazio=True)
    info_banco = obter_info_banco_atual()
    return {
        **base,
        **info_banco,
        "modelo_dados": "Um banco por empresa",
    }
