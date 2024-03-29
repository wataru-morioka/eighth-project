"""empty message

Revision ID: d15b34775092
Revises: c6eae4cc3bad
Create Date: 2019-09-07 09:53:57.973426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd15b34775092'
down_revision = 'c6eae4cc3bad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_contacts_created_datetime'), 'contacts', ['created_datetime'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_contacts_created_datetime'), table_name='contacts')
    # ### end Alembic commands ###
