from marshmallow import Schema, fields
from app.arrangements.constants import PAGE, PER_PAGE


class ArrangementBasicResponseSchema(Schema):
	start_date = fields.DateTime()
	end_date = fields.DateTime()
	destination = fields.String()
	price = fields.Float()


class ArrangementFullResponseSchema(ArrangementBasicResponseSchema):
	description = fields.String()
	vacancies = fields.Integer()


class MetaSchema(Schema):
	page = fields.Integer(default = PAGE, missing = PAGE)
	per_page = fields.Integer(default = PER_PAGE, missing = PER_PAGE)
	total = fields.Integer(default = 0, missing = 0)


class MetaCollectionSchema(Schema):
	meta = fields.Method("get_meta")

	@staticmethod
	def get_meta(data):
		return MetaSchema().dump(data)


class ArrangementsBasicResultSchema(MetaCollectionSchema):
	items = fields.List(fields.Nested(ArrangementBasicResponseSchema()), data_key = "response")


class ArrangementsFullResultSchema(MetaCollectionSchema):
	items = fields.List(fields.Nested(ArrangementFullResponseSchema()), data_key = "response")


class UserRegistrationSchema(Schema):
	name = fields.String(required = True)
	surname = fields.String(required = True)
	email = fields.String(required = True)
	username = fields.String(required = True)
	password = fields.String(required = True)
	password_verification = fields.String(required = True)
	type = fields.Integer(default = 0, missing = 0)
