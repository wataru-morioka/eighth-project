"""empty message

Revision ID: fe44f0915254
Revises: af3e5910bd14
Create Date: 2019-08-19 22:22:07.191340

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe44f0915254'
down_revision = 'af3e5910bd14'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('photos', sa.Column('size', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('photos', 'size')
    # ### end Alembic commands ###