from flask import render_template, url_for, request, flash, redirect
from mlb.forms import RegistrationForm, LoginForm
from mlb.models import User, League, Team, Player
from mlb.teams import get_teams
from mlb import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        # import pdb; pdb.set_trace()
        flash(f'Your account has been created! You may now log in.', 'success')
        return redirect(url_for('login'))
    # else:
        # import pdb; pdb.set_trace()
    return render_template('register.html', title="Register", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login uncussessful. Please check email and password.', 'danger')
    return render_template('login.html', title="Login", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title="Account")

@app.route('/teams')
def teams():
    teams = get_teams()
    return render_template('teams.html', title="Teams", teams=teams)

@app.route('/players')
def players():
    players = get_players
    return render_template('players.html', title="Players", players = players)