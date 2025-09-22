"""Transforms the loaded data with computed fields"""

def get_team_record(team_id, df2):
    """Function to get teams record from their ID"""
    # team_name = teams.loc[teams.id == team_id, 'name'].values[0]

    record_df = df2[ (df2['team_h'] == team_id) | (df2['team_a'] == team_id) ]
    record_df = record_df.reset_index()
    # record_df[['name_y','team_h_score', 'team_a_score', 'name_x']].head(11)

    w = d = l = gd = gf = 0

    for row in record_df.itertuples():
        if row.team_a_score is None or  row.team_h_score is None:
            continue
        # print(row.team_h,row.team_h_score, row.team_a_score, row.team_a)
        if row.team_h == team_id:
            if row.team_h_score > row.team_a_score:
                w += 1
                # print("home win")
            elif row.team_h_score == row.team_a_score:
                d += 1
                # print("home draw")
            elif row.team_h_score < row.team_a_score:
                l += 1
                # print("home loss")

        if row.team_a == team_id:
            if row.team_a_score > row.team_h_score:
                w += 1
                # print("away win")
            elif row.team_a_score == row.team_h_score:
                d += 1
                # print("away draw")
            elif row.team_a_score < row.team_h_score:
                l += 1
                # print("away loss")

    for row in record_df.itertuples():
        if row.team_a_score is None or  row.team_h_score is None:
            continue
        # if team is at home, and the game has happened(==), add home goals and subtract away goals
        if row.team_h == team_id and (row.team_h_score == row.team_h_score):
            gd += row.team_h_score
            gd -= row.team_a_score
            gf += row.team_h_score
        # if team is away, and the game has happened(==), subtract home goals and add away goals
        elif row.team_a == team_id and (row.team_h_score == row.team_h_score):
            gd -= row.team_h_score
            gd += row.team_a_score
            gf += row.team_a_score

    gd = int(gd)
    if gd >= 0:
        gd = str(f'+{gd}')
    else:
        gd = str(gd)

    # fixture is in the future if it has not: Finished, Provisionally Finished, or Started
    remaining_df = df2.loc[ ((~df2['finished']) & (~df2['finished_provisional']) &
                             ( (df2['started'] == False) | (df2['started'].isnull()) )) &
                            ((df2['team_h'] == team_id) | (df2['team_a'] == team_id)) ]
    remaining_df = remaining_df.reset_index()

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
    filtered_df = df2.loc[ ((~df2['finished']) & (~df2['finished_provisional']) &
                            ( (df2['started'] == False) | (df2['started'].isnull()) )) &
                           ((df2['team_h'] == team_id) | (df2['team_a'] == team_id)) ]
    filtered_df = filtered_df.reset_index()
    #filtered_df[['name_y','team_h_score', 'team_a_score', 'name_x']]

    remaining_fix = []
    fix_location = []
    opposition = []
    opp_name = []
    diff = []

    for row in filtered_df.itertuples():
        if row.team_h == team_id:
            location = "H"
            oppos = row.team_a
            tname = row.name_x
            try:
                opp_diff = row.team_h_difficulty
            except AttributeError:
                opp_diff = 3
        else:
            location = "A"
            oppos = row.team_h
            tname = row.name_y
            try:
                opp_diff = row.team_a_difficulty
            except AttributeError:
                opp_diff = 3

        if (row.kickoff_time is None) or (row.kickoff_time == "None"):
            newdate = "TBC"
            opp_diff = "TBC"
        else:
            date = row.kickoff_time[5:10]
            left, right = date.split('-')
            newdate = f"{location} {right}-{left}"
        # print(newdate)
        remaining_fix.append(newdate)
        fix_location.append(location)
        opposition.append(oppos)
        opp_name.append(tname)
        diff.append(opp_diff)

    # print(remaining_fix)
    filtered_df['remaining_fixtures'] = remaining_fix
    filtered_df['fixture_location'] = fix_location
    filtered_df['opposition_id'] = opposition
    filtered_df['opposition_name'] = opp_name
    filtered_df['opposition_difficulty'] = diff

    filtered_df = filtered_df[['remaining_fixtures', 'fixture_location',
                               'opposition_id', 'opposition_name', 'opposition_difficulty']]

    for row in filtered_df.itertuples():
        if row.remaining_fixtures == "TBC":
            # Moves the specified index in dataframe to the top of the dataframe
            filtered_df["new"] = range(1,len(filtered_df)+1)
            filtered_df.loc[filtered_df.index==row.Index, 'new'] = 0
            filtered_df.sort_values("new", inplace=True)
            filtered_df.drop('new', axis=1)

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

    if row == 0:
        pass

    return points, max_pts
