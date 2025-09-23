"""Transforms the loaded data with computed fields"""

import numpy as np
import pandas as pd

def get_team_record(team_id, df2):
    """Function to get teams record from their ID"""
    # team_name = teams.loc[teams.id == team_id, 'name'].values[0]

    record_df = df2[ (df2['team_h'] == team_id) | (df2['team_a'] == team_id) ]
    record_df = record_df.reset_index()
    # record_df[['name_y','team_h_score', 'team_a_score', 'name_x']].head(11)

    w = d = l = gd = gf = 0
    record_df = record_df.query("status != 'CANCELLED' and team_a_score.notnull() and team_h_score.notnull()")

    for row in record_df.itertuples():
        score_for  = row.team_h_score if row.team_h == team_id else row.team_a_score
        score_against = row.team_a_score if row.team_h == team_id else row.team_h_score

        # W/D/L
        if score_for > score_against:
            w += 1
        elif score_for == score_against:
            d += 1
        else:
            l += 1

        # GD / GF
        gd += score_for - score_against
        gf += score_for


    gd = int(gd)
    if gd >= 0:
        gd = str(f'+{gd}')
    else:
        gd = str(gd)

    # fixture is in the future if it has not: Finished, Provisionally Finished, or Started
    remaining_df = df2.query(
            "(status == 'CANCELLED' or status != 'FINISHED') "
            "and (team_h == @team_id or team_a == @team_id)"
        ).reset_index()

    pts = int((w*3)+(d))

    # when testing smaller, - amount of removed fixtures here
    left = int(len(remaining_df))
    max_theory = int(pts + 3*left)

    ply = int(w+d+l)
    # print(f"{team_name} Record: Played: {ply}, Won: {w}, Draw: {d}, Loss: {l},"
    #       f"Points: {pts}, Goal Difference: {gd}, Remaining: {left}")

    return pts, max_theory, gd, gf, ply


def get_remaining_fixtures(team_id, df2):
    """Takes a team ID and returns a pandas dataframe of remaining fixtures."""

    filtered_df = df2.query(
        "(status == 'CANCELLED' or status != 'FINISHED') "
        "and (team_h == @team_id or team_a == @team_id)"
    ).reset_index()

    #filtered_df[['name_y','team_h_score', 'team_a_score', 'name_x']]

    filtered_df['fixture_location'] = np.where(
        filtered_df['team_h'] == team_id,
        'H', 
        'A')

    filtered_df['opposition_id'] = np.where(
        filtered_df['team_h'] == team_id,
        filtered_df['team_a'],
        filtered_df['team_h']
    )

    filtered_df['opposition_name'] = np.where(
        filtered_df['team_h'] == team_id,
        filtered_df['name_x'],
        filtered_df['name_y']
    )

    filtered_df['opposition_difficulty'] = np.where(
        filtered_df['team_h'] == team_id,
        filtered_df.get('team_h_difficulty', 3),
        filtered_df.get('team_a_difficulty', 3)
    )

    filtered_df['kickoff_time'] = pd.to_datetime(filtered_df['kickoff_time'], errors='coerce')
    filtered_df['location_date'] = np.where(
        filtered_df['status'] == 'CANCELLED',
            'TBC',
            np.where(
                filtered_df['kickoff_time'].isna(),
                'TBC',
                filtered_df['fixture_location'] + ' ' + filtered_df['kickoff_time'].dt.strftime('%d-%m')
            )
        )

    # cancelled
    filtered_df['opposition_difficulty'] = np.where(
        filtered_df['status'] == 'CANCELLED',
        'CAN',
        np.where((filtered_df['kickoff_time'].isnull()) | (filtered_df['kickoff_time'] == 'None'),
                 'TBC',
                 filtered_df['opposition_difficulty'])
    )

    # print(remaining_fix)

    filtered_df = filtered_df[['location_date', 'fixture_location',
                               'opposition_id', 'opposition_name', 'opposition_difficulty']]

    # move TBC fixtures to the top of the frame (bottom fixture on generated bar)
    filtered_df["new"] = (filtered_df["location_date"] != "TBC").astype(int)
    filtered_df.sort_values("new", inplace=True)
    filtered_df = filtered_df.drop("new", axis=1)

    # testing for smaller image size, need to -10 to remaining as well
    # filtered_df.drop(filtered_df.tail(10).index, inplace=True)
    return filtered_df

def putfirst(df, i):
    "Moves the specified index 'i' in dataframe 'df' to the top of the dataframe"
    df["new"] = range(1,len(df)+1)
    df.loc[df.index==i, 'new'] = 0
    df.sort_values("new", inplace=True)
    df.drop('new', axis=1)


def gen_additional_data(teams, df2):
    '''Generates additional data for each team'''
    # add max points row, goal difference, and goals scored to dataframe (for H2H tiebreakers)
    max_points = []
    gd = []
    gf = []
    for team in teams.itertuples():
        points, max_pts, goal_difference, goals_for, _played = get_team_record(team.id, df2)

        # Calculate points deductions for sorting purposes
        points, max_pts = points_deductions(team.id, points, max_pts)

        max_points.append(max_pts)
        gd.append(int(goal_difference))
        gf.append(goals_for)

    teams['max_points'] = max_points
    teams['goal_difference'] = gd
    teams['goals_for'] = gf
    teams = teams.sort_values(by=['max_points', 'goal_difference', 'goals_for'],
                            ascending=[False, False, False])

    # make dataframe with all teams in, in order to remove extraneous teams from main dataset
    teams_all = teams.copy()

    return teams, teams_all


def points_deductions(row, points, max_pts):
    '''Calculate points deductions for the current team.

    Example:
    if row == 356: # SHU: 2pt deduction for 24/25 ELC
        points -= 2
        max_pts -= 2
        return points, max_pts
    '''
    # Calculate points deductions
    # 2025/26: No current points deductions

    if row == 0:
        pass

    return points, max_pts
