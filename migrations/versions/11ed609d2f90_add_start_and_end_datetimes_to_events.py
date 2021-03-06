"""add start and end datetimes to events

Revision ID: 11ed609d2f90
Revises: 0211ad3236b1
Create Date: 2020-07-23 23:13:44.742410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11ed609d2f90'
down_revision = '0211ad3236b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('end_datetime', sa.DateTime(), nullable=True))
    op.add_column('events', sa.Column('start_datetime', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('events', 'start_datetime')
    op.drop_column('events', 'end_datetime')
    # ### end Alembic commands ###
