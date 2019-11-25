from flask import render_template, url_for, request, flash, redirect, session
from mlb.forms import RegistrationForm, LoginForm, UpdateAccountForm, TeamForm, SearchForm, FantasySelectForm
from mlb.models import User, League, Team, Player, write_to_database
from mlb.teams import get_teams, set_teams_db, search_by_name, search_by_team
from mlb import app, db, bcrypt, user_logger
from flask_login import login_user, current_user, logout_user, login_required
import json


# only run once
# set_teams_db()


# import pdb; pdb.set_trace()

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = FantasySelectForm()  # only need 'csrf_token'
    my_id = current_user.id

    if request.method == 'POST':
        my_players = session['my_players']
        status = request.form['draft_status']
        action = status.split()[0]
        player_id = int(status.split()[1])
        for my_player in my_players:
            if my_player["id"] == player_id:
                affected_player = Player.query.filter_by(id=player_id).first()

                if action == 'draft':
                    drafted = affected_player.draft(current_user.id)
                    if drafted:
                        current_team = Team.query.filter_by(id=current_user.id).first()
                        my_player['draft_status'] = 'my_player'
                        my_player['playing_status'] = 'benched'
                        my_player['fantasy_team'] = current_team.name
                        my_player['team_id'] = current_team.id

                elif action == 'release':
                    affected_player.release()
                    my_player['draft_status'] = 'available'
                    my_player['playing_status'] = None
                    my_player['fantasy_team'] = None
                    my_player['team_id'] = None

    else: # method = 'GET'
        my_players = []
        players = Player.query.filter_by(team_id=my_id).all()
        for player in players:
            my_player = (player.__dict__)
            del my_player['_sa_instance_state']
            my_player['draft_status'] = 'my_player'
            my_players.append(my_player)

    session['my_players'] = my_players
    return render_template('home.html', title="My Team", players = my_players, form = form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        write_to_database(user)
        team = Team(name=form.team_name.data, user=user)
        write_to_database(team)
        user_logger.info(f'User {user.username} created')
        flash(f'Your account has been created! You may now log in.', 'success')
        return redirect(url_for('login'))

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
            user_logger.info(f'{current_user.username} login')
            return redirect(next_page) if next_page else redirect(url_for('home'))

        else:
            flash('Login uncussessful. Please check email and password.', 'danger')
    return render_template('login.html', title="Login", form=form)


@app.route('/logout')
@login_required
def logout():
    user_logger.info(f'{current_user.username} logout')
    logout_user()
    return redirect(url_for('home'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if current_user.is_authenticated and current_user.username == 'admin':
        user_logger.info(f'System admin logged in')
        return render_template('admin.html', title="Admin")
    else:
        flash('Must have admin privileges.', 'danger')
        return redirect(url_for('home'))


@app.route('/team', methods=['GET', 'POST'])
@login_required
def team():
    user = current_user.username
    return render_template('team.html', title="Team Info", user = user)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id = current_user.id).first()
        user.username = form.username.data
        user.email = form.email.data
        write_to_database(user)
        team = Team.query.filter_by(id = current_user.id).first()
        team.name = form.team_name.data
        write_to_database(team)
        user_logger.info(f'{current_user.username} account update')
        flash('Your account information has been updated.', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        team = Team.query.filter_by(id = current_user.id).first()
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.team_name.data = team.name
    return render_template('account.html', title="Account", form = form)


@app.route('/teams', methods=['GET', 'POST'])
@login_required
def teams():
    if request.method == 'POST':
        team_selected = request.form['team_select']
        players = search_by_team(team_selected)

        if players:
            user_logger.info(f'Successfully searched for team {team_selected}')

        session['players'] = players
        return redirect(url_for('show_players'))

    elif request.method == 'GET':
        teams = get_teams()
        return render_template('teams.html', title="Teams", teams=teams)


@app.route('/players', methods=['GET', 'POST'])
@login_required
def show_players():
    # return redirect(url_for('home_page', headers=headers))
    players = session['players']

   # note: if players isn't set, going to the /players URL will throw an error
    if not players:
        selected_team = session.get('team_select', None)
        players = get_players2(selected_team)

    form = FantasySelectForm()  # only need 'csrf_token'
    if request.method == 'POST':
    # if form.is_submitted():
        status = request.form['draft_status']
        action = status.split()[0]
        player_id = int(status.split()[1])
        for player in players:
            if player['id'] == player_id:
                current_team_id = current_user.id
                current_team = Team.query.filter_by(id = current_team_id).first()

                if Player.query.filter_by(id = player_id).first():    # player already in dB
                    p = Player.query.filter_by(id = player_id).first()
                    p.team_id = current_team_id

                else:                                                 # create new player for dB
                    p = Player(id = player['id'],
                               name = player['name'],
                               position = player['position'],
                               position_id = player['position_id'],
                               image_url = player['image_url'],)

                if action == 'draft':
                    drafted = p.draft(current_team_id)
                    # this 'if' block prevents a race condition
                    if drafted:
                        player['draft_status'] = 'my_player'
                        player['playing_status'] = 'benched'
                        player['fantasy_team'] = current_team.name
                        player['fteam_id'] = current_team.id

                elif action == 'release':
                    player['draft_status'] = 'available'
                    player['playing_status'] = None
                    player['fantasy_team'] = None
                    player['fteam_id'] = None
                    p.release()

                elif action == 'activate':
                    p.activate(current_team_id)
                elif action == 'bench':
                    p.bench(current_team_id)
                else:
                    flash('Invalid action.', 'danger')

    session['players'] = players
    return render_template('players.html', title="Players", players = players, form = form)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        #retrieve parameters from MLB endpoint
        name   = request.form['name']
        players = search_by_name(name)

        if players:
            user_logger.info(f'{current_user.username} successfully searched for {name}')
            session['players'] = players
            return redirect(url_for('show_players'))

        else:
            flash('No results - please try again. The server may have shut you out temporarily.', 'danger')
            return redirect(url_for('search'))

    elif request.method == 'GET':
        return render_template('search.html', title="Search", form = form)


@app.route('/show')
def show():
    users   = User.query.all()
    league  = League.query.first()
    teams   = Team.query.all()
    players = Player.query.all()
    return render_template('show.html', users = users, league = league, \
        teams = teams, players = players, config = app.config)


@app.route('/choose/<pick_one>')
def choose(pick_one):
    if pick_one == 'users':
        title = 'Users'
        choices = User.query.all()
    if pick_one == 'teams':
        title = 'Teams'
        choices = Team.query.all()
    elif pick_one == 'league':
        title = 'League'
        choices = League.query.all()
    elif pick_one == 'config':
        title = 'Configuration'
        choices = app.config
    else:
        title = 'Error'
        choices = 'error'
    return render_template('choose.html',  title = title, choices = choices)
