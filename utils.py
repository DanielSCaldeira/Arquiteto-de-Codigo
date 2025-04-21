def salvar_arquivo(nome, conteudo):
    with open(nome, "w", encoding="utf-8") as f:
        f.write(conteudo)
