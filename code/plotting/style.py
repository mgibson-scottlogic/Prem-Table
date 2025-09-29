"""Axis layout styling"""

import matplotlib.ticker as plticker
from matplotlib.ticker import AutoMinorLocator

def style_axes(ax, ax_width, y_labelsize):
    """Apply styling to axes (grid, ticks, spines)."""
    intervals = float(5)
    loc = plticker.MultipleLocator(base=intervals)
    ax.yaxis.set_major_locator(loc)
    minor_locator = AutoMinorLocator(intervals)
    ax.yaxis.set_minor_locator(minor_locator)

    ax.tick_params(axis='y', which='both', length=4, width=1)
    ax.tick_params(axis='x', which='both', pad=15)
    ax.set_axisbelow(True)
    ax.grid(which='major', axis='y', linestyle=(0, (4, 4)))

    ax2 = ax.twinx()
    ax2.set_ylabel("Pgl", labelpad=15, size=y_labelsize, fontname="sans-serif",
                   weight="semibold", color="w", zorder=0)
    ax2.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
    ax2.tick_params(left=False, right=False, labelleft=False,
                    labelbottom=False, labelright=False, bottom=False)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_bounds(-1, ax_width)
    ax.spines['bottom'].set_linewidth(2)
    ax.spines['left'].set_linewidth(2)
