# -*- coding: utf-8 -*-

"""

==========================================
            ERRO NA ESCRITA
==========================================


Created on Mon Nov  7 15:14:08 2022.

@author: E805511
"""

"""Scrip para rodar no código do Rolling Horizon. 

Lógica:
    lista com os caminhos dos arquivos -> identificar os arquivos de forma genérica
    lista com as vazões -> criando um objeto vazões para cada arquivo
    modelos:
        model = {
            vazoes_avg = {
                posto 6 : objeto com cálculo da correlação e teste da amplitude
                posto 74 : objeto com cálculo 
                posto 169 : objeto com cálculo 
                posto 275 : objeto com cálculo 
                
                }
            vazoes_p10 = {
                posto 6 : objeto com cálculo
                posto 74 : objeto com cálculo 
                posto 169 : objeto com cálculo 
                posto 275 : objeto com cálculo 
                
                }
            vazoes_p25 = {
                posto 6 : objeto com cálculo
                posto 74 : objeto com cálculo 
                posto 169 : objeto com cálculo 
                posto 275 : objeto com cálculo 
                
                }
            .
            .
            .
            
            dataframe: postos X arquivos e valores são os anos
            
   +-------+---------------+----------------+-----+-----+             
    postos |VAZOES-AVG.txt | VAZOES-P10.txt	| ... | ... |
    6	   |1949-04	       |2005-04	        | ... | ... |
    74	   |1960-04	       |1985-04	        | ... | ... |
    169	   |1978-04	       |1966-04	        | ... | ... |
    275	   |1977-04	       |1963-04	        | ... | ... |
   +-------+---------------+----------------+-----+-----+
            
            }

"""

#----------------------------------------------------------
import os
import os.path
import sys
from pathlib import Path
import pandas as pd
#módulos internos
from vazoes_txt import VazoesTxt
from modelo_camila import ModeloCamila
#Verificação do arquivo

folderpath = Path(__file__).parent

if (folder := str(folderpath)) not in sys.path:
    sys.path.append(folder)
#----------------------------------------------------------


# Postos principais
POSTOS_PRINCIPAIS = {
    6: 'FURNAS',
    74: 'GBM',
    169: 'SOBRADINHO',
    275: 'TUCURUÍ',
    }

#----------------------------------------------------------
"""MODIFICAR COM AS SUGESTÕES - YANASE"""
#Começa aqui

folderpath = r'C:/Workspace/cenarios_por_correlacao_de_vazoes/Arquivos_de_vazões_NEWAVE'
arquivo_new = r'C:/Workspace/cenarios_por_correlacao_de_vazoes/teste_arquivos_saida'

#diretorio = str(input(Path(r'Digite o diretório: ')))

#Modificando o getcwd() para o diretório
#os.chdir(folderpath)

#Cria uma pasta para os cenários resultante de vazões
#Error se o arquivo existir FileExistsError
#Pular esse warning e atráves so try?
# pasta_saida = 'arquivos_saida_vazoes'
# #exist_ok ignora o FileExistsError: [WinError 183] Não é possível criar um arquivo já existente
# os.makedirs(pasta_saida, exist_ok=True)

lista_caminhos = []
lista_caminhos_nomes = []

#Identifica os arquivos de vazões na pasta
for diretorio, subpastas, arquivos in os.walk(folderpath):
    for nome_arquivo_vazoes in arquivos:
        caminho = os.path.join(os.path.realpath(diretorio), nome_arquivo_vazoes)
        # Criação de uma lista com o caminho de todos os arquivos contidos na pasta
        lista_caminhos.append(caminho)
        lista_caminhos_nomes.append(nome_arquivo_vazoes)


#Gera uma lista com o objeto vazões para cada arquivo
lista_vazoes = []
for path_vazoes in lista_caminhos:    
    vazoes = VazoesTxt(path_vazoes)
    lista_vazoes.append(vazoes)



#PRÓXIMO ETAPA
#a partir do objeto vazões gerar mais 4 objetos para calcular a correlação
#e teste da amplitude

#-----------------------------------------------------------------
lista_postos = list(POSTOS_PRINCIPAIS.keys())
lista_nomes = list(POSTOS_PRINCIPAIS.values())

#lista preferente ao Modelos
modelos = []
#Lista de VAzões preenchidas
modelos_preenchido = []

#faz o cálculo da correlação e teste da amplitude para os postos principais
#para todos os arquivos
#e preenche com a previsão extendida, retornando 20 arquivos

for idx, objeto_vazoes in enumerate(lista_vazoes):
    for posto in lista_postos:
        model = ModeloCamila(coluna=posto, posicao=1)
        model.fit(lista_vazoes[idx].df_period)
        modelos.append(model)
        #Parametrização do modelo
        #Predição para um novo período
        novo_trecho = model.predict()

        # Junção do período do arquivo com o período previsto
        vazoes_new = vazoes.add_novo_periodo(novo_trecho)
        modelos_preenchido.append(vazoes_new)
        # Junção do período do arquivo com o período previsto
        vazoes_new = vazoes.add_novo_periodo(novo_trecho)
        # Salva novo arquivo de vazões no formato txt
        
        vazoes_new.salvar_txt(arquivo_new)
        
#%%
ano_das_correlacoes = []
postos = []

#ano correspondente à correlação
# for i, ano in enumerate(modelos):
#     ano_das_correlacoes.append(modelos[i].mes_final_periodo_)
#     postos.append(modelos[i].coluna)
    


# df_teste_anos = pd.DataFrame(data=ano_das_correlacoes,
#                              index=postos
#                              )
        
# df_teste_anos.index.name = 'postos'
# df_teste_anos.columns = ['anos']
# df_teste_anos["anos"] = pd.DatetimeIndex(pd.to_datetime(df_teste_anos["anos"], format="%Y-%m")).year
# #dataframe com a relação dos postos, arquivos e anos da correlação
# df_relacao_anos = df_teste_anos.groupby(level=0).agg(list)["anos"].apply(pd.Series)
# df_relacao_anos.columns = lista_caminhos_nomes

#Verificação de repetições dos anos em relação ao arquivo e ao posto
# df_verifica_anos = df_relacao_anos.copy()
#df_verifica_anos = df_verifica_anos.nunique()
#df_verifica_anos = df_verifica_anos[df_verifica_anos < 4]
#df_verifica_colunas_duplicadas = df_verifica_anos.iteritems()


#Filtrando os dados
# df[df.duplicated('Column Name', keep=False) == True]
# df.groupby([...]).filter(lambda df:df.shape[0] > 1)
# df.groupby([...], group_keys=False).apply(lambda df:df if df.shape[0] > 1 else None)
# df.drop_duplicates(subset=[df.columns[0:2]], keep = False)



