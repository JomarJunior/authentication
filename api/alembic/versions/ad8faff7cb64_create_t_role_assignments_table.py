"""Create t_role_assignments table

Revision ID: ad8faff7cb64
Revises: edbb6c8f6635
Create Date: 2025-09-04 21:38:06.346592

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from src.Authentication.Infrastructure.Database.Models import RoleAssignmentDatabaseModel


# revision identifiers, used by Alembic.
revision: str = "ad8faff7cb64"
down_revision: Union[str, Sequence[str], None] = "edbb6c8f6635"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "t_role_assignments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("userId", postgresql.UUID(as_uuid=True)),
        sa.Column("roleId", postgresql.UUID(as_uuid=True)),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("t_role_assignments")
