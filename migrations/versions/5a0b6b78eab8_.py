"""empty message

Revision ID: 5a0b6b78eab8
Revises: 64e233431e5b
Create Date: 2023-03-23 20:12:18.392414

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a0b6b78eab8'
down_revision = '64e233431e5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subscriptions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('expirydate', sa.DateTime(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subscriptions', schema=None) as batch_op:
        batch_op.drop_column('expirydate')

    # ### end Alembic commands ###