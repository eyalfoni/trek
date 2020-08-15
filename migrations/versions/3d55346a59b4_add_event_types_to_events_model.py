"""add event types to events model

Revision ID: 3d55346a59b4
Revises: e72b07553fd2
Create Date: 2020-08-11 19:47:55.879007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d55346a59b4'
down_revision = 'e72b07553fd2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('event_type', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('events', 'event_type')
    # ### end Alembic commands ###