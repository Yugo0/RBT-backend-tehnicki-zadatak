from marshmallow import Schema, fields


class ArrangementsBasicResponseSchema(Schema):
	start_date = fields.DateTime()
	end_date = fields.DateTime()
	destination = fields.String()
	price = fields.Float()
