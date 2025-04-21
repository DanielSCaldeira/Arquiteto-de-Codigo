def analisar_codigo(arquivos):
    with open("relatorio_tecnico.txt", "w", encoding="utf-8") as rel:
        for arquivo in arquivos:
            if "Controller" in arquivo:
                rel.write(f"{arquivo}: possível violação do princípio de responsabilidade única.\n")
        rel.write("\nSugestões: aplicar SOLID, remover duplicações, manter métodos simples.\n")
    print("✅ Relatório gerado: relatorio_tecnico.txt")
