"""add review status

Revision ID: 10ef282b605f
Revises: d7e1cbacd36f
Create Date: 2026-10-16 14:19:18.752392

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '10ef282b605f'
down_revision: Union[str, Sequence[str], None] = 'd7e1cbacd36f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

status_enum = postgresql.ENUM(
    "pending", "approved", "hidden", name="reviewstatus", create_type=False
)


def upgrade() -> None:
    # add_column does not create the enum type for you, so create it explicitly.
    status_enum.create(op.get_bind(), checkfirst=True)
    # The temporary server_default lets this work on a table that already has rows.
    op.add_column(
        "reviews",
        sa.Column("status", status_enum, nullable=False, server_default="pending"),
    )
    op.execute("UPDATE reviews SET status = 'approved' WHERE approved")
    # Dropping the column also drops its index in Postgres.
    op.drop_column("reviews", "approved")
    op.alter_column("reviews", "status", server_default=None)
    op.create_index(op.f("ix_reviews_status"), "reviews", ["status"])


def downgrade() -> None:
    op.add_column(
        "reviews",
        sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.execute("UPDATE reviews SET approved = true WHERE status = 'approved'")
    op.alter_column("reviews", "approved", server_default=None)
    op.create_index(op.f("ix_reviews_approved"), "reviews", ["approved"])
    op.drop_index(op.f("ix_reviews_status"), table_name="reviews")
    op.drop_column("reviews", "status")
    status_enum.drop(op.get_bind(), checkfirst=True)
