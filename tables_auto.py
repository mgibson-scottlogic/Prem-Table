"""Code to generate a bar graph of English Premier League teams who can still qualify for Europe"""

# importing package
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import requests
import pandas as pd

pd.set_option('display.max_columns', None)


def generate_data():
    """A function to generate the 'teams' and 'df2' dataframes"""
    # base url for all FPL API endpoints
    BASE_URL = 'https://fantasy.premierleague.com/api/'


    # get data from fixtures endpoint
    fix = requests.get(BASE_URL+'fixtures/', timeout=10).json()


    # create fixtures dataframe
    fixtures = pd.json_normalize(fix)


    # get data from bootstrap-static endpoint
    r = requests.get(BASE_URL+'bootstrap-static/', timeout=10).json()


    # create teams dataframe
    teams = pd.json_normalize(r['teams'])

    # add team colours to dataframe
    team_colours = ['#e20814', '#91beea', '#ca0b17', '#b60501', '#004a9b',
                    '#021581', '#004b97', '#024593', '#282624', '#0c3e94',
                    '#13428d', '#b30011', '#b1d4fa', '#dc1116', '#0d0805',
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

    return teams, df2


def get_team_record(team_id, df2):
    """Function to get teams record from their ID"""
    # team_name = teams.loc[teams.id == team_id, 'name'].values[0]

    record_df = df2[ (df2['team_h'] == team_id) | (df2['team_a'] == team_id) ]
    record_df = record_df.reset_index()
    # record_df[['name_y','team_h_score', 'team_a_score', 'name_x']].head(11)

    w = 0
    d = 0
    l = 0

    gd = 0
    gf = 0

    for row in record_df.itertuples():
        # print(row['name_y'],row['team_h_score'], row['team_a_score'], row['name_x'])
        if row.team_h == team_id and (row.team_h_score > row.team_a_score):
            w += 1
            # print("home win")
        elif row.team_h == team_id and (row.team_h_score == row.team_a_score):
            d += 1
            # print("home draw")
        elif row.team_h == team_id and (row.team_h_score < row.team_a_score):
            l += 1
            # print("home loss")

        if row.team_a == team_id and (row.team_a_score > row.team_h_score):
            w += 1
            # print("away win")
        elif row.team_a == team_id and (row.team_a_score == row.team_h_score):
            d += 1
            # print("away draw")
        elif row.team_a == team_id and (row.team_a_score < row.team_h_score):
            l += 1
            # print("away loss")

    for row in record_df.itertuples():
        # if team is at home, add home goals and subtract away goals
        if row.team_h == team_id and (row.team_h_score == row.team_h_score):
            gd += row.team_h_score
            gf += row.team_h_score
            gd -= row.team_a_score
        # if team is away, subtract home goals and add away goals
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
    remaining_df = df2[ ((df2['finished'] == False) & (df2['finished_provisional'] == False) & (df2['started'] == False)) &
                        ((df2['team_h'] == team_id) | (df2['team_a'] == team_id)) ]
    remaining_df = remaining_df.reset_index()

    pts = int((w*3)+(d))

    # when testing smaller, - amount of removed fixtures here
    left = int(len(remaining_df))
    max_theory = int(pts + 3*left)

    # ply = int(w+d+l)
    # print(f"{team_name} Record: Played: {ply}, Won: {w}, Draw: {d}, Loss: {l}, Points: {pts}, Goal Difference: {gd}, Remaining: {left}")

    return pts, max_theory, gd, gf


def get_remaining_fixtures(team_id, df2):
    """Takes a team ID and returns a pandas dataframe of remaining fixtures."""
    filtered_df = df2[ ((df2['finished'] == False) & (df2['finished_provisional'] == False) & (df2['started'] == False)) &
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
            opp_diff = row.team_h_difficulty
        else:
            location = "A"
            oppos = row.team_h
            tname = row.name_y
            opp_diff = row.team_a_difficulty

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

    filtered_df = filtered_df[['remaining_fixtures', 'fixture_location', 'opposition_id', 'opposition_name', 'opposition_difficulty']]

    # testing for smaller image size, need to -10 to remaining as well
    # filtered_df.drop(filtered_df.tail(10).index, inplace=True)


    return filtered_df


def generate_table(pos_one=1, pos_two=20):
    """Function to generate the visualization of the table
    
    Keyword Arguments:
    pos_one -- the first position in the table to show on the image (default 1)
    pos_two -- the second position in the table to show on the image (default 20)
    """
    # use the global teams variable
    teams, df2 = generate_data()


    # add max points row, goal difference, and goals scored to dataframe (for H2H tiebreakers)
    max_points = []
    gd = []
    gf = []
    for team in teams.itertuples():
        points, max_pts, goal_difference, goals_for = get_team_record(team.id, df2)
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


    # convert table position to usable numbers
    remove_from_top = pos_one - 1
    remove_from_bottom = 20 - pos_two

    teams.drop(teams.tail(remove_from_bottom).index, inplace=True)
    teams.drop(teams.head(remove_from_top).index, inplace=True)


    # create the canvas and general constants
    starting_x = 18
    step_x = 0.8869
    default_x = 20

    x_offset = {
        20: 0.0150,
        19: 0.0160,
        18: 0.0175,
        17: 0.0185,
        16: 0.0200,
        15: 0.0210,
        14: 0.0225,
        13: 0.0240,
        12: 0.0260,
        11: 0.0280,
        10: 0.0305,
        9: 0.0330,
        8: 0.0395,
        7: 0.0440,
        6: 0.0550,
        5: 0.0660,
        4: 0.0825,
        3: 0.1130,
        2: 0.1750 }

    starting_y = 26
    step_y = 0.2601
    default_y = 100

    barwidth = 0.7
    theory_min = 114
    plt.figure(figsize=(starting_x, starting_y))

    # Fixture Difficulty Colours
    colours = {2: '#b5f7c6', 3: '#e7e7e7', 4: '#f5a1b2', 5: '#f47272'}

    # create dictionary of team crests
    team_crest = {}
    for row in teams_all.itertuples():
        crest_name = f"Logos/{row.id}.png"
        crest_load = plt.imread(crest_name)
        team_crest[row.id] = crest_load

    # loop for every team that needs a bar
    for row in teams.itertuples():
        points, max_pts, goal_difference, goals_for = get_team_record(row.id, df2)
        goal_difference = f'GD {goal_difference}'

        # update lowest theoretical points total if new teams is lower
        theory_min = min(theory_min, points)

        # create bar for current points, with team colour
        cpts = plt.bar(row.name, points, color=row.colours, edgecolor=row.colours, width=barwidth)
        bot = points

        # loop for every remaining fixture for current team: row['id]
        fixtures_remaining = get_remaining_fixtures(row.id, df2)
        for fx in fixtures_remaining.itertuples():

            dif_col = colours[fx.opposition_difficulty]
            cur_bar = plt.bar(row.name, 3, bottom=bot,
                              color=dif_col, edgecolor="#808080", lw=1.5, width=barwidth)
            perma_y = points

            # positioning of image and text in upcoming fixture bar
            for bar_im in cur_bar:
                x,y = bar_im.get_xy()
                w, h = bar_im.get_width(), bar_im.get_height()

                xleft = x + w/8.5
                xright = x + w/1.121212
                ybot = y + h/3.5
                ytop = y + h/1.09

                # plot the team logo and the fixture date
                imdis =  team_crest[fx.opposition_id]
                plt.imshow(imdis, extent=[xleft, xright, ybot, ytop], aspect='auto', zorder=2)

                plt.text(x+w/2, y+0.18, fx.remaining_fixtures,
                         ha='center', fontname='sans-serif', c="#757171",
                         weight='semibold', size='x-small')

            # goal difference label
            plt.text(x+w/2, perma_y-0.5, goal_difference,
                     ha='center', fontname='sans-serif', c='white',
                     weight='semibold', size='x-small')

            # increment counter by 3, as each fixture has a possible value of 3 points
            bot += 3

        # remove bottom box outline
        for bar_a in cpts:
            x,y = bar_a.get_xy()
            w, h = bar_a.get_width(), bar_a.get_height()
            #print(x,y,w,h)
            plt.bar(x+w/2, color=bar_a.get_facecolor(),
                    lw=1.5, height=h+0.01, edgecolor=row.colours, width=barwidth)

    # axis is slightly shorter than the number of teams being plotted
    ax_width = len(teams.index) - 0.5

    # get the max and min points, then add padding to graph to improve readability
    theory_max = teams['max_points'].max()
    total_y = int((theory_max + 2) - (theory_min-3))
    plt.ylim((theory_min-3), (theory_max + 2))
    plt.yticks(np.arange((theory_min-2), (theory_max + 2), 1))

    # correct the plot size
    new_x = starting_x - (step_x * (default_x - len(teams.index)))
    new_y = starting_y - (step_y * (default_y - total_y))

    plt.gcf().set_size_inches(new_x, new_y)


    # choose correct x offset from x_offset dict
    main_offset = x_offset[len(teams.index)]
    plt.margins(x=main_offset, tight=None)


    # format position numbers
    title_pos = [remove_from_top+1, 20 - remove_from_bottom]
    for i, x in enumerate(title_pos):
        if x == 1:
            title_pos[i] = '1st'
        elif x == 2:
            title_pos[i] = '2nd'
        elif x == 3:
            title_pos[i] = '3rd'
        else:
            title_pos[i] = f'{title_pos[i]}th'


    # set axis lables and title
    cur_day = datetime.today().strftime('%d-%m-%y')
    title_text = (
        f'EPL: The race for European Competitions'
        f'\n{title_pos[0]} to {title_pos[1]} as of {cur_day}'
        )

    plt.title(title_text, size=17, fontname='sans-serif', weight='semibold')
    plt.xlabel("Teams in order of highest possible points total",
               labelpad=15, size=17, fontname='sans-serif', weight='semibold')
    plt.ylabel("Points and remaining fixures in chronological order",
                labelpad=30, size=17, fontname='sans-serif', weight='semibold')
    plt.xticks(rotation=60)


    # add lines denoting UCL, UEL and CONF qualification: CONF #00be14
    teams_all = teams_all.reset_index()
    ucl_required = teams_all['max_points'][4]
    plt.axhline(y=ucl_required, color='#00004b', linestyle=(0, (5, 5)) )
    plt.text(ax_width, ucl_required+0.25, f"Above {ucl_required} points guarantees UCL",
             color='#00004b', ha='center', weight='semibold', size='medium')

    # offset the line and label if overlapping UCL and UEL
    uel_required = teams_all['max_points'][5]
    if uel_required == ucl_required:
        stylo_uel = (5, (5,5))
        offset = -0.25
        alig = 'top'
    else:
        stylo_uel = (0, (5,5))
        offset = 0.25
        alig = 'baseline'

    plt.axhline(y=uel_required, color='#ff6900', linestyle=stylo_uel)
    plt.text(ax_width, uel_required+offset, f"Above {uel_required} points guarantees UEL",
             color='#ff6900', ha='center', weight='semibold', size='medium', va=alig) #va='top',


    # Axis modifications
    axes = plt.gca() #Getting the current axis
    axes.spines['top'].set_visible(False)
    axes.spines['right'].set_visible(False)

    axes.spines['bottom'].set_bounds(-1, ax_width)
    axes.spines['bottom'].set_linewidth(2)
    axes.spines['left'].set_linewidth(2)

    date_time = datetime.today().strftime('%d-%m-%y %H.%M')
    title_name = f'History/PL Europe Race {date_time}.png'
    plt.savefig(title_name, bbox_inches='tight', pad_inches=0.5, dpi=300)
    print('Done')
    # plt.show()

generate_table(1, 9)
