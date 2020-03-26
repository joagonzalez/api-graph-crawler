import sqlite3

###############
## FUNCTIONS ##
###############

def connect_sql():
    conn = sqlite3.connect('data/spider.sqlite')
    cur = conn.cursor()

    return cur, conn

def team_weight(cur, conn, team):
    cur.execute('INSERT OR IGNORE INTO teams (name, team_id) VALUES ( ?, ? )', ( team['displayName'], team['id'] ))
    conn.commit()

cur, conn = connect_sql()

################
## JSON MAKER ##
################

print("Creating JSON output on spider.js...")
howmany = int(input("How many nodes? "))

fhand = open('data/spider.js','w')
nodes = list()


fhand.write('spiderJson = {"nodes":[\n')

# NODES
# load teams  
cur.execute('''SELECT team_id, name 
    FROM teams GROUP BY team_id ORDER BY team_id''')

for team in cur:
    nodes.append(team)
    if len(nodes) > howmany : break

count = 0
number_teams = 0
map = dict() # to map users and teams ids with d3 document ids
for team in nodes :
    if count > 0 : fhand.write(',\n')
    fhand.write('{'+'"weight":'+str(30)+',')
    fhand.write(' "id":'+str(count)+', "name":"'+ team[1]+'"}')
    map[team[0]] = count
    count = count + 1
    number_teams = count + 1

# load users
cur.execute('''SELECT user_id, mail 
    FROM users GROUP BY user_id ORDER BY user_id''')

for user in cur:
    nodes.append(user)
    if len(nodes) > howmany : break

for user in nodes[number_teams:]:
    if count > 0 : fhand.write(',\n')
    # print row
    fhand.write('{'+'"weight":'+str(5)+',')
    fhand.write(' "id":'+str(count)+', "name":"'+ user[1]+'"}')
    map[user[0]] = count
    count = count + 1

print('nodos: ' + str(nodes))
print('map: ' + str(map))


# LINKS
cur.execute('''SELECT team_id, user_id FROM teams_users''')
fhand.write('],\n"links":[\n')

count = 0

# dict map to build json
for team in cur:
    if team[0] not in map or team[1] not in map : continue
    if count > 0 : fhand.write(',\n')
    fhand.write('{"source":'+str(map[team[0]])+',"target":'+str(map[team[1]])+',"value":3}')
    count = count + 1
fhand.write(']};')
fhand.close()

cur.close()

print("Open graph.html in a browser to view the visualization")
