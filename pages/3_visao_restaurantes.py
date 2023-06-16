# Bibliotecas de dados
import pandas as pd
from datetime import datetime
import numpy as np

# Bibliotecas gráficas
import streamlit as st
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from haversine import haversine # Good for short distances: assumes earth as sphere.



st.set_page_config(page_title="Visao Restaurantes", layout='wide')



# Dataset
df_raw = pd.read_csv('food_delivery_train.csv')
df = df_raw.copy()




# ==============================================================================================================================================
#SA LIMPEZA DO DATASET
# ==============================================================================================================================================

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






# ==============================================================================================================================================
# STREAMLIT
# ==============================================================================================================================================


# BARRA LATERAL e CONTROLES
# ============================================

# Imagem da barra lateral
image_path = 'images/'
image_sidebar = Image.open(image_path + 'logo.png')
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


# CONTROLES
# Data
lines_date = (df['Order_Date'] <= date_slider)
df = df.loc[lines_date, :]

# Tráfego
lines_traffic = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[lines_traffic, :]




# LAYOUT da tela principal
# ============================================

# TÍTULO principal
st.markdown('# Marketplace - Visão dos Restaurantes')
st.markdown('#### {}'.format(date_slider.strftime("%d-%m-%Y")))


# Container 01
with st.container():
    # Título do container 01:
    st.markdown("## Métricas gerais")
    
    outercol1, outercol2 = st.columns(2, gap="large")
    
    # Colunas 01 e 02
    with outercol1:
        innercol1, innercol2 = st.columns(2)
        # Container 01, coluna 01
        with innercol1:
            #SA 1. Quantidade de entregadores únicos.
            #PE Usar .unique() para selecionar valores únicos de entregadores e len() para contar o tamanho dessa seleção.
            quant_entregadores = len(df['Delivery_person_ID'].unique())
            
            #PE Mostrar no streamlit com o .metric().
            innercol1.metric(label='Entregadores', value=quant_entregadores)
        
        # Container 01, coluna 02
        with innercol2:
            #SA 2. Média de distância de entregas.
            #PE Usar haversine() para calcular distâncias entre coordenadas e criar nova coluna com distâncias calculadas.
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df['Delivery_distance'] = ( df.loc[:, cols]
                                       .apply(lambda x: haversine(  (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])  ), axis=1) )
            
            #PE Tirar média das distâncias de entrega.
            distancia_media_entregas = df['Delivery_distance'].mean()
            
            #PE Mostrar no streamlit com o .metric().
            innercol2.metric(label='Dist. média de entrega', value="{:.1f} km".format(distancia_media_entregas))

    # Colunas 03 e 04
    with outercol2:
        innercol3, innercol4 = st.columns(2)
        # Container 01, coluna 03
        with innercol3:
            #SA 6. Tempo de entrega com festival.
            #P Agrupar entregas entre os de festival e os que não foram em festival. Tirar média e std do tempo de entrega.
            #E .groupby para agrupar e .mean() para média.
            media_tempo_de_entrega_festival = df.loc[:, ['Time_taken(min)', 'Festival']].groupby(['Festival'], as_index=False).mean()
            media_tempo_de_entrega_festival.columns = ['Festival', 'Delivery_time_mean']

            #E .groupby para agrupar e .std() para desvio.
            std_tempo_de_entrega_festival = df.loc[:, ['Time_taken(min)', 'Festival']].groupby(['Festival'], as_index=False).std()
            std_tempo_de_entrega_festival.columns = ['Festival', 'Delivery_time_std']

            tempo_entrega_festival = media_tempo_de_entrega_festival.merge(std_tempo_de_entrega_festival)
            tempo_com_festival = tempo_entrega_festival.loc[1, 'Delivery_time_mean']
            std_com_festival = tempo_entrega_festival.loc[1, 'Delivery_time_std']

            ( innercol3.metric(label='Tempo de entrega com festival', 
                               value="{:.0f} min".format(tempo_com_festival), 
                               delta="{:.0f} min".format(std_com_festival), 
                               delta_color='inverse', help='Tempo de entrega com festival') )
            
        # Container 01, coluna 04
        with innercol4:
            #SA 6. Tempo de entrega sem festival.
            tempo_sem_festival = tempo_entrega_festival.loc[0, 'Delivery_time_mean']
            std_sem_festival = tempo_entrega_festival.loc[0, 'Delivery_time_std']
            
            ( innercol4.metric(label='Tempo de entrega sem festival', 
                               value="{:.0f} min".format(tempo_sem_festival), 
                               delta="{:.0f} min".format(std_sem_festival), 
                               delta_color='inverse', help='Tempo de entrega sem festival') )
   
    st.markdown("""---""")
        

# Container 02
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        #SA 3. Tempo de entrega por cidade.
        st.markdown("#### Tempo de entrega por cidade")
        
        #P Agrupar entregas por cidade, com informação de média e desvio padrão de tempo de entrega.
        #E .groupby() para agrupar, com .agg({}) para calcular média e desvio.
        tempo_entrega_por_cidade = df.loc[:, ['Time_taken(min)', 'City']].groupby(['City']).agg({'Time_taken(min)': ['mean', 'std']}).reset_index()

        tempo_entrega_por_cidade.columns = ['City', 'avg_time', 'std_time']

        #E Usa-se go.Figure() para criar gráfico de barras com incerteza.
        bar_chart = go.Figure()
        bar_chart.add_trace(go.Bar(
                            name='', x=tempo_entrega_por_cidade['City'], y=tempo_entrega_por_cidade['avg_time'],
                            error_y=dict(type='data', array=tempo_entrega_por_cidade['std_time']) ))

        bar_chart.update_layout(barmode='group')
        
        st.plotly_chart(bar_chart, use_container_width=True) 

    with col2:
        #SA 4. Tempo de entrega por cidade e por pedido.
        st.markdown("#### Tempo de entrega por cidade e por pedido")
        
        tempo_entrega_por_cidade_tipo_de_pedido = df.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
        tempo_entrega_por_cidade_tipo_de_pedido.columns = ['City', 'Type_of_order', 'avg_time', 'std_time']
        
        #PE Com st.dataframe(), mostramos a tabela na webpage.
        st.dataframe(tempo_entrega_por_cidade_tipo_de_pedido)

    st.markdown("""---""")
    
    
# Container 03
with st.container():
    
        #SA 5. Gráfico sunburst de tempo de entrega por cidade e tipo de tráfego.
        st.markdown("### Tempo de entrega por cidade e por tipo de tráfego")
        
        tempo_entrega_por_cidade_trafego = df.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
        tempo_entrega_por_cidade_trafego.columns = ['City', 'Road_traffic_density', 'avg_time', 'std_time']

        deliv_time_sunburst_chart = px.sunburst(tempo_entrega_por_cidade_trafego, path=['City', 'Road_traffic_density'], 
                                                values='avg_time', color='std_time', color_continuous_scale='RdBu', 
                                                color_continuous_midpoint=np.average(tempo_entrega_por_cidade_trafego['std_time']))
        
        st.plotly_chart(deliv_time_sunburst_chart)