class ThresholdLine():
    """Class representing a horizontal competition threshhold line"""
    def __init__(self, position, label, colour, teams, teams_all):
        self.position = position
        self.pts_required = teams_all['max_points'][self.position]
        self.label = label.replace('__', str(self.pts_required))
        self.colour = colour
        self.linestyle = (0, (5, 5))
        self.text = None
        self.line = None
        self.labelpos = self._calculate_label_pos(teams)
        self.label_offset = self.pts_required + 0.12

    def _calculate_label_pos(self, teams):
        for x in teams.itertuples():
            if x.max_points == self.pts_required:
                return x.Index - 0.5
        return None

    def __str__(self):
        return f"{self.position} {self.label} {self.colour}"

    def label_space(self, teams):
        """A function to calculate the positioning of a label on a competition line"""
        # adjust text spacing to not overlap any data bars
        for x in teams.itertuples():
            if x.max_points == self.pts_required:
                label_space = x.Index - 0.5
                break
            label_space = None

        self.labelpos = label_space

    def generate(self, axes):
        """Function to generate the line and plot it on the figure"""
        # only draw the line if there are bars that max out under the value
        # e.g: if image shows pos 1 - 10, dont draw the relegation line, as there is no need
        if self.labelpos is not None:
            lne = axes.axhline(y=self.pts_required, color=self.colour, linestyle=self.linestyle)
            txt = axes.text(self.labelpos, self.label_offset, self.label,
                    color=self.colour, ha='left', weight='semibold', size='medium', va='bottom', zorder=2)
            self.text = txt
            self.line = lne
        else:
            pass