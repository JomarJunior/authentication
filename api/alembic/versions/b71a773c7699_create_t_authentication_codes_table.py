"""Create t_authentication_codes table

Revision ID: b71a773c7699
Revises: d3287015cc67
Create Date: 2025-09-05 16:37:59.965470

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from src.Authentication.Infrastructure.Database.Models import AuthenticationCodeDatabaseModel


# revision identifiers, used by Alembic.
revision: str = "b71a773c7699"
down_revision: Union[str, Sequence[str], None] = "d3287015cc67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        AuthenticationCodeDatabaseModel.__tablename__,
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.String, unique=True, nullable=False),
        sa.Column("userId", postgresql.UUID(as_uuid=True), sa.ForeignKey("t_users.id")),
        sa.Column("clientId", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scopes", sa.String, nullable=True),  # Comma-separated scopes
        sa.Column("codeChallenge", sa.String, nullable=True),
        sa.Column("expiresAt", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "createdAt", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updatedAt", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table(AuthenticationCodeDatabaseModel.__tablename__)
