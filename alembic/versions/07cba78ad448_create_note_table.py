"""create note table

Revision ID: 07cba78ad448
Revises: 
Create Date: 2026-09-13 11:06:17.732407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07cba78ad448'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'Note',
        sa.Column('note_id', sa.Integer, primary_key=True),
        sa.Column('note', sa.String, nullable=False),
        sa.Column('created_at',sa.Date),
    )


def downgrade():
    op.drop_table('Note')
