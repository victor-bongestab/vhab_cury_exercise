# Bibliotecas de dados
import pandas as pd
from datetime import datetime

# Bibliotecas gráficas
import streamlit as st
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from haversine import haversine # Good for short distances: assumes earth as sphere.



st.set_page_config(page_title="Visao Entregadores", layout='wide')



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
st.markdown('# Marketplace - Visão dos Entregadores')
st.markdown('#### {}'.format(date_slider.strftime("%d-%m-%Y")))
st.markdown("""---""")


# Container 01
with st.container():
    
    #SA 3. Média e desvio padrão das avaliações dos entregadores.

    #PE Organizar avaliações por entregador com .groupby(). Tirar média por entregador com .mean() e tirar média das médias depois.
    avaliacoes_medias_cada_entregador = df.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby('Delivery_person_ID', as_index=False).mean()
    media_geral = avaliacoes_medias_cada_entregador['Delivery_person_Ratings'].mean()
    
    #PE Tirar desvio padrão das médias de cada entregador com .std().
    std_media_geral = avaliacoes_medias_cada_entregador['Delivery_person_Ratings'].std()

    #PE Mostrar valores na tela.
    st.markdown(u'#### Avaliação média dos entregadores: {:.2f} \u00B1 {:.2f}'.format(media_geral, std_media_geral))
    st.markdown("""---""")


# Container 02
with st.container():
    # Título do container 02:
    st.markdown("## Métricas gerais")
    
    outercol1, outercol2 = st.columns(2, gap="large")
    
    # Colunas 01 e 02
    with outercol1:
        innercol1, innercol2 = st.columns(2)
        # Container 02, coluna 01
        with innercol1:
            #SA 1. Menor idade.
            #PE .min() dá o menor valor da coluna.
            menor_idade = df['Delivery_person_Age'].min()
            st.metric(label='Menor idade', value=menor_idade)
        
        # Container 02, coluna 02
        with innercol2:
            #SA 1. Maior idade.
            #PE .max() dá o menor valor da coluna.
            maior_idade = df['Delivery_person_Age'].max()
            st.metric(label='Maior idade', value=maior_idade)

    # Colunas 03 e 04
    with outercol2:
        innercol3, innercol4 = st.columns(2)
        # Container 02, coluna 03
        with innercol3:
            #SA 2. Pior condição de veículo.
            #PE .min() dá o menor valor da coluna.
            pior_veiculo = df['Vehicle_condition'].min()
            st.metric(label='Pior veículo', value=pior_veiculo)
            
        # Container 02, coluna 04
        with innercol4:
            #SA 2. Pior condição de veículo.
            #PE .min() dá o menor valor da coluna.
            melhor_veiculo = df['Vehicle_condition'].max()
            st.metric(label='Melhor veículo', value=melhor_veiculo)
   
    st.markdown("""---""")
        
        
# Container 03
with st.container():
    col1, col2 = st.columns(2)
    
    # Container 03, coluna 01
    with col1:
        #SA 4. Tabela com avaliação por tipo de tráfego.
        st.markdown("#### Avaliação por tipo de tráfego")
        
        #PE Usa-se .groupby() para agrupar avaliações por tráfego e e agg('mean', 'std') para calcular média e desvio padrão.
        avaliacao_por_trafego = df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby(['Road_traffic_density'], as_index=False).agg({'Delivery_person_Ratings':['mean', 'std']})
        
        #PE Muda-se o nome das colunas com .columns.
        avaliacao_por_trafego.columns = ['Road_traffic_density', 'media', 'desvio']
        
        #PE Com st.dataframe(), mostramos a tabela na webpage.
        st.dataframe(avaliacao_por_trafego)
    
    # Container 03, coluna 02
    with col2:
        #SA 5. Tabela com avaliação por tipo climático.
        st.markdown("#### Avaliação por tipo de condição climática")
        
        #PE Usa-se .groupby() para agrupar avaliações por clima e e agg('mean', 'std') para calcular média e desvio padrão.
        avaliacao_por_clima = df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby(['Weatherconditions'], as_index=False).agg({'Delivery_person_Ratings':['mean', 'std']})
        
        #PE Muda-se o nome das colunas com .columns.
        avaliacao_por_clima.columns = ['Weatherconditions', 'media', 'desvio']
        
        #PE Com st.dataframe(), mostramos a tabela na webpage.
        st.dataframe(avaliacao_por_clima)
    
    st.markdown("""---""")
    
    
# Container 04
with st.container():
    col1, col2 = st.columns(2)
    
    # Container 04, coluna 01
    with col1:
        #SA 6. Tabela com 10 entregadores mais rápidos por cidade.
        st.markdown("### 10 entregadores mais rápidos por cidade")
        
        #PE .groupby() para agrupar em relação à média com .mean() por cada cidade e por cada entregador. Usar .sort_values() para ordenar (crescente) e .head() para pegar os 10 primeiros.
        mais_rapidos_urban = ( df.loc[ (df['City'] == 'Urban') , ['Time_taken(min)', 'City', 'Delivery_person_ID'] ]
                              .groupby(['City', 'Delivery_person_ID']).mean()
                              .sort_values('Time_taken(min)').head(10).reset_index() )

        mais_rapidos_metro = ( df.loc[ (df['City'] == 'Metropolitian') , ['Time_taken(min)', 'City', 'Delivery_person_ID'] ]
                              .groupby(['City', 'Delivery_person_ID']).mean()
                              .sort_values('Time_taken(min)').head(10).reset_index() )

        mais_rapidos_semi = ( df.loc[ (df['City'] == 'Semi-Urban') , ['Time_taken(min)', 'City', 'Delivery_person_ID'] ]
                             .groupby(['City', 'Delivery_person_ID']).mean()
                             .sort_values('Time_taken(min)').head(10).reset_index() )

        #PE Concatenar as tabelas com pd.concat() para termos os 10 primeiros de cada cidade juntos.
        mais_rapidos_por_cidade = pd.concat([mais_rapidos_urban, mais_rapidos_metro, mais_rapidos_semi])
        
        #PE Com st.dataframe(), mostramos a tabela na webpage.
        st.dataframe(mais_rapidos_por_cidade)
    
    # Container 04, coluna 02
    with col2:
        #SA 6. Tabela com 10 entregadores mais lentos por cidade.
        st.markdown("### 10 entregadores mais lentos por cidade")
        
        #PE .groupby() para agrupar em relação à média com .mean() por cada cidade e por cada entregador. Usar .sort_values() para ordenar (crescente) e .head() para pegar os 10 primeiros.
        mais_lentos_urban = ( df.loc[ (df['City'] == 'Urban') , ['Time_taken(min)', 'City', 'Delivery_person_ID']]
                             .groupby(['City', 'Delivery_person_ID']).mean()
                             .sort_values('Time_taken(min)', ascending=False).head(10).reset_index() )

        mais_lentos_metro = ( df.loc[ (df['City'] == 'Metropolitian') , ['Time_taken(min)', 'City', 'Delivery_person_ID']]
                             .groupby(['City', 'Delivery_person_ID']).mean()
                             .sort_values('Time_taken(min)', ascending=False).head(10).reset_index() )

        mais_lentos_semi = ( df.loc[ (df['City'] == 'Semi-Urban') , ['Time_taken(min)', 'City', 'Delivery_person_ID']]
                            .groupby(['City', 'Delivery_person_ID']).mean()
                            .sort_values('Time_taken(min)', ascending=False).head(10).reset_index() )

        #PE Concatenar as tabelas com pd.concat() para termos os 10 primeiros de cada cidade juntos.
        mais_lentos_por_cidade = pd.concat([mais_lentos_urban, mais_lentos_metro, mais_lentos_semi])
        
        #PE Com st.dataframe(), mostramos a tabela na webpage.
        st.dataframe(mais_lentos_por_cidade)