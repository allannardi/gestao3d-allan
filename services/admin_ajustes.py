"""
Ajustes pontuais de administração do Gestão 3D.

Este módulo concentra ações de manutenção que hoje ficam na seção
Configurações > Ajustes de Admin.
No futuro, essas funções devem ser chamadas apenas por usuários com perfil Admin da Empresa.
"""

from database import conectar


def contar_pedidos_sem_impressora():
    conn = conectar()

    try:
        total = conn.execute("""
        SELECT COUNT(*)
        FROM pedidos
        WHERE impressora_id IS NULL
        """).fetchone()[0]
    except Exception:
        total = 0

    conn.close()
    return total


def aplicar_impressora_padrao_pedidos_antigos(impressora_id):
    conn = conectar()

    resultado = conn.execute("""
    UPDATE pedidos
    SET impressora_id = ?
    WHERE impressora_id IS NULL
    """, (impressora_id,))

    quantidade = resultado.rowcount if resultado.rowcount is not None else 0

    conn.commit()
    conn.close()

    return quantidade


def contar_pedidos_para_ajuste_datas_previstas():
    conn = conectar()

    try:
        total = conn.execute("""
        SELECT COUNT(*)
        FROM pedidos
        WHERE data_entrega_prevista IS NOT NULL
          AND TRIM(data_entrega_prevista) <> ''
          AND (
                data_final_producao IS NULL
                OR TRIM(data_final_producao) = ''
                OR data_entrega_real IS NULL
                OR TRIM(data_entrega_real) = ''
          )
        """).fetchone()[0]

        sem_data_final = conn.execute("""
        SELECT COUNT(*)
        FROM pedidos
        WHERE data_entrega_prevista IS NOT NULL
          AND TRIM(data_entrega_prevista) <> ''
          AND (data_final_producao IS NULL OR TRIM(data_final_producao) = '')
        """).fetchone()[0]

        sem_data_entrega = conn.execute("""
        SELECT COUNT(*)
        FROM pedidos
        WHERE data_entrega_prevista IS NOT NULL
          AND TRIM(data_entrega_prevista) <> ''
          AND (data_entrega_real IS NULL OR TRIM(data_entrega_real) = '')
        """).fetchone()[0]

    except Exception:
        total = 0
        sem_data_final = 0
        sem_data_entrega = 0

    conn.close()

    return {
        "total": total,
        "sem_data_final": sem_data_final,
        "sem_data_entrega": sem_data_entrega,
    }


def aplicar_entrega_prevista_nas_datas_antigas():
    conn = conectar()

    resultado = conn.execute("""
    UPDATE pedidos
    SET
        data_final_producao = CASE
            WHEN data_final_producao IS NULL OR TRIM(data_final_producao) = ''
            THEN data_entrega_prevista
            ELSE data_final_producao
        END,
        data_entrega_real = CASE
            WHEN data_entrega_real IS NULL OR TRIM(data_entrega_real) = ''
            THEN data_entrega_prevista
            ELSE data_entrega_real
        END
    WHERE data_entrega_prevista IS NOT NULL
      AND TRIM(data_entrega_prevista) <> ''
      AND (
            data_final_producao IS NULL
            OR TRIM(data_final_producao) = ''
            OR data_entrega_real IS NULL
            OR TRIM(data_entrega_real) = ''
      )
    """)

    quantidade = resultado.rowcount if resultado.rowcount is not None else 0

    conn.commit()
    conn.close()

    return quantidade
