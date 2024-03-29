"""empty message

Revision ID: 3ab13fe04df2
Revises: 43ee4498ee8e
Create Date: 2019-11-13 11:09:13.659478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ab13fe04df2'
down_revision = '43ee4498ee8e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fantasy_team', sa.Column('has_draft', sa.Integer(), nullable=True))
    op.add_column('player', sa.Column('fantasy_score', sa.Integer(), nullable=True))
    op.add_column('player', sa.Column('fantasy_status', sa.String(length=20), nullable=True))
    op.add_column('player', sa.Column('position_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player', 'position_id')
    op.drop_column('player', 'fantasy_status')
    op.drop_column('player', 'fantasy_score')
    op.drop_column('fantasy_team', 'has_draft')
    # ### end Alembic commands ###
