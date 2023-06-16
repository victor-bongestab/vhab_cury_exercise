# BIBLIOTECAS
# --------------------------------------
import streamlit as st
from PIL import Image
# --------------------------------------




st.set_page_config(page_title="Home", page_icon="🌏", layout='wide')

image_path = 'images/'
image_sidebar = Image.open(image_path + 'logo.png')

st.sidebar.image(image_sidebar, width=80)

# Primeira seção da barra lateral
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Dashboard de Crescimento da Cury Company")

st.markdown(
            """
            Dashboard de Crescimento construído para acompanhas as métricas de crescimento da Empresa, Entregadores e Restaurantes.
            ### Como utilizar este Dashboard?
            - Visão da Empresa:
                - Visão Gerencial: Métricas gerais de comportamento;
                - Visão Tática: Indicadores semanais de crescimento;
                - Visão Geográfica: Insights de geolocalização.
            
            - Visão dos Entregadores:
                - Acompanhamento dos indicadores semanais de crescimento.
            
            - Visão dos Restaurantes:
                - Indicadores semanais de crescimento dos restaurantes.
                
            ### Ask for help
                victorhabongestab@hotmail.com
            """)