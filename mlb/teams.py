import re, requests, json
import lxml, fileinput
from bs4 import BeautifulSoup as soup
from mlb.models import League, Team, Player
from mlb import db
from flask import session

OFFLINE = False

# translate MLB url to ESPN url
url_lookup = {
    'orioles': 'bal', 'redsox': 'bos', 'yankees': 'nyy', 'rays': 'tb', 'bluejays': 'tor',
    'whitesox': 'chw', 'indians': 'cle', 'tigers': 'det', 'royals': 'kc', 'twins': 'min',
    'astros': 'hou', 'angels': 'laa', 'athletics': 'oak', 'mariners': 'sea', 'rangers': 'tex',
    'braves': 'atl', 'marlins': 'mia', 'mets': 'nym', 'phillies': 'phi', 'nationals': 'wsh',
    'cubs': 'chc', 'reds': 'cin', 'brewers': 'mil', 'pirates': 'pit', 'cardinals': 'stl',
    'dbacks': 'ari', 'rockies': 'col', 'dodgers': 'lad', 'padres': 'sd', 'giants': 'sf',
}

espn_to_mlb = {
    'bal': 'orioles', 'bos': 'redsox', 'nyy': 'yankees', 'tb': 'rays', 'tor': 'bluejays',
    'chw': 'whitesox', 'cle': 'indians', 'det': 'tigers', 'kc': 'royals', 'min': 'twins',
    'hou': 'astros', 'laa': 'angels', 'oak': 'athletics', 'sea': 'mariners', 'tex': 'rangers',
    'atl': 'braves', 'mia': 'marlins', 'nym': 'mets', 'phi': 'phillies', 'wsh': 'nationals',
    'chc': 'cubs', 'cin': 'reds', 'mil': 'brewers', 'pit': 'pirates', 'stl': 'cardinals',
    'ari': 'dbacks', 'col': 'rockies', 'lad': 'dodgers', 'sd': 'padres', 'sf': 'giants'}

# Isolates a JSON string within a text string.
# 'blob' is a string of indeterminant length and content, such as a web page.
# 'start' is the index to begin searching
# Takes a string of indeterminant length and finds the first '{' character, or
# the first opening delimiter character.
# Finds its matching '}' (matching closing) character and returns a JSON string.
# Note - this will not work if non-matching '{}' characters are embedded in strings.
def find_json(blob, start, open='{', close='}'):
    text = blob[start :]
    first_curly = text.index(open)
    index = first_curly + 1
    count = 1
    while count > 0:
        if text[index] == open:
            count += 1
        if text[index] == close:
            count -=1
        index += 1
    return text[first_curly:index]


def set_teams_db():
    mlb = get_teams()

    leagues = mlb['leagues']
    for league in leagues:
        league_name = league['name']
        divisions = league['divisions']
        for division in divisions:
            division_name = division['name']
            teams = division['teams']
            for team in teams:
                t = Team()
                # note - this 'if' block prevents the database updating
                if bool(Team.query.filter_by(id=team['id']).first()):
                    t = Team.query.filter_by(id=team['id'])
                    continue

                t.id = team['id']
                t.logo = team['logo']
                t.name = team['name']
                t.shortName = team['shortName']
                t.url = team['url'][1:]
                t.league = league_name
                t.division = division_name
                if not bool(Team.query.filter_by(id=team['id']).first()):
                    db.session.add(t)
                db.session.commit()


def get_teams():
    if OFFLINE:
        with open('teams.json', 'r') as f:
            teams = json.load(f)
            # return json.loads(f)
            return teams
    else:
        league = League().query.first()
        return league.info if league else seed_teams()


def get_players(team_id):
    ''' Receives the MLB-designated team id and returns a list of the team players.
    Each item in the list is a dictionary containing:
    .
    .
    .
    '''
    team_id = int(team_id)

    # set_teams_db()
    player_list = []      # function will return a list of dictionaries of players

    team = Team.query.filter_by(id = team_id).first()
    long_url = team.url
    short_url = url_lookup[long_url]
    info = requests.get('http://m.mlb.com/' + short_url + '/roster/40-man/')
    team_info = soup(info.text, 'html.parser')

    groups = team_info.find_all('section', class_='module')

    for group in groups:
        if group.find('h4'):
            position = group.find('h4').text
            body = group.find('tbody')
            players = body.find_all('tr')

            for player in players:
                player_info = player.find_all('td')
                image_url = player.find('img')
                pic_url = image_url['src']
                if pic_url:
                    start_index = pic_url.index('/mlb/')
                    end_index = pic_url.index('@2x')
                    id = int(pic_url[start_index+5: end_index])
                    if Player.query.filter_by(id = id).first():
                        p = Player.query.filter_by(id = id).first()
                    else:
                        p = Player()
                    p.image_url = pic_url
                    p.id = int(pic_url[start_index+5: end_index])

                position = position[:-1] if position[-1]=='s' else position
                p.position = position
                p.team_id = team_id
                p.active  = True
                # import pdb; pdb.set_trace()

                team = Team.query.filter_by(id=team_id).first()

                team_name = team.name
                p.team_name = team_name

                items = player.find_all('td')
                player_info = [item.text for item in items]
                jersey, _, name, bats_throws, height, weight, dob = player_info

                name = name.rstrip().lstrip()
                p.name = name

                # other info I could add to db: jersey, bats_throws, height, weight, dob
                # print(jersey, name, bats_throws, height, weight, dob)
                current_player = {'name': name, 'image_url': pic_url, 'position': position, 'status': 'True', 'team': team_name, 'id': id, 'team_id': team_id}
                player_list.append(current_player)

                #try:
                db.session.add(p)
                #except:
                    # error message - could not add to database
                db.session.commit()

    return player_list


def update_teams():
    league = League.query.first()
    league.info = get_teams()
    db.session.commit()
    return

def get_db_teams():
    league = League.query.first()
    teams = league.info
    return teams

def seed_teams():
    league = League()
    page = requests.get('https://www.mlb.com/standings')
    target = soup(page.text, 'lxml')
    pattern = re.compile(r'window.reactHeaderState')
    my_script = target.find('script', text=pattern)
    my_script = my_script.text
    teams = find_json(my_script, my_script.index('teamData'))
    teams = json.loads(teams)
    league = League(info = teams)
    db.session.add(league)
    db.session.commit()
    return teams


# https://appac.github.io/mlb-data-api-docs/#player-data-player-search-get
def search_players(name, status):

    str1 = "http://lookup-service-prod.mlb.com/json/"
    str2 = "named.search_player_all.bam?sport_code='mlb'&active_sw='"
    str3 = status
    str4 = "'&name_part='"
    str5 = name
    str6 = "%25'"

    request_string = str1 + str2 + str3 + str4 + str5 + str6

    #try:
    json_results = requests.get(request_string).json()
    number_of_players = json_results["search_player_all"]['queryResults']["totalSize"]
    if number_of_players == "0":
        return None
    if number_of_players == "1":
        results = [json_results["search_player_all"]['queryResults']["row"]]
        # results = results.append(json_results["search_player_all"]['queryResults']["row"])
    else:
        results = json_results["search_player_all"]['queryResults']["row"]
    #except
    #error handling if the search yields no results
    players = []
    for result in results:

        player_id = result["player_id"]

        if Player.query.filter_by(id = player_id).first():
            p = Player.query.filter_by(id = player_id).first()
        else:
            p = Player()

        active_status = result["active_sw"]
        active_status = False if active_status == 'N' else True

        pic_url = 'http://gdx.mlb.com/images/gameday/mugshots/mlb/' + player_id + '@2x.jpg'
        player_id = int(player_id)
        current_player = {'name': result["name_display_first_last"],
                          'image_url': pic_url,
                          'position': result["position"],
                          'id': player_id,
                          'team': result["team_full"],
                          'status': active_status,
                          'team_id': int(result["team_id"])}

        players.append(current_player)

        p.image_url = pic_url
        p.id = player_id
        p.position = current_player['position']
        p.team_id = current_player['team_id']
        p.name = current_player['name']
        p.active = active_status
        p.team_name = result["team_full"]
        db.session.add(p)
        db.session.commit()

    return players
