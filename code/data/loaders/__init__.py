"""Factory function to load standings for a given league"""

from . import premier_league
from . import championship

# Add future loaders here
LOADERS = {
    "PL": premier_league.load_fixture_data,
    "ELC": championship.load_fixture_data,
}

def load_standings(league: str):
    """
    Factory function to load standings for a given league.\n
    Current Valid leagues:\n
        PL (English Premier League)
        ELC (English Football League Championship)
    """
    try:
        return LOADERS[league]()
    except KeyError as exc:
        raise ValueError(f"Unknown league code: {league}. Available: {list(LOADERS.keys())}") from exc
