"""Load data from the external Premier League API"""

import requests
import pandas as pd
from PIL import Image

def load_fixture_data():
    """
    Generates data for the English Premier League\n
    No API key needed, free access available to the Fantasy PL API\n
    API used: https://fantasy.premierleague.com/api/
    """
    # base url for all FPL API endpoints
    base_url = 'https://fantasy.premierleague.com/api/'

    # get data from fixtures endpoint
    fix = requests.get(base_url+'fixtures/', timeout=10).json()

    # create fixtures dataframe
    fixtures = pd.json_normalize(fix)

    # get data from bootstrap-static endpoint
    r = requests.get(base_url+'bootstrap-static/', timeout=10).json()

    # create teams dataframe
    teams = pd.json_normalize(r['teams'])

    # add team colours to dataframe CHAMPIONS: #c99b05
    team_colours = ['#e20814', '#91beea', "#690039", '#ca0b17', '#b60501',
                    '#004a9b', '#021581', '#004b97', '#024593', '#282624', 
                    "#ffdf1a", '#b30011', '#b1d4fa', '#dc1116', '#0d0805', 
                    '#f4031c', '#d20911', '#152055', '#7d2d3f', '#feb906']
    teams['colours'] = team_colours

    # join fixtures to teams
    df = pd.merge(
        left=fixtures,
        right=teams,
        left_on='team_a',
        right_on='id'
    )

    df2 = pd.merge(
        left=df,
        right=teams,
        left_on='team_h',
        right_on='id'
    )

    df2['status'] = 'SCHEDULED'
    df2.loc[df2['finished'], 'status'] = 'FINISHED'
    df2.loc[
        (df2['started']) & (~df2['finished']), 'status'
    ] = 'IN_PLAY'

    # create dictionary of team crests
    team_crest = {}
    for row in teams.itertuples():
        crest_id = f"https://raw.githubusercontent.com/MatthewG375/Prem-Table/refs/heads/main/Logos/PL/{row.id}.png"
        crest_load = Image.open(requests.get(crest_id, stream=True, timeout=10).raw).convert('RGBA')
        # crest_name = f"Logos/Colour/{row.id}.png"
        # crest_load = Image.open(crest_name)
        team_crest[row.id] = crest_load

    return teams, df2, team_crest
