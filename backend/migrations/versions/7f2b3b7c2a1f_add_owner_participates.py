"""add owner participates

Revision ID: 7f2b3b7c2a1f
Revises: 51646340c789
Create Date: 2026-05-17

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7f2b3b7c2a1f"
down_revision = "51646340c789"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "rooms",
        sa.Column("owner_participates", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.alter_column("rooms", "owner_participates", server_default=None)


def downgrade():
    op.drop_column("rooms", "owner_participates")

