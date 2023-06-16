# BIBLIOTECAS
# --------------------------------------
import pandas as pd
from datetime import datetime

import streamlit as st
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from haversine import haversine # Good for short distances: assumes earth as sphere.
# --------------------------------------




st.set_page_config(page_title="Visao Empresa", layout='wide')




# MODULARIZAÇÃO - FUNÇÕES DO CÓDIGO
# --------------------------------------

# Limpeza
# --------------------------------------------------------------------------------------------------------------------------------
def clean_code(df):
    """
        Esta função faz a limpeza do dataframe.
        
        1. Remove dados tipo NaN;
        2. Adequa os tipos das colunas;
        3. Remove espaços em branco à direita das strings;
        4. Formata a coluna de datas;
        5. Limpa a coluna de tempo de entrega (remove texto da variável numérica).
        
        Input: Dataframe.
        Output: Dataframe.
        
    """
    
    
    #PE Elimina-se linhas com 'NaN', 'NaN ', etc. Usando booleans para identificar e eliminar tais linhas.
    df = df.loc[(df['ID'].str.contains('NaN') == False), :]
    df = df.loc[(df['Delivery_person_ID'].str.contains('NaN') == False), :]
    df = df.loc[(df['Delivery_person_Age'].str.contains('NaN') == False), :]
    df = df.loc[(df['Delivery_person_Ratings'].str.contains('NaN') == False), :]
    df = df.loc[(df['Order_Date'].str.contains('NaN') == False), :]
    df = df.loc[(df['Time_Orderd'].str.contains('NaN') == False), :]
    df = df.loc[(df['Time_Order_picked'].str.contains('NaN') == False), :]
    df = df.loc[(df['Weatherconditions'].str.contains('NaN') == False), :]
    df = df.loc[(df['Road_traffic_density'].str.contains('NaN') == False), :]
    df = df.loc[(df['Type_of_order'].str.contains('NaN') == False), :]
    df = df.loc[(df['Type_of_vehicle'].str.contains('NaN') == False), :]
    df = df.loc[(df['multiple_deliveries'].str.contains('NaN') == False), :]
    df = df.loc[(df['Festival'].str.contains('NaN') == False), :]
    df = df.loc[(df['City'].str.contains('NaN') == False), :]
    df = df.loc[(df['Time_taken(min)'].str.contains('NaN') == False), :]


    #PE Transforma-se o tipo das colunas numéricas usando astype().
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)


    #PE Usando str.strip() para remover espaços em branco à direita das strings da coluna.
    cols = ['ID', 'Delivery_person_ID', 'Road_traffic_density', 'Type_of_order', 'Type_of_vehicle', 'Festival', 'City']
    for col in cols:
        df[col] = df[col].str.strip()


    #PE Muda-se o formato de data de %d-%m-%Y para %Y-%m-%d.  Usando pd.to_datetime(dataframe['coluna_alvo'], format='...')
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')

    #PE E no formato de tempo: '(min) ##' para '##', usando .apply( lambda x: x.split()[1] ou x.replace() ), remove-se a parte '(min) '
    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split()[1] ).astype(int)

    return df
# --------------------------------------------------------------------------------------------------------------------------------


# Gráficos
# --------------------------------------------------------------------------------------------------------------------------------
# Tab1, container 01:
def bar_chart(df):
    #SA 1. Quantidade de pedidos por dia em um gráfico de barras.
    #PE Com groupby(), é feito o agrupamento de dados por dia para se contar os pedidos com .count().
    cols = ['Order_Date', 'ID']
    pedidos_diarios = df.loc[:, cols].groupby(['Order_Date'], as_index=False).count()

    #PE Pode-se usar o plotly.express.bar() para plotar o gráfico, em que x=dia e y=quantidade de pedidos.
    bar_chart = px.bar(pedidos_diarios, x='Order_Date', y='ID')

    return bar_chart
# --------------------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------------------------
# Tab1, container 02, coluna 01:
def pizza_chart(df):
    #SA 3. Distribuição dos pedidos por tipo de tráfego em gráfico pizza.
    #PE Agrupa-se e conta-se os pedidos por tipo de tráfego com .groupby() e .count().
    pedidos_trafego = df.loc[:, ['Road_traffic_density', 'ID']].groupby(['Road_traffic_density'], as_index=False).count()

    #PE é criada uma coluna com a proporção entre entregas por tipo de tráfego.
    pedidos_trafego['Deliv_per_traffic'] = pedidos_trafego['ID']/pedidos_trafego['ID'].sum()

    #PE Com px.pie(), é feito o gráfico de pizza.
    pizza_chart = px.pie(pedidos_trafego, values='Deliv_per_traffic', names='Road_traffic_density')

    return pizza_chart
# --------------------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------------------------
# Tab1, container 02, coluna 02:
def bubble_chart(df):
    #SA 4. Comparação do volume de pedidos por cidade e tipo de tráfego usando um gráfico de bolhas.
    #PE Agrupa-se pedidos por cidade e tráfego com .groupby() e conta-se com .count().
    pedidos_cidade_trafego = df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density'], as_index=False).count()

    #PE É feito um gráfico de bolhas com px.scatter()
    bubble_chart = px.scatter(pedidos_cidade_trafego, x='City', y='Road_traffic_density', size='ID', color='City')

    return bubble_chart
# --------------------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------------------------
# Tab2, container 01:
def line_chart(df):
    #SA 2. Quantidade de pedidos por semana do ano num gráfico de linhas.
    #PE Criar coluna de número da semana baseada no dia do ano usando .dt.strftime(%U) (.strftime transforma um datetime em um string equivalente escolhendo-se o formato). 
    df['Order_Week'] = df['Order_Date'].dt.strftime('%U')

    #PE Agrupar pedidos por semana com .groupby() e contar pedidos de cada semana usando .count().
    cols = ['Order_Week', 'ID']
    pedidos_semanais = df.loc[:, cols].groupby(['Order_Week'], as_index=False).count()

    #PE Cria-se um gráfico de linhas de quantidade de pedidos por semana com px.line(), sendo x=semana e y=quantidade de pedidos.
    line_chart = px.line(pedidos_semanais, x='Order_Week', y='ID')

    return line_chart
# --------------------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------------------------
# Tab2, container 02:        
def line_chart2(df):
    #SA 2. Quantidade de pedidos por entregador por semana do ano descrito por um gráfico de linhas.
    #PE Usa-se .groupby() e .nunique() para agrupar e contar entregadores ÚNICOS por semana.
    entregadores_semana = df.loc[:, ['Delivery_person_ID', 'Order_Week']].groupby(['Order_Week'], as_index=False).nunique()
    #PE Usa-se .groupby() e .count() para agrupar e contar pedidos por semana.
    pedidos_semana = df.loc[:, ['ID', 'Order_Week']].groupby(['Order_Week'], as_index=False).count()

    #PE Juntar pedidos_semana e entregadores_semana numa mesma tabela usando .merge().
    ped_entreg_semana = pd.merge(pedidos_semana, entregadores_semana, how='inner')

    #PE Criar nova coluna com a divisão pedidos_semana/entregadores_semana.
    ped_entreg_semana['pedidos_por_entregador'] = ped_entreg_semana['ID']/ped_entreg_semana['Delivery_person_ID']

    #PE Fazer um gráfico de linhas com px.line().
    line_chart2 = px.line(ped_entreg_semana, x='Order_Week', y='pedidos_por_entregador')

    return line_chart2
# --------------------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------------------------
# Tab3
def folium_map(df):
    #SA 6. A localização central de cada cidade por tipo de tráfego exposta num mapa.
    #PE Usa-se .groupby() para fazer o agrupamento por cidade e tipo de tráfego e .median() para calcular a mediana das coordenadas (mediana pega um 
    #PE valor real dos dados, ou seja, vamos localizar os restaurantes reais, não um local próximo a eles). Guarda-se numa tabela.

    location_by_city_and_traffic = df.loc[:, ['City', 'Road_traffic_density', 'Restaurant_latitude', 'Restaurant_longitude']].groupby(['City', 'Road_traffic_density'], as_index=False).median()

    #PE Criar um mapa limpo com folium.Map() e preencher com as informações da nossa tabela usando folium.Marker().
    folium_map = folium.Map()

    for i in range(len(location_by_city_and_traffic)):
        folium.Marker([location_by_city_and_traffic.loc[i, 'Restaurant_latitude'], 
                       location_by_city_and_traffic.loc[i, 'Restaurant_longitude']], 
                       popup=location_by_city_and_traffic.loc[i, ['City', 'Road_traffic_density']]).add_to(folium_map)

    return folium_map
# --------------------------------------------------------------------------------------------------------------------------------




# ETL - EXTRACT
# --------------------------------------
df_raw = pd.read_csv('food_delivery_train.csv')
df = df_raw.copy()


# ETL - TRANSFORM
# --------------------------------------
# Limpeza dos dados
df = clean_code(df)


# ETL - LOAD
# --------------------------------------
# Dados carregados em Dataframe na memória a partir deste código.




# STREAMLIT
# --------------------------------------

# Barra lateral
# --------------------------------------

# Imagem da barra lateral
image_path = 'images/'
image_sidebar = Image.open(image_path + "logo.png")
st.sidebar.image(image_sidebar, width=80)

# Primeira seção da barra lateral
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

# Segunda seção da barra lateral
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 13),
    value=datetime(2022, 4, 13),
    format='DD-MM-YYYY')
st.sidebar.markdown("""---""")

# Terceira seção da barra lateral
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""---""")


# Controles
# --------------------------------------

# Data
lines_date = (df['Order_Date'] <= date_slider)
df = df.loc[lines_date, :]

# Tráfego
lines_traffic = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[lines_traffic, :]




# Layout da Tela Principal
# --------------------------------------

# Título principal
st.markdown('# Marketplace - Visão da Empresa')
st.markdown('#### {}'.format(date_slider.strftime("%d-%m-%Y")))

# Abas na tela principal
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])



# Primeira aba: 'Visão Gerencial'
with tab1:
    # Tab1, Container 01
    with st.container():
        # Título do Container 01:
        st.markdown('### Pedidos por dia')
        
        # Criação do gráfico de barras com quantidade de pedidos por dia.
        daily_orders_bar_chart = bar_chart(df)
        
        #PE Plotando no StreamLit.
        st.plotly_chart(daily_orders_bar_chart, use_container_width=True)
    
    
    # Tab1, Container 02
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            # Título do Container 02, coluna 01:
            st.markdown('### Pedidos por tipo de Tráfego')
            
            # Gráfico de pizza de pedidos por tipo de tráfego.
            orders_by_traffic_pizza_chart = pizza_chart(df)
            
            #PE Gráfico plotado no StreamLit com st.plotly_chart().
            st.plotly_chart(orders_by_traffic_pizza_chart, use_container_width=True)

        with col2:
            # Título do Container 02, coluna 02:
            st.markdown('### Pedidos por tipo de Tráfego e Cidade')
            
            # Gráfico de bolha por tipo de tráfego e cidade.
            orders_by_traffic_and_city_bubble_chart = bubble_chart(df)
            
            #PE Gráfico plotado no StreamLit com st.plotly_chart().
            st.plotly_chart(orders_by_traffic_and_city_bubble_chart, use_container_width=True)



# segunda aba: 'Visão Tática'
with tab2:
    # Tab2, Container 01
    with st.container():
        # Título do Container 01:
        st.markdown('### Quantidade de Pedidos em cada Semana')
        
        # Gráfico de linha com pedidos por dia.
        order_by_week_chart = line_chart(df)
        
        #PE Gráfico plotado no StreamLit com st.plotly_chart().
        st.plotly_chart(order_by_week_chart, use_container_width=True)
        
        
    # Tab2, Container 02
    with st.container():
        # Título do Container 02:
        st.markdown('### Quantidade de Pedidos por Entregador em cada Semana')
        
        # Gráfico de linha de quantidade de pedidos por quantidade de entregador por semana
        order_by_delivery_person_by_week_chart = line_chart2(df)
        
        #PE Gráfico plotado no StreamLit com st.plotly_chart().
        st.plotly_chart(order_by_delivery_person_by_week_chart, use_container_width=True)



# Terceira aba: 'Visão Geográfica'
with tab3:
    # Tab3
    with st.container():
        # Título do container:
        st.markdown('### Mapa de Restaurantes: Cidade e tipo de Tráfego')
        
        # Criando mapa com marcadores de restaurantes.
        location_by_city_and_traffic_map = folium_map(df)
        
        # Plotando mapa no streamlit.
        folium_static(location_by_city_and_traffic_map, width=703, height=300)