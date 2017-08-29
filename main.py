import urllib
from bs4 import BeautifulSoup
from networkx import *
import pandas
from unicodedata import normalize
import matplotlib.pyplot as plt

# Dados para filtragem
uf = 'PB'

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

# Abre o CSV
df_cota = pandas.read_csv("cota/Ano-2016.csv", sep=";", decimal=',', header=0)

# Separa apenas os deputados da PB
df_cota = df_cota[df_cota['sgUF'] == uf]

# Remove os valores nulos (sem CNPJ/CPF ou sem valor)
df_cota = df_cota[df_cota.txtCNPJCPF.notnull()]
df_cota = df_cota[df_cota.vlrLiquido.notnull()]

# Remove a notação científica do CNPJ/CPF
df_cota['txtCNPJCPF'] = (df_cota['txtCNPJCPF'].map(lambda x: '{:.0f}'.format(x)))

df_cota_resumo = df_cota.groupby(["txNomeParlamentar", "sgPartido", "sgUF", "txtCNPJCPF", "txtFornecedor"]).agg(
    {"vlrLiquido": ["sum", "count"]}).reset_index()

# Advinha
print(df_cota_resumo)

# Criando grafo completo
G = nx.from_pandas_dataframe(df_cota, "txNomeParlamentar", 'txtCNPJCPF', create_using=nx.DiGraph())

# Desenha o grafo :D
nx.draw(G, style="solid", with_labels=True, width=list(df_cota['vlrLiquido'] / 8000), arrows=True)

# Mostra o grafo
plt.show()
