"""Utils for module data processing"""

def get_current_gameweek(fixtures):
    """A function to calculate the current gameweek, for use in the title"""
    fixtures = fixtures.sort_values("kickoff_time").reset_index(drop=True)

    finished_fixtures = fixtures[fixtures.finished_provisional]
    if finished_fixtures.empty:
        return 'Start of Season'

    most_recent = finished_fixtures.iloc[-1]

    upcoming_fixtures = fixtures.loc[most_recent.name + 1 :]
    next_fixture = upcoming_fixtures[upcoming_fixtures.status != 'CANCELLED'].head(1)

    if next_fixture.empty:
        return 'End of Season'

    next_fixture = next_fixture.iloc[0]

    # event is gameweek
    if (next_fixture.event == most_recent.event) or (next_fixture.started):
        return f"Mid GW{int(next_fixture.event)}"
    if next_fixture.event > most_recent.event:
        return f"End of GW{int(most_recent.event)}"
    return ""
