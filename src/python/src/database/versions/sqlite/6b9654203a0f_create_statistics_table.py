"""create statistics table

Revision ID: 6b9654203a0f
Revises: a86c1dcd8acd
Create Date: 2022-12-23 20:37:58.079029

"""
import sqlalchemy as sa
from alembic import op

from database.utils.triggers import CurrentTimestampOnUpdateTriggerDDL

# revision identifiers, used by Alembic.
revision = '6b9654203a0f'
down_revision = 'a86c1dcd8acd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('statistics',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('proxy_comrade_limit_id', sa.INTEGER(), nullable=False),
                    sa.Column('from_timestamp', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'),
                              nullable=False),
                    sa.Column('to_timestamp', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'),
                              nullable=False),
                    sa.Column('trigger', sa.VARCHAR(length=255), nullable=False),
                    sa.Column('number_of_requests', sa.INTEGER(), server_default=sa.text('0'), nullable=False),
                    sa.Column('upload_traffic_bytes', sa.INTEGER(), server_default=sa.text('0'), nullable=False),
                    sa.Column('number_of_responses', sa.INTEGER(), server_default=sa.text('0'), nullable=False),
                    sa.Column('download_traffic_bytes', sa.INTEGER(), server_default=sa.text('0'), nullable=False),
                    sa.Column('total_traffic_bytes', sa.INTEGER(), server_default=sa.text('0'), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'),
                              nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_statistics')),
                    sa.UniqueConstraint('proxy_comrade_limit_id', 'from_timestamp', 'to_timestamp', 'trigger',
                                        name=op.f(
                                            'uq_statistics_proxy_comrade_limit_id_from_timestamp_to_timestamp_trigger'))
                    )
    with op.batch_alter_table('statistics', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_statistics_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_statistics_from_timestamp'), ['from_timestamp'], unique=False)
        batch_op.create_index(batch_op.f('ix_statistics_from_timestamp_statistics_to_timestamp_statistics_trigger'),
                              ['from_timestamp', 'to_timestamp', 'trigger'], unique=False)
        batch_op.create_index(batch_op.f('ix_statistics_proxy_comrade_limit_id'), ['proxy_comrade_limit_id'],
                              unique=False)
        batch_op.create_index(batch_op.f('ix_statistics_to_timestamp'), ['to_timestamp'], unique=False)
        batch_op.create_index(batch_op.f('ix_statistics_updated_at'), ['updated_at'], unique=False)
        batch_op.execute(str(CurrentTimestampOnUpdateTriggerDDL("statistics")))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('statistics', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_statistics_updated_at'))
        batch_op.drop_index(batch_op.f('ix_statistics_to_timestamp'))
        batch_op.drop_index(batch_op.f('ix_statistics_proxy_comrade_limit_id'))
        batch_op.drop_index(batch_op.f('ix_statistics_from_timestamp_statistics_to_timestamp_statistics_trigger'))
        batch_op.drop_index(batch_op.f('ix_statistics_from_timestamp'))
        batch_op.drop_index(batch_op.f('ix_statistics_created_at'))

    op.drop_table('statistics')
    # ### end Alembic commands ###
