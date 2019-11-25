import re, requests, json
import lxml, fileinput
from bs4 import BeautifulSoup as soup
from mlb.models import League, Team, Player, write_to_database
from mlb import db
from flask import session
from flask_login import current_user

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

position_name = {0: 'DH', 1: 'P', 2: 'C', 3: '1B', 4: '2B', 5: '3B', 6: 'SS', 7: 'RF', 8: 'CF', 9: 'LF'}

# import pdb; pdb.set_trace()


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
                write_to_database()


def get_teams():
    if OFFLINE:
        with open('teams.json', 'r') as f:
            teams = json.load(f)
            # return json.loads(f)
            return teams
    else:
        league = League().query.first()
        return league.info if league else seed_teams()


def update_teams():
    league = League.query.first()
    league.info = get_teams()
    write_to_database()
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
    write_to_database(league)
    return teams

def search_by_team(team_id):
    player_list = []
    url = "http://lookup-service-prod.mlb.com/json/named.roster_40.bam?team_id='" + str(team_id) + "'"
    info = requests.get(url).text

    json_results = json.loads(info)
    return format_results(json_results, 'search_by_team')


def search_by_name(name):

    str1 = "http://lookup-service-prod.mlb.com/json/"
    str2 = "named.search_player_all.bam?sport_code='mlb'&active_sw='Y'"
    str3 = "&name_part='"
    str4 = name
    str5 = "%25'"

    request_string = str1 + str2 + str3 + str4 + str5

    #try:
        # put the request in a try-except block
    json_results = requests.get(request_string).json()

    #except:
        #error-handling code
    return format_results(json_results, 'search_by_name')

def format_results(json_results, search_method):

    if search_method == 'search_by_team':
        number_of_players = json_results["roster_40"]['queryResults']["totalSize"]
        if number_of_players == "0":
            return None
        if number_of_players == "1":
            results = [json_results["roster_40"]['queryResults']["row"]]
        else:
            results = json_results["roster_40"]['queryResults']["row"]
    elif search_method == 'search_by_name':
        number_of_players = json_results["search_player_all"]['queryResults']["totalSize"]
        if number_of_players == "0":
            return None
        if number_of_players == "1":
            results = [json_results["search_player_all"]['queryResults']["row"]]
        else:
            results = json_results["search_player_all"]['queryResults']["row"]

    players = []
    for result in results:
        if search_method == 'search_by_team':
            position_id = result['primary_position']
            position = result['position_txt']
            mlb_team = result['team_name']
        else:
            position_id = result['position_id']
            position = result['position']
            mlb_team = result['team_full']

        player_id = result["player_id"]
        draft_status = 'available'
        fantasy_team = None

        if Player.query.filter_by(id = player_id).first():
            # drafted, already in database
            p = Player.query.filter_by(id = player_id).first()
            team_id = p.team_id
            fantasy_team = '-'

            if team_id:
                f_team = Team.query.filter_by(id = team_id).first()
                fantasy_team = f_team.name
                if f_team.id == current_user.id:
                    draft_status = 'my_player'
                else:
                    draft_status = 'drafted'

        pic_url = 'http://gdx.mlb.com/images/gameday/mugshots/mlb/' + player_id + '@2x.jpg'
        player_id = int(player_id)

        current_player = {'name': result["name_display_first_last"],
                          'image_url': pic_url,
                          'position': position,
                          'position_id': position_id,
                          'id': player_id,
                          'team': mlb_team,
                          'status': True,
                          'team_id': int(result["team_id"]),
                          'draft_status': draft_status,
                          'fantasy_team': fantasy_team,
                          'playing_status': None}

        players.append(current_player)

    return players
