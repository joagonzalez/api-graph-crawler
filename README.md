# MS Graph API crawler
MS Graph API crawler using OAuth app tokens and d3 library

### Ejecution
Parameter.json file is received via arg as in the example.

```
$ python3 spider.py parameters.json 
```

spider.sqlite should not exist so the crawler can start.

### SQL Model
Tables users, teams and teams_users. Due to users and teams has many-to-many relationship a relation database (teams_users) was created. The way in which  you can query and map this both elements is shown below.

```
sqlite> .schema
CREATE TABLE users
    (id INTEGER PRIMARY KEY, mail TEXT UNIQUE, user_id TEXT,
     display_name TEXT, job_title REAL);
CREATE TABLE teams_users
    (id INTEGER PRIMARY KEY, team_id TEXT, user_id TEXT);
CREATE TABLE teams
    (id INTEGER PRIMARY KEY, name TEXT, team_id TEXT);

```

```
sqlite> select display_name, mail from users join teams join teams_users on users.user_id = teams_users.user_id and teams.team_id = teams_users.team_id where teams.name = 'I+D';

Joaquin Gonzalez|joaquin.gonzalez@newtech.com.ar
Leonardo Bispo|leonardo.bispo@newtech.com.ar
Juan Leite|juan.leite@newtech.com.ar
Diego Ceraso|diego.ceraso@newtech.com.ar
Pablo Ceraso|pablo.ceraso@newtech.com.ar
Javier Windler|javier.windler@newtech.com.ar
Lucas Machado|Lucas.Machado@newtech.com.ar
Noel Naveda|noel.naveda@newtech.com.ar

```

![Figura 1](https://github.com/joagonzalez/api_graph_crawler/blob/master/doc/img/api_graph_crawler.png)
