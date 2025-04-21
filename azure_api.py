import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

ORG_URL = os.getenv("AZURE_ORG_URL")  # Ex: https://dev.azure.com/SistemasFuncef/
PROJECT = os.getenv("AZURE_PROJECT")  # Ex: PortalFinanceiro
PAT = os.getenv("AZURE_PAT")
BRANCH = os.getenv("AZURE_BRANCH", "main")  # Padrão: main

# Definindo os padrões de caminho e as extensões desejadas
CAMINHOS_DESEJADOS = {
    "PortalFinanceiro.Service": [".cs"],               # Arquivos .cs dentro de Service
    "PortalFinanceiro.Transport": [".cs"],             # Arquivos .cs dentro de Transport
    "PortalFinanceiro.Api/Controllers": [".cs"],       # Arquivos .cs dentro de Api/Controllers
    "PortalFinanceiro.Model": [".sql", ".cs", "hbm.xml"]       # Arquivos .cs dentro de Model
}

def listar_arquivos_do_repositorio(repo_id, repo_name):
    arquivos = []

    items_url = (
        f"{ORG_URL}{PROJECT}/_apis/git/repositories/{repo_id}/items"
        f"?scopePath=/&recursionLevel=Full"
        f"&versionDescriptor.version={BRANCH}&versionDescriptor.versionType=branch"
        f"&includeContentMetadata=true&api-version=7.0"
    )

    response = requests.get(items_url, auth=('', PAT))
    if response.status_code != 200:
        print(f"❌ Erro ao acessar repositório {repo_name}: {response.status_code}")
        return arquivos

    items = response.json().get("value", [])
    for item in items:
        path = item.get("path", "")
        git_type = item.get("gitObjectType")

        # Verifica se o tipo de objeto é "blob" e se o arquivo corresponde a algum dos padrões desejados
        if git_type == "blob":
            for caminho, extensoes  in CAMINHOS_DESEJADOS.items():               
                for extensao in extensoes:
                    if path.endswith(extensao) and caminho in path:
                        arquivos.append({
                            "repo": repo_name,
                            "path": path,
                            "url": item.get("url")
                        })
            

    return arquivos


def baixar_repositorios():
    url = f"{ORG_URL}{PROJECT}/_apis/git/repositories?api-version=7.0"
    response = requests.get(url, auth=('', PAT))
    response.raise_for_status()

    repos = response.json().get("value", [])
    todos_arquivos = []

    for repo in repos:
        repo_id = repo.get("id")
        repo_name = repo.get("name")
        print(f"📁 Processando repositório: {repo_name}...")

        if not repo_id:
            continue

        arquivos = listar_arquivos_do_repositorio(repo_id, repo_name)
        todos_arquivos.extend(arquivos)

    salvar_arquivos_em_pastas(todos_arquivos)
    return todos_arquivos

def salvar_arquivos_em_pastas(todos_arquivos):
    """Salva os arquivos em pastas específicas conforme o tipo"""
    for arquivo in todos_arquivos:
        path = arquivo["path"]
        url = arquivo["url"]
        nome_arquivo = os.path.basename(path)

        # Determina a pasta com base no caminho
        if "PortalFinanceiro.Api/Controllers" in path:
            pasta_destino = "Controller"
        elif "PortalFinanceiro.Transport" in path:
            pasta_destino = "Transport"
        elif "PortalFinanceiro.Service" in path:
            pasta_destino = "Service"
        elif "PortalFinanceiro.Model" in path and nome_arquivo.endswith("hbm.xml"):
            pasta_destino = "XMLModel"
        elif "PortalFinanceiro.Model" in path and nome_arquivo.endswith(".cs"):
            pasta_destino = "Model"
        elif "PortalFinanceiro.Model" in path and nome_arquivo.endswith(".sql"):
            pasta_destino = "Sql"
        else:
            continue  # Ignora arquivos que não se encaixam nas categorias

        # Cria pasta se não existir
        os.makedirs(pasta_destino, exist_ok=True)

        # Baixa conteúdo
        conteudo = obter_conteudo_arquivo(url)
        if conteudo:
            caminho_completo = os.path.join(pasta_destino, nome_arquivo)

            # Se o arquivo já existir, cria uma versão com contador
            if os.path.exists(caminho_completo) and pasta_destino == "Sql":
                base, ext = os.path.splitext(nome_arquivo)
                contador = 1
                while os.path.exists(caminho_completo):
                    novo_nome = f"{base}_{contador}{ext}"
                    caminho_completo = os.path.join(pasta_destino, novo_nome)
                    contador += 1

            with open(caminho_completo, "w", encoding="utf-8") as f:
                f.write(conteudo)
            print(f"✅ Arquivo salvo em: {caminho_completo}")


def obter_conteudo_arquivo(url):
    """Obtém o conteúdo de um arquivo a partir da URL fornecida"""
    response = requests.get(url, auth=('', PAT))
    if response.status_code == 200:
        return response.text
    else:
        print(f"❌ Erro ao acessar arquivo: {url} ({response.status_code})")
        return None
    

if __name__ == "__main__":
    arquivos_encontrados = baixar_repositorios()
    print(f"\n✅ Total de arquivos encontrados: {len(arquivos_encontrados)}")
    for arq in arquivos_encontrados:
        print(f"- {arq['path']} ({arq['url']})")
