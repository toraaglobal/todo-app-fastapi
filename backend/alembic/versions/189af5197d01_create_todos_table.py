"""create todos table

Revision ID: 189af5197d01
Revises: 84b29e2ae377
Create Date: 2024-08-24 23:56:42.465491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '189af5197d01'
down_revision: Union[str, None] = '84b29e2ae377'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
