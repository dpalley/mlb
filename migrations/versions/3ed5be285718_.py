"""empty message

Revision ID: 3ed5be285718
Revises: b12a8c2bd6ba
Create Date: 2019-11-23 16:18:13.294296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ed5be285718'
down_revision = 'b12a8c2bd6ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('fantasy_team')
    op.add_column('team', sa.Column('has_draft', sa.Boolean(), nullable=True))
    op.add_column('team', sa.Column('latest_score', sa.Integer(), nullable=True))
    op.add_column('team', sa.Column('total_score', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('team', 'total_score')
    op.drop_column('team', 'latest_score')
    op.drop_column('team', 'has_draft')
    op.create_table('fantasy_team',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('latest_score', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('total_score', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('has_draft', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='fantasy_team_pkey'),
    sa.UniqueConstraint('name', name='fantasy_team_name_key')
    )
    # ### end Alembic commands ###
