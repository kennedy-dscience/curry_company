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

st.set_page_config(page_title = 'Country', page_icon='🌎',layout='wide')

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

def restaurant_quantity(df1):
    res2 = df1.loc[:, ['country_code', 'restaurant_id']].groupby(['country_code']).count().sort_values(by=['restaurant_id'], ascending=False).reset_index()
    fig = px.bar(res2, x='country_code', y='restaurant_id', labels={'country_code': 'Países', 'restaurant_id': 'Quantidade de Restaurantes'}, text_auto=True, title='Quantidade de Restaurantes Registrados por País')
    return fig

def city_per_country_qtd(df1):
    res1 = df1.loc[:, ['country_code', 'city', 'restaurant_id']].groupby(['country_code', 'city']).count().sort_values(by='country_code', ascending=False).reset_index()
    res1 = res1.loc[:, ['country_code', 'city']].groupby(['country_code']).count().sort_values(by='city', ascending=False).reset_index()
    fig = px.bar(res1, x='country_code', y='city', labels={'country_code':'Países', 'city':'Quantidade de Cidades'}, text_auto=True, title='Quantidade de Cidades Registradas por País')
    return fig
        
def mean_rating_per_country(df1):
    res8 = round(df1.loc[:, ['country_code', 'votes']].groupby(['country_code']).mean().sort_values(by='votes', ascending=False).reset_index(),2)
    fig = px.bar(res8, x='country_code', y='votes', labels={'country_code':'Países', 'votes':'Quantidade de Avaliações'}, text_auto=True, title='Média de Avaliações por País')
    return fig

def mean_cost_for_two_per_country(df1):
    res11 = round(df1.loc[:, ['country_code', 'average_cost_for_two']].groupby(['country_code']).mean().sort_values(by='average_cost_for_two', ascending=False).reset_index(), 2)
    fig = px.bar(res11, x='country_code', y='average_cost_for_two', labels={'country_code':'Países', 'average_cost_for_two': 'Preço de prato para duas Pessoas'}, text_auto=True, title='Média de Preço de um Prato para duas pessoas por País')
    return fig
# ========================Inicio da Estrutura Lógica ===========================
# ==============================================================================
# Importando o Dataset
# =================================================
df = pd.read_csv('./dataset/zomato.csv')

# =================================================
# Limpeza dos dados
# =================================================
df1 = clean_code(df)
df1 = funcoes(df1)

# =================================================
# Barra Lateral
# =================================================
image = Image.open('logo.png')
st.sidebar.image(image, width=170)

st.sidebar.markdown('# Fome Zero')

st.sidebar.markdown('### Filtros')

country_options = st.sidebar.multiselect(
    'Escolha os Paises que Deseja visualizar os Restaurantes',
    ['Philippines', 'Brazil', 'Australia', 'United States of America',
     'Canada', 'Singapure', 'United Arab Emirates', 'India',
     'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
     'Sri Lanka', 'Turkey'],
    default=['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia'])

paises_selecionados = df1['country_code'].isin(country_options)
df1 = df1.loc[paises_selecionados, :]

# ==================================================
# Layout no Streamlit
# ==================================================

st.markdown('# 🌎 Visão Países')

with st.container():
    fig = restaurant_quantity(df1)
    st.plotly_chart(fig, use_container_width=True, theme=None)

with st.container():
    fig = city_per_country_qtd(df1)
    st.plotly_chart(fig, use_container_width=True, theme=None)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        fig = mean_rating_per_country(df1)
        st.plotly_chart(fig, use_container_width=True, theme=None)

    with col2:
        fig = mean_cost_for_two_per_country(df1)
        st.plotly_chart(fig, use_container_width=True, theme=None)