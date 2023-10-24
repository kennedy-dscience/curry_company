#libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium
import numpy as np
#bibliotecas necessárias
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
from pathlib import Path

st.set_page_config(page_title='Visão Empresas', page_icon='💵', layout='wide')

#--------------------------------------------
# Funções
#--------------------------------------------
def country_maps(df1):
    data_plot = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                 .groupby( ['City', 'Road_traffic_density'])
                 .median()
                 .reset_index())
    data_plot = data_plot[data_plot['City'] != 'NaN']
    data_plot = data_plot[data_plot['Road_traffic_density'] != 'NaN']
    
        # Desenhar o mapa
    map = folium.Map()
    for index, location_info in data_plot.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width=1024, height=600)

def order_by_week(df1):               
    # Quantidade de pedidos por entregador por Semana
    # Quantas entregas na semana / Quantos entregadores únicos por semana
    df_aux1 = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'Order_Date']].groupby('Order_Date').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # gráfico
    fig = px.line( df_aux, x='Order_Date', y='order_by_delivery' )

    return fig

def traffic_order_city (df1):
    
    df_aux = (df.loc[:, ['ID', 'City', 'Road_traffic_density']]
              .groupby(['City', 'Road_traffic_density'])
              .count()
              .reset_index())
        
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return fig

def traffic_order_share(df1):

    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
              .groupby( 'Road_traffic_density')
              .count()
              .reset_index())
    
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )

    fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )

    return fig

def order_metric(df1):
    # O que essa função order metric faz? recebe um dataframe(df1), executa o datafra, gera uma figura
    # e passa a figura pra mim!
    # Order Metric
    st.markdown('# Orders by Day')
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']
    # gráfico
    fig = px.bar( df_aux, x='order_date', y='qtde_entregas' )

    return fig

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
df = pd.read_csv(r'C:./data/train22.csv')

#  --------------------
# Limpando os dados
#  --------------------
df1 = clean_code(df)

#VISÃO EMPRESA
# Quantidade de pedidos por dia
df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
df_aux.columns = ['order_date', 'qtde_entregas']
# gráfico
px.bar( df_aux, x='order_date', y='qtde_entregas' )

# =========================
# Barra Lateral
# =========================

#LAYOUT NO STREAMLIT
st.header('Marketplace - Visão Empresas')

image_path = r'C:\Users\kenne\Comunidade DS\FTC\CICLO 6\logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?', 
    value = datetime(2022, 4, 13),
    min_value = datetime(2022, 2, 11),
    max_value = datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as opções do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Kennedy')

#filtro de data

linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        fig = order_metric(df1)
        #legenda: chamei a função order metric passando df1, recebi uma figura e segui. O objetivo é reduzir as
        # linhas
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fig = traffic_order_share(df1)
            st.header("Traffic Order Share")
            st.plotly_chart(fig, use_container_width=True)
            
            def traffic_order_share(df1):
            
                df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density' ).count().reset_index()
                df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
                # gráfico
                fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )

                return fig
                
        with col2:
                st.header("Traffic Order City")
                fig = traffic_order_city(df1)
                st.plotly_chart(fig, use_container_width=True)

                def traffic_order_city(df1):
            
                    df_aux = (df.loc[:, ['ID', 'City', 'Road_traffic_density']]
                              .groupby(['City', 'Road_traffic_density'])
                              .count()
                              .reset_index())
        
                    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
        
                    return fig

with tab2:
    with st.container():
        st.markdown('# Orders by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
        st.markdown('# Country Maps')
        country_maps(df1)