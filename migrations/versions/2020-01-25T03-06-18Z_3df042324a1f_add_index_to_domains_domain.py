"""add index to domains.domain

Revision ID: 3df042324a1f
Revises: b1362f9fad30
Create Date: 2020-01-25 03:06:18.331532+00:00

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3df042324a1f"
down_revision = "b1362f9fad30"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_domains_domain", "domains", ["domain"])


def downgrade():
    op.drop_index("ix_domains_domain", "domains")
