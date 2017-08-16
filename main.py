from networkx import *
import pandas

df = pandas.read_csv("Ano-2017.csv", sep = ";", header = 0)
df = df[df['sgUF'] == 'PB']
print (df)