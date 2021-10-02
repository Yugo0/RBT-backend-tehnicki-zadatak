from app.arrangements import arrangement_bp
from flask import request, session, redirect
from app.arrangements.schemas import ArrangementFullResponseSchema, ArrangementsBasicResultSchema, \
	ArrangementsFullResultSchema, UserRegistrationSchema, UserLoginSchema, TypeChangeRequestSchema, \
	TypeChangeResponseSchema, ReservationsResponseSchema, ReserveRequestSchema, ReserveResponseSchema, \
	ArrangementsDescriptionChangeRequestSchema, TypeChangeListSchema, TypeChangeDecisionSchema, SearchRequestSchema, \
	IdRequestSchema, SetGuideSchema, ArrangementGuideResponseSchema, UserResponseSchema, UserUpdateSchema, \
	ArrangementUpdateRequestSchema, UserListResponseSchema, UserMetaSchema, ArrangementBasicResponseMetaSchema, \
	ArrangementFullResponseMetaSchema, ReservationResponseMetaSchema, TypeChangeViewMetaSchema
from app.arrangements.services import ArrangementService, UserService
from werkzeug.exceptions import NotFound, Forbidden, BadRequest, NotAcceptable
import bcrypt

arrangement_full_response_schema = ArrangementFullResponseSchema()
arrangements_basic_result_schema = ArrangementsBasicResultSchema()
arrangements_full_result_schema = ArrangementsFullResultSchema()
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
type_change_request_schema = TypeChangeRequestSchema()
type_change_response_schema = TypeChangeResponseSchema()
reservations_response_schema = ReservationsResponseSchema()
reserve_request_schema = ReserveRequestSchema()
reserve_response_schema = ReserveResponseSchema()
arrangement_description_change_request_schema = ArrangementsDescriptionChangeRequestSchema()
type_change_list_schema = TypeChangeListSchema()
type_change_decision_schema = TypeChangeDecisionSchema()
search_request_schema = SearchRequestSchema()
id_request_schema = IdRequestSchema()
set_guide_schema = SetGuideSchema()
arrangement_guide_response_schema = ArrangementGuideResponseSchema()
user_response_schema = UserResponseSchema()
user_update_schema = UserUpdateSchema()
arrangement_update_request_schema = ArrangementUpdateRequestSchema()
user_list_response_schema = UserListResponseSchema()
user_meta_schema = UserMetaSchema()
arrangements_basic_response_meta_schema = ArrangementBasicResponseMetaSchema()
arrangements_full_response_meta_schema = ArrangementFullResponseMetaSchema()
reservation_response_meta_schema = ReservationResponseMetaSchema()
type_change_view_meta_schema = TypeChangeViewMetaSchema()


def validate_session(user_type):
	user_id = session.get("id")
	if not user_id:
		raise Forbidden("Access forbidden")

	user = UserService.get_by_id(user_id)

	if not user:
		raise NotFound(f"User with id {user_id} not found")

	if user.type != user_type:
		raise Forbidden("Access forbidden for this account type")

	return user


# all arrangements - no user
@arrangement_bp.get("all")
def get_all():
	data = arrangements_basic_response_meta_schema.load(request.args.to_dict())
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

	data = arrangements_full_response_meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_all(data)

	return arrangements_full_result_schema.dump(arrangements)


# created arrangements - admin
@arrangement_bp.get("user/created")
def get_created():
	user = validate_session(2)

	data = arrangements_full_response_meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_created(data, user.id)

	return arrangements_full_result_schema.dump(arrangements)


# designated arrangements - guide
@arrangement_bp.get("user/designated")
def get_designated():
	user = validate_session(1)

	data = arrangements_full_response_meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_designated(data, user.id)

	return arrangements_full_result_schema.dump(arrangements)


# available arrangements - tourist
@arrangement_bp.get("user/available")
def get_available():
	user = validate_session(0)

	data = arrangements_full_response_meta_schema.load(request.args.to_dict())
	arrangements = ArrangementService.get_available(data, user.id)

	return arrangements_full_result_schema.dump(arrangements)


# reservations - tourist
@arrangement_bp.get("user/reservations")
def get_reservations():
	user = validate_session(0)

	data = reservation_response_meta_schema.load(request.args.to_dict())
	reservations = ArrangementService.get_reservations(data, user.id)

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

	user = UserService.get_by_id(user_id)

	if not user:
		raise NotFound(f"User with id {user_id} not found")

	data = type_change_request_schema.load(request.json)
	new_type = data.get("new_type")

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


# reserve arrangement - tourst
@arrangement_bp.post("arrangement/reserve")
def reserve_arrangement():
	user = validate_session(0)

	data = reserve_request_schema.load(request.json)
	reservation = ArrangementService.reserve(data, user.id)

	return reserve_response_schema.dump(reservation)


# change arrangement description - guide
@arrangement_bp.patch("arrangement/change_description")
def change_description():
	user = validate_session(0)
	data = arrangement_description_change_request_schema.load(request.json)
	user = UserService.update_user(data, user.id)
	return arrangement_full_response_schema.dump(user)


# view type change requests - admin
@arrangement_bp.get("user/type_change_requests")
def view_all_requests():
	validate_session(2)

	data = type_change_view_meta_schema.load(request.args.to_dict())
	requests = UserService.get_requests(data)

	return type_change_list_schema.dump(requests)


# view type change requests - admin
@arrangement_bp.patch("user/type_change/decide")
def decide_on_type_change():
	validate_session(2)

	data = type_change_decision_schema.load(request.json)

	if not data.get("accepted") and data.get("comment") is None:
		raise NotAcceptable("Type request denial must be commented on")

	requests = UserService.decide_on_request(data)

	return type_change_decision_schema.dump(requests)


# search arrangements - tourist
@arrangement_bp.get("arrangements/search")
def search_arrangements():
	validate_session(0)
	data = search_request_schema.load(request.args.to_dict())
	arrangements = ArrangementService.search_arrangements(data)
	return arrangements_full_result_schema.dump(arrangements)


# cancel arrangement - admin
@arrangement_bp.delete("cancel")
def cancel_arrangement():
	user = validate_session(2)
	data = id_request_schema.load(request.json)
	ArrangementService.cancel(data, user.id)
	return redirect("user/created")


# set guide - admin
@arrangement_bp.patch("arrangement/set_guide")
def set_guide():
	user = validate_session(2)
	data = set_guide_schema.load(request.json)
	arrangement = ArrangementService.set_guide(data, user.id)

	return arrangement_guide_response_schema.dump(arrangement)


# view profile - tourst
@arrangement_bp.get("user/profile")
def get_profile():
	user = validate_session(0)
	return user_response_schema.dump(user)


# update profile - tourst
@arrangement_bp.patch("user/profile")
def update_profile():
	user = validate_session(0)
	data = user_update_schema.load(request.json)
	user = UserService.update_user(data, user.id)
	return user_response_schema.dump(user)


# update arrangement - admin
@arrangement_bp.patch("arrangement/update")
def update_arrangement():
	user = validate_session(2)
	data = arrangement_update_request_schema.load(request.json)
	arrangement = ArrangementService.update_arrangement(data, user.id)
	return arrangement_full_response_schema.dump(arrangement)


# view arrangement - admin
@arrangement_bp.get("arrangement/details")
def view_arrangement():
	validate_session(2)
	data = id_request_schema.load(request.json)
	arrangement = ArrangementService.get_by_id(data.get("id"))

	if not arrangement:
		raise NotFound(f"Arrangement with id {data.get('id')} not found")

	return arrangement_full_response_schema.dump(arrangement)


# view user - admin
@arrangement_bp.get("user/details")
def view_user():
	validate_session(2)
	data = id_request_schema.load(request.json)
	user = UserService.get_by_id(data.get("id"))

	if not user:
		raise NotFound(f"User with id {data.get('id')} not found")

	return user_response_schema.dump(user)


# view user list - admin
@arrangement_bp.get("users")
def view_users():
	validate_session(2)
	data = user_meta_schema.load(request.args.to_dict())
	users = UserService.get_users(data)

	return user_list_response_schema.dump(users)


# view tourist's past arrangements - admin
@arrangement_bp.get("user/past")
def view_past_arrangements():
	validate_session(2)
	data = id_request_schema.load(request.json)
	metadata = arrangements_full_response_meta_schema.load(request.args)
	user = UserService.get_by_id(data.get("id"))

	if not user:
		raise NotFound(f"User with id {data.get('id')} not found")

	if user.type != 0:
		raise Forbidden("Access forbidden")

	arrangements = ArrangementService.get_past(metadata, user.id)

	return arrangements_full_result_schema.dump(arrangements)


# view tourist's future arrangements - admin
@arrangement_bp.get("user/future")
def view_future_arrangements():
	validate_session(2)
	data = id_request_schema.load(request.json)
	metadata = arrangements_full_response_meta_schema.load(request.args)
	user = UserService.get_by_id(data.get("id"))

	if not user:
		raise NotFound(f"User with id {data.get('id')} not found")

	if user.type != 0:
		raise Forbidden("Access forbidden")

	arrangements = ArrangementService.get_future(metadata, user.id)

	return arrangements_full_result_schema.dump(arrangements)


# view gide's arrangements - admin
@arrangement_bp.get("user/guide")
def view_guide_arrangements():
	validate_session(2)
	data = id_request_schema.load(request.json)
	metadata = arrangements_full_response_meta_schema.load(request.args)
	user = UserService.get_by_id(data.get("id"))

	if not user:
		raise NotFound(f"User with id {data.get('id')} not found")

	if user.type != 1:
		raise Forbidden("Access forbidden")

	arrangements = ArrangementService.get_guide_arrangements(metadata, user.id)

	return arrangements_full_result_schema.dump(arrangements)
