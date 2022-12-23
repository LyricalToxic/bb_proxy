"""create proxy_credentials table

Revision ID: a86c1dcd8acd
Revises: 7b2948dbb02f
Create Date: 2022-12-23 20:37:01.990762

"""
import sqlalchemy as sa
from alembic import op

from database.utils.triggers import CurrentTimestampOnUpdateTriggerDDL

# revision identifiers, used by Alembic.
revision = 'a86c1dcd8acd'
down_revision = '7b2948dbb02f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('proxy_credentials',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('type', sa.VARCHAR(length=255), nullable=False),
                    sa.Column('protocol', sa.VARCHAR(length=255), nullable=False),
                    sa.Column('host', sa.VARCHAR(length=255), nullable=False),
                    sa.Column('port', sa.INTEGER(), nullable=False),
                    sa.Column('username', sa.VARCHAR(length=255), nullable=True),
                    sa.Column('password', sa.TEXT(), nullable=True),
                    sa.Column('description', sa.TEXT(), nullable=True),
                    sa.Column('options', sa.TEXT(), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'),
                              nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_proxy_credentials')),
                    sa.UniqueConstraint('host', 'port', 'username',
                                        name=op.f('uq_proxy_credentials_host_port_username'))
                    )
    with op.batch_alter_table('proxy_credentials', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_proxy_credentials_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_proxy_credentials_type'), ['type'], unique=False)
        batch_op.create_index(batch_op.f('ix_proxy_credentials_updated_at'), ['updated_at'], unique=False)
        batch_op.execute(str(CurrentTimestampOnUpdateTriggerDDL("proxy_credentials")))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('proxy_credentials', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_proxy_credentials_updated_at'))
        batch_op.drop_index(batch_op.f('ix_proxy_credentials_type'))
        batch_op.drop_index(batch_op.f('ix_proxy_credentials_created_at'))

    op.drop_table('proxy_credentials')
    # ### end Alembic commands ###