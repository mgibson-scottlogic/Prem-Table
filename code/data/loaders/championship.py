"""Load data from the external Championship API"""

from datetime import datetime, timezone
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from PIL import Image

def load_fixture_data():
    """
    Generate data for the EFL Championship\n
    Load your API Key from .env file in the '/utils' directory.\n
        FOOTBALL_DATA_KEY=[YOUR KEY HERE]\n
    API used: https://www.football-data.org/
    """

    load_dotenv("../utils")
    football_data_api_key = os.getenv('FOOTBALL_DATA_KEY')
    pd.set_option('future.no_silent_downcasting', True)

    url = 'https://api.football-data.org/v4/'
    headers = { 'X-Auth-Token': football_data_api_key }

    raw_response = requests.get(url+'competitions/ELC/matches?season=2025',
                         headers=headers, timeout=10).json()
    fixtures = pd.json_normalize(raw_response['matches'])

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