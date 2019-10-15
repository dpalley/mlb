from flask import render_template, url_for, request, flash, redirect
import json
import secrets
from forms import RegistrationForm, LoginForm
from models import *


app.config['SECRET_KEY'] = secrets.token_hex(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mlb:password@localhost:5432/mlb'


# def get_teams():
#     with open('teams.json', 'r') as f:
#         teams = json.load(f)
#         return teams

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # import pdb; pdb.set_trace()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    # else:
        # import pdb; pdb.set_trace()
    return render_template('register.html', title="Register", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'test@test.com' and form.password.data == 'password':
            flash(f'Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login uncussessful. Please check email and password.', 'danger')
    return render_template('login.html', title="Login", form=form)

@app.route('/teams')
def teams():
    teams = get_teams()
    return render_template('teams.html', title="Teams", teams=teams)

@app.route('/players')
def players():
    return render_template('players.html', title="Players")

if __name__ == '__main__':
    app.run(debug=True)
