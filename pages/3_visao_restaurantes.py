# Instalar as bibliotecas necessárias
# para instalar as bibliotecas necessárias você deve colocar no prompt de comando o pip install (a biblioteca que você quer)

# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Bibliotecas necessárias
import pandas as pd
import numpy as np
import streamlit as st
import folium
from PIL import Image

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

def distance(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'] )), axis=1)
    avg_distance = np.round(df1['distance'].mean(), 2)

    return avg_distance

def avg_std_time_delivery(df1, festival, op):
    """
    Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
    Paramêtros:
    Input: 
        - df: Dataframe com os dados necessários para o cáculo
        - op: tipo de operação que precisa ser calculado.
            'avg_time': calcula o tempo médio.
            'std_time': calcula o desvio padrão do tempo.
    Output: 
        - df: Dataframe com 2 colunas e 1 linha.
    """
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)
    # avg_time_yes_festival = df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'].iloc[0]
    # avg_time_yes_festival_str = str(round(avg_time_yes_festival, 2))
    return str(df_aux)


def avg_std_time_graph(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby(['City']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_on_traffic(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig
# ---------------------------- Início da estrutura lógica do código -------------------------------------
# --------------------------------------
# Import Dataset - Leitura do arquivo 
# --------------------------------------
df = pd.read_csv('../dataset/train.csv')

# --------------------------------------
# Limpando o código
# --------------------------------------
df1 = clean_code(df)

# VISÃO RESTAURANTES
# =============================================
# BARRA LATERAL NO STREAMLIT - FILTROS
# =============================================
st.header('Marketplace - Visão Restaurantes')

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
        cols1, cols2, cols3, cols4, cols5, cols6 = st.columns(6)
        with cols1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            cols1.metric('Entregadores únicos', delivery_unique)

        with cols2:
            avg_distance = distance(df1)
            cols2.metric('Distância média das entregas', avg_distance)

        with cols3:
            df1_aux = avg_std_time_delivery(df1,'Yes' ,'avg_time')
            cols3.metric('AVG entrega com festival', df1_aux)

        with cols4:
            df1_aux = avg_std_time_delivery(df1, 'Yes' ,'std_time')
            cols4.metric('STD entrega com festival', df1_aux)

        with cols5:
            df1_aux = avg_std_time_delivery(df1, 'No' ,'avg_time')
            cols5.metric('AVG entrega sem festival', df1_aux)
        
        with cols6:
            df1_aux = avg_std_time_delivery(df1, 'No' ,'std_time')
            cols6.metric('STD entrega sem festival', df1_aux)

    with st.container():
        st.markdown("""___""")
        st.title('Distribuição da distância')
        cols1, cols2 = st.columns (2)
        with cols1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)

        with cols2:
            st.markdown("""___""")
            df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)
        
    with st.container():
        st.markdown("""___""")
        st.title('Distribuição do tempo')

        cols1, cols2 = st.columns(2)

        with cols1:
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'] )), axis=1)
            avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            # fig.show()
            st.plotly_chart(fig, use_container_width=True)

        with cols2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)


