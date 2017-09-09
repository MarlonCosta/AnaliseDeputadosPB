import pandas
import os

lista_csv = []

for file in os.listdir('cota'):
    df_cota = pandas.read_csv("cota/"+file, sep=";", decimal=',', header=0)
    lista_csv.append(df_cota)


resultado = pandas.concat(lista_csv)


