"""add rotate strategy and protocol

Revision ID: 29d57de76d74
Revises: 680a9c8176f8
Create Date: 2022-03-30 18:24:57.844348

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '29d57de76d74'
down_revision = '680a9c8176f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('proxy_comrades', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('rotate_strategy', sa.INTEGER(), server_default=sa.text('0'), nullable=False),
                            insert_after="used_bandwidth_b")

    with op.batch_alter_table('proxy_credentials', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('protocol', sa.VARCHAR(length=255), nullable=False),
                            insert_after="type")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('proxy_credentials', schema=None) as batch_op:
        batch_op.drop_column('protocol')

    with op.batch_alter_table('proxy_comrades', schema=None) as batch_op:
        batch_op.drop_column('rotate_strategy')
    # ### end Alembic commands ###
