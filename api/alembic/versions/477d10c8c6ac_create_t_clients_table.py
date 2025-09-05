"""Create t_clients table

Revision ID: 477d10c8c6ac
Revises: 31278aa9f620
Create Date: 2025-09-05 19:01:34.022525

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "477d10c8c6ac"
down_revision: Union[str, Sequence[str], None] = "31278aa9f620"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "t_clients",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("secret", sa.VARCHAR(), nullable=False),
        sa.Column("redirectUris", postgresql.ARRAY(sa.VARCHAR()), nullable=False),
        sa.Column(
            "createdAt",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updatedAt",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_t_clients")),
        sa.UniqueConstraint("name", name=op.f("uq_t_clients_name")),
    )


def downgrade() -> None:
    op.drop_table("t_clients")
