import os
import re
import xml.etree.ElementTree as ET

# Função para extrair o nome da tabela a partir do nome do arquivo
def extrair_nome_tabela(nome_arquivo):
    base = os.path.basename(nome_arquivo)
    
    # Remove sufixos de Controller ou Service, se existirem
    nome = re.sub(r'(Controller|Service|DTO)\.cs$', '', base)
    
    # Remove as extensões e mantém o nome base
    nome = nome.replace(".mapping.hbm.xml", "").replace(".cs", "")
    return nome.lower()

# Função para agrupar os arquivos por tabela
def agrupar_arquivos_por_tabela(arquivos):
    arquivos_por_tabela = {}
    
    for arquivo in arquivos:
        nome_tabela = extrair_nome_tabela(arquivo['path'])
        
        if nome_tabela not in arquivos_por_tabela:
            arquivos_por_tabela[nome_tabela] = {
                'Model': False,
                'XMLModel': False,
                'Service': False,
                'Controller': False,
                'Transport': False
            }
        
        # Verifica em qual pasta o arquivo se encontra e marca como encontrado
    # Verifica em qual pasta o arquivo se encontra e marca como encontrado
        if 'Model' in arquivo['path'] and arquivo['path'].endswith(".cs"):
            arquivos_por_tabela[nome_tabela]['Model'] = True
        elif 'XMLModel' in arquivo['path'] and arquivo['path'].endswith((".hbm.xml", ".xml")):
            arquivos_por_tabela[nome_tabela]['XMLModel'] = True
        elif 'Service' in arquivo['path'] and arquivo['path'].endswith(".cs"):
            arquivos_por_tabela[nome_tabela]['Service'] = True
        elif 'Controller' in arquivo['path'] and arquivo['path'].endswith(".cs"):
            arquivos_por_tabela[nome_tabela]['Controller'] = True
        elif 'Transport' in arquivo['path'] and arquivo['path'].endswith(".cs"):
            arquivos_por_tabela[nome_tabela]['Transport'] = True


    # Filtra apenas as tabelas que possuem todos os arquivos necessários
    tabelas_completas = {
        tabela: arquivos_por_tabela[tabela]
        for tabela, arquivos in arquivos_por_tabela.items()
        if all(arquivos.values())  # Verifica se todas as pastas têm o arquivo
    }
    # Exibindo as tabelas completas (com todos os arquivos)
    for tabela, arquivos in tabelas_completas.items():
        print(f"Tabela: {tabela} - Todos os arquivos presentes.")

    return list(tabelas_completas.keys())

def listar_arquivos_por_pasta(base_dir="./"):
    pastas_alvo = ['Model', 'XMLModel', 'Service', 'Controller', 'Transport']
    arquivos_encontrados = []

    for pasta in pastas_alvo:
        caminho_pasta = os.path.join(base_dir, pasta)
        if os.path.isdir(caminho_pasta):
            for nome_arquivo in os.listdir(caminho_pasta):
                caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
                if os.path.isfile(caminho_arquivo):
                    arquivos_encontrados.append({"path": f"{pasta}/{nome_arquivo}"})

    return agrupar_arquivos_por_tabela(arquivos_encontrados)


def gerar_dataset_para_treinamento(entidades, base_dir="./", output="dataset.txt"):
    with open(output, "w", encoding="utf-8") as f_out:
        for entidade in entidades:
            f_out.write(f"### Pergunta:\n")
            f_out.write(f"Crie um CRUD completo para a entidade `{entidade}`.\n\n")
            f_out.write(f"### Resposta:\n")

            for pasta in ["Model", "XMLModel", "Service", "Controller", "Transport"]:
                nome_arquivo = f"{entidade.capitalize()}"
                if pasta == "XMLModel":
                    arquivo = os.path.join(base_dir, pasta, f"{entidade.lower()}.nhibernate.hbm.xml")
                else:
                    arquivo = os.path.join(base_dir, pasta, f"{entidade}.cs")

                if os.path.exists(arquivo):
                    f_out.write(f"\n// {pasta} - {os.path.basename(arquivo)}\n")
                    with open(arquivo, "r", encoding="utf-8") as f_in:
                        f_out.write(f_in.read())
                        f_out.write("\n")
                else:
                    f_out.write(f"\n// {pasta} - ARQUIVO NÃO ENCONTRADO: {arquivo}\n")

            f_out.write("\n" + "="*80 + "\n\n")

    print(f"✅ Dataset gerado com sucesso em: {output}")


def extrair_nome_tabela_do_xml(entidades):
    """
    Extrai o nome da tabela a partir do arquivo .hbm.xml para cada entidade.
    Retorna um dicionário onde a chave é o nome da entidade e o valor é o nome da tabela.
    """
    tabelas = {}

    for entidade in entidades:
        try:
            caminho_arquivo = f"./XMLModel/{entidade}.mapping.hbm.xml"
                # Verificar se o arquivo existe antes de tentar abrir
            if not os.path.exists(caminho_arquivo):
                print(f"Arquivo não encontrado: {caminho_arquivo}")
                continue  # Pula para a próxima entidade
            tree = ET.parse(caminho_arquivo)
            root = tree.getroot()

            namespace = ""
            if "}" in root.tag:
                namespace = root.tag.split("}")[0] + "}"

            # Encontrar a tag <class> e extrair o nome da entidade (name) e da tabela (table)
            for classe in root.findall(f".//{namespace}class"):
                nome_entidade = classe.get('name')
                nome_tabela = classe.get('table')
                if nome_entidade and nome_tabela:
                    tabelas[nome_entidade] = nome_tabela

        except Exception as e:
            print(f"Erro ao processar o arquivo {entidade}: {e}")

    return tabelas


def buscar_sql_create(nome_tabela, caminho_sql_dir="./Sql"):
    """
    Busca o SQL CREATE TABLE correspondente à tabela no diretório de arquivos SQL.
    Retorna o SQL CREATE TABLE ou None caso não seja encontrado.
    """
    try:
        # Percorrer todos os arquivos SQL no diretório
        for root, dirs, files in os.walk(caminho_sql_dir):
            for file in files:
                if file.endswith(".sql"):
                    caminho_arquivo_sql = os.path.join(root, file)
                    
                    with open(caminho_arquivo_sql, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                        # Procurar pelo comando CREATE TABLE que contenha o nome da tabela
                        match = re.search(rf'CREATE\s+TABLE\s+`?{nome_tabela}`?', conteudo, re.IGNORECASE)
                        
                        if match:
                            return conteudo  # Retorna o conteúdo do arquivo onde a tabela é encontrada
    except Exception as e:
        print(f"Erro ao buscar SQL para a tabela {nome_tabela}: {e}")
    
    return None


def agrupar_dados_com_sql(entidades):
    """
    Função que agrupa os dados de tabela e SQL CREATE Table para cada entidade.
    Retorna um dicionário onde a chave é o nome da entidade e o valor é outro dicionário com a tabela e o SQL CREATE.
    """
    # Primeiro, extrai os nomes das entidades e suas tabelas
    tabelas = extrair_nome_tabela_do_xml(entidades)
    
    dados_completos = {}

    # Para cada entidade, buscamos o SQL CREATE
    for entidade, nome_tabela in tabelas.items():
        sql_create = buscar_sql_create(nome_tabela)
        
        if sql_create:
            dados_completos[entidade] = {
                "tabela": nome_tabela,
                "sql_create": sql_create
            }
        else:
            dados_completos[entidade] = {
                "tabela": nome_tabela,
                "sql_create": "SQL CREATE não encontrado"
            }

    return dados_completos

def remover_estranho_visivel_dos_xml(pasta="./XMLModel"):
    for nome_arquivo in os.listdir(pasta):
        if nome_arquivo.endswith(".hbm.xml"):
            caminho_arquivo = os.path.join(pasta, nome_arquivo)

            try:
                with open(caminho_arquivo, "r", encoding="utf-8") as f:
                    conteudo = f.read()

                # Remove a sequência visível ï»¿
                conteudo_corrigido = conteudo.replace("ï»¿", "")

                with open(caminho_arquivo, "w", encoding="utf-8") as f:
                    f.write(conteudo_corrigido)

                print(f"✔ Sequência ï»¿ removida de: {nome_arquivo}")
            except Exception as e:
                print(f"❌ Erro ao processar {nome_arquivo}: {e}")





