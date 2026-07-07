"""add google oauth fields to users

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-05 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # hashed_password стає необов'язковим (у Google-користувачів пароля немає)
    op.alter_column('users', 'hashed_password', existing_type=sa.String(255), nullable=True)

    # google_id - унікальний ідентифікатор користувача від Google
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)

    # auth_provider - "local" (email+пароль) або "google"
    op.add_column(
        'users',
        sa.Column('auth_provider', sa.String(50), nullable=False, server_default='local'),
    )


def downgrade() -> None:
    op.drop_column('users', 'auth_provider')
    op.drop_index('ix_users_google_id', table_name='users')
    op.drop_column('users', 'google_id')
    op.alter_column('users', 'hashed_password', existing_type=sa.String(255), nullable=False)