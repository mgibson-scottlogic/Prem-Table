"""Code to check for updated data from an API"""
import sys
import hashlib
import requests

def generate_pl_data_hash():
    """Check for new data from the Premier League API"""
    base_url = 'https://fantasy.premierleague.com/api/'

    sha256 = hashlib.sha256()

    fixture_data = requests.get(base_url+'fixtures/', timeout=10).json()

    sha256.update(str(fixture_data).encode('utf-8'))
    new_hash = sha256.hexdigest()

    return new_hash

if __name__ == "__main__":
    valid_leagues = ["PL", "EFL"]
    league_to_check = sys.argv[1]
    league_to_check = league_to_check.upper()

    if league_to_check not in valid_leagues:
        print(f"Error: Invalid league '{league_to_check}'. Valid leagues are: {valid_leagues}")
        sys.exit(1)
    elif league_to_check == "PL":
        print(generate_pl_data_hash())
    elif league_to_check == "EFL":
        print("EFL data hash generation not yet implemented")
