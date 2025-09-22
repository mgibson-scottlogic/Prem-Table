"""Utils for module data processing"""

def get_current_gameweek(fixtures):
    """A function to calculate the current gameweek, for use in the title"""
    # get all values where the fixture is finished, then get the most recent finished one
    finished_fixtures = fixtures[fixtures.finished_provisional]
    if not finished_fixtures.empty:
        most_recent = fixtures[fixtures.finished_provisional].iloc[-1]
    else:
        return 'Start of Season'
    # get the next fixture after the most recent finished fixture
    try:
        next_fix = fixtures.iloc[most_recent.name + 1]
    except IndexError: # if season is over, there is no next fixture
        return 'End of Season'

    # if the next fixture is: in the same gameweek as the most recent, or has started, it is midweek
    if (next_fix.event == most_recent.event) or (next_fix.started):
        return f'Mid GW{int(next_fix.event)}'
    # if the next fixture is in the next gameweek, the week is over
    if next_fix.event > most_recent.event:
        return f'End of GW{int(most_recent.event)}'
    # if next fixture is in the past, error safely and return blank
    return ""
