from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

def replace_xticks_with_logos(ax, tick_ids, team_crest, min_lim):
    """Replace x-tick labels with team crests"""
    for i, team_id in enumerate(tick_ids):
        img = team_crest[team_id]
        im = OffsetImage(img, zoom=0.18)
        im.image.axes = ax
        ab = AnnotationBbox(im, (i, min_lim), xybox=(0., -30.),
                            frameon=False, xycoords="data",
                            boxcoords="offset points", pad=0)
        ax.add_artist(ab)

def add_comp_logo(ax, comp_name, x, w, points, row_colour):

    """Add a logo to teams with guaranteed european competition"""

    # width
    cxleft = x + w/12
    cxright = x + w/1.09174
    cxwid = cxright - cxleft

    #height
    cybot = points - 4.5 + (3/3.5)
    cytop = points - 4.5 + (3/1.09)
    cyheight = cytop - cybot

    # load comp logo, plot logo and team coloured box behind for visibility
    crb =  Image.open(f"Logos/COMPS/{comp_name}LOGO.png").convert('RGBA')
    ax.imshow(crb, extent=[cxleft, cxright, cybot, cytop], aspect='auto', zorder=5)
    ax.bar(cxleft+(cxwid/2), cyheight, bottom=cybot, width=cxwid,
           color=row_colour, edgecolor=row_colour, lw=1, zorder=4)

def add_key(ax, colours):
    """Add graph key, and calculations to place the key"""
    key_im = Image.open('key.png')

    # horizontal
    kxwid = 3.6
    kxright = int(ax.get_xlim()[1]) - 0.7
    kxleft = kxright - kxwid

    # vertical
    kxheight = 14
    kytop = int(ax.get_ylim()[1]) - 3.9
    kybot = kytop - kxheight

    # plot the image and surrounding box
    ax.imshow(key_im, extent=[kxleft, kxright, kybot, kytop], aspect='auto', zorder=4)
    ax.bar(kxleft+(kxwid/2), kxheight, bottom=kybot, width=kxwid,
            color=colours[3], edgecolor="#808080", lw=2.5)
