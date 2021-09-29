from app.arrangements import arrangement_bp
from flask import request, session, redirect
from app.arrangements.schemas import ArrangementBasicResponseSchema, ArrangementFullResponseSchema, MetaSchema, \
	ArrangementsBasicResultSchema, ArrangementsFullResultSchema, UserRegistrationSchema, UserLoginSchema
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
		raise Forbidden(f"Access forbidden")

	user = UserService.get_by_id(id)

	if not user:
		raise NotFound(f"User with id {id} not found")

	if user.type == 0:
		raise Forbidden(f"Access forbidden for this account type")

	data = meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_all(data)

	return arrangements_full_result_schema.dump(arrangements)


# available arrangements - tourist
@arrangement_bp.get("user/available")
def get_available():
	id = session.get("id")
	if not id:
		raise Forbidden(f"Access forbidden")

	user = UserService.get_by_id(id)

	if not user:
		raise NotFound(f"User with id {id} not found")

	if user.type != 0:
		raise Forbidden(f"Access forbidden for this account type")

	data = meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_available(data, id)

	return arrangements_full_result_schema.dump(arrangements)


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
		return redirect(f"user/available")
	else:
		return redirect(f"user/all")


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
		return redirect(f"user/available")
	else:
		return redirect(f"user/all")
