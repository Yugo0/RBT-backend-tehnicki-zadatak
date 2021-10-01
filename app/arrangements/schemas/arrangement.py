from marshmallow import Schema, fields, validates, ValidationError
from app.arrangements.constants import PAGE, PER_PAGE
from datetime import datetime


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


class UserLoginSchema(Schema):
	username = fields.String(required = True)
	password = fields.String(required = True)


class TypeChangeRequestSchema(Schema):
	new_type = fields.Integer(required = True)


class TypeChangeResponseSchema(Schema):
	type = fields.Integer(required = True)
	accepted = fields.Boolean()
	comment = fields.String()


class ReservationResponseSchema(Schema):
	start_date = fields.DateTime()
	end_date = fields.DateTime()
	destination = fields.String()
	count = fields.Integer()
	price = fields.Float()


class ReservationsResponseSchema(MetaCollectionSchema):
	items = fields.List(fields.Nested(ReservationResponseSchema()), data_key = "response")


class ReserveRequestSchema(Schema):
	count = fields.Integer(default = 1, missing = 1)
	arrangement_id = fields.Integer(required = True)


class ReserveResponseSchema(Schema):
	count = fields.Integer()
	price = fields.Float()


class ArrangementsDescriptionChangeRequestSchema(Schema):
	description = fields.String()
	arrangement_id = fields.Integer()


class TypeChangeViewSchema(Schema):
	id = fields.Integer()
	username = fields.String()
	type = fields.Integer()


class TypeChangeListSchema(MetaCollectionSchema):
	items = fields.List(fields.Nested(TypeChangeViewSchema()), data_key = "response")


class TypeChangeDecisionSchema(Schema):
	id = fields.Integer(required = True)
	accepted = fields.Boolean(required = True)
	comment = fields.String()


class SearchRequestSchema(MetaSchema):
	date_from = fields.String()
	date_to = fields.String()
	destination = fields.String()

	@validates("date_from")
	def validate_date_from(self, value):
		try:
			datetime.strptime(value, "%Y-%m-%d")
		except ValueError:
			raise ValidationError("Wrong date format")

	@validates("date_to")
	def validate_date_to(self, value):
		try:
			datetime.strptime(value, "%Y-%m-%d")
		except ValueError:
			raise ValidationError("Wrong date format")
