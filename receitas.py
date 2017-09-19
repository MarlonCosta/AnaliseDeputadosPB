import urllib
from unicodedata import normalize

import pandas
from bs4 import BeautifulSoup

lista_csv = []
import os

page = urllib.request.urlopen(
    "http://www.camara.leg.br/SitCamaraWS/Deputados.asmx/ObterDeputados")  # link com os dados básicos dos deputados
soup = BeautifulSoup(page, "lxml")
lista_dados_deputados = soup.find_all("deputado")


def remover_acentos(txt):
    return normalize("NFKD", txt).encode("ASCII", "ignore").decode("ASCII")


deputados_dict = {}
for i in range(0, len(lista_dados_deputados)):
    deputados_dict[lista_dados_deputados[i].idecadastro.string] = [
        remover_acentos(lista_dados_deputados[i].nome.string), lista_dados_deputados[i].urlfoto.string]


def nome_completo(x):
    if str(int(x)) in list(deputados_dict.keys()):
        y = deputados_dict[str(int(x))][0]
    else:
        y = "sem_info"
    return y


df_cota = pandas.DataFrame()
for file in sorted(os.listdir('cota')):
    if file.startswith("Ano-"):
        print("Carregando: " + file)
        df_cota = pandas.read_csv("cota/" + file, sep=";", decimal=',', header=0,
                                  dtype={'txtCNPJCPF': str, 'idecastastro': int, 'txNomeParlamentar': str,
                                         'vlrRestituicao': str,
                                         'txtDescricaoEspecificacao': str})
        lista_csv.append(df_cota)
    df_cota = pandas.DataFrame(pandas.concat(lista_csv))

df_cota = df_cota[df_cota.idecadastro.notnull()]
df_cota["txNomeParlamentar"] = df_cota["idecadastro"].map(nome_completo)
df_cota = df_cota[df_cota["txNomeParlamentar"] != "sem_info"]
