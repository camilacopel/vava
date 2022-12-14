# -*- coding: utf-8 -*-
"""Em desenvolvimento."""

from modelos import calc_corr_last12
import pandas as pd
from typing import Optional
import numpy as np

class ModeloCamila:
    """
    Classe que representa o um modelo de correlações simples e Teste da amplitude.

    Attributes
    ----------
    coluna : int
        Coluna referência para a escolha da <posicao> maior correlação.
    posicao : int
        Posição na ordem de maior correlação relativo à <coluna>.
    df_base : DataFrame
        Base utilizada para o modelo
    df_correlacao_ : DataFrame
        Tabela com a correlação entre os últimos 12 meses e
        estes doze meses em outros anos.
    correlacao_ : float
        Correlação encontrada para <posicao> melhor correlação para <coluna>
    correlacao_outros_ : Series
        Correlação para as outras colunas na <posicao>
    mes_final_periodo_ : str
        'Ano-mes' do perído com a <posicao> melhor correlação para <coluna>
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 coluna: int,
                 posicao: int = 1,
                 ignore_step_corr: bool = True):
        """
        Criação do modelo.

        Parameters
        ----------
        coluna : int
            Coluna a ser usada para ordenação das maiores correlações.
        posicao : int, optional
            Posição na ordenação de maiores correlações.
            O default é a usar a primeira posição (1).

        """
        self.coluna = coluna
        self.posicao = posicao
        self.ignore_step_corr = ignore_step_corr

        # Atributos que serão definidos apenas ao realizar o fit
        self.df_base = None
        self.df_correlacao = None
        self._period_ = None
        self.correlacao_ = None
        self.correlacao_outros_ = None
        self.mes_final_periodo_ = None


    def fit(self, df_base: pd.DataFrame) -> 'ModeloCamila':
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
        #Ranking das correlações
        top_corr = self.df_correlacao[self.coluna].sort_values(ascending=False)
        
        
        #Condições para o realizae o teste da amplitude
        #Substituir as posição no ranking
        #posicao_atual = self.posicao
        
        #ERROR
        #ESTÁ INDO ATÉ A DÉCIMA POSIÇÃO
        for posicao_atual in range(1, 11):
            
            # Dados que serão usados para previsão
            self._period_ = top_corr.index[posicao_atual]
            
            
            #Para selecionar o primeiro mês da previsão extendida
            mes_escolhido_ini = self._period_ + 1        
            #série com os dados do primeiro mês da previsão extendida
            series_proximo_mes = self.df_base.loc[mes_escolhido_ini]
            #Renomeando index
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
            teste_da_amplitude = (self.coluna in teste_amplitude_max.index.to_list() or
                                  self.coluna in teste_amplitude_min.index.to_list())
            
            
            #Se a usina falhar no teste, utiliza a próxima correlação até a décima posição no ranking
            
            # validação_amplitude = []
            # if teste_da_amplitude is True:
            #     validação_amplitude.append(posicao_atual)
            
            
            # if self.ignore_step_corr == False and teste_da_amplitude == True:
            #     continue
            #     #self.ignore_step_corr = True
            if teste_da_amplitude is False:
                self.posicao = posicao_atual
                break
                
                
            
                
            
            self.qualquer_coisa = top_corr.head(11).index
        
        
        # Outras informações sobre o modelo 'treinado'
        # Usando sufixo _ semelhante ao scikit-learn
        self.correlacao_ = top_corr.iloc[self.posicao]
        self.correlacao_outros_ = self.df_correlacao.loc[top_corr.index[self.posicao]]
        self.mes_final_periodo_ = self._period_.strftime('%Y-%m')


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
        # Mês seguinte ao período selecionado pelo modelo
        try:
            # Não havendo erro supomos que o fit foi realizado
            mes_escolhido_ini = self._period_ + 1
        except TypeError:
            # Podemos futuramente usar o erro sklearn.exceptions.NotFittedError,
            # mas para simplificar:
            raise Exception("Realizar o fit do modelo antes") from None

        # Primeiro mês a ser previsto
        next_month = self.df_base.index[-1] + 1

        # Se num_meses não for informado vai o final do ano
        num_meses = num_meses if num_meses else (13 - mes_escolhido_ini.month)

        # Dados do período escolhido
        df_escolhido = self.df_base.loc[mes_escolhido_ini:].iloc[:num_meses]

        # Ajusta o index para o novo período
        df_trecho_ajust = df_escolhido.copy()
        df_trecho_ajust.index = pd.period_range(next_month,
                                                periods=len(df_trecho_ajust),
                                                freq='M')

        return df_trecho_ajust
