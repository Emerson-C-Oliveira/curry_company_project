import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon=" "
)

# image_path = 'C:/Users/emers/Documents/repos/ftc_programacao_python/notebooks/'
image = Image.open( 'logo.png' )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company') # os asteristicos aqui servem como títulos maiores e menores.
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write('# Curry Company Growth Dashboard')
st.markdown(
"""
   Growth dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
   ### Como utilizar esse Growth Dashboard?
   - Visão empresa:
     - Visão gerencial: métricas gerais de comportamento.
     - Visão tática: indicadores semanais de crescimento.
     - Visão geográfica: insights de geolocalização.

   - Visão entragadores:
     - Acompanhamento dos indicadores semanais de crescimento.

   - Visão restaurantes:
     - Indicadores semanais de crescimento dos restaurantes.

   ### Ask for Help
   - Time de Data Science no Discord
       - @emersoncoliveira

""")