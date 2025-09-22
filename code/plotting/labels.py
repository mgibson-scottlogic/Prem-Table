from datetime import datetime
from utils import utils
from matplotlib.axes import Axes

def ordinal_suffix(n: int) -> str:
    """Convert integer into its ordinal representation (1 -> 1st)."""
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return f"{n}{suffix}"

def format_title_and_axes_labels(ax: Axes, base_title, title_pos, df2, teams, total_y):
    """Generate formatted title string for chart"""
    title_pos = [ordinal_suffix(x) for x in title_pos]

    cur_day = datetime.today().strftime('%d-%m-%y')

    title_text = (
        f"{base_title}\n"
        f"{title_pos[0]} to {title_pos[1]} as of {cur_day}, {utils.get_current_gameweek(df2)}   "
    )

    x_labelsize = 17
    y_labelsize = 17

    if total_y < 40:
        y_labelsize = 15

    if len(teams.index) < 10:
        x_labelsize = 15

    ax.set_title(title_text, size=16, fontname='sans-serif', weight='semibold')

    ax.set_xlabel("Teams in order of highest possible points total   ",
            labelpad=15, size=x_labelsize, fontname='sans-serif', weight='semibold', loc='center')
    ax.set_ylabel("Points and remaining fixures in chronological order",
            labelpad=15, size=y_labelsize, fontname='sans-serif', weight='semibold')
    ax.tick_params(axis='x', rotation=60, labelcolor='w')

    return y_labelsize
