"""Create t_authentication_credentials table

Revision ID: d5f1e7d50c03
Revises:
Create Date: 2025-09-04 21:23:42.725595

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from src.Authentication.Infrastructure.Database.Models import AuthenticationCredentialsDatabaseModel

# revision identifiers, used by Alembic.
revision: str = "d5f1e7d50c03"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "t_authentication_credentials",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("userId", postgresql.UUID(as_uuid=True)),
        sa.Column("username", sa.String, unique=True, nullable=False),
        sa.Column("passwordHash", sa.String, nullable=False),
        sa.Column("mfaEnabled", sa.Boolean, default=False),
        sa.Column("mfaSecret", sa.String, nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("t_authentication_credentials")
