import pandas as pd
import numpy as np
import joblib

class DataProcessor:
    def __init__(self, dados):
        self.dados = dados
        self.svm = joblib.load('modelo\svc_model.pkl')
        self.scaler = joblib.load('modelo\scaler.pkl')
        self.pca = joblib.load('modelo\pca.pkl')
        colunas = list(self.dados.columns)
        if 'IAA' in colunas:
            if 'IEG' in colunas:
                if 'IPS' in colunas:
                    if 'IDA' in colunas:
                        if 'IAN' in colunas:
                            if 'INDE' in colunas:
                                self.dados = self.dados[['Codigo Aluno', 'IAA', 'IEG', 'IPS', 'IDA', 'IAN', 'INDE']]
                                self.dados.rename(columns={'INDE': 'Development_Index'}, inplace = True)
                                self.dados.set_index('Codigo Aluno', inplace=True)
                            else:
                                self.dados = "Colunas da planilha modelo não encontrada"
                        else:
                            self.dados = "Colunas da planilha modelo não encontrada"
                    else:
                        self.dados = "Colunas da planilha modelo não encontrada"
                else:
                    self.dados = "Colunas da planilha modelo não encontrada"
            else:
                self.dados = "Colunas da planilha modelo não encontrada"
        else:
            self.dados = "Colunas da planilha modelo não encontrada"
    
    def predict(self):
        X_predict = self.dados

        X_predict_scaled = self.scaler.transform(X_predict)

        X_predict_pca = self.pca.transform(X_predict_scaled)

        y_predict_final = self.svm.predict(X_predict_pca)
        #self.dados = y_predict_final
        y_predict_proba = self.svm.predict_proba(X_predict_pca)
        positive_probabilities = np.round(y_predict_proba[:, 1], 2)
        negative_probabilities = np.round(y_predict_proba[:, 0], 2)
        with pd.option_context('mode.chained_assignment', None):
            self.dados.loc[self.dados.index, 'Positive_Probability'] = positive_probabilities
            self.dados.loc[self.dados.index, 'Negative_Probability'] = negative_probabilities
            self.dados.loc[self.dados.index, 'Predict_Turning_Point'] = np.where(positive_probabilities > negative_probabilities, 'Sim', 'Não')