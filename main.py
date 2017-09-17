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
    uf = input("Estado: ")
    if uf not in estados and uf != "":
        print("UF inexistente")
        continue
    else:
        break
while True:
    try:
        ano = input("Ano: ")
    except ValueError:
        print("Digite um NÚMERO entre 2013 e 2017")
    if ano == "":
        break
    if int(ano) < 2013 or int(ano) > 2017:
        print("O ano deve estar entre 2013 e 2017")
        continue
    else:
        break

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

# Remove a notação científica do CNPJ/CPF
df_cota['txtCNPJCPF'] = df_cota['txtCNPJCPF'].str.replace(',', '.')
df_cota['txtCNPJCPF'] = df_cota['txtCNPJCPF'].astype(float)
df_cota['txtCNPJCPF'] = (df_cota['txtCNPJCPF'].map(lambda x: '{:.0f}'.format(x)))

# Resume os dados
df_cota['vlrLiquido'] = df_cota['vlrLiquido'].astype(float)
df_cota_resumo = pandas.DataFrame(
    df_cota.groupby(["txNomeParlamentar", "sgUF", "sgPartido", "txtCNPJCPF"]).agg(
        {"vlrLiquido": "sum"}).reset_index())

# Salva um CSV com os dados que foram filtrados
df_cota_resumo.to_csv(path_or_buf=("resumos/resumo_%s_%s_%s.csv" % (deputado, uf, ano)), sep=";", decimal=",")

# Advinha :D
print(df_cota_resumo)

# Criando grafo completo
G = nx.from_pandas_dataframe(df_cota_resumo, "txNomeParlamentar", "txtCNPJCPF", create_using=nx.DiGraph())

# Desenha o grafo :D
nx.draw(G, style="solid", with_labels=True, width=list(df_cota.vlrLiquido / 8000), arrows=True)

# Mostra o grafo
plt.show()
