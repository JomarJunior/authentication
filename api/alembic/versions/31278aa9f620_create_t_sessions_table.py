"""Create t_sessions table

Revision ID: 31278aa9f620
Revises: b71a773c7699
Create Date: 2025-09-05 18:43:05.422281

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from src.Session.Infrastructure.Database.Models import SessionDatabaseModel


# revision identifiers, used by Alembic.
revision: str = "31278aa9f620"
down_revision: Union[str, Sequence[str], None] = "b71a773c7699"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        SessionDatabaseModel.__tablename__,
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "userId", postgresql.UUID(as_uuid=True), sa.ForeignKey("t_users.id"), nullable=False
        ),
        sa.Column("clientId", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scopes", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("codeChallenge", sa.String, nullable=False),
        sa.Column("expiresAt", sa.DateTime(timezone=True), nullable=True),
        sa.Column("authenticationMethod", sa.String, nullable=False),
        sa.Column(
            "authenticationCodeId",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("t_authentication_codes.id"),
            nullable=True,
        ),
        sa.Column(
            "createdAt",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updatedAt",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table(SessionDatabaseModel.__tablename__)
