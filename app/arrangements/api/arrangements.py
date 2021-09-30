from app.arrangements import arrangement_bp
from flask import request, session, redirect
from app.arrangements.schemas import ArrangementBasicResponseSchema, ArrangementFullResponseSchema, MetaSchema, \
	ArrangementsBasicResultSchema, ArrangementsFullResultSchema, UserRegistrationSchema, UserLoginSchema, \
	TypeChangeRequestSchema, TypeChangeResponseSchema, ReservationsResponseSchema, ReserveRequestSchema, \
	ReserveResponseSchema
from app.arrangements.services import ArrangementService, UserService
from werkzeug.exceptions import NotFound, Forbidden, BadRequest, NotAcceptable
import re
import bcrypt

arrangement_basic_response_schema = ArrangementBasicResponseSchema()
arrangement_full_response_schema = ArrangementFullResponseSchema()
meta_schema = MetaSchema()
arrangements_basic_result_schema = ArrangementsBasicResultSchema()
arrangements_full_result_schema = ArrangementsFullResultSchema()
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
type_change_request_schema = TypeChangeRequestSchema()
type_change_response_schema = TypeChangeResponseSchema()
reservations_response_schema = ReservationsResponseSchema()
reserve_request_schema = ReserveRequestSchema()
reserve_response_schema = ReserveResponseSchema()


# all arrangements - no user
@arrangement_bp.get("all")
def get_all():
	data = meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_all(data)
	return arrangements_basic_result_schema.dump(arrangements)


# all arrangements - admin, guide
@arrangement_bp.get("user/all")
def get_all_user():
	id = session.get("id")
	if not id:
		raise Forbidden("Access forbidden")

	user = UserService.get_by_id(id)

	if not user:
		raise NotFound(f"User with id {id} not found")

	if user.type == 0:
		raise Forbidden("Access forbidden for this account type")

	data = meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_all(data)

	return arrangements_full_result_schema.dump(arrangements)


# created arrangements - admin
@arrangement_bp.get("user/created")
def get_created():
	id = session.get("id")
	if not id:
		raise Forbidden("Access forbidden")

	user = UserService.get_by_id(id)

	if not user:
		raise NotFound(f"User with id {id} not found")

	if user.type != 2:
		raise Forbidden("Access forbidden for this account type")

	data = meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_created(data, user.id)

	return arrangements_full_result_schema.dump(arrangements)


# available arrangements - tourist
@arrangement_bp.get("user/available")
def get_available():
	id = session.get("id")
	if not id:
		raise Forbidden("Access forbidden")

	user = UserService.get_by_id(id)

	if not user:
		raise NotFound(f"User with id {id} not found")

	if user.type != 0:
		raise Forbidden("Access forbidden for this account type")

	data = meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_available(data, id)

	return arrangements_full_result_schema.dump(arrangements)


# reservations - tourist
@arrangement_bp.get("user/reservations")
def get_reservations():
	id = session.get("id")
	if not id:
		raise Forbidden("Access forbidden")

	user = UserService.get_by_id(id)

	if not user:
		raise NotFound(f"User with id {id} not found")

	if user.type != 0:
		raise Forbidden("Access forbidden for this account type")

	data = meta_schema.load(request.args.to_dict())
	reservations = ArrangementService.get_reservations(data, id)

	return reservations_response_schema.dump(reservations)


# user login
@arrangement_bp.post("login")
def user_login():
	data = user_login_schema.load(request.json)
	username = data.get("username")
	user = UserService.get_by_username(username)

	if not user:
		raise NotFound(f"User with username {username} not found")

	if not bcrypt.checkpw(data.get("password").encode("utf-8"), user.password_hash.encode("utf-8")):
		raise NotAcceptable("Password doesn't match")

	session["id"] = user.id

	if user.type == 0:
		return redirect("user/available")
	else:
		return redirect("user/all")


# user logout
@arrangement_bp.get("logout")
def user_logout():
	session.pop("id", None)
	return redirect("all")


# user registration
@arrangement_bp.post("registration")
def register_user():
	data = user_registration_schema.load(request.json)

	if data.get("password") != data.get("password_verification"):
		raise BadRequest("Password is not verified")

	if not re.fullmatch(".+@.+", data.get("email")):
		raise BadRequest("Email is not in valid format")

	user = UserService.register(data)

	session["id"] = user.id

	if user.type == 0:
		return redirect("user/available")
	else:
		return redirect("user/all")


# type change request
@arrangement_bp.post("user/request_change")
def request_type_change():
	user_id = session.get("id")
	if not user_id:
		raise Forbidden(f"Access forbidden")

	data = type_change_request_schema.load(request.json)
	new_type = data.get("new_type")

	user = UserService.get_by_id(user_id)

	if new_type <= user.type:
		raise NotAcceptable("Cannot request that type")

	UserService.request_type_change(new_type, user_id)

	return redirect("user/request")


# inspect type change request
@arrangement_bp.get("user/request")
def inspect_request():
	user_id = session.get("id")
	if not user_id:
		raise Forbidden("Access forbidden")

	req = UserService.get_request_by_user_id(user_id)

	return type_change_response_schema.dump(req)


# reserve arrangement
@arrangement_bp.post("arrangement/reserve")
def reserve_arrangement():
	user_id = session.get("id")
	if not user_id:
		raise Forbidden("Access forbidden")

	data = reserve_request_schema.load(request.json)
	reservation = ArrangementService.reserve(data, user_id)

	return reserve_response_schema.dump(reservation)
