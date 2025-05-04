# config.py

import argparse
import os

DATABASE = {
    'host':'         ,
    'user':'        ',
    'password':'        ',
    'database':'      '
}
HAAR_CASCADE_MODEL = ''
API_KEY = "" # os.environ.get('API_KEY')
SPEECH_KEY = '' # os.environ.get('SPEECH_KEY')
SPEECH_REGION = 'eastus' # os.environ.get('SPEECH_REGION')
SPEECH_LANG = 'en-IN'
SPEECH_VOICE = 'en-IN-AashiNeural' # 'en-US-AvaMultilingualNeural'
FACE_DISTANCE = 1 # in meters
APP_SECRET_KEY = ""

def parse_arguments():
    parser = argparse.ArgumentParser(description='Command portal for the application.')
    parser.add_argument('--web', action='store_true', help='Run the web server')
    parser.add_argument('--ai', action='store_true', help='Run the AI engine')
    parser.add_argument('--cs_user', action='store_true', help='Create a super user')
    parser.add_argument('--us_user', action='store_true', help='Update a super user')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    if args.web:
        from web.app import app
        print("Starting the web server...")
        app.run(debug=True)
    
    if args.ai:
        from modules.assistant import assistant
        print("Starting the AI engine...")
        assistant()
        
    if args.cs_user:
        from modules.utils import create_super_user
        email = input("Enter Email: ")
        password = input("Enter password: ")
        res = create_super_user(email, password)
        print(res)

    if args.us_user:
        from modules.utils import update_super_user
        email = input("Enter Email: ")
        password = input("Enter password: ")
        update_super_user(username, password)
        print("Super user updated successfully.")
