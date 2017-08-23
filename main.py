from networkx import *
import pandas

# Abre o CSV
df = pandas.read_csv("Ano-2017.csv", sep = ";", header = 0)

# Mantém apenas as colunas descritas como argumento
df = df[['NomeParlamentar','CNPJCPF','sgUF','vlrDocumento','Fornecedor']]

#Separa apenas os deputados da PB
df = df[df['sgUF']== 'PB']

#Converte a coluna de valores pra float
df['vlrDocumento'] = df['vlrDocumento'].astype(float)

#Remoção da notação científica da coluna de CNPJ/CPF
df['CNPJCPF'] = (df['CNPJCPF'].map(lambda x: '{:.0f}'.format(x)))

#Agrupa os valores por Nome do Parlamentar e do Fornecedor

df = df.groupby(['NomeParlamentar', 'CNPJCPF'])['vlrDocumento'].sum()

#Converte o groupby novamente pra DataFrame
df = pandas.DataFrame(df)

#Exporta o resultado
df.to_csv(path_or_buf='resultado.csv', sep=';', header=True)

#Advinha
print(df)