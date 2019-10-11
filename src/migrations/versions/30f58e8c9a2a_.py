"""empty message

Revision ID: 30f58e8c9a2a
Revises: 29af61d85562
Create Date: 2019-09-04 11:30:45.847045

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30f58e8c9a2a'
down_revision = '29af61d85562'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contacts', sa.Column('uid', sa.String(length=128), nullable=True))
    op.create_unique_constraint(None, 'contacts', ['uid'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'contacts', type_='unique')
    op.drop_column('contacts', 'uid')
    # ### end Alembic commands ###
