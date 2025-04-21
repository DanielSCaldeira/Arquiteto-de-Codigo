def gerar_crud(nome, campos):
    model = f"class {nome}:\n"
    for campo in campos:
        model += f"    {campo.lower()} = None\n"
    with open(f"{nome}.cs", "w", encoding="utf-8") as f:
        f.write(model)

    with open(f"{nome}Controller.cs", "w", encoding="utf-8") as f:
        f.write(f"// Controller para {nome}\n")

    with open(f"{nome}Service.cs", "w", encoding="utf-8") as f:
        f.write(f"// Service para {nome}\n")

    print(f"✅ CRUD de {nome} gerado com sucesso")
