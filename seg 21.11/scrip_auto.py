# -*- coding: utf-8 -*-
"""Apenas para testes de funcionamento."""

#%% Ajuste Local
# Manobra inicial para funcionar localmente para testes
import sys
from pathlib import Path
from vazoes_txt import VazoesTxt
from modelo_camila_new import ModeloCamila



folderpath = Path(__file__).parent

if (folder := str(folderpath)) not in sys.path:
    sys.path.append(folder)


#%% Script de testes
# Aqui começa o script para testes



lista_arquivos = list()
lista_modelos = list()
anos_usados = list()
resultados = dict()
#por enquanto uma lista
resultados = list()


#caminho = Path.home()
caminho = r'C:/Workspace/cenarios_por_correlacao_de_vazoes/Arquivos_de_vazões_NEWAVE'


def walk(caminho): 
    for p in Path(caminho).iterdir(): 
        if p.is_dir(): 
            yield from walk(p)
            continue
        yield p.resolve()


# recursively traverse all files from current directory
# the function returns a generator so if you need a list you need to build one

all_files = list(walk(caminho))
lista_vazoes = list()
anos_usados = list()


for arq in all_files:    
    # Criação do objeto de vazões
    vazoes = VazoesTxt(arq)
    lista_vazoes.append(vazoes)
    #posteriormente modificar os parâmetros na classe Vazões
    lista_arquivos.append(vazoes._filepath.stem)

    
for vaz in lista_vazoes:
    # Criação do modelo.
    # O modelo criado está bem simplificado, e estamos tentando seguir o exemplo
    # do scikit-learn, com métodos fit e predict.
    model = ModeloCamila()
    model.fit(vaz.df_period, anos_proibidos=anos_usados)
    lista_modelos.append(model)
    
    
    """verificar com o Yanase método extend"""
    anos_usados.append(model.anos_)
    
    
    """modifiacr aqui"""
    # Predição para um novo período
    resultados.append(model.predict())
    
        
        #anos_usados.extend(model.anos_)
