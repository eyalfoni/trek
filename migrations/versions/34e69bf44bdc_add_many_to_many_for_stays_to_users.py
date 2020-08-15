"""add many to many for stays to users

Revision ID: 34e69bf44bdc
Revises: 9e25e8b67c93
Create Date: 2020-08-14 20:10:37.876321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34e69bf44bdc'
down_revision = '9e25e8b67c93'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users_stays',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('stay_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['stay_id'], ['stays.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_stays')
    # ### end Alembic commands ###