import os

def get_nome_base_arquivo(nome_arquivo):
    """
    Extrai o nome base da entidade removendo:
     - O sufixo completo '.mapping.hbm.xml'
     - Depois a extensão genérica ('.cs', '.xml', etc.)
     - E por fim outros sufixos de tipo (Controller, Service, etc.)
    """
    # 1) Se for HBM mapping, remova esse sufixo completo
    mapping_suffix = ".mapping.hbm.xml"
    if nome_arquivo.endswith(mapping_suffix):
        nome_sem_ext = nome_arquivo[: -len(mapping_suffix)]
    else:
        # 2) Caso contrário, remova apenas a extensão genérica
        nome_sem_ext = os.path.splitext(nome_arquivo)[0]

    # 3) Remova outros sufixos de tipo, se existirem
    for sufixo in ("Controller", "Service", "Transport", "DTO", "Model"):
        if nome_sem_ext.endswith(sufixo):
            nome_sem_ext = nome_sem_ext[: -len(sufixo)]
            break

    return nome_sem_ext


def get_tipo_arquivo(nome_arquivo):
    """Determina o tipo do arquivo a partir de seu sufixo."""
    if nome_arquivo.endswith("Controller.cs"):
        return "Controller"
    if nome_arquivo.endswith("Service.cs"):
        return "Service"
    if nome_arquivo.endswith("Transport.cs") or nome_arquivo.endswith("DTO.cs"):
        return "Transport"
    # Só .hbm.xml aqui para XMLModel
    if nome_arquivo.endswith("hbm.xml"):
        return "XMLModel"
    if nome_arquivo.endswith(".cs"):
        return "Model"
    return None

def carregar_arquivos_organizado(diretorio_base="./_dados"):
    """
    Retorna um dict onde cada chave é o nome da entidade, e o valor é
    outro dict com as chaves Controller, Service, Transport, XMLModel, Model
    apontando para o conteúdo de cada arquivo.
    """
    documentos = {}

    for root, _, files in os.walk(diretorio_base):
        for file in files:
            tipo = get_tipo_arquivo(file)
            if not tipo:
                continue

            nome_base = get_nome_base_arquivo(file)
            caminho = os.path.join(root, file)
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
            except Exception as e:
                print(f"❌ falha ao ler {caminho}: {e}")
                continue

            if nome_base not in documentos:
                documentos[nome_base] = {}

            documentos[nome_base][tipo] = conteudo

    return documentos

