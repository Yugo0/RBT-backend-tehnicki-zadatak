from app.arrangements import arrangement_bp
from flask import request
from app.arrangements.schemas import ArrangementBasicResponseSchema, ArrangementFullResponseSchema, MetaSchema, \
	ArrangementsBasicResultSchema, ArrangementsFullResultSchema, UserRegistrationSchema
from app.arrangements.services import ArrangementService, UserService
from werkzeug.exceptions import NotFound, Forbidden, BadRequest
import re

arrangement_basic_response_schema = ArrangementBasicResponseSchema()
arrangement_full_response_schema = ArrangementFullResponseSchema()
meta_schema = MetaSchema()
arrangements_basic_result_schema = ArrangementsBasicResultSchema()
arrangements_full_result_schema = ArrangementsFullResultSchema()
user_registration_schema = UserRegistrationSchema()


# TODO - Remove this
@arrangement_bp.get("test")
def get_test():
	arrangement = ArrangementService.get_test()

	return arrangement_basic_response_schema.dump(arrangement)


# all arrangements - no user
@arrangement_bp.get("all")
def get_all():
	data = meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_all(data)
	return arrangements_basic_result_schema.dump(arrangements)


# all arrangements - admin, guide
@arrangement_bp.get("user/<int:id>/all")
def get_all_user(id):
	# TODO - Check if session exists
	user = UserService.get_by_id(id)

	if not user:
		raise NotFound(f"User with id {id} not found")

	if user.type == 0:
		raise Forbidden(f"Access forbidden for this account type")

	data = meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_all(data)

	return arrangements_full_result_schema.dump(arrangements)


# available arrangements - tourist
@arrangement_bp.get("user/<int:id>/available")
def get_available(id):
	# TODO - Check if session exists
	user = UserService.get_by_id(id)

	if not user:
		raise NotFound(f"User with id {id} not found")

	if user.type != 0:
		raise Forbidden(f"Access forbidden for this account type")

	data = meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_available(data, id)

	return arrangements_full_result_schema.dump(arrangements)

# user registration
@arrangement_bp.post("registration")
def register_user():
	data = user_registration_schema.load(request.json)

	if data.get("password") != data.get("password_verification"):
		raise BadRequest("Password is not verified")

	if not re.fullmatch(".+@.+", data.get("email")):
		raise BadRequest("Email is not in valid format")

	UserService.register(data)

	# TODO - Call login
	return "Call login"
