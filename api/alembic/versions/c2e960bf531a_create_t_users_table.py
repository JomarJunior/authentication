"""Create t_users table

Revision ID: c2e960bf531a
Revises: ad8faff7cb64
Create Date: 2025-09-04 21:38:30.830748

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from src.Authentication.Infrastructure.Database.Models import UserDatabaseModel


# revision identifiers, used by Alembic.
revision: str = "c2e960bf531a"
down_revision: Union[str, Sequence[str], None] = "ad8faff7cb64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "t_users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("isActive", sa.Boolean, default=True),
        sa.Column("isVerified", sa.Boolean, default=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("t_users")
