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

def order_metric(df1):
    cols = ['ID', 'Order_Date']
    # seleção das linhas
    df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()

    # desenhar o gráfico de barras (Matplotlib - Seaborn - Bokeh - Plotly)
    fig = px.bar( df_aux, x='Order_Date', y='ID')

    return fig

def traffic_order_share(df1):
    # 3. Distribuição dos pedidos por tipo de tráfego
    # seleção das colunas necessárias
    cols = ['ID', 'Road_traffic_density']

    # seleção das linhas
    df_aux = df1.loc[:, cols].groupby(['Road_traffic_density']).count().reset_index()

    # percentual
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux['entregas_percentual'] = df_aux['ID'] / df_aux['ID'].sum()

    # desenhar o gráfico de pizza (Matplotlib - Seaborn - Bokeh - Plotly)
    fig = px.pie( df_aux, values='entregas_percentual', names='Road_traffic_density')

    return fig

def traffic_order_city(df1):
    # 4. Comparação de volumes de pedidos por cidade e por tipo de tráfego
    # seleção das colunas necessárias
    cols = ['ID', 'Road_traffic_density', 'City']

    # seleção das linhas
    df_aux = df1.loc[:, cols].groupby([ 'City','Road_traffic_density']).count().reset_index()

    # gráfico de bolhas
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return fig

def order_by_week(df1):
    # 2. Quantidade de pedidos por semana
    # criar a coluna de semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )

    # seleção das colunas necessárias
    cols = ['ID', 'week_of_year']

    # seleção das linhas
    df_aux = df1.loc[:, cols].groupby(['week_of_year']).count().reset_index()

    # desenhar o gráfico de linhas (Matplotlib - Seaborn - Bokeh - Plotly)
    fig = px.line( df_aux, x='week_of_year', y='ID')
        
    return fig

def order_share_by_week(df1):
     # 5. Quantidade de pedidos por entregador por semana 
    # Quantidade de pedidos / número único de entregadores por semana.

    # contar a quantidade de pedidos por semana
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

    # contar o número de entregadores únicos por semana
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

    # para juntar os dois dataframes criados
    df_aux = pd.merge( df_aux1, df_aux2, how='inner')

    df_aux['Order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    # gráfico de linhas
    fig = px.line( df_aux, x='week_of_year', y='Order_by_deliver')
    st.plotly_chart(fig, use_container_width=True)

    return fig

def country_maps(df1):
    # 6. A localização central de cada tipo de tráfego
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

    # desenho do mapa
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], 
                        location_info['Delivery_location_longitude']], popup=location_info[['City', 'Road_traffic_density']]).add_to( map )
    folium_static(map, width=1024, height=600 )

# ---------------------------- Início da estrutura lógica do código -------------------------------------
# --------------------------------------
# Import Dataset - Leitura do arquivo 
# --------------------------------------
df = pd.read_csv('../dataset/train.csv')

# --------------------------------------
# Limpando o código
# --------------------------------------
df1 = clean_code(df)

# --------------------------------------
# VISÃO EMPRESA 
# --------------------------------------
# =============================================
# BARRA LATERAL NO STREAMLIT - FILTROS
# =============================================
st.header('Marketplace - Visão Empresa')

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
tab1, tab2, tab3 = st.tabs(['Visão gerencial', 'Visão tática', 'Visão geográfica']) # CRIA ABAS

with tab1:
    with st.container():
        fig = order_metric(df1)
        st.markdown('# Orders by Day')
        st.plotly_chart(fig, use_container_width=True)
       
    with st.container():
           col1, col2 = st.columns(2)
           with col1:
                fig = traffic_order_share(df1)
                st.markdown('# Pedidos por tipo de tráfego')
                st.plotly_chart(fig, use_container_width=True)
                
           with col2:
                fig = traffic_order_city(df1)
                st.markdown('# Volumes de pedido por cidade e tipo de tráfego')
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        fig = order_by_week(df1)
        st.markdown('# Pedidos por semana')
        st.plotly_chart(fig, use_container_width=True)
         
    with st.container():
        fig = order_share_by_week(df1)
        st.markdown('# Pedidos por entregador')
        st.plotly_chart(fig, use_container_width=True)


with tab3:
    st.header('Country Maps')
    country_maps(df1)
