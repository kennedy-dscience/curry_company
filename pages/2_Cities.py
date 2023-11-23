#===================================================================
#Bibliotecas
#===================================================================
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium
import numpy as np
import pandas as pd
import streamlit as st
import inflection
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
from pathlib import Path
from haversine import haversine

st.set_page_config(page_title = 'Cities', page_icon='🏙️',layout='wide')

#===================================================================
#Funções
#===================================================================

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
def country_name(country_id):
    return COUNTRIES[country_id]

def create_price_type(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]

def funcoes(df1):
    df1 = rename_columns(df1)
    df1['country_code'] = df1.loc[:, 'country_code'].apply(lambda x: country_name(x))
    df1['price_range'] = df1.loc[:, 'price_range'].apply(lambda x: create_price_type(x))
    df1['rating_color'] = df1.loc[:, 'rating_color'].apply(lambda x: color_name(x))
    return df1
    
def clean_code(df):
    # copiando o dataframe
    df1 = df.copy()
    # deletando colunas inúteis para a análise
    df1 = df1.drop(['Switch to order menu'], axis=1)
    
    # Categorizando os restaurantes somente por um tipo de culinária
    df1['Cuisines'] = df1['Cuisines'].astype(str)
    df1["Cuisines"] = df1.loc[:, "Cuisines"].apply(lambda x: x.split(",")[0])
    
    # selecionando linhas que tenham valores diferentes de zero nas colunas longitude e latitude
    df1 = df1.loc[df1['Longitude'] != 0, :].copy()
    df1 = df1.loc[df1['Latitude'] != 0, :].copy()
    
    # deletando valor nulo da coluna Cuisines
    df1 = df1.loc[df1['Cuisines'] != 'nan', :].copy()
    
    # Eliminando dados duplicados do dataframe
    df1 = df1.drop_duplicates().reset_index(drop=True)
    return df1

def top_cities(df1):
        re1 = df1.loc[:, ['city', 'restaurant_id', 'country_code']].groupby(['city','country_code']).count().sort_values(by=['restaurant_id', 'country_code'], ascending=False).reset_index()
        fig = px.bar(re1.head(10), x='city', y='restaurant_id', hover_data=['country_code', 'city', 'restaurant_id'], labels={'city':'Cidades', 'restaurant_id':'Quantidade de Restaurantes', 'country_code':'País'}, text_auto=True, color='country_code', title='Top 10 Cidades com mais Restaurantes na Base de Dados')
        return fig

def restaurant_acima(df1):
            re2 = df1.loc[:, ['city', 'aggregate_rating', 'restaurant_id', 'country_code']].groupby(['city', 'restaurant_id', 'country_code']).mean().sort_values(by=['restaurant_id', 'city'], ascending=False).reset_index()
            re2 = re2.loc[re2['aggregate_rating'] > 4, ['country_code', 'restaurant_id', 'city']].groupby(['country_code','city']).count().sort_values(by=['restaurant_id', 'city'], ascending=[False, True]).reset_index()
            fig = px.bar(re2.head(7), x='city', y='restaurant_id', labels={'country_code':'País', 'city':'Cidades', 'restaurant_id':'Quantidade de Restaurantes'}, text_auto=True, hover_data=['country_code', 'city', 'restaurant_id'], color='country_code', title='Top 7 Cidades com Restaurantes com média de avaliação acima de 4')
            return fig

def restaurante_abaixo(df1):
            re3 = df1.loc[:, ['city', 'aggregate_rating', 'restaurant_id', 'country_code']].groupby(['city', 'restaurant_id', 'country_code']).mean().sort_values(by=['restaurant_id', 'city'], ascending=False).reset_index()
            re3 = re3.loc[re3['aggregate_rating'] < 2.5, ['country_code', 'restaurant_id', 'city']].groupby(['country_code','city']).count().sort_values(by=['restaurant_id', 'city'], ascending=[False, True]).reset_index()
            fig = px.bar(re3.head(7), x='city', y='restaurant_id', labels={'country_code':'País', 'city':'Cidades', 'restaurant_id':'Quantidade de Restaurantes'}, text_auto=True, hover_data=['country_code', 'city', 'restaurant_id'], color='country_code', title='Top 7 Cidades com Restaurantes com média de avaliação abaixo de 2.5')
            return fig

def top_cities_cuisines(df1):
        re5 = df1.loc[:, ['city', 'cuisines', 'restaurant_id', 'country_code']].groupby(['city', 'cuisines', 'country_code']).count().sort_values(by='restaurant_id', ascending=False).reset_index()
        re5 = re5.loc[:, ['city', 'cuisines', 'country_code']].groupby(['country_code', 'city']).count().sort_values(by='cuisines', ascending=False).reset_index()
        fig = px.bar(re5.head(10), x='city', y='cuisines', labels={'country_code':'País', 'city':'Cidade', 'cuisines':'Quantidade de Tipos culinários únicos'}, text_auto=True, hover_data=['country_code', 'city', 'cuisines'], color='country_code' ,title='Top 10 cidades com mais restaurantes com tipos culinários distintos')
        return fig

#===================================================================
#Importação do dataset:
#===================================================================

df = pd.read_csv('./dataset/zomato.csv')

#===================================================================
#Limpeza do dataset:
#===================================================================

df1 = clean_code(df)
df1 = funcoes(df1)
# =================================================
# Barra Lateral
# =================================================

st.header ('🏙️ Visão Cidades')

st.sidebar.markdown ("--------")

image = Image.open('logo.png')
st.sidebar.image(image, width=170)

country_options = st.sidebar.multiselect(
    'Escolha os Paises que Deseja visualizar os Restaurantes',
    ['Philippines', 'Brazil', 'Australia', 'United States of America',
     'Canada', 'Singapure', 'United Arab Emirates', 'India',
     'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
     'Sri Lanka', 'Turkey'],
    default=['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia'])

st.sidebar.markdown ("___")
st.sidebar.markdown ('###### Powered by Kennedy S')

#Filtro de país

paises_selecionados = df1['country_code'].isin(country_options)
df1 = df1.loc[paises_selecionados, :]

# ==================================================
# Layout no Streamlit
# ==================================================

with st.container():
    
    fig = top_cities(df1)
    st.plotly_chart(fig, use_container_width=True, theme=None)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        fig = restaurant_acima(df1)
        st.plotly_chart(fig, use_container_width=True, theme=None)

    with col2:
        fig = restaurante_abaixo(df1)
        st.plotly_chart(fig, use_container_width=True, theme=None)

with st.container():
    fig = top_cities_cuisines(df1)
    st.plotly_chart(fig, use_container_width=True, theme=None)