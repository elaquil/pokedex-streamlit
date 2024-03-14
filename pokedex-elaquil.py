import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import requests

def get_details(poke_number):
    ''' Create an entry for our favourite pokemon '''
    try:
        url = f'https://pokeapi.co/api/v2/pokemon/{poke_number}/'
        response = requests.get(url)
        pokemon = response.json()
        return (pokemon['name'], pokemon['height'], pokemon['weight'], 
                len(pokemon['moves']), [type['type']['name'] for type in pokemon['types']], 
                pokemon['sprites']['other']['official-artwork']['front_default'],
                pokemon['cries'],
                pokemon['moves'],
                pokemon['sprites']['versions'])
    except:
        return 'Error', np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN
      
def render_types(column, types):
  subcolumns = column.columns(len(types))
  i = 0
  for type in types:
    subcolumns[i].markdown(f'<div style="width:100%; display: grid; align-items: center; justify-items: center"> <p style="background-color:{type_color_dict.get(type)}; color:{"white" if type_color_dict.get(type) in ["darkgray", "darkpurple", "darkblue", "purple", "blue", "green", "gray"] else "black"}; font-size: 18px; font-weight: bold; width: fit-content; padding: 0.5em; border-radius: 15px; margin: 0.25em;">{type.title()}</p> </div>', unsafe_allow_html=True)
    i+=1
    
type_color_dict = {
    'normal': 'gray', 
    'fire': 'orange', 
    'flying': 'gray',
    'water': 'blue',
    'bug': 'green',
    'poison': 'purple',
    'electric': 'yellow',
    'ground': 'brown',
    'fairy': 'pink',
    'grass': 'lightgreen',
    'fighting': 'red',
    'psychic': 'lightpurple',
    'rock': 'darkgray',
    'steel': 'darkgray',
    'ice': 'lightblue',
    'ghost': 'darkpurple',
    'dragon': 'lightblue',
    'dark': 'purple',
    'fairy': 'pink',
    'stellar': 'cyan'}

st.title("Pokedex!")

pokemon_number = st.number_input('Enter a pokemon number:', min_value=1, 
                                  max_value=1008, value=1, step=1)

name, height, weight, num_moves, types, official_art, cries, learnable_moves, sprites = get_details(pokemon_number)

height_data = {'Pokemon': ['Charmander', name.title(), 'Charizard'],
                'Height': [6, height, 17]}

graph_colors = ['lightgray', type_color_dict.get(types[0]), 'lightgray']

col1, col2 = st.columns(2)

col1.header(f"#{pokemon_number} - {name.title()}")
col1.image(official_art, use_column_width=True)
col2.table(pd.DataFrame({'Attribute': ['Height', 'Weight', 'Number of Moves'],
              'Value': [height, weight, num_moves]}).set_index('Attribute'))
col2.subheader('Types')

render_types(col2, types)

col2.subheader('Cry')
if cries.get('legacy') != None:
  cry_choice = col2.selectbox('', list(cries.keys()))
else:
  cry_choice = list(cries.keys())[0]
col2.audio(cries.get(cry_choice), format='audio/wav')

with st.expander('Sprites'):
  bigspritecol1, bigspritecol2 = st.columns(2)
  generation = bigspritecol1.selectbox('Generation', list(sprites.keys()))
  version = bigspritecol1.selectbox('Version', list(sprites[generation].keys()))
  spritecol1, spritecol2 = bigspritecol1.columns(2)
  back = spritecol1.toggle('Back Sprite', disabled=generation in ['generation-vi', 'generation-vii', 'generation-viii'])
  shiny = spritecol2.toggle('Shiny', disabled=generation == 'generation-i' or version == 'icons')
  if generation in ['generation-vi', 'generation-vii', 'generation-viii']:
    back = False
  if generation == 'generation-i' or version == 'icons':
    shiny = False
  locator1 = 'front_'
  if back:
    locator1 = 'back_'
  locator2 = 'default'
  if shiny:
    locator2 = 'shiny'
  bigspritecol2.image(sprites[generation][version][locator1+locator2], use_column_width=True)

with st.expander('Learnable Moves'):
  move_df = pd.DataFrame({'Move': [move['move']['name'].replace("-", " ").title() for move in learnable_moves], 'URL': [move['move']['url'] for move in learnable_moves]}).set_index('URL')
  st.table(move_df)

comparisoncol1, comparisoncol2 = st.columns(2)

with comparisoncol1.expander('Height Comparison'):
  height_df = pd.DataFrame(height_data)
  fig, ax = plt.subplots()
  sns.barplot(x='Pokemon', y='Height', data=height_df, ax=ax, 
              palette=graph_colors, )
  ax.set_xlabel('Pokemon', fontweight='bold', fontsize=12)
  ax.set_ylabel('Height', fontweight='bold', fontsize=12)
  st.pyplot(fig)
  
with comparisoncol2.expander('Weight Comparison'):
  weight_df = pd.DataFrame({'Pokemon': ['Charmander', name.title(), 'Charizard'],
                            'Weight': [8.5, weight, 90.5]})
  fig, ax = plt.subplots()
  sns.barplot(x='Pokemon', y='Weight', data=weight_df, ax=ax, 
              palette=graph_colors)
  ax.set_xlabel('Pokemon', fontweight='bold', fontsize=12)
  ax.set_ylabel('Weight', fontweight='bold', fontsize=12)
  st.pyplot(fig)