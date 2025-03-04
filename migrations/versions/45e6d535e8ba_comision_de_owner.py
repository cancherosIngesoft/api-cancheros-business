"""Comision de owner

Revision ID: 45e6d535e8ba
Revises: 13ecea267950
Create Date: 2025-02-21 10:31:14.171476

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45e6d535e8ba'
down_revision = '13ecea267950'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('duenio', schema=None) as batch_op:
        batch_op.add_column(sa.Column('commission_amount', sa.Numeric(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('duenio', schema=None) as batch_op:
        batch_op.drop_column('commission_amount')

    # ### end Alembic commands ###
