import os
import sqlite3

DB_NAME = "pecas_industria.db"


def conectar():
    return sqlite3.connect(DB_NAME)


conn = conectar()
cursor = conn.cursor()


def coluna_existe(nome_tabela, nome_coluna):
    cursor.execute(f"PRAGMA table_info({nome_tabela})")
    colunas = cursor.fetchall()
    return any(coluna[1] == nome_coluna for coluna in colunas)


def tabela_existe(nome_tabela):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (nome_tabela,)
    )
    return cursor.fetchone() is not None


def recriar_banco():
    cursor.execute("DROP TABLE IF EXISTS pecas")
    cursor.execute("DROP TABLE IF EXISTS caixas")

    cursor.execute("""
        CREATE TABLE pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peso REAL NOT NULL,
            cor TEXT NOT NULL,
            comprimento REAL NOT NULL,
            status TEXT NOT NULL,
            motivo TEXT,
            caixa_id INTEGER,
            FOREIGN KEY (caixa_id) REFERENCES caixas(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE caixas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL
        )
    """)

    conn.commit()


def inicializar_banco():
    # Se existir banco antigo com estrutura diferente, recria automaticamente
    if tabela_existe("caixas") and not coluna_existe("caixas", "id"):
        print("Banco antigo detectado. Recriando estrutura automaticamente...")
        recriar_banco()
        return

    if tabela_existe("pecas") and not coluna_existe("pecas", "id"):
        print("Banco antigo detectado. Recriando estrutura automaticamente...")
        recriar_banco()
        return

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caixas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peso REAL NOT NULL,
            cor TEXT NOT NULL,
            comprimento REAL NOT NULL,
            status TEXT NOT NULL,
            motivo TEXT,
            caixa_id INTEGER,
            FOREIGN KEY (caixa_id) REFERENCES caixas(id)
        )
    """)
    conn.commit()


def validar_peca(peso, cor, comprimento):
    erros = []

    if not (95 <= peso <= 105):
        erros.append(f"Peso fora do limite ({peso}g)")

    if cor.lower() not in ["azul", "verde"]:
        erros.append(f"Cor '{cor}' nao permitida")

    if not (10 <= comprimento <= 20):
        erros.append(f"Comprimento fora do limite ({comprimento}cm)")

    if erros:
        return False, " | ".join(erros)
    return True, "Aprovada"


def obter_caixa_aberta():
    cursor.execute("SELECT id FROM caixas WHERE status = 'aberta' ORDER BY id LIMIT 1")
    caixa = cursor.fetchone()

    if caixa:
        return caixa[0]

    cursor.execute("INSERT INTO caixas (status) VALUES ('aberta')")
    conn.commit()
    return cursor.lastrowid


def contar_pecas_na_caixa(caixa_id):
    cursor.execute("SELECT COUNT(*) FROM pecas WHERE caixa_id = ?", (caixa_id,))
    return cursor.fetchone()[0]


def cadastrar_peca():
    try:
        peso = float(input("Peso (g): "))
        cor = input("Cor (azul/verde): ").strip().lower()
        comprimento = float(input("Comprimento (cm): "))

        aprovada, motivo = validar_peca(peso, cor, comprimento)

        if aprovada:
            caixa_id = obter_caixa_aberta()

            cursor.execute("""
                INSERT INTO pecas (peso, cor, comprimento, status, motivo, caixa_id)
                VALUES (?, ?, ?, 'aprovada', '', ?)
            """, (peso, cor, comprimento, caixa_id))
            conn.commit()

            peca_id = cursor.lastrowid
            print(f"Peca {peca_id} APROVADA e armazenada na caixa {caixa_id}.")

            if contar_pecas_na_caixa(caixa_id) >= 10:
                cursor.execute("UPDATE caixas SET status = 'fechada' WHERE id = ?", (caixa_id,))
                conn.commit()
                print(f"Caixa {caixa_id} cheia e fechada.")
        else:
            cursor.execute("""
                INSERT INTO pecas (peso, cor, comprimento, status, motivo, caixa_id)
                VALUES (?, ?, ?, 'reprovada', ?, NULL)
            """, (peso, cor, comprimento, motivo))
            conn.commit()

            peca_id = cursor.lastrowid
            print(f"Peca {peca_id} REPROVADA por: {motivo}")

    except ValueError:
        print("Erro: use apenas numeros para peso e comprimento.")


def listar_pecas():
    cursor.execute("""
        SELECT id, peso, cor, comprimento, status, motivo, caixa_id
        FROM pecas
        ORDER BY id
    """)
    pecas = cursor.fetchall()

    if not pecas:
        print("\nNenhuma peca cadastrada.")
        return

    print("\n--- PECAS CADASTRADAS ---")
    for p in pecas:
        id_peca, peso, cor, comprimento, status, motivo, caixa_id = p
        if status == "aprovada":
            print(
                f"ID: {id_peca} | Peso: {peso}g | Cor: {cor} | "
                f"Comprimento: {comprimento}cm | Status: {status} | Caixa: {caixa_id}"
            )
        else:
            print(
                f"ID: {id_peca} | Peso: {peso}g | Cor: {cor} | "
                f"Comprimento: {comprimento}cm | Status: {status} | Motivo: {motivo}"
            )


def remover_peca():
    try:
        id_remover = int(input("ID da peca para remover: "))
    except ValueError:
        print("Digite um ID numerico.")
        return

    cursor.execute("SELECT id, status, caixa_id FROM pecas WHERE id = ?", (id_remover,))
    peca = cursor.fetchone()

    if not peca:
        print("Peca nao encontrada.")
        return

    _, status, caixa_id = peca

    cursor.execute("DELETE FROM pecas WHERE id = ?", (id_remover,))
    conn.commit()
    print(f"Peca {id_remover} removida com sucesso.")

    if status == "aprovada" and caixa_id is not None:
        cursor.execute("SELECT COUNT(*) FROM pecas WHERE caixa_id = ?", (caixa_id,))
        quantidade = cursor.fetchone()[0]

        if quantidade == 0:
            cursor.execute("DELETE FROM caixas WHERE id = ?", (caixa_id,))
            conn.commit()
            print(f"Caixa {caixa_id} removida, pois ficou vazia.")
        elif quantidade < 10:
            cursor.execute("UPDATE caixas SET status = 'aberta' WHERE id = ?", (caixa_id,))
            conn.commit()


def listar_caixas():
    cursor.execute("SELECT id, status FROM caixas ORDER BY id")
    caixas = cursor.fetchall()

    if not caixas:
        print("\nNenhuma caixa cadastrada.")
        return

    print("\n--- CAIXAS ---")
    for caixa_id, status in caixas:
        print(f"\nCaixa {caixa_id} - {status}")
        cursor.execute("""
            SELECT id, cor, peso, comprimento
            FROM pecas
            WHERE caixa_id = ?
            ORDER BY id
        """, (caixa_id,))
        pecas = cursor.fetchall()

        if not pecas:
            print("  Sem pecas.")
        else:
            for p in pecas:
                print(f"  Peca {p[0]} | Cor: {p[1]} | Peso: {p[2]}g | Comprimento: {p[3]}cm")


def gerar_relatorio():
    cursor.execute("SELECT COUNT(*) FROM pecas WHERE status = 'aprovada'")
    aprovadas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pecas WHERE status = 'reprovada'")
    reprovadas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM caixas")
    total_caixas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM caixas WHERE status = 'fechada'")
    caixas_fechadas = cursor.fetchone()[0]

    cursor.execute("""
        SELECT id, motivo
        FROM pecas
        WHERE status = 'reprovada'
        ORDER BY id
    """)
    reprovacoes = cursor.fetchall()

    print("\n--- RELATORIO FINAL ---")
    print(f"Total de pecas aprovadas: {aprovadas}")
    print(f"Total de pecas reprovadas: {reprovadas}")
    print(f"Quantidade de caixas utilizadas: {total_caixas}")
    print(f"Caixas fechadas: {caixas_fechadas}")

    if reprovacoes:
        print("\nMotivos de reprovacao:")
        for item in reprovacoes:
            print(f"ID {item[0]}: {item[1]}")
    else:
        print("\nNao ha pecas reprovadas.")


def menu():
    while True:
        print("\n" + "=" * 40)
        print("   SISTEMA DE VERIFICACAO")
        print("=" * 40)
        print("1. Cadastrar nova peca")
        print("2. Listar pecas aprovadas/reprovadas")
        print("3. Remover peca cadastrada")
        print("4. Listar caixas")
        print("5. Gerar relatorio final")
        print("0. Sair")

        opcao = input("\nEscolha uma opcao: ").strip()

        if opcao == "1":
            cadastrar_peca()
        elif opcao == "2":
            listar_pecas()
        elif opcao == "3":
            remover_peca()
        elif opcao == "4":
            listar_caixas()
        elif opcao == "5":
            gerar_relatorio()
        elif opcao == "0":
            print("Encerrando sistema...")
            break
        else:
            print("Opcao invalida. Tente novamente.")


if __name__ == "__main__":
    inicializar_banco()
    menu()
    conn.close()
