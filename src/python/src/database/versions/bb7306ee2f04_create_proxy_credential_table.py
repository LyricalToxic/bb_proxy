"""create proxy credential table

Revision ID: bb7306ee2f04
Revises: 36d8230cdd0b
Create Date: 2022-03-28 14:47:29.248868

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'bb7306ee2f04'
down_revision = '36d8230cdd0b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('proxy_comrade_limits',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('proxy_credential_id', sa.INTEGER(), nullable=False),
                    sa.Column('comrade_id', sa.INTEGER(), nullable=False),
                    sa.Column('bandwidth_limit', sa.INTEGER(), server_default=sa.text('(1024)'), nullable=False),
                    sa.Column('concurrency_threads_limit', sa.INTEGER(), server_default=sa.text('1'), nullable=False),
                    sa.Column("status", sa.INTEGER(), server_default=sa.text("0"), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'),
                              nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('bandwidth_limit_mb', 'proxy_comrade_limits', ['concurrency_threads_limit'], unique=False)
    op.create_index(op.f('ix_proxy_comrade_limits_comrade_id'), 'proxy_comrade_limits', ['comrade_id'], unique=False)
    op.create_index(op.f('ix_proxy_comrade_limits_proxy_credential_id'), 'proxy_comrade_limits',
                    ['proxy_credential_id'], unique=False)
    op.create_index(op.f('ix_proxy_comrade_limits_status'), 'proxy_comrade_limits', ['status'], unique=False)
    op.create_index(op.f('ix_proxy_comrade_limits_updated_at'), 'proxy_comrade_limits', ['updated_at'], unique=False)
    op.create_index('proxy_credential_id', 'proxy_comrade_limits', ['comrade_id'], unique=False)
    op.execute(
        "CREATE TRIGGER IF NOT EXISTS UpdateOnCurrentTimestamp2 AFTER UPDATE ON proxy_comrade_limits "
        "BEGIN "
        "UPDATE proxy_comrade_limits set updated_at=CURRENT_TIMESTAMP WHERE id=id; "
        "END;"
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('proxy_credential_id', table_name='proxy_comrade_limits')
    op.drop_index(op.f('ix_proxy_comrade_limits_updated_at'), table_name='proxy_comrade_limits')
    op.drop_index(op.f('ix_proxy_comrade_limits_proxy_credential_id'), table_name='proxy_comrade_limits')
    op.drop_index(op.f('ix_proxy_comrade_limits_comrade_id'), table_name='proxy_comrade_limits')
    op.drop_index('bandwidth_limit_mb', table_name='proxy_comrade_limits')
    op.drop_table('proxy_comrade_limits')
    # ### end Alembic commands ###
