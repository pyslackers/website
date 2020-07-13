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
    sa.Index("ix_domains_domain", "domain"),
)

SlackChannels = sa.Table(
    "slack_channels",
    metadata,
    sa.Column("id", sa.Text, primary_key=True),
    sa.Column("name", sa.Text, unique=True),
    sa.Column("created", sa.DateTime(timezone=True)),
    sa.Column("archived", sa.Boolean),
    sa.Column("members", sa.Integer),
    sa.Column("topic", sa.Text),
    sa.Column("purpose", sa.Text),
    sa.Index("ix_slack_channels_id", "id"),
    sa.Index("ix_slack_channels_name", "name"),
)

SlackUsers = sa.Table(
    "slack_users",
    metadata,
    sa.Column("id", sa.Text, primary_key=True),
    sa.Column("deleted", sa.Boolean),
    sa.Column("admin", sa.Boolean),
    sa.Column("bot", sa.Boolean),
    sa.Column("timezone", sa.Text),
    sa.Column("first_seen", sa.DateTime(timezone=True), default=datetime.now),
    sa.Index("ix_slack_users_id", "id"),
    sa.Index("ix_slack_users_admin", "id", "admin"),
    sa.Index("ix_slack_users_timezone", "id", "timezone"),
)
