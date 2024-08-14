import streamlit as st
import pandas as pd
from utils import DataProcessor
from io import BytesIO 
from xlsxwriter import Workbook

class StreamlitApp:

    def load_data(self, url):
        """Carrega os dados."""
        return self.data_processor.get_data(url)

    def run(self):
        """Executa o aplicativo."""
        st.title('Passos Mágicos - Datathon - Grupo 54')
        st.title('Simule se haverá o ponto de virada')
        st.subheader('Use a planilha modelo para inserir os dados dos Indicadores para calcularmos quais alunos provavelmente terão seu ponto de virada')
        df = pd.DataFrame(columns = ['Codigo Aluno', 'IAA', 'IEG', 'IPS', 'IDA', 'IAN', 'INDE'])
        excel = to_excel(df)
        col9, col10, col11 = st.columns(3)
        col10.download_button(
            label='Download da planilha modelo de importação',
            data=excel,
            file_name='Modelo.xlsx'
        )

        uploaded_file = st.file_uploader("Selecione ou arraste o arquivo com os valores preenchidos na planilha modelo")
        if uploaded_file is not None:
            dataframe = pd.read_excel(uploaded_file, sheet_name='Sheet1')
            dp = DataProcessor(dataframe)
            dp.predict()
            dados = dp.dados
            dados.rename(
                columns={
                    'Development_Index': 'INDE', 
                    'Positive_Probability': 'Probabilidade_Positiva',
                    'Negative_Probability': 'Probabilidade_Negativa',
                    'Predict_Turning_Point': 'Predição_Ponto_de_Virada'
                }, 
                inplace=True
            )
            st.divider()

            #Cards
            st.title('Resultado Predição')
            col1, col2 = st.columns([1,2])
            col3, col4, col5 = st.columns([1,1,1])
            qtd_alunos = len(dados.index)
            qtd_sim = len(dados[dados["Predição_Ponto_de_Virada"]=="Sim"])
            qtd_nao =len(dados[dados["Predição_Ponto_de_Virada"]=="Não"])
            qtd_sim_pc = round((qtd_sim/qtd_alunos)*100,1)
            qtd_nao_pc = round((qtd_nao/qtd_alunos)*100,1)
            col1.header('')
            col2.header('Ponto de Virada?')
            col3.metric("Qtd Alunos", qtd_alunos)
            col4.metric("Sim", str(qtd_sim) + ' | ' + str(qtd_sim_pc) + '%')
            col5.metric("Não", str(qtd_nao) + ' | ' + str(qtd_nao_pc) + '%')

            #Grafíco
            chart_data = dados.groupby('Predição_Ponto_de_Virada')['IAA'].aggregate('count')
            chart_data.name = "Qtd Alunos"
            st.bar_chart(
                chart_data, 
                color='#DCDCDC', 
                horizontal=True,
                x_label="Qtd Alunos",
                y_label="Ponto de Virada"
                )

            chart_data2 = dados
            chart_data2['Probabilidade_Positiva_Grp'] = round(chart_data2['Probabilidade_Positiva'],1)*100
            chart_data2 = dados.groupby('Probabilidade_Positiva_Grp')['Probabilidade_Positiva_Grp'].aggregate('count')
            chart_data2.name = "Qtd Alunos"
            
            st.scatter_chart(
                chart_data2,
                color="#DCDCDC",
                x_label="Probabilidade",
                y_label="Qtd Alunos"
            )

            #Exportar Dados
            df_export = dados
            df_export['Código Aluno'] = df_export.index
            df_export.rename(
                columns={
                    'Development_Index': 'INDE', 
                    'Positive_Probability': 'Probabilidade_Positiva',
                    'Negative_Probability': 'Probabilidade_Negativa',
                    'Predict_Turning_Point': 'Predição_Ponto_de_Virada'
                }, 
                inplace=True
            )
            df_export = df_export.loc[:, ['Código Aluno', 'IAA', 'IEG', 'IPS', 'IDA', 'IAN', 'INDE','Probabilidade_Positiva','Probabilidade_Negativa','Predição_Ponto_de_Virada','Probabilidade_Positiva_Grp']]
            excel_precidt = to_excel(df_export)
            col6, col7, col8 = st.columns(3)
            col7.download_button(
                label='Download do resultado da predição',
                data=excel_precidt,
                file_name='Predição.xlsx'
            )

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer._save()
    processed_data = output.getvalue()
    return processed_data

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
