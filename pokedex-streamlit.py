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
    subcolumns[i].markdown(f'<div style="width:100%; display: grid; align-items: center; justify-items: center"> <p style="background-color:{type_color_dict.get(type)}; color:{"white" if type_color_dict.get(type) in ["darkgray", "darkpurple", "darkblue", "purple", "blue", "green", "gray"] else "black"}; font-size: 18px; font-weight: bold; width: fit-content; padding: 0.25em 0.5em; border-radius: 15px; margin: 0.25em;">{type.title()}</p> </div>', unsafe_allow_html=True)
    i+=1
    
@st.cache_data
def fetch_learnable_moves(move_df):
  start_index = st.session_state.num_of_moves
  end_index = min(st.session_state.num_of_moves+15, len(learnable_moves))
  for move in learnable_moves[start_index:end_index]:
      move_details = requests.get(move['move']['url']).json()
      move_df.loc[move_details['id']] = [move['move']['name'], move_details['type']['name'], move_details['power'], move_details['accuracy'], move_details['pp'], move_details['damage_class']['name']]
  st.session_state.num_of_moves = end_index
  return move_df

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
  back = spritecol1.toggle('Back Sprite', disabled=sprites[generation][version].get('back_default') == None)
  shiny = spritecol2.toggle('Shiny', disabled=sprites[generation][version].get('front_shiny') == None)
  if sprites[generation][version].get('back_default') == None:
    back = False
  if sprites[generation][version].get('front_shiny') == None:
    shiny = False
  locator1 = 'front_'
  if back:
    locator1 = 'back_'
  locator2 = 'default'
  if shiny:
    locator2 = 'shiny'
  bigspritecol2.image(sprites[generation][version][locator1+locator2], use_column_width=True)

with st.expander('Learnable Moves'):
  if 'move_df' not in st.session_state or st.session_state['current_pokemon_number'] != pokemon_number:
      st.session_state['move_df'] = pd.DataFrame(columns=["ID", "Move", "Type", "Power", "Accuracy", "PP", "Class"]).set_index('ID')
      st.session_state['current_pokemon_number'] = pokemon_number
      st.session_state['num_of_moves'] = 0
      st.cache_data.clear()
  move_df = st.session_state['move_df']
  load_more = st.button('Load More Moves', disabled=st.session_state.num_of_moves == len(learnable_moves))
  if load_more:
    st.session_state['move_df'] = fetch_learnable_moves(st.session_state['move_df'])
  st.table(st.session_state['move_df'])
  st.caption(f"{st.session_state.num_of_moves}/{len(learnable_moves)}")

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