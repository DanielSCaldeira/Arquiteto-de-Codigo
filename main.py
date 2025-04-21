import os
from dotenv import load_dotenv
from assitente import carregar_arquivos_organizado
from azure_api import baixar_repositorios as baixar_azure 
from github_api import baixar_repositorio_github as baixar_github
from analyzer import analisar_codigo
from doc_generator import gerar_documentacao
from crud_generator import gerar_crud
from organizar_dados import agrupar_arquivos_por_tabela, agrupar_dados_com_sql, listar_arquivos_por_pasta, remover_estranho_visivel_dos_xml
import ollama 

load_dotenv()  # Carrega variáveis do .env

ORIGEM = os.getenv("CODIGO_ORIGEM", "Azure").lower()  # Pode ser "azure" ou "github"

if __name__ == "__main__":
    if ORIGEM == "azure":
        # print("🔁 Acessando repositório Azure...")
        # arquivos = baixar_azure()
        # remover_estranho_visivel_dos_xml()
        # nomes_entidades  = listar_arquivos_por_pasta()
        # dados = agrupar_dados_com_sql(nomes_entidades)
        docs = carregar_arquivos_organizado()
        # Define o modelo que você quer usar (instale antes com: `ollama run llama3` por exemplo)
        print("⏳ Enviando arquivos para o modelo...")

        client = ollama()
        modelo = "ollama"
        system_msg = {"role": "system", "content": "Você é um assistente que entende a estrutura de projetos C#."}

        # 1) Enviar cada bloco de código sem esperar resposta
        for entidade, tipos in docs.items():
            ingest_msg = {
                    "role": "user",
                    "content": f"[INGESTÃO] Inserindo dados da entidade `{entidade}` no contexto."
                }

            data_msg = f"## Entidade: {entidade}\n"
            for tipo, corpo in tipos.items():
                data_msg += f"\n### {tipo}\n{corpo}\n"

            ollama.chat(model=modelo, messages=[system_msg, ingest_msg, data_msg])

        # 2) Depois de “alimentar” o contexto, faz a pergunta final
        resposta = ollama.chat(model=modelo, messages=[
            system_msg,
            {"role": "user", "content": "Quais entidades você consegue identificar nesse projeto e como elas se relacionam?"}
        ])

        print(resposta["message"]["content"])



            
            

    else:
        owner = os.getenv("GITHUB_OWNER")
        repo = os.getenv("GITHUB_REPO")
        print(f"🔁 Acessando repositório GitHub {owner}/{repo}...")
        arquivos = baixar_github(owner, repo)


