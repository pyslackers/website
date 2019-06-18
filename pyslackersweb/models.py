from marshmallow import Schema, fields


class InviteSchema(Schema):
    email = fields.Email(required=True)
    agree_tos = fields.Boolean(required=True)
