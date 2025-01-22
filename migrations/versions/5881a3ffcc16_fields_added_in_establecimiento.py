"""Fields added in establecimiento

Revision ID: 5881a3ffcc16
Revises: e5e032eef5ee
Create Date: 2025-01-21 13:16:08.202166

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5881a3ffcc16'
down_revision = 'e5e032eef5ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('duenio_establecimiento')
    with op.batch_alter_table('establecimiento', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nombre', sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column('localidad', sa.String(length=80), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('establecimiento', schema=None) as batch_op:
        batch_op.drop_column('localidad')
        batch_op.drop_column('nombre')

    op.create_table('duenio_establecimiento',
    sa.Column('id_establecimiento', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id_duenio', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['id_duenio'], ['duenio.id_duenio'], name='duenio_establecimiento_id_duenio_fkey'),
    sa.ForeignKeyConstraint(['id_establecimiento'], ['establecimiento.id_establecimiento'], name='duenio_establecimiento_id_establecimiento_fkey'),
    sa.PrimaryKeyConstraint('id_establecimiento', 'id_duenio', name='duenio_establecimiento_pkey')
    )
    # ### end Alembic commands ###
