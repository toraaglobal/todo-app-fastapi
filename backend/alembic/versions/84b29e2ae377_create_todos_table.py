"""create todos table

Revision ID: 84b29e2ae377
Revises: 
Create Date: 2024-08-24 23:41:46.561767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84b29e2ae377'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
    create table todos(      
      id BIGSERIAL PRIMARY KEY,
      name TEXT,
      completed BOOLEAN NOT NULL DEFAULT FALSE             
    )
    """)


def downgrade():
    op.execute("drop table todos;")