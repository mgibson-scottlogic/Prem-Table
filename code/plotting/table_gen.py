"""Code to generate a bar graph of English Premier League teams who can still qualify for Europe"""

from datetime import datetime
from collections import defaultdict
import os
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from data.loaders import load_standings
from data.transformers import gen_additional_data, get_team_record, get_remaining_fixtures, points_deductions
from .logos import replace_xticks_with_logos, add_comp_logo
from .threshold import ThresholdLine
from .labels import format_title_and_axes_labels
from .style import style_axes

pd.set_option('display.max_columns', None)


def generate_table(competition: str, lines_to_generate: list, title_text_1: str,
                   file_text: str, pos_one=1, pos_two=20):
    """Function to generate the visualization of the table

    Keyword Arguments:
        competition -- a string denoting which competition to generate the graph for ('PL' or 'ELC)

        lines_to_generate -- a 2D list containing all lines to be shown on the image 
        ( [[position, 'message to show on line', line colour], ...] )
        include __ in the message to replace with the points value of the line

        title_text_1 -- the first line of the image title

        file_text -- the name of the file

        pos_one -- the first position in the table to show on the image (default 1)

        pos_two -- the second position in the table to show on the image (default 20)
    """
    origin_time = time.time()

    # convert competition code into correct data load
    teams, df2, team_crest = load_standings(competition)
    teams, teams_all = gen_additional_data(teams, df2)

    # convert table position to usable numbers
    remove_from_top = pos_one - 1
    remove_from_bottom = len(teams_all.index) - pos_two

    teams.drop(teams.tail(remove_from_bottom).index, inplace=True)
    teams.drop(teams.head(remove_from_top).index, inplace=True)

    # create the canvas and general constants
    starting_x = 18
    step_x = 0.8869
    default_x = 20

    x_offset = {
        24: 0.0120,
        23: 0.0125,
        22: 0.0135,
        21: 0.0140,
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

    fig, ax = plt.subplots(figsize=(starting_x, starting_y))

    data_time = time.time()

    # Fixture Difficulty Colours
    colours = {'1': '#68c47d',
               '2': '#b5f7c6',
               '3': '#e7e7e7',
               '4': '#f5a1b2',
               '5': '#f47272',
               'TBC': '#a1a1a1',
               'CAN': "#fdd663"
               }

    # loop for every team that needs a bar
    for team in teams.itertuples():
        points, max_pts, goal_difference, _goals_for, games_played = get_team_record(team.id, df2)
        goal_difference = "" if points <= 0 else f"GD {goal_difference}"
        games_played = "" if points <= 0 else f"MP {games_played}"

        # Calculate points deductions
        points, max_pts = points_deductions(team.id, points, max_pts)

        # update lowest theoretical points total if new teams is lower
        theory_min = min(theory_min, points)

        # create bar for current points, with team colour
        team_current_bar = ax.bar(team.short_name, points,
                                  color=team.colours, edgecolor=team.colours,
                                  width=barwidth
                                  )
        top_prev = points

        # loop for every remaining fixture for current team: row.id
        fixtures_remaining = get_remaining_fixtures(team.id, df2)
        for fixture in fixtures_remaining.itertuples():

            difficulty_colour = colours[fixture.opposition_difficulty]
            current_fixture = ax.bar(team.short_name, 3, bottom=top_prev,
                                     color=difficulty_colour, edgecolor="#808080",
                                     lw=1.5, width=barwidth
                                     )[0]

            # positioning of image and text in upcoming fixture bar
            x,y = current_fixture.get_xy()
            w, h = current_fixture.get_width(), current_fixture.get_height()

            xleft = x + w/8.5
            xright = x + w/1.121212
            ybot = y + h/3.5
            ytop = y + h/1.09

            # plot the team logo and the fixture date
            opp_crest_grey =  team_crest[fixture.opposition_id].convert('LA')
            ax.imshow(opp_crest_grey, extent=[xleft, xright, ybot, ytop], aspect='auto', zorder=2)

            ax.text(x+w/2, y+0.18, fixture.location_date,
                        ha='center', fontname='sans-serif', c="#757171",
                        weight='semibold', size='x-small')

            # increment counter by 3, as each fixture has a possible value of 3 points
            top_prev += 3

        # remove bottom box outline
        bar_a = team_current_bar[0]
        x,y = bar_a.get_xy()
        w, h = bar_a.get_width(), bar_a.get_height()
        ax.bar(x+w/2, color=bar_a.get_facecolor(),
                lw=1.5, height=h+0.01, edgecolor=team.colours, width=barwidth)

        # goal difference label
        gd_y = points-0.85 if points <2 else points-1
        ax.text(x+w/2, gd_y, goal_difference,
                ha='center', fontname='sans-serif', c='white',
                weight='semibold', size='x-small')

        # matches played label
        mp_y = points-0.35 if points <2 else points-0.5
        ax.text(x+w/2, mp_y, games_played,
                ha='center', fontname='sans-serif', c='white',
                weight='semibold', size='x-small')

    # add_comp_logo(ax, comp_name, x, w, points, row.color)

    # axis is slightly shorter than the number of teams being plotted
    ax_width = len(teams.index) - 0.5

    # add_key(ax, colours[3])

    # offset y axis if bottom would fall on a multiple of 5, for readability
    if (theory_min-3) % 5 == 0:
        theory_min -= 1

    # get the max and min points, then add padding to graph to improve readability
    theory_max = teams['max_points'].max()
    total_y = int((theory_max + 2) - (theory_min-3))

    # if y height under 30, set height to 30 for better visual
    if total_y < 32:
        total_y = 32
        theory_min = theory_max - 30

    if theory_min-3 < 0:
        min_lim = 0
    else:
        min_lim = theory_min-3


    # change limits for improved readability, and set ticks between new limits
    ax.set_ylim((min_lim), (theory_max + 2))

    ticks = np.arange(min_lim + 1, theory_max + 2, 1)
    labels = ["" if tick == 0 else str(tick) for tick in ticks]
    ax.set_yticks(ticks, labels)


    # correct the plot size
    new_x = starting_x - (step_x * (default_x - len(teams.index)))
    new_y = starting_y - (step_y * (default_y - total_y))

    fig.set_size_inches(new_x, new_y)

    # choose correct x offset from x_offset dict
    main_offset = x_offset[len(teams.index)]
    ax.margins(x=main_offset, tight=None)

    title_pos = [pos_one, pos_two]
    y_labelsize = format_title_and_axes_labels(ax, title_text_1, title_pos, df2, teams, total_y)

    # reset teams index for use in generating label position
    teams = teams.reset_index()
    teams_all = teams_all.reset_index()

    dash_width = 5

     # Position, Label, Hex Colour Code
    obj_lst = [ThresholdLine(x[0], x[1], x[2], teams, teams_all) for x in lines_to_generate]
    for line in obj_lst:
        line.generate(ax)

    # Group lines by pts_required
    grouped = defaultdict(list)
    for line in obj_lst:
        grouped[line.pts_required].append(line)

    # Track the count of processed lines per pts_required
    offset_counters = {key: 0 for key in grouped.keys()}

    for line in obj_lst:
        pts = line.pts_required
        group_size = len(grouped[pts])
        idx = offset_counters[pts]

        if group_size > 1:
            total_gap = dash_width * (group_size - 1)
            dash_offset = (group_size - idx) * dash_width  # the offset is in the pattern, not the start point

            # Reverse label offset: first label highest, last label lowest
            line.label_offset += (group_size - 1 - idx) * 0.8

            line.linestyle = (dash_offset, (dash_width, total_gap))
        else:
            # Single line default style
            line.linestyle = (0, (dash_width, dash_width))

        if line.text:
            line.text.set_position((line.labelpos, line.label_offset))

        offset_counters[pts] += 1

    for line in obj_lst:
        line.generate(ax)

    style_axes(ax, ax_width, y_labelsize)

    replace_xticks_with_logos(ax, teams['id'].tolist(), team_crest, min_lim)

    graph_time = time.time()

    date_time = datetime.today().strftime('%d-%m-%y %H.%M')
    title_name = f'{file_text} {date_time}.png'

    if os.getenv("GITHUB_ACTIONS") == "true":
        base_folder = os.path.join(os.getcwd(), "HistoryGenerated", competition)
    else:
        base_folder = os.path.join(os.getcwd(), "History", competition)

    os.makedirs(base_folder, exist_ok=True)

    file_path = os.path.join(base_folder, title_name)

    plt.savefig(file_path, bbox_inches='tight', pad_inches=0.25, dpi=300)
    print(f'Done. \nTime to gen data: {round(data_time - origin_time, 3)} sec.'
          f'\nTime to gen graph: {round(graph_time - data_time, 3)} sec.'
          f'\nTime to save: {round(time.time() - graph_time, 3)} sec.')
    # plt.show()

if __name__ == "__main__":
    print("Please run the code in main.py to generate a graph")
