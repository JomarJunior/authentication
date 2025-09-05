"""Create t_roles table

Revision ID: edbb6c8f6635
Revises: d5f1e7d50c03
Create Date: 2025-09-04 21:37:27.934629

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from src.Authentication.Infrastructure.Database.Models import RoleDatabaseModel


# revision identifiers, used by Alembic.
revision: str = "edbb6c8f6635"
down_revision: Union[str, Sequence[str], None] = "d5f1e7d50c03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "t_roles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("description", sa.String, nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("t_roles")
