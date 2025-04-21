import os
from dotenv import load_dotenv
from azure_api import baixar_repositorio as baixar_azure
from github_api import baixar_repositorio_github as baixar_github
from analyzer import analisar_codigo
from doc_generator import gerar_documentacao
from crud_generator import gerar_crud

load_dotenv()  # Carrega variáveis do .env

ORIGEM = os.getenv("CODIGO_ORIGEM", "Azure").lower()  # Pode ser "azure" ou "github"

if __name__ == "__main__":
    if ORIGEM == "azure":
        print("🔁 Acessando repositório Azure...")
        arquivos = baixar_azure()
    else:
        owner = os.getenv("GITHUB_OWNER")
        repo = os.getenv("GITHUB_REPO")
        print(f"🔁 Acessando repositório GitHub {owner}/{repo}...")
        arquivos = baixar_github(owner, repo)

    print("📊 Analisando código...")
    analisar_codigo(arquivos)

    print("📚 Gerando documentação...")
    gerar_documentacao(arquivos)

    print("🛠️ Gerando CRUD (exemplo)...")
    gerar_crud("Aluno", ["Id", "Nome", "CursoId"])
