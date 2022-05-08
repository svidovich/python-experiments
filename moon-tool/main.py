import argparse
import base64
import datetime
import jmespath
import json
import os
import requests

APPLICATION_ID = os.environ.get('APPLICATION_ID', 'Your application id')
APPLICATION_SECRET = os.environ.get('APPLICATION_SECRET', 'Your application secret')

# Lol mansfield fuck u
DEFAULT_LATITUDE = 40.7584 
DEFAULT_LONGITUDE = 82.5154

BODIES_ENDPOINT = 'https://api.astronomyapi.com/api/v2/bodies'
POSITIONS_ENDPOINT = f'{BODIES_ENDPOINT}/positions/'
AVAILABLE_BODIES = ["sun", "moon", "mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]

path_expressions = {
    'moon_phase': 'data.table.rows[0].cells[0].extraInfo.phase.string',
    'constellation': 'data.table.rows[0].cells[0].position.constellation.name'
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--planet', type=str, choices=AVAILABLE_BODIES, help='The planet whose position you wish to check')
    parser.add_argument('--lat', type=float, help='Latitude. Required for body positions')
    parser.add_argument('--long', type=float, help='Longitude. Required for body positions')
    parser.add_argument('-m', '--moon-phase', action='store_true', help='Only return the current moon phase.')
    parser.add_argument('-c', '--constellation', action='store_true', help='Show the constellation of the body.')
    args = parser.parse_args()
    body_to_check = args.planet
    auth =  base64.b64encode(f'{APPLICATION_ID}:{APPLICATION_SECRET}'.encode('utf-8')).decode()
    current_datetime = datetime.datetime.now()
    today_as_date = current_datetime.strftime('%Y-%m-%d')
    current_time = current_datetime.strftime('%H:%M:%S')

    default_parameters = {
        'latitude': DEFAULT_LATITUDE,
        'longitude': DEFAULT_LONGITUDE,
        'from_date': today_as_date,
        'to_date': today_as_date,
        'time': current_time,
        'elevation': 0,
    }

    if body_to_check:
        uri_body_position = f'{POSITIONS_ENDPOINT}{body_to_check}'
        body_position = requests.get(uri_body_position, headers={'Authorization': f'Basic {auth}'}, params=default_parameters).json()
        if args.constellation:
            body_constellation = jmespath.search(path_expressions['constellation'], body_position)
            print(f'{body_to_check.title()} is in the house of {body_constellation}.')
        else:
            print(json.dumps(body_position))
    elif args.moon_phase:
        body_to_check = 'moon'
     
        uri_moon_position = f'{POSITIONS_ENDPOINT}{body_to_check}'
        moon_data = requests.get(uri_moon_position, headers={'Authorization': f'Basic {auth}'}, params=default_parameters).json()

        moon_phase = jmespath.search(path_expressions['moon_phase'], moon_data)

        print(f'The current moon phase is {moon_phase}.')



if __name__ == "__main__":
    main()