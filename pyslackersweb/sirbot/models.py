import dataclasses

from datetime import datetime
from typing import Optional
from decimal import Decimal

import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import JSONB

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


@dataclasses.dataclass(frozen=True)
class StockQuote:
    # pylint: disable=too-many-instance-attributes

    symbol: str
    company: str
    price: Decimal
    change: Decimal
    change_percent: Decimal
    market_open: Decimal
    market_close: Decimal
    high: Decimal
    low: Decimal
    volume: Decimal
    time: datetime
    logo: Optional[str] = None


SlackMessage = sa.Table(
    "slack_messages",
    metadata,
    sa.Column("id", sa.Text, primary_key=True),
    sa.Column("send_at", sa.DateTime),
    sa.Column("user", sa.Text),
    sa.Column("channel", sa.Text),
    sa.Column("message", sa.Text),
    sa.Column("raw", JSONB),
    sa.Index("ix_slack_messages_user", "user", "send_at"),
    sa.Index("ix_slack_messages_channel", "channel", "send_at"),
    sa.Index("ix_slack_messages_user_channel", "user", "channel", "send_at"),
)
