from datetime import datetime
from enum import Enum, unique

import sqlalchemy as sa

metadata = sa.MetaData()


@unique
class Source(Enum):
    WESBOS = "wesbos"
    INVITE = "invite"
    MANUAL = "manual"


domains = sa.Table(
    "domains",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("domain", sa.Text, nullable=False, unique=True),
    sa.Column("blocked", sa.Boolean, nullable=False, default=False),
    sa.Column("source", sa.Enum(Source), nullable=False, default=Source.MANUAL),
    sa.Column("created_at", sa.DateTime(timezone=True), default=datetime.now, nullable=False),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    ),
    sa.Index("ix_domain_blocked", "domain", "blocked"),
)
