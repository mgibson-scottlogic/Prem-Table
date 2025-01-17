# importing package
import matplotlib.pyplot as plt
import numpy as np


# create data: Team Name, Team Colour, Current Points, Fixtures Played
dayta = [['Aston Villa', 'lightblue', 63, 33], ['Tottenham', 'darkblue', 60, 32], ['Newcastle', 'black', 50, 32], ['Man Utd', 'red', 50, 32], ['Chelsea', 'mediumblue', 47, 31], ['West Ham', 'maroon', 48, 33]]

image1 = "Logos/1.png"
im1 = plt.imread(image1)
barwidth = 0.7



plt.figure(figsize=(9, 15))
# each bar/team
for team, colour, pts, played in dayta:
    cpts = plt.bar(team, pts, color=colour, edgecolor=colour, width=barwidth)
    fixtures_remaining = 38 - played
    bot = pts

    # remaining fixtures
    for i in range(fixtures_remaining):
        cur_bar = plt.bar(team, 3, bottom=bot, color='#d9d9d9', edgecolor="#808080", lw=1.5, width=barwidth)

        # positioning of image and text in upcoming fixture bar
        for bar_im in cur_bar:
            x,y = bar_im.get_xy()
            w, h = bar_im.get_width(), bar_im.get_height()

            xleft = x + w/8.5
            xright = x + w/1.121212
            ybot = y + h/3.5
            ytop = y + h/1.09

            xwid = xright - xleft
            ywid = ytop - ybot
            #print(xwid, ywid)

            axes1 = plt.gca()
            xmin, xmax = axes1.get_xlim()
            xtot = xmax - xmin

            ymin, ymax = axes1.get_ylim()
            ytot = ymax - ymin

            #print(xwid*9/(xtot), ywid*15/(ytot))

            # plot the team logo and the fixture date
            plt.imshow(im1, extent=[xleft, xright, ybot, ytop], aspect='auto', zorder=2)
            plt.text(x+w/2, y+0.15, 'H 14-01', ha='center', fontname='sans-serif', c="#757171", weight='semibold')
        bot += 3

    # remove bottom box outline
    for bar_a in cpts:
        x,y = bar_a.get_xy()
        w, h = bar_a.get_width(), bar_a.get_height()
        #print(x,y,w,h)
        plt.bar(x+w/2, color=bar_a.get_facecolor(), lw=1.5, height=h+0.01, edgecolor=colour, width=barwidth)


current_points = [y[2] for y in dayta]
fixtures_played = [y[3] for y in dayta]

theory_max = [x + (38-y)*3 for x,y in zip(current_points, fixtures_played)]
plt.ylim((min(current_points)-3), (max(theory_max) + 2))
plt.yticks(np.arange((min(current_points)-2), (max(theory_max) + 2), 1))
plt.tick_params(bottom=False, left=False)

plt.title("EPL: The race for European Competitions \n4th to 9th as of 15/05/24", size=17, fontname='sans-serif', weight='semibold')
plt.xlabel("Teams in order of highest possible points total", labelpad=15, size=17, fontname='sans-serif', weight='semibold')
plt.ylabel("Points and remaining fixures in chronological order", labelpad=30, size=17, fontname='sans-serif', weight='semibold')


axes = plt.gca() #Getting the current axis
axes.spines['top'].set_visible(False)
axes.spines['right'].set_visible(False)

axes.spines['bottom'].set_bounds(-1, 5.5)
axes.spines['bottom'].set_linewidth(2)
axes.spines['left'].set_linewidth(2)


plt.savefig('test.png', bbox_inches='tight', pad_inches=0.5, dpi=300)
plt.show()
