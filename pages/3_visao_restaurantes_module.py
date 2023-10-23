#libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#bibliotecas necessárias
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

#--------------------------------------------
# Funções
#--------------------------------------------
def avg_std_time_delivery(df1, festival, op):
    df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                  .groupby('Festival')
                  .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = df_aux.loc[df_aux['Festival'] == festival, op].round(2)
    col3.metric('Tempo médio', df_aux)

    return df_aux

def distance(df1):           
    cols_ = ['Delivery_location_latitude', 'Delivery_location_longitude', 
             'Restaurant_latitude', 'Restaurant_longitude']
    df1['distance'] = df1.loc[:, cols_].apply( lambda x:
                                 haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

    avg_distance = df1['distance'].mean().round(2)

    return avg_distance

def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo de colunas de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável númerica)

        input: Dataframe
        Output: Dataframe
    """

    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    ## 4. convertendo a coluna 'multiple_deliveries' de 'string' para 'int':
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    
    df1 = df1[df1['Time_taken(min)'] != 'NaN ']
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1] if isinstance(x, str) else x)
    df1['Time_taken(min)'].fillna(0, inplace=True)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(float).astype(int)

    return df1

#--------------------Início da estrutura lógica do código----------------------------------
# --------------------
# Import dataset
# --------------------
df = pd.read_csv(r'C:\Users\kenne\Comunidade DS\FTC\CICLO 6\train22.csv')

#  --------------------
# Limpando os dados
#  --------------------
df1 = clean_code(df)

#BARRA LATERAL
st.header('Marketplace - Visão Restaurantes')

image_path = r'C:\Users\kenne\OneDrive\Área de Trabalho\DS\repos\FTC\CICLO 6\logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?', value = datetime(2022, 4, 13), min_value = datetime(2022, 2, 11), max_value = datetime(2022, 4, 6), format='DD-MM-YYYY')

st.sidebar.markdown("""---""")
#date_slider = st.sidebar.slider(
#    'Até qual valor?', value = datetime(2022, 4, 13), min_value = datetime(2022, 2, 11), max_value = datetime(2022, 4, 6), format='DD-MM-YYYY')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown(""" --- """)

st.sidebar.markdown('#### Powered by Geraldo Pedro Dambros')


# filtro de data:
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtro de trânsito:
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]
st.dataframe(df1)

# ==================
# Layout no Streamlit
# ==================
tab1, tab2, tab3 = st.tabs (['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title("Overal Metrics")
    
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len((df1['Delivery_person_ID']).unique())
            col1.metric('# Entregadores Únicos', delivery_unique)
            
        with col2:
            avg_distance = distance(df1)
            col2.metric('A distância média das entregas:', avg_distance)
            
        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric('Tempo médio', df_aux)
            
        with col4:
            df_aux = avg_std_time_delivery(df1,'Yes', 'std_time')
            col4.metric('STD c/ Festival', df_aux)

        with col5:
            df_aux = avg_std_time_delivery(df1,'No', 'avg_time')
            col5.metric('Tempo médio', df_aux)

        with col6:   
            df_aux = avg_std_time_delivery(df1,'No', 'std_time')
            col6.metric('STD s/ Festival', df_aux)

    with st.container():
        st.markdown("""---""")
        st.title("Tempo Medio de Entrega por Cidade")
        cols_ = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance'] = df1.loc[:, cols_].apply( lambda x:
                                    haversine(  (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)    
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure( data=[go.Pie(labels=avg_distance['City'], values= avg_distance['distance'], pull=[0.05, 0.05, 0.05])])
        st.plotly_chart(fig)
        

    with st.container():
        st.markdown("""---""")
        st.title("Distribuição do tempo")
        col1, col2 = st.columns(2)
        
    col1, col2 = st.columns(2)
    with col1:
            st.markdown ('###### Coluna 1')
    with col2:
            st.markdown ('###### Coluna 2')
    
    with st.container():
        st.markdown("""---""")
        st.title("Distribuição da Distância")
 