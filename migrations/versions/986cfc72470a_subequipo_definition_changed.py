"""Subequipo definition changed

Revision ID: 986cfc72470a
Revises: 6c8da6605876
Create Date: 2025-02-04 13:53:27.059668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '986cfc72470a'
down_revision = '6c8da6605876'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('partido', schema=None) as batch_op:
        batch_op.alter_column('goles_A',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('goles_B',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('partido', schema=None) as batch_op:
        batch_op.alter_column('goles_B',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('goles_A',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
