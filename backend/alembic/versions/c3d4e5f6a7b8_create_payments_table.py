from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column(
            'listing_id', sa.Integer(),
            sa.ForeignKey('listings.id', ondelete='CASCADE'),
            nullable=False, index=True,
        ),
        sa.Column(
            'buyer_id', sa.Integer(),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False, index=True,
        ),
        sa.Column(
            'seller_id', sa.Integer(),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False, index=True,
        ),
        sa.Column('stripe_checkout_session_id', sa.String(255), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='usd'),
        sa.Column(
            'status',
            sa.Enum('pending', 'completed', 'failed', 'cancelled', name='payment_status'),
            nullable=False,
            server_default='pending',
        ),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index(
        'ix_payments_stripe_checkout_session_id',
        'payments',
        ['stripe_checkout_session_id'],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index('ix_payments_stripe_checkout_session_id', table_name='payments')
    op.drop_table('payments')
    op.execute('DROP TYPE IF EXISTS payment_status')