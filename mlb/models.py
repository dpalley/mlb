from mlb import db, login_manager, user_logger
# from teams import get_teams, get_players
from sqlalchemy.dialects.postgresql import JSON
from flask_login import UserMixin, current_user
from flask import flash

# what is the standard makeup of fantasy teams
# 4 pitchers, 2 catchers, 6 infielders, 4 outfielders - is this reasonable?
# what do fantasy teams do about players who are pulled during the game

# will probably go into a different file  P / C / 1 / 2 / 3 / SS / RF / CF / LF
# each user can have one team (1-to-1)

positions = {1:'P', 2:'C'}
pos = (1,'P','Pitcher'), (2, 'C', 'Catcher')

def write_to_database(item=None):
    if item:
        db.session.add(item)
        db.session.commit()
    try:
        db.session.commit()
    except:
        flash(f'Error writing {item} to database', 'danger')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id        = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(20), unique=True, nullable=False)
    email     = db.Column(db.String(50), unique=True, nullable=False)
    password  = db.Column(db.String(60), nullable=False)
    team      = db.relationship('Team', backref='user', uselist=False)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Team(db.Model):
    id           = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name         = db.Column(db.String(20), unique=True, nullable=False)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'))
    players      = db.relationship('Player', backref='team', lazy=True)
    latest_score = db.Column(db.Integer)
    total_score  = db.Column(db.Integer)
    has_draft    = db.Column(db.Boolean, default = False)

    # 4 pitchers, 1 DH, 2 of everything else
    allocation = {0: 1, 1:4, 2:2, 3:2, 4:2, 5:2, 6:2, 7:2, 8:2, 9:2 }

    def __repr__(self):
        return f"{self.name} {self.total_score}"

# position numbers 0-9, fantasy status = active, inactive, undrafted (default)
#fantasy team, fantasy score
class Player(db.Model):
    id             = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name           = db.Column(db.String(50), unique=False, nullable=False)
    position       = db.Column(db.String(10), unique=False)
    position_id    = db.Column(db.Integer,unique=False)
    image_url      = db.Column(db.String(80))
    last_check     = db.Column(db.DateTime)
    active         = db.Column(db.Boolean, default=False)
    team_id        = db.Column(db.Integer, db.ForeignKey('team.id'))
    fantasy_score  = db.Column(db.Integer)
    draft_status   = db.Column(db.String(20), unique=False, default='undrafted')
    playing_status = db.Column(db.String(20), unique=False, default=None)

    def __repr__(self):
        # team = Team.query.filter_by(team_id = id).first()
        return f'{self.name}, {self.position}'
        # return f'{self.name}, {self.position} for {team.name}'

    def __init__(self, id=0, name='', position='', position_id=-1, image_url='',
                 active=False, team_id=0, fantasy_score=0, draft_status='undrafted',
                 playing_status='benched'):
        self.id = id
        self.name = name
        self.position = position
        self.position_id = position_id
        self.image_url = image_url
        self.active = active
        self.team_id = team_id
        self.fantasy_score = fantasy_score
        self.draft_status = draft_status
        self.playing_status = playing_status


    def draft(self, team_id):
        if self.draft_status != 'drafted':  # race condition between this line
            self.team_id = team_id          #          ^
            self.draft_status = 'drafted'   #          |
            self.playing_status = 'benched' #          v
            write_to_database(self)         # and this line (if 2 users draft same player)
            flash(f'Player {self.name} has been drafted and dB has been updated.', 'success')
            user_logger.info(f'Player {self.name} has been drafted and dB has been updated.')
            return True
        else:
            flash(f'You didn\'t get {self.name}. Someone beat you to him.', 'danger')
            user_logger.info(f'Someone tried to draft {self.name} but was unsuccessful.')
            return False


    def release(self):
        self.team_id = None
        self.draft_status = 'undrafted'
        self.playing_status = None
        write_to_database(self)
        flash(f'Player {self.name} has been released and dB has been updated.', 'success')
        user_logger.info(f'Player {self.name} has been released and dB has been updated.')
        return True, f'{self.name} is no longer on your team.'



    def activate(self):
        self.active = True
        # write_to_database(self)
        return True, f'{self.name} will be playing.'


    def bench(self):
        self.active = False
        # write_to_database(self)
        return False, f'{self.name} will be in the dugout.'


class League(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    info = db.Column(JSON)
    def __repr__(self):
        return f"League('{self.info}')"
