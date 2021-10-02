from marshmallow import Schema, fields, validates, ValidationError, pre_load
from app.arrangements.constants import PAGE, PER_PAGE
from datetime import datetime
import re


class ArrangementBasicResponseSchema(Schema):
	id = fields.Integer()
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

	@validates("email")
	def validate_email(self, value):
		if not re.fullmatch(".+@.+", value):
			raise ValidationError("Email is not in valid format")


class UserLoginSchema(Schema):
	username = fields.String(required = True)
	password = fields.String(required = True)


class TypeChangeRequestSchema(Schema):
	new_type = fields.Integer(required = True)

	@validates("new_type")
	def validate_date_from(self, value):
		if 0 > value > 2:
			raise ValidationError("Unknown user type")


class TypeChangeResponseSchema(Schema):
	type = fields.Integer()
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

	@validates("count")
	def validate_count(self, value):
		if value < 1:
			raise ValidationError("Count cannot be less than 1")


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


class ArrangementRequestSchema(Schema):
	id = fields.Integer(required = True)


class SetGuideSchema(Schema):
	arrangement_id = fields.Integer(required = True)
	guide_id = fields.Integer()


class ArrangementGuideResponseSchema(ArrangementFullResponseSchema):
	guide_id = fields.Integer()


class UserResponseSchema(Schema):
	name = fields.String()
	surname = fields.String()
	email = fields.String()
	username = fields.String()
	type = fields.Integer()


class UserUpdateSchema(Schema):
	name = fields.String()
	surname = fields.String()
	email = fields.String()
	username = fields.String()
	new_password = fields.String()
	old_password = fields.String()

	@validates("email")
	def validate_date_to(self, value):
		if not re.fullmatch(".+@.+", value):
			raise ValidationError("Email is not in valid format")

	@pre_load()
	def func(self, data, **kwargs):
		if "name" not in data and "surname" not in data and "email" not in data and "username" not in data and \
				"new_password" not in data and "old_password" not in data:
			raise ValidationError("Nothing to patch")
		return data


class ArrangementUpdateRequestSchema(Schema):
	id = fields.Integer(required = True)
	start_date = fields.String()
	end_date = fields.String()
	description = fields.String()
	destination = fields.String()
	vacancies = fields.Integer()
	price = fields.Float()

	@validates("start_date")
	def validate_start_date(self, value):
		try:
			datetime.strptime(value, "%Y-%m-%d")
		except ValueError:
			raise ValidationError("Wrong date format")

	@validates("end_date")
	def validate_end_date(self, value):
		try:
			datetime.strptime(value, "%Y-%m-%d")
		except ValueError:
			raise ValidationError("Wrong date format")

	@validates("price")
	def validate_price(self, value):
		if value < 0:
			raise ValidationError("Price cannot be negative")

	@validates("vacancies")
	def validate_vacancies(self, value):
		if value < 0:
			raise ValidationError("Vacancies cannot be negative")

	@pre_load()
	def func(self, data, **kwargs):
		if "start_date" not in data and "end_date" not in data and "description" not in data and \
				"destination" not in data and "vacancies" not in data and "price" not in data:
			raise ValidationError("Nothing to patch")
		return data
