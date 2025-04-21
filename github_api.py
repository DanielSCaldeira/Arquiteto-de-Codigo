import os
import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_PAT = os.getenv("GITHUB_PAT")

def baixar_repositorio_github(owner, repo):
    headers = {"Authorization": f"token {GITHUB_PAT}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    response = requests.get(url, headers=headers)
    arquivos = [item["path"] for item in response.json() if item["name"].endswith(('.cs', '.md', '.json'))]
    return arquivos
