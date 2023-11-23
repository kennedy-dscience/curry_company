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

st.set_page_config(page_title = 'Cuisines', page_icon='🍽️',layout='wide')

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
    df1 = df1.loc[df1['Cuisines'] != 'Drinks Only', :].copy()
    df1 = df1.loc[df1['Cuisines'] != 'Mineira', :].copy()
    
    # Eliminando dados duplicados do dataframe
    df1 = df1.drop_duplicates().reset_index(drop=True)
    return df1

def max_rating_cuisine(df1, cuisine):
    res1 = df1.loc[(df1['cuisines'] == cuisine), ['restaurant_name', 'restaurant_id', 'aggregate_rating']].groupby(['restaurant_name','restaurant_id']).mean().sort_values(by='aggregate_rating', ascending=False).reset_index()
    res1 = res1.loc[res1['aggregate_rating'] == res1['aggregate_rating'].max(), ['restaurant_name', 'restaurant_id']].groupby(['restaurant_name']).min().sort_values(by='restaurant_id', ascending=True).reset_index()
    
    res1 = df1.loc[df1['restaurant_id'] == res1.iloc[0,1], ['restaurant_name', 'country_code', 'city', 'average_cost_for_two', 'currency', 'cuisines', 'aggregate_rating']]
    cuisine_rest_name = f'{res1.iloc[0,5]}: {res1.iloc[0,0]}'
    rating = f'{res1.iloc[0,6]}/5.0'
    general_info = f'''
    País: {res1.iloc[0,1]}
    
    Cidade: {res1.iloc[0,2]}
    
    Média Prato para dois: {res1.iloc[0,3]}({res1.iloc[0,4]})'''
    return cuisine_rest_name, rating, general_info


def top_restaurants(df1):
    dataframe = df1.loc[df1['aggregate_rating'] == df1['aggregate_rating'].max(), ['restaurant_id', 'restaurant_name', 'country_code', 'city', 'cuisines', 'average_cost_for_two', 'aggregate_rating', 'votes']].sort_values(by='restaurant_id', ascending=True)
    return dataframe


def top_cuisines(df1, restaurant_slider):
    res12 = df3.loc[:, ['cuisines', 'aggregate_rating']].groupby(['cuisines']).mean().sort_values(by='aggregate_rating', ascending=False).reset_index()
    fig = px.bar(res12.head(restaurant_slider), x='cuisines', y='aggregate_rating', labels={'cuisines': 'Tipos de culinária', 'aggregate_rating':'Média da Avaliação Média'}, title=f'Top {restaurant_slider} Melhores tipos de Culinária', text_auto=True)
    return fig

def top_worst_cuisines(df1, restaurant_slider):
    graph_2 = round(df3.loc[:, ['cuisines', 'aggregate_rating']].groupby(['cuisines']).mean().sort_values(by='aggregate_rating').reset_index(), 2)

    fig = px.bar(graph_2.head(restaurant_slider), x='cuisines', y='aggregate_rating', labels={'cuisines': 'Tipos de culinária', 'aggregate_rating':'Avaliação Média'}, title=f'Top {restaurant_slider} Piores tipos de Culinária', text_auto=True)
    return fig
# ========================Inicio da Estrutura Lógica ===========================
# ==============================================================================
# Importando o Dataset
# =================================================
df = pd.read_csv('zomato.csv')

# =================================================
# Limpeza dos dados
# =================================================
df1 = clean_code(df)
df1 = funcoes(df1)
df2 = df1.copy()
df3 = df1.copy()

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



restaurant_slider = st.sidebar.slider('Selecione a quantidade de Restaurantes que deseja visualizar', value=10, min_value=1, max_value=20)

cuisines_options = st.sidebar.multiselect(
    'Escolha os Tipos de Culinária',
    ['Italian', 'European', 'Filipino', 'American', 'Korean', 'Pizza',
       'Taiwanese', 'Japanese', 'Coffee', 'Chinese', 'Seafood',
       'Singaporean', 'Vietnamese', 'Latin American', 'Healthy Food',
       'Cafe', 'Fast Food', 'Brazilian', 'Argentine', 'Arabian', 'Bakery',
       'Tex-Mex', 'Bar Food', 'International', 'French', 'Steak',
       'German', 'Sushi', 'Grill', 'Peruvian', 'North Eastern',
       'Ice Cream', 'Burger', 'Mexican', 'Vegetarian', 'Contemporary',
       'Desserts', 'Juices', 'Beverages', 'Spanish', 'Thai', 'Indian',
       'BBQ', 'Mongolian', 'Portuguese', 'Greek', 'Asian', 'Author',
       'Gourmet Fast Food', 'Lebanese', 'Modern Australian', 'African',
       'Coffee and Tea', 'Australian', 'Middle Eastern', 'Malaysian',
       'Tapas', 'New American', 'Pub Food', 'Southern', 'Diner', 'Donuts',
       'Southwestern', 'Sandwich', 'Irish', 'Mediterranean', 'Cafe Food',
       'Korean BBQ', 'Fusion', 'Canadian', 'Breakfast', 'Cajun',
       'New Mexican', 'Belgian', 'Cuban', 'Taco', 'Caribbean', 'Polish',
       'Deli', 'British', 'California', 'Others', 'Eastern European',
       'Creole', 'Ramen', 'Ukrainian', 'Hawaiian', 'Patisserie',
       'Yum Cha', 'Pacific Northwest', 'Tea', 'Moroccan', 'Burmese',
       'Dim Sum', 'Crepes', 'Fish and Chips', 'Russian', 'Continental',
       'South Indian', 'North Indian', 'Salad', 'Finger Food', 'Mandi',
       'Turkish', 'Kerala', 'Pakistani', 'Biryani', 'Street Food',
       'Nepalese', 'Goan', 'Iranian', 'Mughlai', 'Rajasthani', 'Mithai',
       'Maharashtrian', 'Gujarati', 'Rolls', 'Momos', 'Parsi',
       'Modern Indian', 'Andhra', 'Tibetan', 'Kebab', 'Chettinad',
       'Bengali', 'Assamese', 'Naga', 'Hyderabadi', 'Awadhi', 'Afghan',
       'Lucknowi', 'Charcoal Chicken', 'Mangalorean', 'Egyptian',
       'Malwani', 'Armenian', 'Roast Chicken', 'Indonesian', 'Western',
       'Dimsum', 'Sunda', 'Kiwi', 'Asian Fusion', 'Pan Asian', 'Balti',
       'Scottish', 'Cantonese', 'Sri Lankan', 'Khaleeji', 'South African',
       'Durban', 'World Cuisine', 'Izgara', 'Home-made', 'Giblets',
       'Fresh Fish', 'Restaurant Cafe', 'Kumpir', 'Döner',
       'Turkish Pizza', 'Ottoman', 'Old Turkish Bars', 'Kokoreç'],
    default=['Home-made', 'BBQ', 'Japanese', 'Brazilian', 'Arabian', 'American', 'Italian'])

paises_selecionados = df1['country_code'].isin(country_options)
df1 = df1.loc[paises_selecionados, :]

culinarias_selecionadas = df1['cuisines'].isin(cuisines_options)
df1 = df1.loc[culinarias_selecionadas, :]

# ==================================================
# Layout no Streamlit
# ==================================================

st.markdown('# 🍽️ Visão Culinárias')

st.markdown('## Melhores Restaurantes dos Principais tipos Culinários')

with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        cuisine_rest_name, rating, general_info = max_rating_cuisine(df2, 'Italian')
        col1.metric(cuisine_rest_name, rating, help=general_info)

    with col2:
        cuisine_rest_name, rating, general_info = max_rating_cuisine(df2, 'American')
        col2.metric(cuisine_rest_name, rating, help=general_info)

    with col3:
        cuisine_rest_name, rating, general_info = max_rating_cuisine(df2, 'Arabian')
        col3.metric(cuisine_rest_name, rating, help=general_info)

    with col4:
        cuisine_rest_name, rating, general_info = max_rating_cuisine(df2, 'Japanese')
        col4.metric(cuisine_rest_name, rating, help=general_info)

    with col5:
        cuisine_rest_name, rating, general_info = max_rating_cuisine(df2, 'Brazilian')
        col5.metric(cuisine_rest_name, rating, help=general_info)

with st.container():
    st.markdown(f'## Top {restaurant_slider} Restaurantes')
    dataframe = top_restaurants(df1)
    st.dataframe(dataframe.head(restaurant_slider))

with st.container():
    col1, col2 = st.columns(2)

    with col1:
       fig = top_cuisines(df1, restaurant_slider)
       st.plotly_chart(fig, use_container_width=True, theme=None)

    with col2:
       fig = top_worst_cuisines(df1, restaurant_slider)
       st.plotly_chart(fig, use_container_width=True, theme=None)