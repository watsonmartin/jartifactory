import argparse
import os
import logging
import requests
import dotenv
from requests.auth import HTTPBasicAuth
import datetime
from getpass import getpass
from datetime import timedelta

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

ARTIFACTORY_HOST = os.environ.get('JARTIFACTORY_HOST')

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TOKEN_DURATION = 86400 # 24 hours 

TOKEN_EXPIRED_MESSAGE = "Token expired. Please sign in again with \'python jartifactory.py --sign-in\'"
MISSING_KEY_MESSAGE = "Unable to find valid Artifactory API Key. Please sign in with \'python jartifactory.py --sign-in\'"

REPOSITORY_PACKAGE_TYPES = [
    'alpine', 'cargo', 'composer', 'bower', 'chef', 'cocoapods', 'conan', 'cran', 'debian',
    'docker', 'helm', 'gems', 'gitlfs', 'go', 'gradle', 'ivy', 'maven', 'npm', 'nuget', 'opkg',
    'pub', 'puppet', 'pypi', 'rpm', 'sbt', 'swift', 'terraform', 'vagrant', 'yum', 'generic'
    ]

if ARTIFACTORY_HOST is None:
    ARTIFACTORY_HOST = "https://wmartinassignment.jfrog.io/artifactory"

def token_expired():
    if 'TOKEN_EXPIRATION' in os.environ and datetime.datetime.now() < datetime.datetime.strptime(os.environ['TOKEN_EXPIRATION'], TIME_FORMAT):
        logging.debug("Token not expired")
        return False
    return True

def get_token():
    return os.environ.get('JARTIFACTORY_TOKEN')

def get_user_info():
    username = input("Username: ")
    password = getpass()
    return {
        "username": username,
        "password": password
    }

def get_create_user_details():
    email = input("Email: ")
    username = input("Username (default same as email): ")
    if username == "":
        username = email
    password = getpass()
    return {
        "username": username,
        "email": email,
        "password": password
    }


parser = argparse.ArgumentParser(description='Interact with JFrog Artifactory from the command line.')

parser.add_argument('--set-default-host', metavar='host', nargs=1, help='Sets hostname of the artifactory instance where jartifactory.py will carry out operations by default.')
parser.add_argument('--sign-in',  action='store_true', help='Sign in to Artifactory in order to allow jartifactory.py to carry out authenticated actions.')
parser.add_argument('--ping', '-p', action='store_true', help="Sends a system ping to the Artifactory host.")
parser.add_argument('--version', '-v', action='store_true', help="Gets the version of Artifactory running on Artifactory host.")
parser.add_argument('--create-user', action='store_true', help='Prompts user to enter details for new Artifactory user to be created, then creates that user.')
parser.add_argument('--get-storage-info', action='store_true', help='Returns storage summary information regarding binaries, file store, and repositories.')
parser.add_argument('--delete-user', metavar='username', help='Deletes the user with the given user name.')
parser.add_argument('--create-repo', '--create-repository', choices=['local', 'remote', 'virtual'], help='Creates a repository of a specified type (one of local, remote, virtual, or federated).')
parser.add_argument('--delete-repo', '--delete-repository', metavar='repository-key', help='Deletes the repository with the given key.')

args = parser.parse_args()

if args.set_default_host:
    logging.debug(f"set-default-host invoked. Attempting to set default host to \"{args.set_default_host[0]}\"")
    os.environ['JARTIFACTORY_HOST'] = args.set_default_host[0]
    dotenv.set_key(dotenv_file, "JARTIFACTORY_HOST", os.environ['JARTIFACTORY_HOST'])

elif args.sign_in:
    got_token = False
    got_key = False
    print("Signing in to Artifactory. Please enter log-in details.")
    user_info = get_user_info()
    user = user_info['username']
    password = user_info['password']
    logging.debug(f"sign-in invoked. Attempting sign in with user: {user} and pass: {password}")
    url = f"{ARTIFACTORY_HOST}/api/security/token"

    data = {
        "username": user,
        "expires_in": TOKEN_DURATION
    }
    
    now = datetime.datetime.now()
    response = requests.post(url=url, auth=HTTPBasicAuth(user, password), data=data)
    logging.debug(f"Got response json {response.json()} from artifactory.")

    if response.status_code == 200:
        response_json = response.json()

        if 'expires_in' in response_json:
            expiration_date = now + timedelta(seconds=response_json['expires_in'])
            os.environ['TOKEN_EXPIRATION'] = expiration_date.strftime(TIME_FORMAT)
            dotenv.set_key(dotenv_file, "TOKEN_EXPIRATION", os.environ['TOKEN_EXPIRATION'])

        logging.debug(f"Retrieved token {response_json['access_token']} from artifactory. Adding to ENV...")
        os.environ['JARTIFACTORY_TOKEN'] = response_json['access_token']
        dotenv.set_key(dotenv_file, "JARTIFACTORY_TOKEN", os.environ['JARTIFACTORY_TOKEN'])

        logging.info("Log in successful. Token added to ENV")
        got_token = True
    else:
        logging.error(f"Failed sign in with user={user} and password={password}\nResponse code is {response.status_code} ({response.reason})")
    
    url = f"{ARTIFACTORY_HOST}/api/security/apiKey"

    response = requests.get(url=url, auth=HTTPBasicAuth(user, password))

    if response.status_code == 200:
        response_json = response.json()

        if 'apiKey' in response_json:
            logging.debug(f"Retrieved apiKey {response_json['apiKey']} from artifactory. Adding to ENV...")
            os.environ['JARTIFACTORY_KEY'] = response_json['apiKey']
            dotenv.set_key(dotenv_file, "JARTIFACTORY_KEY", os.environ['JARTIFACTORY_KEY'])
            got_key = True
        else:
            logging.warning(f"No API key exists for user {user}. Attempting to create one...")
            response = requests.post(url=url, auth=HTTPBasicAuth(user, password))
            if response.status_code == 201:
                response_json = response.json()
                logging.warning(f"Created API key for {user}")
                logging.debug(f"Retrieved apiKey {response_json['apiKey']} from artifactory. Adding to ENV...")
                os.environ['JARTIFACTORY_KEY'] = response_json['apiKey']
                dotenv.set_key(dotenv_file, "JARTIFACTORY_KEY", os.environ['JARTIFACTORY_KEY'])
                got_key = True
                logging.info("Log in successful. Key added to ENV")
            else:
                logging.error("Failed to create API key.")
    else:
        logging.error(f"Failed sign in with user={user} and password={password}\nResponse code is {response.status_code} ({response.reason})")
    if got_key and got_token:
        print("Log in successful")
    else:
        print("Log in failed. Please verify credentials.")

elif args.ping:
    if not token_expired():
        url = f"{ARTIFACTORY_HOST}/api/system/ping"
        headers = {
            "Authorization": f"Bearer {get_token()}"
        }

        response = requests.get(url=url, headers=headers)

        print(f"{response.status_code} {response.reason}")
    else:
        print(TOKEN_EXPIRED_MESSAGE)

elif args.version:
    if not token_expired():
        url = f"{ARTIFACTORY_HOST}/api/system/version"
        headers = {
            "Authorization": f"Bearer {get_token()}"
        }

        response = requests.get(url=url, headers=headers)

        if response.status_code == 200:
            try:
                print(f"Artifactory Version {response.json()['version']} - revision {response.json()['revision']}")
            except:
                logging.error(f"Error parsing version from response: {response.json()}")
        else:
            print(f"Could not retrieve version information. Got {response.status_code} ({response.reason}) from host.")
    else:
        print(TOKEN_EXPIRED_MESSAGE)
        
elif args.create_user:
    if 'JARTIFACTORY_KEY' in os.environ:
        print("Creating user. Please enter user log-in info")
        user_info = get_create_user_details()
        user = user_info['username']
        password = user_info['password']
        email = user_info['email']
        url = f"{ARTIFACTORY_HOST}/api/security/users/{user}"

        headers = {
            "X-JFrog-Art-Api": os.environ['JARTIFACTORY_KEY'],
            "Content-Type": "application/json"
        }

        data = {
            "name": user, 
            "email": email,
            "password": password
        }

        logging.debug(f"Sending PUT request to {url} with headers: {headers} and body {data}")
        response = requests.put(url=url, headers=headers, json=data)
        if response.status_code == 201:
            logging.info("User creation successful.")
            print(f"Created user {user}")
        else:
            print(f"Failed user creation for user {user}. Got {response.status_code} ({response.reason}) from host.")
    else:
        print(MISSING_KEY_MESSAGE)

elif args.get_storage_info:
    if 'JARTIFACTORY_KEY' in os.environ:
        url = f"{ARTIFACTORY_HOST}/api/storageinfo"
        headers = {
            "X-JFrog-Art-Api": os.environ['JARTIFACTORY_KEY']
        }

        response = requests.get(url=url, headers=headers)

        if response.status_code == 200: 
            print(response.json())
    else:
        print(MISSING_KEY_MESSAGE)

elif args.delete_user:
    if 'JARTIFACTORY_KEY' in os.environ:
        user = args.delete_user
        url = f"{ARTIFACTORY_HOST}/api/security/users/{user}"
        headers = {
            "X-JFrog-Art-Api": os.environ['JARTIFACTORY_KEY']
        }

        response = requests.delete(url=url, headers=headers)

        if response.status_code == 200: 
            print(response.text)
        elif response.status_code == 404: 
            print(f"Could not find user matching username \'{user}\'. Check the username is correct and try again.")
        else:
            print(f"Error deleting user {user}. Got {response.status_code} ({response.reason}) from host.")
    else:
        print(MISSING_KEY_MESSAGE)

elif args.create_repo:
    if 'JARTIFACTORY_KEY' in os.environ:
        repo_type = args.create_repo
        repo_key = input("Enter repo name/key: ")

        data = {}
        if repo_type == 'local':
            data = {
                "key": repo_key,
                "rclass": repo_type
            }
        elif repo_type == 'remote':
            repo_url = input("Enter url for remote repository: ")
            external_dependencies_enabled = None
            while external_dependencies_enabled == None:
                external_dependencies_response = input("External dependencies enabled? Enter Y/N. (Default N): ")
                if external_dependencies_response.lower() == "y":
                    external_dependencies_enabled = True
                elif external_dependencies_response.lower() == "n" or external_dependencies_response == "":
                    external_dependencies_enabled = False
                else:
                    print("Please enter Y to enable external dependencies on remote repository or N to disable them. (Only applies to Docker repositories)")
            data = {
                "key": repo_key,
                "rclass": repo_type,
                "url": repo_url,
                "external_dependencies_enabled": external_dependencies_enabled
            }
        elif repo_type == 'virtual':
            package_type = None
            while package_type == None:
                package_type_response = input("Please specify package type for virtual repository (default generic): ")
                if package_type_response.lower() in REPOSITORY_PACKAGE_TYPES:
                    package_type = package_type_response.lower()
                elif package_type_response == "":
                    package_type = 'generic'
                else:
                    print(f"Please enter a supported package type. \nSupported package types:{REPOSITORY_PACKAGE_TYPES}")
            data = {
                "key": repo_key,
                "rclass": repo_type,
                "packageType": package_type
            }
        url = f"{ARTIFACTORY_HOST}/api/repositories/{repo_key}"
        headers = {
                "X-JFrog-Art-Api": os.environ['JARTIFACTORY_KEY']
            }
        response = requests.put(url=url, headers=headers, json=data)

        if response.status_code == 200:
            print(f"Successfully created repository \'{repo_key}\'.")
        else:
            logging.error(f"Failed creating repository with spec: {data}\nServer response was {response.status_code} ({response.reason}).")
            print(f"Failed creating repository {repo_key}. Got {response.status_code} ({response.reason}) from host.")
    else:
        print(MISSING_KEY_MESSAGE)
    
elif args.delete_repo:
    if 'JARTIFACTORY_KEY' in os.environ:
        repo_key = args.delete_repo
        url = f"{ARTIFACTORY_HOST}/api/repositories/{repo_key}"
        headers = {
            "X-JFrog-Art-Api": os.environ['JARTIFACTORY_KEY']
        }
        response = requests.delete(url=url, headers=headers)

        if response.status_code == 200:
            print(f"Successfully deleted repository \'{repo_key}\'.")
        elif response.status_code == 404:
            logging.warning(f"Failed to find repository with key {repo_key} while attempting to delete.")
            print(f"Could not find repository with key \'{repo_key}\'. Please check the key is correct and try again.")
        else: 
            print(f"Failed to delete repository with key \'{repo_key}\'. Got {response.status_code} ({response.reason}) from host.")
    else:
        print(MISSING_KEY_MESSAGE)

else:
    parser.error("No arguments provided.")