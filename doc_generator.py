def gerar_documentacao(arquivos):
    with open("README.md", "w", encoding="utf-8") as readme:
        readme.write("# Documentação Automática\n\n")
        readme.write("## Funcionalidade do Sistema\n")
        readme.write("Sistema gerado a partir do código-fonte com base em padrões da empresa.\n\n")
        readme.write("## Estrutura dos Arquivos\n")
        for arq in arquivos:
            readme.write(f"- {arq}\n")
    print("✅ README.md gerado")
