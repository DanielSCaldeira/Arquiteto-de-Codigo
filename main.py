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

        modelo = "mistral"

        historico = [{
            "role": "system",
            "content": (
                "Você é um desenvolvedor especializado em padrões de projeto e criação de novas entidades "
                "com base em um modelo organizacional. Neste projeto, a arquitetura segue a estrutura: "
                "Entidade.mapping.hbm.xml, Entidade.cs, EntidadeService.cs e EntidadeController.cs."
            )
        }]
        # Adiciona os arquivos no histórico
        for entidade, tipos in docs.items():
            conteudo = f"## Entidade: {entidade}\n"
            for tipo, corpo in tipos.items():
                if tipo == "XMLModel": 
                    conteudo += "```XML Nhibenate mapping \n"
                else: 
                    conteudo += f"```csharp \n"
                    
                conteudo += f"\n### {tipo}\n{corpo.strip()}\n"

            historico.append({
                "role": "user",
                "content": f"[INGESTÃO] Inserindo dados da entidade `{entidade}`:\n{conteudo}"
            })
            break;

        # Adiciona a pergunta final
        historico.append({
            "role": "user",
            "content": "Quais são os nomes das entidades que você reconhece nesse projeto com base nos arquivos apresentados?"
        })

        try:
            resposta = ollama.chat(model=modelo, messages=historico)
            print(resposta["message"]["content"])
        except Exception as e:
            import traceback
            print("❌ Erro ao enviar mensagem para o modelo:")
            print(e)
            traceback.print_exc()



            
            

    else:
        owner = os.getenv("GITHUB_OWNER")
        repo = os.getenv("GITHUB_REPO")
        print(f"🔁 Acessando repositório GitHub {owner}/{repo}...")
        arquivos = baixar_github(owner, repo)


