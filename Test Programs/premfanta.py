import requests, json
from pprint import pprint
import pandas as pd

# base url for all FPL API endpoints
base_url = 'https://fantasy.premierleague.com/api/'

# get data from bootstrap-static endpoint
r = requests.get(base_url+'bootstrap-static/').json()


pd.set_option('display.max_columns', None)


# create players dataframe
players = pd.json_normalize(r['elements'])

# show some information about first five players
players[['id', 'web_name', 'team', 'element_type']].head()

# create teams dataframe
teams = pd.json_normalize(r['teams'])

teams.head()