"""add_hnsw_index_to_transactions

Revision ID: 47f4965bfe9e
Revises: 5eb7e16d8667
Create Date: 2026-08-13 22:10:44.005376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47f4965bfe9e'
down_revision: Union[str, Sequence[str], None] = '5eb7e16d8667'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_index(
        'idx_transactions_embedding',
        'transactions',
        ['embedding'],
        postgresql_using='hnsw',
        postgresql_ops={'embedding': 'vector_cosine_ops'}
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_transactions_embedding', table_name='transactions')
