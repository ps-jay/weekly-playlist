import argparse
import datetime
import dateutil.relativedelta
import os

import requests

API_ENDPOINT = 'https://api.spotify.com/v1'
HEADERS = {
    'Accept': 'application/json',
    'Authorization': f"Bearer {os.environ['SPOTIFY_TOKEN']}",
}

CURRENT_DATE = datetime.date.today()

def parse_args():
    """Parse the arguments given to the application"""
    parser = argparse.ArgumentParser(
    )

    parser.add_argument('increment',
        help='New playlist every: day, week, or, month',
        choices=['day', 'week', 'month'])
    parser.add_argument('name_template',
        help='Name the playlist as per template with strftime replacements possible')

    return parser.parse_args()

def create_playlist(template):
    name = CURRENT_DATE.strftime(template)

    data = {
        'name': name,
        'public': False,
        'collaborative': True,
    }

    response = requests.post(f"{API_ENDPOINT}/me/playlists", json=data, headers=HEADERS)
    return response.json()

def lookup_previous_playlist(increment, template):
    if increment == 'day':
        previous_date = CURRENT_DATE - dateutil.relativedelta.relativedelta(days=1)
    elif increment == 'week':
        previous_date = CURRENT_DATE - dateutil.relativedelta.relativedelta(weeks=1)
    elif increment == 'month':
        previous_date = CURRENT_DATE - dateutil.relativedelta.relativedelta(months=1)

    name = previous_date.strftime(template)
    print(f"Looking for {name}")

    previous = None
    params = (
        ('limit', '10'),
    )
    response = requests.get(f"{API_ENDPOINT}/me/playlists", headers=HEADERS, params=params)
    rj = response.json()
    while rj['next'] is not None:
        for playlist in rj['items']:
            if playlist['name'] == name:
                previous = playlist
                break
        if previous:
            break
        params = (
            ('limit', '10'),
            ('offset', f"{rj['offset'] + 10}"),
        )
        response = requests.get(f"{API_ENDPOINT}/me/playlists", headers=HEADERS, params=params)
        rj = response.json()

    return previous


def main():
    args = parse_args()
    previous = lookup_previous_playlist(args.increment, args.name_template)
    if previous:
        print(f"Last {args.increment}'s playlist:\n{previous}")

    new = create_playlist(args.name_template)


if __name__ == "__main__":
    main()
