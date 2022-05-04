import argparse
import base64
import json
import requests

APPLICATION_ID = 'Your application id'
APPLICATION_SECRET = 'Your application secret'

def main():
    parser = argparse.ArgumentParser()
    auth =  base64.b64encode(f'{APPLICATION_ID}:{APPLICATION_SECRET}'.encode('utf-8')).decode()
    bodies = requests.get('https://api.astronomyapi.com/api/v2/bodies', headers={'Authorization': f'Basic {auth}'}).json()
    print(json.dumps(bodies))


if __name__ == "__main__":
    main()