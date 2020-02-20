import os

DISABLE_INVITES = os.getenv("DISABLE_INVITES", "no").lower() in [
    "yes",
    "ok",
    "y",
    "1",
    "on",
    "t",
    "true",
]
