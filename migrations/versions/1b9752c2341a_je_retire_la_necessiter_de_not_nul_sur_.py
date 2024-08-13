"""je retire la necessiter de not nul  sur le nom et le prenom

Revision ID: 1b9752c2341a
Revises: 
Create Date: 2024-08-12 06:21:26.150508

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b9752c2341a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('first_name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('last_name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('last_name',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('first_name',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)

    # ### end Alembic commands ###