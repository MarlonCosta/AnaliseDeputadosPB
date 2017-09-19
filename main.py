import urllib
from bs4 import BeautifulSoup
from networkx import *
import pandas
from unicodedata import normalize
import matplotlib.pyplot as plt
import os
import sys
from difflib import SequenceMatcher


def BSS(string, deputados):
    string = string.upper()
    sugestoes = []
    if string in deputados:
        return [string]
    for deputado in deputados:
        if SequenceMatcher(deputado, string).ratio() > 0.7:
            sugestoes.append(deputado)
        for nome in [nome for nome in string.split(" ") if len(nome) > 3]:
            for palavra in deputado.split(" "):
                if SequenceMatcher(lambda x: x in " ", a=palavra, b=nome).ratio() > 0.8:
                    sugestoes.append(deputado)

    return set(sugestoes)


# Dados para filtragem

estados = ['PB', 'PE', 'RN', 'BA', 'CE', 'PI', 'AL', 'MA', 'SE', 'MG', 'ES', 'SP', 'RJ', 'SC',
           'PR', 'RS', 'MT', 'MS', 'DF', 'GO', 'AM', 'PA', 'RO', 'RR', 'AC', 'AP']

print("Preencha os campos a seguir para filtrar a busca.\n"
      "Para escolher todos em qualquer campo, basta deixá-lo em branco.")
deputado = input("Deputado(a): ")

while True:
    uf = input("Estado: ").upper()
    if uf not in estados and uf != "":
        print("UF inexistente")
        continue
    else:
        break
while True:
    try:
        ano = input("Ano: ")
    except ValueError:
        print("Digite um NÚMERO entre 2009 e 2017")
    if ano == "":
        break
    if int(ano) < 2009 or int(ano) > 2017:
        print("O ano deve estar entre 2013 e 2017")
        continue
    else:
        break

# Concatena os CSVs contidos na pasta 'cota'
lista_csv = []
df_cota = pandas.DataFrame()
print("Buscando arquivos na pasta \'cota\'...")
if not os.listdir('cota'):
    print("Diretório vazio")
    sys.exit(1)

if ano:
    if "Ano-" + ano + ".csv" in os.listdir('cota'):
        file = "Ano-" + ano + ".csv"
        print("Carregando: " + file)
        df_cota = pandas.read_csv("cota/" + file, sep=";", decimal=',', header=0,
                                  dtype={'txtCNPJCPF': str, 'txNomeParlamentar': str, 'vlrRestituicao': str,
                                         'txtDescricaoEspecificacao': str})
else:
    for file in sorted(os.listdir('cota')):
        if file.startswith("Ano-"):
            print("Carregando: " + file)
            df_cota = pandas.read_csv("cota/" + file, sep=";", decimal=',', header=0,
                                      dtype={'txtCNPJCPF': str, 'txNomeParlamentar': str, 'vlrRestituicao': str,
                                             'txtDescricaoEspecificacao': str})
            lista_csv.append(df_cota)
    df_cota = pandas.DataFrame(pandas.concat(lista_csv))

df_receitas = pandas.read_csv(
    "receitas_candidatos_2014_brasil.csv", sep=';', decimal=',',
    encoding='latin-1')  # csv baixado em http://www.tse.jus.br/eleicoes/estatisticas/repositorio-de-dados-eleitorais
df_receitas = df_receitas[df_receitas["Cargo"] == "Deputado Federal"]  # somente deputados federais

# Separa apenas os deputados da UF desejada
if uf:
    df_cota = df_cota[df_cota['sgUF'] == uf]

# Isola o deputado desejado
if deputado:
    if deputado not in df_cota.txNomeParlamentar.unique():
        print("\nDeputado(a) %s não encontrado, escolha uma sugestão abaixo (digite o número): " % deputado)
        sugestoes = [sug for sug in BSS(deputado, df_cota.txNomeParlamentar.unique().astype(str))]

        if sugestoes:
            [print("        ", i, sug) for i, sug in enumerate(sugestoes)]
        else:
            print("         Nenhuma sugestão encontada para %s" % deputado)
            sys.exit(0)

        deputado = sugestoes[int(input())]
        print("\nDeputado(a) %s selecionado!\n" % deputado)

    df_cota = df_cota[df_cota['txNomeParlamentar'] == deputado]

if ano:
    df_cota = df_cota[df_cota['numAno'].astype(str) == ano]

# Remove os valores nulos (sem CNPJ/CPF/sem valor/sem nome do palarmentar)
df_cota = df_cota[df_cota.txtCNPJCPF.notnull()]
df_cota = df_cota[df_cota.vlrLiquido.notnull()]
df_cota = df_cota[df_cota.txNomeParlamentar.notnull()]

# # 1.1. Criando dicionário com identificador e nome completo do deputado (será necessário porque a tabela de reembolsos não tem o nome completo, só o apelido)
# page = urllib.request.urlopen(
#     "http://www.camara.leg.br/SitCamaraWS/Deputados.asmx/ObterDeputados")  # link com os dados básicos dos deputados
# soup = BeautifulSoup(page, "lxml")
# lista_dados_deputados = soup.find_all("deputado")
#
#
# def remover_acentos(txt):
#     return normalize("NFKD", txt).encode("ASCII", "ignore").decode("ASCII")
#
#
# deputados_dict = {}
# for i in range(0, len(lista_dados_deputados)):
#     deputados_dict[lista_dados_deputados[i].idecadastro.string] = [
#         remover_acentos(lista_dados_deputados[i].nome.string), lista_dados_deputados[i].urlfoto.string]
#
# df_receitas["Nome candidato"] = df_receitas["Nome candidato"].map(remover_acentos)
#
#
# def nome_completo(x):
#     if str(int(x)) in list(deputados_dict.keys()):
#         y = deputados_dict[str(int(x))][0]
#     else:
#         y = "sem_info"
#     return y


df_cota = df_cota[df_cota.idecadastro.notnull()]
df_cota["txNomeParlamentar"] = df_cota["idecadastro"].map(nome_completo)
df_cota = df_cota[df_cota["txNomeParlamentar"] != "sem_info"]

# Remove a notação científica do CNPJ/CPF
df_cota['txtCNPJCPF'] = df_cota['txtCNPJCPF'].str.replace(',', '.')
df_cota['txtCNPJCPF'] = df_cota['txtCNPJCPF'].astype(float)
df_cota['txtCNPJCPF'] = (df_cota['txtCNPJCPF'].map(lambda x: '{:.0f}'.format(x)))

# Resume os dados
df_cota['vlrLiquido'] = df_cota['vlrLiquido'].astype(float)
df_cota_resumo = pandas.DataFrame(
    df_cota.groupby(["txNomeParlamentar", "sgUF", "sgPartido", "txtCNPJCPF"]).agg(
        {"vlrLiquido": "sum"}).reset_index())

df_receitas_resumo = pandas.DataFrame(
    df_receitas.groupby(["Nome candidato", "UF", "Sigla  Partido", "CPF/CNPJ do doador"]).agg(
        {"Valor receita": "sum"}).reset_index())

df_ciclos = pandas.DataFrame(pandas.concat([df_cota_resumo["txNomeParlamentar", "txtCNPJCPF", "vlrLiquido"],
                                            df_receitas["CNPJ Prestador Conta", "Nome candidato"]]))

# Salva um CSV com os dados que foram filtrados
# df_cota_resumo.to_csv(path_or_buf=("resumos/resumo_reemb_%s_%s_%s.csv" % (deputado, uf, ano)), sep=";", decimal=",")
df_receitas.to_csv(path_or_buf=("resumos/resumo_doacoes_%s_%s_%s.csv" % (deputado, uf, ano)), sep=";", decimal=",")

# Advinha :D
# print(df_cota_resumo)
print(df_receitas_resumo)

# Criando grafo completo
# G = nx.from_pandas_dataframe(df_cota_resumo, "txNomeParlamentar", "txtCNPJCPF", create_using=nx.DiGraph())
GG = nx.from_pandas_dataframe(df_cota_resumo, "CPF/CNPJ do doador", "Nome candidato", create_using=nx.DiGraph())
# Desenha o grafo :D
nx.draw(GG, style="solid", with_labels=True, width=list(df_cota.vlrLiquido / 8000), arrows=True)

# Mostra o grafo
plt.show()

# nx.draw(G, style="solid", with_labels=True, width=list(df_cota.vlrLiquido / 2000), arrows=True)

# Mostra o grafo
plt.show()
