"""Load data from the external data APIs"""

from datetime import datetime, timezone
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from PIL import Image

def generate_efl_data():
    """Generate data for the EFL Championship"""

    # Load API Key from .env file in the '/utils' directory.
    # API used: https://www.football-data.org/
    load_dotenv("../utils")
    football_data_key = os.getenv('FOOTBALL_DATA_KEY')
    pd.set_option('future.no_silent_downcasting', True)

    url = 'https://api.football-data.org/v4/'
    headers = { 'X-Auth-Token': football_data_key }

    fdorg = requests.get(url+'competitions/ELC/matches?season=2025',
                         headers=headers, timeout=10).json()
    fixtures = pd.json_normalize(fdorg['matches'])

    fixtures = fixtures.rename(columns={'homeTeam.id': 'team_h',
                                        'awayTeam.id': 'team_a', 
                                        'score.fullTime.home': 'team_h_score', 
                                        'score.fullTime.away': 'team_a_score',
                                        'status': 'finished',
                                        'matchday': 'event',
                                        'awayTeam.name': 'name_x',
                                        'homeTeam.name': 'name_y',
                                        'utcDate': 'kickoff_time'
                                        })
    fixtures = fixtures.replace({'FINISHED': True,
                                 'TIMED': False,
                                 'IN_PLAY': False,
                                 'PAUSED': False,
                                 'SCHEDULED': False})

    teams = requests.get(url+'competitions/ELC/standings', headers=headers, timeout=10).json()
    teams = pd.json_normalize(teams['standings'], 'table')
    teams = teams.rename(columns={'team.tla': 'short_name'})
    teams.sort_values('team.name', inplace=True)

    team_colours = ['#183b90', '#009ee0', '#e21a23', '#ec4040',
                    '#009edc', '#8d8d8d', '#f18a01', '#3a64a3',
                    '#0053a0', '#e40f1b', '#00367a', '#00a650',
                    '#fff500', '#323c9c', '#0799d5', '#1a59a3',
                    '#ee2227', '#4681cf', '#ee1338', '#e1393e', 
                    '#030303', '#fff002', '#173675', '#007b4d']
    teams['colours'] = team_colours
    teams = teams.rename(columns={'team.id': 'id'})

    # replace Sheffield Wednesday short name, as it is the same as Sheffield United's
    teams.loc[teams.id==345, 'short_name'] = "SHW"

    # create dictionary of team crests
    team_crest = {}
    for row in teams.itertuples():
        crest_id = f"https://raw.githubusercontent.com/MatthewG375/Prem-Table/refs/heads/main/Logos/ELC/{row.id}.png"
        crest_id = f"Logos/ELC/{row.id}.png"
        loaded_crest = Image.open(crest_id)
        # loaded_crest = Image.open(requests.get(crest_id,
        #                                        stream=True,
        #                                        timeout=10).raw).convert('RGBA')
        team_crest[row.id] = loaded_crest


    def get_start_time(row):
        fix_time = datetime.strptime(row, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        cur_time = datetime.now(timezone.utc)

        if cur_time > fix_time:
            return True
        return False


    def opponent_difficulty(t_id):
        # determine difficulty of the team by league table position
        pos = teams.loc[teams.id == t_id, 'position'].item()
        if pos <= 4:
            return 5
        if 5 <= pos <= 8:
            return 4
        if 9 <= pos <= 20:
            return 3
        return 2


    fixtures.loc[fixtures["finished"] == "POSTPONED", 'kickoff_time'] = "None"
    fixtures.loc[fixtures["finished"] == "POSTPONED", 'finished'] = False

    fixtures['started'] = [get_start_time(team) for team in fixtures['kickoff_time']]
    fixtures['team_h_difficulty'] = [opponent_difficulty(team) for team in fixtures['team_a']]
    fixtures['team_a_difficulty'] = [opponent_difficulty(team) for team in fixtures['team_h']]

    fixtures['finished_provisional'] = fixtures['finished']

    return teams, fixtures, team_crest


def generate_data():
    """A function to generate the 'teams' and 'df2' dataframes for the EPL"""
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

    # create dictionary of team crests
    team_crest = {}
    for row in teams.itertuples():
        crest_id = f"https://raw.githubusercontent.com/MatthewG375/Prem-Table/refs/heads/main/Logos/PL/{row.id}.png"
        crest_load = Image.open(requests.get(crest_id, stream=True, timeout=10).raw).convert('RGBA')
        # crest_name = f"Logos/Colour/{row.id}.png"
        # crest_load = Image.open(crest_name)
        team_crest[row.id] = crest_load

    return teams, df2, team_crest
