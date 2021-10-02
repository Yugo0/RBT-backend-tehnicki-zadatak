from app import db, mail
from app.arrangements.models import Arrangement, User, TypeChangeRequest, Reservation
from datetime import datetime, timedelta
import bcrypt
from werkzeug.exceptions import BadRequest, NotAcceptable, NotFound, Forbidden
from flask_mail import Message
import logging


class ArrangementService:
	@staticmethod
	def get_all(data):
		arrangements = db.session.query(Arrangement).paginate(page = data.get("page"), per_page = data.get("per_page"))
		return arrangements

	@staticmethod
	def get_available(data, id):
		from_date = datetime.now() + timedelta(days = 5)

		reservations = db.session.query(Reservation).filter(Reservation.user_id == id)
		exclude = [ex.arrangement_id for ex in reservations]

		arrangements = db.session.query(Arrangement).filter(Arrangement.start_date >= from_date)
		for ex in exclude:
			arrangements = arrangements.filter(Arrangement.id != ex)
		arrangements = arrangements.paginate(page = data.get("page"), per_page = data.get("per_page"))
		return arrangements

	@staticmethod
	def get_reservations(data, id):
		reservations = db.session.query(Arrangement.start_date, Arrangement.end_date, Arrangement.destination,
			Reservation.count, Reservation.price).join(Arrangement).filter(
			Arrangement.id == Reservation.arrangement_id, Reservation.user_id == id).paginate(
			page = data.get("page"), per_page = data.get("per_page"))
		return reservations

	@staticmethod
	def get_created(data, id):
		arrangements = db.session.query(Arrangement).filter(Arrangement.admin_id == id).paginate(
			page = data.get("page"), per_page = data.get("per_page"))
		return arrangements

	@staticmethod
	def get_designated(data, id):
		arrangements = db.session.query(Arrangement).filter(Arrangement.guide_id == id).paginate(
			page = data.get("page"), per_page = data.get("per_page"))
		return arrangements

	@staticmethod
	def reserve(data, user_id):
		arrangement = db.session.query(Arrangement).filter(Arrangement.id == data.get("arrangement_id")).one_or_none()

		from_date = datetime.now() + timedelta(days = 5)
		if arrangement.start_date < from_date:
			raise NotAcceptable("Too late to reserve")

		count = data.get("count")
		if count > arrangement.vacancies:
			raise NotAcceptable("Not enough vacancies")

		arrangement.vacancies = arrangement.vacancies - count

		price_of_one = arrangement.price
		price = count * price_of_one if count <= 3 else 3 * price_of_one + (count - 3) * price_of_one * 0.9

		reservation = Reservation(count, price, user_id, arrangement.id)

		db.session.add(reservation)
		db.session.commit()

		return reservation

	@staticmethod
	def change_description(data, user_id):
		arrangement_id = data.get("arrangement_id")
		arrangement = db.session.query(Arrangement).filter(Arrangement.id == arrangement_id).one_or_none()

		if not arrangement:
			raise NotFound(f"Arrangement with id {arrangement_id} not found")

		if arrangement.guide_id != user_id:
			raise Forbidden("Access forbidden")

		from_date = datetime.now() + timedelta(days = 5)
		if arrangement.start_date < from_date:
			raise NotAcceptable("Too late to change description")

		arrangement.description = data.get("description")
		db.session.commit()

		return arrangement

	@staticmethod
	def search_arrangements(data):
		arrangements = db.session.query(Arrangement)

		if data.get("destination"):
			arrangements = arrangements.filter(Arrangement.destination == data.get("destination"))
		if data.get("date_from"):
			date_from = datetime.strptime(data.get("date_from"), "%Y-%m-%d")
			arrangements = arrangements.filter(Arrangement.start_date > date_from)
		if data.get("date_to"):
			date_to = datetime.strptime(data.get("date_from"), "%Y-%m-%d")
			arrangements = arrangements.filter(Arrangement.end_date < date_to)

		arrangements = arrangements.paginate(page = data.get("page"), per_page = data.get("per_page"))
		return arrangements

	@staticmethod
	def cancel(data, user_id):
		arrangement_id = data.get("id")
		arrangement = db.session.query(Arrangement).filter(Arrangement.id == arrangement_id).one_or_none()

		if not arrangement:
			raise NotFound(f"Arrangement with id {arrangement_id} not found")

		if arrangement.admin_id != user_id:
			raise Forbidden("Access forbidden")

		from_date = datetime.now() + timedelta(days = 5)
		if arrangement.start_date < from_date:
			raise NotAcceptable("Too late to cancel")

		emails = []

		for reservation in arrangement.reservations:
			user = db.session.query(User).filter(User.id == reservation.user_id).one_or_none()
			emails.append(user.email)
			db.session.delete(reservation)

		db.session.delete(arrangement)
		db.session.commit()

	# TODO - This works, but not through dorm's proxy server, keep commented for now
	# msg = Message("Arrangement canceled", recipients = [emails])
	# msg.body = f"Dear customer,\n" \
	# 		   f"\n" \
	# 		   f"We must inform you that out arrangement to {arrangement.destination} due between " \
	# 		   f"{arrangement.start_date} and {arrangement.end_date} has been cancelled."
	# mail.send(msg)

	@staticmethod
	def set_guide(data, user_id):
		arrangement_id = data.get("arrangement_id")
		arrangement = db.session.query(Arrangement).filter(Arrangement.id == arrangement_id).one_or_none()

		if not arrangement:
			raise NotFound(f"Arrangement with id {arrangement_id} not found")

		if arrangement.admin_id != user_id:
			raise Forbidden("Access forbidden")

		guide_id = data.get("guide_id")
		if guide_id is not None:
			guide = db.session.query(User).filter(User.id == guide_id, User.type == 1).one_or_none()
			if not guide:
				raise NotFound(f"Guide with id {guide_id} not found")

			guide_arrangements = db.session.query(Arrangement).filter(Arrangement.guide_id == guide_id)

			for arr in guide_arrangements:
				if arrangement.end_date > arr.start_date and arrangement.start_date < arr.end_date:
					raise NotAcceptable(f"Guide with id {guide_id} is engaged in that time period")

		arrangement.guide_id = guide_id
		db.session.commit()

		return arrangement


class UserService:
	@staticmethod
	def get_by_id(id):
		user = db.session.query(User).filter(User.id == id).one_or_none()
		return user

	@staticmethod
	def get_by_username(username):
		user = db.session.query(User).filter(User.username == username).one_or_none()
		return user

	@staticmethod
	def register(data):
		name = data.get("name")
		surname = data.get("surname")
		email = data.get("email")
		username = data.get("username")
		password = data.get("password")
		type = data.get("type")

		check = db.session.query(User).filter(User.username == username).one_or_none()
		if check:
			raise BadRequest(f"Username {username} already exists")

		password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

		user = User(name, surname, email, username, password_hash, 0)

		db.session.add(user)
		db.session.flush()

		if type != 0:
			request = TypeChangeRequest(type, user.id)
			db.session.add(request)

		db.session.commit()

		return user

	@staticmethod
	def request_type_change(new_type, user_id):
		request = db.session.query(TypeChangeRequest).filter(TypeChangeRequest.user_id == user_id).one_or_none()
		if request is not None:
			request.type = new_type
			request.accepted = None
			request.comment = None
		else:
			request = TypeChangeRequest(new_type, user_id)
			db.session.add(request)

		db.session.commit()

	@staticmethod
	def get_request_by_user_id(user_id):
		request = db.session.query(TypeChangeRequest).filter(TypeChangeRequest.user_id == user_id).one_or_none()
		return request

	@staticmethod
	def get_requests(data):
		requests = db.session.query(TypeChangeRequest.id, User.username, TypeChangeRequest.type).join(User).filter(
			User.id == TypeChangeRequest.user_id).paginate(page = data.get("page"), per_page = data.get("per_page"))
		return requests

	@staticmethod
	def decide_on_request(data):
		id = data.get("id")
		request = db.session.query(TypeChangeRequest).filter(TypeChangeRequest.id == id).one_or_none()

		if not request:
			raise NotFound(f"Request with id {id} not found")

		request.accepted = data.get("accepted")
		request.comment = data.get("comment")

		if request.accepted:
			user = UserService.get_by_id(request.user_id)
			user.type = request.type

		db.session.commit()

		# TODO - This works, but not through dorm's proxy server, keep commented for now
		# if request.accepted:
		# 	msg = Message("Request accepted", recipients = [user.email])
		# 	msg.body = f"Dear {user.name} {user.surname},\n" \
		# 			   f"\n" \
		# 			   f"Your request has been accepted."
		# 	mail.send(msg)
		# else:
		# 	msg = Message("Request denied", recipients = [user.email])
		# 	msg.body = f"Dear {user.name} {user.surname},\n" \
		# 			   f"\n" \
		# 			   f"Your request has been denied, reason being:\n" \
		# 			   f"\n" \
		# 			   f"{request.comment}"
		# 	mail.send(msg)

		return request
