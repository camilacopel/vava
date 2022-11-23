# -*- coding: utf-8 -*-
"""Em desenvolvimento."""

from typing import Optional

import numpy as np
import pandas as pd
from modelos import calc_corr_last12
from collections import Counter


class ModeloCamila:
    
    def __init__(self):
        """ Criação do modelo.

        Parameters
        ----------
        posto : int
            Coluna a ser usada para ordenação das maiores correlações.
        posicao : int, optional
            Posição na ordenação de maiores correlações.
            O default é a usar a primeira posição (1).

        """
        
        
        #definição dos postos principais
        self.postos_principais = {
            6: 'FURNAS',
            74: 'GBM',
            169: 'SOBRADINHO',
            275: 'TUCURUÍ'
        }
            
        
        self.posicao = 1
        
        # Atributos que serão definidos apenas ao realizar o fit
        self.df_base = None
        self.df_correlacao = None
        self._period_ = None
        self.correlacao_ = list()
        #self.correlacao_outros_ = list()
        self.mes_final_periodo_ = None
        self.anos_ = list()


    def fit(self, df_base: pd.DataFrame,
            anos_proibidos:list) -> 'ModeloCamila':
        """
        Cálculo das correlações e verificação do Teste de Amplitude.

        O teste consiste em verificar se a relação da previsão está em intervalo
        entre o valor máximo e o mínimo da relação das vazôes do histórico.
        
        
        Parameters
        ----------
        df_base : DataFrame
            Dados históricos para cálculo das correlações.
            
        Return
        ----------
            O próprio objeto: self.

        """
        self.df_base = df_base.copy()
        #Realiza o cálculo da correlação
        self.df_correlacao = calc_corr_last12(df_base)
        
        #Ranking das correlações dos postos principais
        self._ranking_corr_principais = list()
        
        #lista com ranking das correlações dos principais postos
        for coluna in self.postos_principais.keys():
            ranking_corr = self.df_correlacao[coluna].sort_values(ascending=False)
            self._ranking_corr_principais.append(ranking_corr)    
            
        
        #Armazena a informação dos anos dos arquivos
        #Counter é um contêiner que armazena elementos e suas contagens em dict
        _counter_ = Counter()
        for anos in anos_proibidos:
            _counter_.update(anos)
        

        #A maior correlação
        FIRST_RANK_CORR = 1
        #número arbitário, mas que seja entre 10 e 25.
        #escolhendo uma correlação alta, mas que passe pelos testes
        POSICAO_LIMITE_RANK_CORR = 20
        
        
        
        for corr_postos in self._ranking_corr_principais:
            
            for posicao_atual in range(FIRST_RANK_CORR, POSICAO_LIMITE_RANK_CORR):      
                
                #TESTE DA AMPLITUDE INICIA AQUI
                # Dados que serão usados para previsão
                self._period_ = corr_postos.index[posicao_atual]
                #Para selecionar o primeiro mês da previsão extendida
                mes_escolhido_ini = self._period_ + 1       
                #série com os dados do primeiro mês da previsão extendida
                series_proximo_mes = self.df_base.loc[mes_escolhido_ini]
                
                #Renomeando index para ano e mes da previsão extendida
                series_proximo_mes.name = self.df_base.index[-1] + 1
                
                
                #Acrescentando o primeiro mês da previsão extendida nos dados originais
                df_base_modif = pd.concat([self.df_base, series_proximo_mes.to_frame().T])
                
                #Cálculo da razão
                #Dividindo a vazão dos meses pelo seu mês posterior
                df_razao = df_base_modif.shift(1) / df_base_modif
                #substitui os valores NaN e infinito por zero
                df_razao.replace([np.inf, np.nan], 0, inplace=True)
                #Identifica o mês para aplicar o teste da amplitude e retorna para todos os anos
                #O mês selecionado é o que inicia a previsão
                df_razao = df_razao[df_razao.index.month == mes_escolhido_ini.month]
                #Razão da vazao da previsaõ da Refinitiv pelo primeiro mês da vazão extendida
                df_razao_previsao = df_razao.iloc[-1, :]
                #Valor máximo do histórico, excluindo a previsão da Refinitiv
                df_razao_maximo = df_razao.iloc[:-1, :].max()
                #Valor da razão mínima do histórico
                df_razao_minima = df_razao.iloc[:-1, :].min()
            
                
                #Variáveis que guardam quais foram as usinas que não passaram no teste
                teste_amplitude_max = df_razao_previsao[df_razao_previsao >= df_razao_maximo]
                teste_amplitude_min = df_razao_previsao[df_razao_previsao <= df_razao_minima]
                
                #Verifica se a usina de referência consta nas variáveis das usinas que falharam
                teste_da_amplitude = (ranking_corr.name in teste_amplitude_max.index.to_list() or
                                      ranking_corr.name in teste_amplitude_min.index.to_list())
                
                
                
                
                #anos que passaram no teste da amplitude
                if teste_da_amplitude is False:
                    
                    #TESTE QUE EVITA REPETIÇÃO DOS ANOS
                    #verifica se o ano foi usado anterior no mesmo arquivo ou nos outros arquivos
                    #se sim, utiliza o próximo ano do ranking
                    if self._period_.year in _counter_.keys():
                        continue
                    
                    
                    else:
                        #caso o ano não tenha sido usado
                        self.posicao = posicao_atual
                        
                        # Outras informações sobre o modelo 'treinado'
                        # Usando sufixo _ semelhante ao scikit-learn
                        self.anos_.append(self._period_.year)
                        self.correlacao_.append(corr_postos.iloc[self.posicao])
                        
                        """verificar se realmente há necessidade dessa informação"""
                        #self.correlacao_outros_.append(self.df_correlacao.loc[corr_postos.index[self.posicao]])
                        break
                    
                    
           
        """modificar aqui.
            porque pega apenas o último ano do último arquivo.
        """
        #self.mes_final_periodo_ = self._period_.strftime('%Y-%m')


        return self


    def predict(self,
                num_meses: Optional[int] = None,
                ) -> pd.DataFrame:
        """
        Previsão para os próximos 'num_meses'.

        Parameters
        ----------
        num_meses : int, optional
            Número de meses a serem previstos.
            Se não informado será feita a previsão até final do último ano informado.

        Returns
        -------
        DataFrame
            Previsão para os próximos meses.

        """
        #Caso não tenha rodado o fit a lista self.anos_ estará vazia
        try:
            # Não havendo erro supomos que o fit foi realizado
            
            len(self.anos_) != 0
            
            
        except TypeError:
            # Podemos futuramente usar o erro sklearn.exceptions.NotFittedError,
            # mas para simplificar:
            raise Exception("Realizar o fit do modelo antes") from None

        
        # Primeiro mês a ser previsto
        next_month = self.df_base.index[-1] + 1

        # Se num_meses não for informado vai o final do ano
        #num_meses = num_meses if num_meses else (13 - mes_escolhido_ini.month)
        num_meses = num_meses if num_meses else (13 - next_month.month)
        
        #lista de dataframes com os trechos selecionados para preencher
        #dados da previsão extendida
        self.list_trecho_escolhido = list()
        for anos in self.anos_:
        
            # Mês seguinte ao período selecionado pelo modelo
            mes_escolhido_ini = pd.Period(year=anos, month=next_month.month, freq='M')
            # Dados do período escolhido
            df_escolhido = self.df_base.loc[mes_escolhido_ini:].iloc[:num_meses]

            # Ajusta o index para o novo período
            df_trecho_ajust = df_escolhido.copy()
            df_trecho_ajust.index = pd.period_range(next_month,
                                                    periods=len(df_trecho_ajust),
                                                    freq='M')
            
            self.list_trecho_escolhido.append(df_trecho_ajust)
            
        return self.list_trecho_escolhido

    
    def salvar_txt(self):
        
        #Retorna uma lista com nome das usinas
        nome_postos = self.postos_principais.values()
        #Convertendo os anos em strings para concontenar no nome
        #dos novos arquivos criados
        anos_string = list(map(str, self.anos_))
        
        
        
        
        
        pass
