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

st.set_page_config(
    page_title='Main Page',
    page_icon="📊",
    layout='wide'
)

# =================================================
# Funções
# =================================================

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
    
def clean_code(df1):
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
    df1 = df1.loc[df1['Cuisines'] != 'Drinks Only', :].copy()
    df1 = df1.loc[df1['Cuisines'] != 'Mineira', :].copy()
    
    # Eliminando dados duplicados do dataframe
    df1 = df1.drop_duplicates().reset_index(drop=True)
    return df1

def map_general(df1):
    map_general = df1.loc[:,['restaurant_name', 'country_code', 'city', 'cuisines', 'aggregate_rating', 'average_cost_for_two', 'currency', 'latitude', 'longitude']]
    m = folium.Map(location=[0, 0], zoom_start=1)
    marker_cluster = folium.plugins.MarkerCluster().add_to(m)

    for index, location in map_general.iterrows():
        folium.Marker([location['latitude'], location['longitude']], popup=folium.Popup(f'''<h6><strong>{location['restaurant_name']}</strong></h6>
                  <h6>Price: {location["average_cost_for_two"]:.2f}({location["currency"]}) para dois<br>
                  Type: {location["cuisines"]}<br>
                  Aggregate Rating: {location["aggregate_rating"]}/5.0''', max_width=450, min_width=150),
                  icon=folium.Icon(icon="home", color='green', prefix='fa')).add_to(marker_cluster)
    folium_static(m, width=1024, height=600)
    

# ========================Inicio da Estrutura Lógica ===========================
# ==============================================================================
# Importando o Dataset
# =================================================
df = pd.read_csv('./dataset/zomato.csv')
df1 = df.copy()

# =================================================
# Limpeza dos dados
# =================================================
df1 = clean_code(df)
df1 = funcoes(df1)
df2 = df1.copy()


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

st.markdown('# Fome Zero!')

st.markdown('## O Melhor lugar para encontrar seu mais novo restaurante favorito!')

st.markdown('### Temos as seguintes marcas dentro da nossa plataforma:')

with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        unique = len(df2.loc[:, 'restaurant_id'].unique())
        st.metric('Restaurantes Cadastrados', unique)
    with col2:
        countries = len(df2.loc[:, 'country_code'].unique())
        st.metric('Países Cadastrados', countries)
    with col3:
        cities = len(df2.loc[:, 'city'].unique())
        st.metric('Cidades Cadastradas', cities)
    with col4:
        votes = df2.loc[:, 'votes'].sum()
        st.metric('Avaliações Feitas na Plataforma', votes)
    with col5:
        cuisine_type = len(df2['cuisines'].unique())
        st.metric('Tipos de Culiária Oferecidas', cuisine_type)

with st.container():
    map_general(df1)