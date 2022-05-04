import argparse
import base64
import datetime
import json
import os
import requests

APPLICATION_ID = os.environ.get('APPLICATION_ID', 'Your application id')
APPLICATION_SECRET = os.environ.get('APPLICATION_SECRET', 'Your application secret')

BODIES_ENDPOINT = 'https://api.astronomyapi.com/api/v2/bodies'
POSITIONS_ENDPOINT = f'{BODIES_ENDPOINT}/positions/'
AVAILABLE_BODIES = ["sun", "moon", "mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--planet', type=str, choices=AVAILABLE_BODIES, help='The planet whose position you wish to check')
    parser.add_argument('--lat', type=float, help='Latitude. Required for body positions')
    parser.add_argument('--long', type=float, help='Longitude. Required for body positions')
    args = parser.parse_args()
    body_to_check = args.planet
    auth =  base64.b64encode(f'{APPLICATION_ID}:{APPLICATION_SECRET}'.encode('utf-8')).decode()
    current_datetime = datetime.datetime.now()
    today_as_date = current_datetime.strftime('%Y-%m-%d')
    current_time = current_datetime.strftime('%H:%M:%S')
    if body_to_check:
        uri_body_position = f'{POSITIONS_ENDPOINT}{body_to_check}?latitude={args.lat}&longitude={args.long}&from_date={today_as_date}&to_date={today_as_date}&time={current_time}&elevation=0'
        body_position = requests.get(uri_body_position, headers={'Authorization': f'Basic {auth}'}).json()
        print(json.dumps(body_position))


if __name__ == "__main__":
    main()