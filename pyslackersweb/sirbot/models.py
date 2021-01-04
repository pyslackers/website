from datetime import datetime

import sqlalchemy as sa

from pyslackersweb.models import metadata

codewars = sa.Table(
    "codewars_challenge",
    metadata,
    sa.Column("id", sa.Text, primary_key=True),
    sa.Column("added_at", sa.DateTime(timezone=True), default=datetime.now, nullable=False),
    sa.Column(
        "posted_at",
        sa.DateTime(timezone=True),
        default=None,
        onupdate=datetime.now,
        nullable=True,
    ),
)
