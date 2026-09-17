"""Add a column

Revision ID: 0c65e6abe469
Revises: 07cba78ad448
Create Date: 2026-09-13 11:15:13.165335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c65e6abe469'
down_revision: Union[str, Sequence[str], None] = '07cba78ad448'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('Note', sa.Column('is_pinned',sa.Boolean))


def downgrade():
    op.drop_column('Note', 'is_pinned')