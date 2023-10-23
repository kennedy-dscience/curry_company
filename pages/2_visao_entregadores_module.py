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

st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')

#-----------------------------------------
#Funções
#-----------------------------------------

def top_delivers(df1, top_asc):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
              .groupby(['City','Delivery_person_ID'])
              .mean()
              .sort_values(['City','Time_taken(min)'], ascending=top_asc).head(10).reset_index())

    df_aux01 = df2.loc[df2['City'] == 'Metropolitan', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

    return df3

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

#Import dataset
df = pd.read_csv(r'C:\Users\kenne\Comunidade DS\FTC\CICLO 6\train22.csv')

#cleaning data set
df1 = clean_code(df1)

avaliacao_media = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                   .groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']}))

#BARRA LATERAL
st.header('Marketplace - Visão Entregadores')

image_path = r'C:\Users\kenne\Comunidade DS\FTC\CICLO 6\logo.png'
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

maior_idade = df1['Delivery_person_Age'].max()
menor_idade = df1['Delivery_person_Age'].min()
melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
media_entregador = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby('Delivery_person_ID').mean().round(2).reset_index())

avaliacao_media = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                   .groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']}))

avaliacao_media.columns = ['delivery_mean', 'delivery_std']
avaliacao_media.reset_index()

avaliacao_media_clima = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                   .groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']}))
avaliacao_media_clima.columns = ['delivery_mean', 'delivery_std']
avaliacao_media_clima.reset_index()

top_entregadores = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                   .groupby(['City','Delivery_person_ID']).mean().sort_values(['City','Time_taken(min)'], ascending=True).head(10).reset_index())
                   
topdown_entregadores = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                   .groupby(['City','Delivery_person_ID']).mean().sort_values(['City','Time_taken(min)'], ascending=False).head(10).reset_index())

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

#LAYOUT NO STREAMLIT
with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            col1.metric('Maior Idade', maior_idade)

        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade
                       )

        with col3:
            col3.metric('Melhor condição', melhor_condicao)
        with col4:
            col4.metric('Pior Condição', pior_condicao)
            
    with st.container():
        st.markdown("""---""")
        st.title('Avaliacoes')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliacoes Medias por Entregador')
            st.dataframe(media_entregador)

        
        with col2:
            st.markdown('##### Avaliacoes Medias por Transito')
            st.dataframe(avaliacao_media)
            st.markdown('##### Avaliacoes Medias por Clima')
            st.dataframe(avaliacao_media_clima)

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Top Entregadores mais rapidos')
            df3 = top_entregadores
            st.dataframe(df3)
    
        with col2:
            st.subheader('Top Entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)