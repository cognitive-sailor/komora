"""empty message

Revision ID: b26bb0faee74
Revises: 
Create Date: 2024-07-30 09:45:46.913377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b26bb0faee74'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('aktuatorji',
    sa.Column('sid', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('state', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('sid')
    )
    op.create_table('senzorji',
    sa.Column('sid', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('state', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('sid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('senzorji')
    op.drop_table('aktuatorji')
    # ### end Alembic commands ###
