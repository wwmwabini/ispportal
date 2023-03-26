"""Added Transactions and Payments tables

Revision ID: 90e1f7912761
Revises: 371b215fe3be
Create Date: 2023-03-26 15:41:30.960171

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90e1f7912761'
down_revision = '371b215fe3be'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('claimed', sa.Boolean(), nullable=False),
    sa.Column('invoice_id', sa.String(length=50), nullable=True),
    sa.Column('transaction_id', sa.String(length=50), nullable=False),
    sa.Column('state', sa.String(length=50), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('charges', sa.Integer(), nullable=True),
    sa.Column('net_amount', sa.Integer(), nullable=True),
    sa.Column('currency', sa.String(length=50), nullable=False),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('account', sa.String(length=50), nullable=True),
    sa.Column('api_ref', sa.String(length=50), nullable=True),
    sa.Column('host', sa.String(length=100), nullable=True),
    sa.Column('failed_reason', sa.String(length=500), nullable=True),
    sa.Column('failed_code', sa.String(length=50), nullable=True),
    sa.Column('failed_code_link', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.String(length=100), nullable=False),
    sa.Column('updated_at', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    # ### end Alembic commands ###
