import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🖥️",
    layout='wide'
)
#para adicionar emoji atalho: tecla windows + "." ao mesmo tempo#
#image_path = r'C:\Users\kenne\OneDrive\Área de Trabalho\DS\repos\FTC\CICLO 6/'
image = Image.open ('logo.png')
st.sidebar.image(image , width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.""")
    





    
       
st.write("### Ask for Help")
""" Time de Data Science:
    - @Kennedy """
