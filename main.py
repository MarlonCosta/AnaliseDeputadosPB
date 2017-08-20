from networkx import *
import pandas

# Abre o CSV
df = pandas.read_csv("Ano-2017.csv", sep = ";", header = 0)

# Mantém apenas as colunas descritas como argumento
df = df[['NomeParlamentar','sgUF','vlrDocumento','Fornecedor']]

#Separa apenas os deputados da PB
df = df[df['sgUF']== 'PB']

#Agrupa os valores por Nome do Parlamentar e do Fornecedor
df = df.groupby(['NomeParlamentar', 'Fornecedor'])['vlrDocumento'].sum(axis= 1, numeric_only = True)

#Advinha
print(df)