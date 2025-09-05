"""Add createdAt and updatedAt columns to t_users, t_role_assignments, t_authentication_credentials and t_roles table

Revision ID: d3287015cc67
Revises: c2e960bf531a
Create Date: 2025-09-04 22:10:10.569715

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "d3287015cc67"
down_revision: Union[str, Sequence[str], None] = "c2e960bf531a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add createdAt and updatedAt columns to t_users table
    op.add_column(
        "t_users",
        sa.Column(
            "createdAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
    )
    op.add_column(
        "t_users",
        sa.Column(
            "updatedAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
    )

    # Add createdAt and updatedAt columns to t_role_assignments table
    op.add_column(
        "t_role_assignments",
        sa.Column(
            "createdAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
    )
    op.add_column(
        "t_role_assignments",
        sa.Column(
            "updatedAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
    )

    # Add createdAt and updatedAt columns to t_authentication_credentials table
    op.add_column(
        "t_authentication_credentials",
        sa.Column(
            "createdAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
    )
    op.add_column(
        "t_authentication_credentials",
        sa.Column(
            "updatedAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
    )

    # Add createdAt and updatedAt columns to t_roles table
    op.add_column(
        "t_roles",
        sa.Column(
            "createdAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
    )
    op.add_column(
        "t_roles",
        sa.Column(
            "updatedAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove createdAt and updatedAt columns from t_users table
    op.drop_column("t_users", "createdAt")
    op.drop_column("t_users", "updatedAt")

    # Remove createdAt and updatedAt columns from t_role_assignments table
    op.drop_column("t_role_assignments", "createdAt")
    op.drop_column("t_role_assignments", "updatedAt")

    # Remove createdAt and updatedAt columns from t_authentication_credentials table
    op.drop_column("t_authentication_credentials", "createdAt")
    op.drop_column("t_authentication_credentials", "updatedAt")

    # Remove createdAt and updatedAt columns from t_roles table
    op.drop_column("t_roles", "createdAt")
    op.drop_column("t_roles", "updatedAt")
