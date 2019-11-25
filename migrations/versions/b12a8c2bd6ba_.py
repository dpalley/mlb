"""empty message

Revision ID: b12a8c2bd6ba
Revises: 9ab38c3d1034
Create Date: 2019-11-22 17:09:15.894834

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b12a8c2bd6ba'
down_revision = '9ab38c3d1034'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('draft_status', sa.String(length=20), nullable=True))
    op.add_column('player', sa.Column('playing_status', sa.String(length=20), nullable=True))
    op.create_foreign_key(None, 'player', 'team', ['team_id'], ['id'])
    op.drop_column('player', 'fantasy_status')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('fantasy_status', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'player', type_='foreignkey')
    op.drop_column('player', 'playing_status')
    op.drop_column('player', 'draft_status')
    # ### end Alembic commands ###