from networkx import *
import pandas

df = pandas.read_csv("Ano-2017.csv", sep = ";", header = 0)
df = df[['NomeParlamentar','sgUF','vlrDocumento','Fornecedor']]
df = df[df['sgUF']== 'PB']
df = df.groupby(['NomeParlamentar', 'Fornecedor'])['vlrDocumento'].sum(axis= 1, numeric_only = True)
print(df)