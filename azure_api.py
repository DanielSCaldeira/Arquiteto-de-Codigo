import os
import requests
from dotenv import load_dotenv

load_dotenv()

ORG_URL = os.getenv("AZURE_ORG_URL")  # Ex: https://dev.azure.com/SistemasFuncef/
PROJECT = os.getenv("AZURE_PROJECT")  # Ex: PortalFinanceiro
PAT = os.getenv("AZURE_PAT")

BRANCH = "development"

def listar_arquivos_recursivamente(repo_id, caminho="/"):
    arquivos = []

    items_url = (
        f"{ORG_URL}{PROJECT}/_apis/git/repositories/{repo_id}/items"
        f"?recursionLevel=OneLevel&scopePath={caminho}"
        f"&versionDescriptor.version={BRANCH}&versionDescriptor.versionType=branch"
        f"&includeContentMetadata=true&api-version=7.0"
    )

    response = requests.get(items_url, auth=('', PAT))
    if response.status_code != 200:
        return arquivos

    
    items = response.json().get("value", [])
    for item in items:
        path = item.get("path", "")
        is_folder = item.get("isFolder", True)
        print(f"🔍 Buscando arquivos no repositório: {path}...")

        if is_folder:
            arquivos.extend(listar_arquivos_recursivamente(repo_id, path))
        elif path.endswith(('.cs', '.md', '.xml')):
            arquivos.append({
                "repo": repo_id,
                "path": path,
                "url": item.get("url")
            })
    return arquivos


def baixar_repositorio():
    url = f"{ORG_URL}{PROJECT}/_apis/git/repositories?api-version=7.0"
    response = requests.get(url, auth=('', PAT))
    response.raise_for_status()
    repos = response.json().get("value", [])

    arquivos = []
    for repo in repos:
        repo_id = repo.get("id")
        repo_name = repo.get("name")
        print(f"🔍 Buscando arquivos no repositório: {repo_name}...")

        if not repo_id:
            continue

        arquivos.extend(listar_arquivos_recursivamente(repo_id))

    return arquivos
