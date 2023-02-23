# Instalar as bibliotecas necessárias
# para instalar as bibliotecas necessárias você deve colocar no prompt de comando o pip install (a biblioteca que você quer)

# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Bibliotecas necessárias
import pandas as pd
import numpy as np
import re as re
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

# ------------------------------------------------------------------------
# Funções
# ------------------------------------------------------------------------
def clean_code( df1 ):
    """Esta função tem a responsabilidade de limpar o dataframe
       
    Tipos de limpeza:
    1. Remoção dos dados NaN
    2. Mudança do tipo da coluna de dados.
    3. Remoção dos espaços das variaveis de texto
    4. Formatação da coluna de datas
    5. Limpeza da coluna de tempo (remoção do texto variável numérica)

    Input: Dataframe.
    Output: Dataframe.

    """
    # LIMPAR OS DADOS
    # Remover espaço da string
    # for i in range( len(df1)):
    #     df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()
    #     df1.loc[i, 'Delivery_person_ID'] = df1.loc[i, 'Delivery_person_ID'].strip()

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    # EXCLUIR LINHAS COM A IDADE DOS ENTREGADORES VAZIA
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias = df1['Weatherconditions'] != 'conditions NaN'
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias = df1['City'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias = df1['Road_traffic_density'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :]
    # CONVERSAO DE TEXTO/CATEGORIA/STRING PARA NUMEROS INTEIROS
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # CONVERSAO DE TEXTO/CATEGORIA/STRING PARA NUMEROS DECIMAIS
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # CONVERSÃO DE TEXTO PARA DATA
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y')

    # REMOVE AS LINHAS DA COLUNA MULTIPLE_DELIVERIES QUE TENHAM O CONTEUDO IGUAL A 'NaN '
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # REMOVER O TEXTO DE NUMEROS
    # df1 = df1.reset_index( drop=True)
    # for i in range (len(df1)):
    #     df1.loc[i, 'Time_taken(min)'] = re.findall( r'/d+', df1.loc[i, 'Time_taken(min)'])

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1])
    # df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

    return df1

def top_delivers(df1, top_asc):
    df_aux = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).max().sort_values( ['City', 'Time_taken(min)'], ascending=top_asc).reset_index()
    df_aux1 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_aux3 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index()
    return df3
# ---------------------------- Início da estrutura lógica do código -------------------------------------
# --------------------------------------
# Import Dataset - Leitura do arquivo 
# --------------------------------------
df = pd.read_csv('../dataset/train.csv')

# --------------------------------------
# Limpando o código
# --------------------------------------
df1 = clean_code(df)

# VISÃO ENTREGADORES
# =============================================
# BARRA LATERAL NO STREAMLIT - FILTROS
# =============================================
st.header('Marketplace - Visão Entregadores')

# image_path = "C:/Users/emers/Documents/repos/ftc_programacao_python/notebooks/logo.png"
image = Image.open('logo.png')
st.sidebar.image(image, use_column_width=True)


st.sidebar.markdown('# Cury Company') # os asteristicos aqui servem como títulos maiores e menores.
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022,2,12),
    min_value=datetime(2022, 2, 12),
    max_value=datetime(2022, 6, 4),
    format='DD-MM-YYYY'
)

st.header( date_slider )
st.sidebar.markdown("""____""") # para separar o filtro

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)
st.sidebar.markdown("""____""")
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# =============================================
# LAYOUT NO STREAMLIT
# =============================================
tab1, tab2 = st.tabs(['Visão gerencial', '_']) # CRIA ABAS

with tab1:
    with st.container():
        # Overall Metrics
        st.title('Todas as métricas')
        cols1, cols2, cols3, cols4 = st.columns(4, gap='large')
        with cols1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            cols1.metric('Maior de idade', maior_idade)

        with cols2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            cols2.metric('Menor idade', menor_idade)
       
        with cols3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            cols3.metric('Melhor condição', melhor_condicao)


        with cols4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            cols4.metric('Pior condição', pior_condicao)
    

    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')

        cols1, cols2 = st.columns(2)

        with cols1:
            st.subheader('Avaliação média por entregador')
            df_avg_ratings_per_deliver = df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].groupby(['Delivery_person_ID']).mean().reset_index()
            st.dataframe(df_avg_ratings_per_deliver)

        with cols2:
            st.subheader('Avaliação média por trânsito')
            df_avg_ratings_per_traffic = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby(['Road_traffic_density']).agg({'Delivery_person_Ratings': ['mean', 'std']})
            df_avg_ratings_per_traffic.columns = ['delivery_mean', 'delivery_std']

            df_avg_ratings_per_traffic = df_avg_ratings_per_traffic.reset_index()
            st.dataframe(df_avg_ratings_per_traffic)

            st.subheader('Avaliação média por clima')
            df_avg_ratings_per_weatherconditions = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby(['Weatherconditions']).agg({'Delivery_person_Ratings': ['mean', 'std']})
            df_avg_ratings_per_weatherconditions.columns = ['delivery_mean', 'delivery_std']
            df_avg_ratings_per_weatherconditions = df_avg_ratings_per_weatherconditions.reset_index()
            st.dataframe(df_avg_ratings_per_weatherconditions)
        
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de entrega')

        cols1, cols2 = st.columns(2)

        with cols1:
            st.markdown('##### Top 10 entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)

        with cols2:
            st.markdown('##### Top 10 entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)
