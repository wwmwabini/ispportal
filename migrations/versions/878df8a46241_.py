"""empty message

Revision ID: 878df8a46241
Revises: 1e4424ce1886
Create Date: 2023-03-25 20:38:22.634619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '878df8a46241'
down_revision = '1e4424ce1886'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('news',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('author', sa.String(length=100), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('category', sa.Enum('Announcement', 'News', 'Update', 'Alert'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('last_update', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('news')
    # ### end Alembic commands ###
