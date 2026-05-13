"""Add job detail fields (salary, job_type, work_model, experience_level, description)

Revision ID: 3b284eb781ff
Revises: 2a173da670ee
Create Date: 2025-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b284eb781ff'
down_revision: Union[str, Sequence[str], None] = '2a173da670ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add new job detail columns."""
    op.add_column('jobs', sa.Column('salary', sa.String(), nullable=True))
    op.add_column('jobs', sa.Column('job_type', sa.String(), nullable=True))
    op.add_column('jobs', sa.Column('work_model', sa.String(), nullable=True))
    op.add_column('jobs', sa.Column('experience_level', sa.String(), nullable=True))
    op.add_column('jobs', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove job detail columns."""
    op.drop_column('jobs', 'description')
    op.drop_column('jobs', 'experience_level')
    op.drop_column('jobs', 'work_model')
    op.drop_column('jobs', 'job_type')
    op.drop_column('jobs', 'salary')
