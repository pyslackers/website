from marshmallow import Schema, fields, EXCLUDE


class InviteSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields

    email = fields.Email(required=True)
    agree_tos = fields.Boolean(required=True, validate=bool)
