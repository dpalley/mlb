import re, requests, json
import lxml, fileinput
from bs4 import BeautifulSoup as soup
from mlb.models import League, Team, Player
from mlb import db

OFFLINE = False

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
                if bool(Team.query.filter_by(id=team['id']).first()):
                    t = Team.query.filter_by(id=team['id'])
                    continue

                t.id = team['id']
                t.logo = team['logo']
                t.name = team['name']
                t.shortName = team['shortName']
                t.url = team['url']
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


def get_players(team):

    p = Player()     # database entry for a player
    p_list = []      # function will return a list of dictionaries of players

    info = requests.get('http://m.' + team + '.mlb.com/roster/40-man/')
    team_info = soup(info.text, 'html.parser')

    groups = team_info.find_all('section', class_='module')

    for group in groups:
        if group.find('h4'):
            position = group.find('h4').text
            p.position = position[:-1] if position[-1]=='s' else position
            players = group.find_all('tbody > tr')
    #         print(players.text)
            body = group.find('tbody')
            players = body.find_all('tr')
            # print(type(players))

            for player in players:
                player_info = player.find_all('td')
                print(player_info)

                image_url = player.find('img')
                pic_url = image_url['src']
                # print();print(pic_url, type(pic_url))
                if pic_url:
                    start_index = pic_url.index('/mlb/')
                    # print(start_index)
                    end_index = pic_url.index('@2x')
                    # print(end_index)
                    p.id = pic_url[start_index+5: end_index]
                    # print(player_id)

                items = player.find_all('td')
    #             print(items)
                player_info = [item.text for item in items]
    #             print(player_info)
    #             print(type(player_info))
                jersey, _, name, bats_throws, height, weight, dob = player_info
                print(jersey, name, bats_throws, height, weight, dob)
                db.session.add(p)
    db.session.commit()


def update_teams():
    # import pdb; pdb.set_trace()
    league = League.query.first()
    league.info = get_teams()
    db.session.commit()
    return

def get_db_teams():
    league = League.query.first()
    teams = league.info
    # import pdb; pdb.set_trace()
    return teams

def seed_teams():
    league = League()
    page = requests.get('https://www.mlb.com/standings')
    target = soup(page.text, 'lxml')
    pattern = re.compile(r"window.reactHeaderState")
    my_script = target.find('script', text=pattern)
    my_script = my_script.text
    teams = find_json(my_script, my_script.index('"teamData'))
    teams = json.loads(teams)
    # import pdb; pdb.set_trace()
    league = League(info = teams)
    db.session.add(league)
    db.session.commit()
    return teams
