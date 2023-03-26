"""empty message

Revision ID: 35b31f17072f
Revises: 5a0b6b78eab8
Create Date: 2023-03-23 20:13:53.019128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35b31f17072f'
down_revision = '5a0b6b78eab8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subscriptions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('expirydate', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subscriptions', schema=None) as batch_op:
        batch_op.drop_column('expirydate')

    # ### end Alembic commands ###