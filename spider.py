# parameters.json contains azure app id and secrets
# $ python3 spider.py parameters.json
import sys  
import json
import logging
import requests
import msal
import sqlite3

###############
## FUNCTIONS ##
###############

def load_config():
    config = json.load(open(sys.argv[1]))
    return config

def get_graph_token(app):
    result = None
    result = app.acquire_token_silent(config["scope"], account=None)

    return result

def get_graph_data(endpoint, token):
    data = requests.get(endpoint, headers = {'Authorization': 'Bearer ' + token})

    return data

def add_user(cur, conn, user):
    cur.execute('INSERT OR IGNORE INTO users (display_name, mail, job_title, user_id) VALUES ( ?, ?, ?, ? )', ( user['displayName'], user['mail'], user['jobTitle'], user['id'] ))
    conn.commit()

def add_team(cur, conn, team):
    cur.execute('INSERT OR IGNORE INTO teams (name, team_id) VALUES ( ?, ? )', ( team['displayName'], team['id'] ))
    conn.commit()

def add_teams_users(cur, conn, team, user):
    cur.execute('INSERT OR IGNORE INTO teams_users (team_id, user_id) VALUES ( ?, ? )', ( team['id'], user['id'] ))
    conn.commit()

def connect_sql():
    conn = sqlite3.connect('data/spider.sqlite')
    cur = conn.cursor()

    return cur, conn

def create_schema(cur):
    cur.execute('''CREATE TABLE IF NOT EXISTS users
    (id INTEGER PRIMARY KEY, mail TEXT UNIQUE, user_id TEXT,
     display_name TEXT, job_title REAL)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS teams_users
    (id INTEGER PRIMARY KEY, team_id TEXT, user_id TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS teams
    (id INTEGER PRIMARY KEY, name TEXT, team_id TEXT)''')

def check_sql_progress(cur):
    cur.execute('SELECT mail FROM users ORDER BY RANDOM() LIMIT 1')
    row = cur.fetchone()
    
    if row is not None:
        print("Restarting existing crawl.  Remove spider.sqlite to start a fresh crawl.")
        return 1
    else :
        print('Database is empty, we can start the crawler.')
        return 0

#############
## CROWLER ##
#############

# logging.basicConfig(level=logging.DEBUG)

cur, conn = connect_sql()
create_schema(cur)

if not check_sql_progress(cur):
    config = load_config()

    app = msal.ConfidentialClientApplication(
        config["client_id"], 
        authority=config["authority"], 
        client_credential=config["secret"]
    )
    
    result = get_graph_token(app)

    if not result:
        logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
        result = app.acquire_token_for_client(scopes=config["scope"])

    if "access_token" in result:
        token = result['access_token']
        graph_groups_data = get_graph_data(config['endpoint_groups'], token)
        graph_groups_data = graph_groups_data.json()
        
        print("Graph API call result: ")
        #print(json.dumps(graph_groups_data, indent=2))

        teams = []
        users = {}
        
        for group in graph_groups_data["value"]:
            team = {}
            print("Team Name: " + str(group["displayName"]))
            print("Team Enable: " + str(group["resourceProvisioningOptions"]))
            print("Team id: " + str(group["id"]))

            if "Team" in group["resourceProvisioningOptions"]:
                team['id'] = group["id"]
                team['displayName'] = group["displayName"]
                team['teamEnabled'] = group["resourceProvisioningOptions"]
                teams.append(team)
                add_team(cur, conn, team)


        for team in teams:
            members = []
            print('#######################################')
            graph_team_data = get_graph_data(config["endpoint_groups"] + '/' + team['id'] + '/members', token).json()
            print('Graph API call result for team ' + str(team['displayName']) + ': ')
            #print(json.dumps(graph_team_data, indent=2))
            for user in graph_team_data['value']:
                u = {}
                u['id'] = user['id']
                u['displayName'] = user['displayName']
                u['givenName'] = user['givenName']
                u['mail'] = user['mail']
                u['jobTitle'] = user['jobTitle']
                members.append(u['mail'])
                add_teams_users(cur, conn, team, u)
                
                if u['mail'] not in users:
                    users.update({u['mail']: u})
                    add_user(cur, conn, u)

                                        
                print('------------------------------------')
                if 'displayName' in user and user['displayName'] and user['givenName'] is not None: print('displayName: ' + user['displayName'] + user['givenName'])
                if 'mail' in user and user['mail'] is not None: print('mail: ' + user['mail'])
                if 'jobTitle' in user and user['jobTitle'] is not None: print('jobTitle: ' + user['jobTitle'])
        
            team.update({'member': members})
            
        print("Listado de users (" + str(len(users)) + "): " + str(json.dumps(users)))
        print("Listado de teams (" + str(len(teams)) + "): " + str(json.dumps(teams)))

    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))  