from flask import Flask, render_template, escape, request
import json

app = Flask(__name__)

def get_teams():
    with open('teams.json', 'r') as f:
        teams = json.load(f)
        # return json.loads(f)
        return teams

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/teams')
def teams():
    teams = get_teams()
    return render_template('teams.html', title="Teams", teams=teams)

@app.route('/players')
def players():
    return render_template('players.html', title="Players")

@app.route('/login')
def login():
    return render_template('login.html', title="Login")

if __name__ == '__main__':
    app.run(debug=True)
